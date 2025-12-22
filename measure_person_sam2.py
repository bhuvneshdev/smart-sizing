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

# --- SAM 2 segmentation ---
def segment_person_sam2(image_path):
    """Segment person using SAM 2 and crop to bounding box."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Build SAM 2 model
    sam2_model = build_sam2(SAM2_CONFIG, SAM2_CHECKPOINT, device='cpu')
    predictor = SAM2ImagePredictor(sam2_model)
    
    predictor.set_image(image_rgb)
    
    # Use automatic mask generation to find the person
    # Try multiple strategies: center point, and if that fails, try automatic
    h, w = image.shape[:2]
    
    # Strategy 1: Try center point
    input_point = np.array([[w//2, h//2]])
    input_label = np.array([1])
    
    masks, scores, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True  # Get multiple masks to choose the best
    )
    
    # Select the largest mask (likely the person)
    largest_idx = np.argmax([m.sum() for m in masks])
    mask = masks[largest_idx].astype(bool)
    
    # Check if mask is reasonable (should be at least 10% of image)
    mask_ratio = mask.sum() / (h * w)
    if mask_ratio < 0.1:
        print(f"Warning: Mask too small ({mask_ratio:.1%} of image), trying different strategy...")
        # Try points at common person locations (upper-middle, middle, lower-middle)
        test_points = np.array([
            [w//2, h//3],   # upper body
            [w//2, h//2],   # torso  
            [w//2, 2*h//3]  # lower body
        ])
        best_mask = None
        best_size = 0
        
        for point in test_points:
            masks_temp, _, _ = predictor.predict(
                point_coords=point.reshape(1, 2),
                point_labels=np.array([1]),
                multimask_output=True
            )
            for m in masks_temp:
                if m.sum() > best_size:
                    best_size = m.sum()
                    best_mask = m
        
        if best_mask is not None and best_size > 0:
            mask = best_mask.astype(bool)
        else:
            print("Warning: SAM 2 segmentation failed, using original image")
            return image
    
    # Find bounding box of the mask
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    if not rows.any() or not cols.any():
        # No valid mask, return original image
        print("Warning: SAM 2 segmentation failed, using original image")
        return image
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    # Add generous padding to ensure full body (head and feet) is included
    # More padding vertically (50%) to capture head/feet, less horizontally (20%)
    padding_vertical = int(0.50 * (rmax - rmin))
    padding_horizontal = int(0.20 * (cmax - cmin))
    rmin = max(0, rmin - padding_vertical)
    rmax = min(h, rmax + padding_vertical)
    cmin = max(0, cmin - padding_horizontal)
    cmax = min(w, cmax + padding_horizontal)
    
    # Crop image to bounding box
    cropped = image[rmin:rmax, cmin:cmax]
    
    # Debug: save cropped image
    import os
    debug_path = image_path.replace('.png', '_cropped.png').replace('.jpeg', '_cropped.jpeg').replace('.jpg', '_cropped.jpg')
    cv2.imwrite(debug_path, cropped)
    print(f"Saved cropped image to {debug_path}")
    print(f"Original size: {w}x{h}, Cropped size: {cropped.shape[1]}x{cropped.shape[0]}")
    print(f"Bbox: r[{rmin}-{rmax}], c[{cmin}-{cmax}]")
    
    return cropped

# --- MediaPipe measurement ---
def measure_person_image(image, real_height_cm=177.0, draw=True, verbose=True):
    h, w = image.shape[:2]
    
    # Convert to MediaPipe Image format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

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
        return np.array([lm.x * w, lm.y * h])
    
    nose = get(0)  # NOSE
    l_ankle = get(27)  # LEFT_ANKLE
    r_ankle = get(28)  # RIGHT_ANKLE
    l_shoulder = get(11)  # LEFT_SHOULDER
    r_shoulder = get(12)  # RIGHT_SHOULDER
    l_hip = get(23)  # LEFT_HIP
    r_hip = get(24)  # RIGHT_HIP
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
