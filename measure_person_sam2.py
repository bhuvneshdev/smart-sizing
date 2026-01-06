"""
Person measurement pipeline using SAM 2 segmentation + MediaPipe Pose.

Steps:
1. Use SAM 2 to segment the person from the image.
2. Crop/mask the image to just the person.
3. Run MediaPipe Pose on the cleaned image for measurements.

Requires:
- sam2 (Meta's Segment Anything 2)
- mediapipe
- opencv-python
- numpy
- matplotlib

Usage:
    python3 measure_person_sam2.py person.jpg 183
"""

import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
import mediapipe as mp

# Use Tasks API
from mediapipe.tasks.python.vision import PoseLandmarker
from mediapipe.tasks.python import BaseOptions
import urllib.request
import os

try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
except ImportError:
    print("Please install sam2: pip install sam2")
    sys.exit(1)

# Create pose landmarker (reuse the same function)
def create_pose_landmarker():
    """Create pose landmarker with downloaded model"""
    # Download the pose model if not already downloaded
    model_url = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'pose_landmarker_lite.task')
    
    if not os.path.exists(model_path):
        print("Downloading pose model...")
        urllib.request.urlretrieve(model_url, model_path)
        print("Model downloaded successfully")
    
    return PoseLandmarker.create_from_model_path(model_path)

# SAM 2 checkpoint - update this path based on your downloaded model
SAM2_CHECKPOINT = "sam2.1_hiera_small.pt"
SAM2_CONFIG = "configs/sam2.1/sam2.1_hiera_s.yaml"

# --- SAM 2 segmentation (point-based) ---
def segment_person_sam2(image_path):
    """Segment person using SAM 2 with center point prompt."""
    import os
    
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(image_path)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = image.shape[:2]

    print(f"[SAM2] Loading model from {SAM2_CONFIG} and {SAM2_CHECKPOINT}")
    
    # Build SAM 2 model
    sam2_model = build_sam2(SAM2_CONFIG, SAM2_CHECKPOINT, device="cpu")
    predictor = SAM2ImagePredictor(sam2_model)

    print(f"[SAM2] Setting image ({w}x{h})")
    predictor.set_image(image_rgb)

    # 🔹 Use multiple points to capture entire person (head, torso, legs)
    point_coords = np.array([
        [w // 2, h // 4],      # Head area
        [w // 2, h // 2],      # Torso area
        [w // 2, 3 * h // 4],  # Legs area
    ])
    point_labels = np.array([1, 1, 1])  # All foreground
    
    print(f"[SAM2] Predicting with {len(point_coords)} points: head, torso, legs")
    
    try:
        masks, scores, logits = predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True
        )
        
        print(f"[SAM2] Got {len(masks)} masks with scores: {scores}")
        
        # Use the best (highest confidence) mask
        best_idx = np.argmax(scores)
        mask = masks[best_idx].astype(bool)
        
        print(f"[SAM2] Selected mask {best_idx} with score {scores[best_idx]:.4f}")
        
    except Exception as e:
        print(f"[SAM2] Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        print("[SAM2] Returning original image")
        return image

    # 🔹 Crop to bounding box with padding
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    if not rows.any() or not cols.any():
        print("[SAM2] No valid mask found, returning original image")
        return image
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    # Minimal padding - SAM2 with multiple points should capture full person
    padding_v = int(0.05 * (rmax - rmin))  # 5% padding
    padding_h = int(0.05 * (cmax - cmin))  # 5% padding

    rmin = max(0, rmin - padding_v)
    rmax = min(h, rmax + padding_v)
    cmin = max(0, cmin - padding_h)
    cmax = min(w, cmax + padding_h)

    cropped = image[rmin:rmax, cmin:cmax]
    
    # Save cropped image to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.basename(image_path)
    base_name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    
    # Clean up temp filename if it's from API (remove timestamp prefix)
    if base_name.startswith("temp_"):
        # Extract just the original filename part after timestamp and underscore
        parts = base_name.split("_", 2)  # Split on first two underscores
        if len(parts) >= 3:
            base_name = parts[2]  # Get the original filename
    
    cropped_path = os.path.join(script_dir, f"{base_name}_cropped{ext}")
    
    success = cv2.imwrite(cropped_path, cropped)
    if success:
        print(f"[SAM2] ✅ Saved cropped image to {cropped_path}")
        print(f"[SAM2]    Original: {w}x{h}, Cropped: {cropped.shape[1]}x{cropped.shape[0]}")
    else:
        print(f"[SAM2] ❌ Failed to save cropped image to {cropped_path}")

    return cropped

# --- MediaPipe measurement ---
def measure_person_image(image, real_height_cm=177.0, draw=True, verbose=True):
    h, w = image.shape[:2]
    
    # Convert BGR to RGB if needed (cv2 reads in BGR, MediaPipe expects RGB)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Convert to MediaPipe Image format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # Create pose landmarker
    pose_landmarker = create_pose_landmarker()
    
    # Detect pose
    results = pose_landmarker.detect(mp_image)
    
    if not results.pose_landmarks:
        print("No person detected!")
        return None
    
    # Get the first (and typically only) pose
    lms = results.pose_landmarks[0]
    
    def get(idx):
        lm = lms[idx]
        return np.array([lm.x * w, lm.y * h]), lm.visibility
    
    nose, nose_v = get(0)  # NOSE
    l_ankle, la_v = get(27)  # LEFT_ANKLE
    r_ankle, ra_v = get(28)  # RIGHT_ANKLE
    l_shoulder, ls_v = get(11)  # LEFT_SHOULDER
    r_shoulder, rs_v = get(12)  # RIGHT_SHOULDER
    l_hip, lh_v = get(23)  # LEFT_HIP
    r_hip, rh_v = get(24)  # RIGHT_HIP
    
    # Capture visibility scores
    visibility = {
        "nose": float(nose_v),
        "l_ankle": float(la_v),
        "r_ankle": float(ra_v),
        "l_shoulder": float(ls_v),
        "r_shoulder": float(rs_v),
        "l_hip": float(lh_v),
        "r_hip": float(rh_v),
    }
    
    height_px = (np.linalg.norm(nose - l_ankle) + np.linalg.norm(nose - r_ankle)) / 2
    px_to_cm = real_height_cm / (height_px * 1.04)
    shoulder_width = np.linalg.norm(l_shoulder - r_shoulder) * px_to_cm
    hip_bone_width = np.linalg.norm(l_hip - r_hip) * px_to_cm
    slice_fracs = [0.30, 0.40, 0.50, 0.60, 0.70]
    slice_widths_cm = []
    for f in slice_fracs:
        left_point = l_shoulder * (1 - f) + l_hip * f
        right_point = r_shoulder * (1 - f) + r_hip * f
        slice_widths_cm.append(np.linalg.norm(left_point - right_point) * px_to_cm)
    waist_width = float(min(slice_widths_cm))
    chest_approx = slice_widths_cm[0] * 1.03
    if verbose:
        print(f"Height (input)   : {real_height_cm:.1f} cm")
        print(f"Shoulder width   : {shoulder_width:.1f} cm")
        print(f"Chest width      : {chest_approx:.1f} cm")
        print(f"Waist width      : {waist_width:.1f} cm")
        print(f"Hip bone width   : {hip_bone_width:.1f} cm\n")
    if draw:
        annotated = image.copy()
        # Draw landmarks manually since Tasks API drawing is different
        for landmark in lms:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(annotated, (x, y), 5, (0, 255, 0), -1)
        
        plt.figure(figsize=(7, 10))
        plt.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.show()
    return {
        "shoulder_width_cm": shoulder_width,
        "hip_bone_width_cm": hip_bone_width,
        "waist_width_cm": waist_width,
        "chest_width_cm": chest_approx,
        "slice_widths_cm": slice_widths_cm,
        "px_to_cm": px_to_cm,
        "visibility": visibility,
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 measure_person_sam2.py <image_path> <real_height_cm>")
        sys.exit(1)
    image_path = sys.argv[1]
    real_height_cm = float(sys.argv[2])
    print("Segmenting person with SAM 2...")
    masked_img = segment_person_sam2(image_path)
    print("Measuring with MediaPipe...")
    result = measure_person_image(masked_img, real_height_cm=real_height_cm, draw=True, verbose=True)
    print("Result:", result)
