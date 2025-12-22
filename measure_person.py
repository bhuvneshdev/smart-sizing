"""Person measurement utilities using MediaPipe Pose.

NOTE: Accuracy depends on camera perspective (should ideally be fronto-parallel), lens distortion,
and clothing. For improved results, collect calibration data and fit learned ratios.
"""

import cv2
import mediapipe as mp
import numpy as np
from matplotlib import pyplot as plt

# Use Tasks API
from mediapipe.tasks.python.vision import PoseLandmarker
from mediapipe.tasks.python import BaseOptions
import urllib.request
import tempfile
import os

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

def _landmark_px(lms, idx, w, h):
    lm = lms[idx]
    return np.array([lm.x * w, lm.y * h]), lm.visibility

def _landmark_px(lms, idx, w, h):
    lm = lms[idx]
    return np.array([lm.x * w, lm.y * h]), lm.visibility

def measure_person(
    image_path: str = "person.jpg",
    real_height_cm: float = 177.0,
    model_complexity: int = 2,
    min_detection_confidence: float = 0.7,
    draw: bool = True,
    verbose: bool = True,
    return_image: bool = False,
):
    """Compute body width estimates from a single full-body image.

    Parameters
    ----------
    image_path : str
        Path to input image (full body, upright, frontal ideally).
    real_height_cm : float
        Known true height of the subject in centimeters.
    model_complexity : int
        MediaPipe pose model complexity (higher = more accurate, slower).
    min_detection_confidence : float
        Minimum detection confidence for pose inference.
    draw : bool
        Whether to render annotated image (matplotlib).
    verbose : bool
        Whether to print summary measurements.
    return_image : bool
        If True, include annotated image (RGB array) in the result dict.

    Returns
    -------
    dict
        Contains measurement values (in cm), intermediate data and confidence.
        On failure: {"ok": False, "error": str}.
    """

    image = cv2.imread(image_path)
    if image is None:
        return {"ok": False, "error": f"Image not found: {image_path}"}

    h, w = image.shape[:2]
    
    # Convert to MediaPipe Image format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    # Create pose landmarker
    pose_landmarker = create_pose_landmarker()
    
    # Detect pose
    results = pose_landmarker.detect(mp_image)

    if not results.pose_landmarks:
        return {"ok": False, "error": "No person detected"}

    # Get the first (and typically only) pose
    lms = results.pose_landmarks[0]

    def get(idx):
        return _landmark_px(lms, idx, w, h)

    # Required landmarks (2D only for this pass)
    nose, nose_v = get(0)  # NOSE
    l_ankle, la_v = get(27)  # LEFT_ANKLE
    r_ankle, ra_v = get(28)  # RIGHT_ANKLE
    l_shoulder, ls_v = get(11)  # LEFT_SHOULDER
    r_shoulder, rs_v = get(12)  # RIGHT_SHOULDER
    l_hip, lh_v = get(23)  # LEFT_HIP
    r_hip, rh_v = get(24)  # RIGHT_HIP

    visibility = {
        "nose": nose_v,
        "l_ankle": la_v,
        "r_ankle": ra_v,
        "l_shoulder": ls_v,
        "r_shoulder": rs_v,
        "l_hip": lh_v,
        "r_hip": rh_v,
    }

    height_segments = []
    if nose_v > 0.5 and la_v > 0.5:
        height_segments.append(np.linalg.norm(nose - l_ankle))
    if nose_v > 0.5 and ra_v > 0.5:
        height_segments.append(np.linalg.norm(nose - r_ankle))
    if not height_segments:
        return {"ok": False, "error": "Insufficient reliable landmarks for height", "visibility": visibility}

    nose_to_ankle_px = float(np.mean(height_segments))
    # Approximate top-of-head offset (nose is slightly below vertex) ~4%
    effective_height_px = nose_to_ankle_px * 1.04
    px_to_cm = real_height_cm / effective_height_px

    shoulder_width_cm = np.linalg.norm(l_shoulder - r_shoulder) * px_to_cm
    hip_width_cm = np.linalg.norm(l_hip - r_hip) * px_to_cm

    # Multi-slice torso sampling between shoulders & hips (linear interpolation)
    slice_fracs = [0.30, 0.40, 0.50, 0.60, 0.70]
    slice_widths_cm = []
    for f in slice_fracs:
        left_point = l_shoulder * (1 - f) + l_hip * f
        right_point = r_shoulder * (1 - f) + r_hip * f
        slice_widths_cm.append(np.linalg.norm(left_point - right_point) * px_to_cm)

    # Waist heuristic: minimal width slice (inward taper assumption)
    waist_width_cm = float(min(slice_widths_cm))
    # Chest: near upper slice with mild outward adjustment
    chest_width_cm = slice_widths_cm[0] * 1.03

    result = {
        "ok": True,
        "height_input_cm": real_height_cm,
        "pixel_to_cm": px_to_cm,
        "shoulder_width_cm": shoulder_width_cm,
        "hip_width_cm": hip_width_cm,
        "waist_width_cm": waist_width_cm,
        "chest_width_cm": chest_width_cm,
        "torso_slice_widths_cm": slice_widths_cm,
        "slice_fracs": slice_fracs,
        "visibility": visibility,
    }

    if verbose:
        print(f"Height (input)   : {real_height_cm:.1f} cm")
        print(f"Shoulder width   : {shoulder_width_cm:.1f} cm")
        print(f"Chest width      : {chest_width_cm:.1f} cm")
        print(f"Waist width      : {waist_width_cm:.1f} cm")
        print(f"Hip width        : {hip_width_cm:.1f} cm")

    if draw:
        annotated = image.copy()
        # Draw landmarks manually since Tasks API drawing is different
        for landmark in lms:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(annotated, (x, y), 5, (0, 255, 0), -1)
        
        cv2.putText(
            annotated,
            f"Height {real_height_cm:.1f}cm",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            annotated,
            f"Shoulders {shoulder_width_cm:.1f}cm Waist {waist_width_cm:.1f}cm",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            2,
        )
        plt.figure(figsize=(7, 10))
        plt.imshow(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.show()
        if return_image:
            result["annotated_image_rgb"] = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Measure person widths from a single image using MediaPipe Pose")
    parser.add_argument("image", help="Path to input image (e.g. 1.jpeg)")
    parser.add_argument("height_cm", type=float, help="Known subject height in centimeters (e.g. 183)")
    parser.add_argument("--draw", action="store_true", help="Display annotated image")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    args = parser.parse_args()

    output = measure_person(str(args.image), real_height_cm=float(args.height_cm), draw=args.draw, verbose=(not args.quiet))
    if not output.get("ok"):
        print("Error:", output.get("error"))
        raise SystemExit(1)

    # Print concise results only when --quiet is used
    # If not quiet, `measure_person` already printed verbose output
    if args.quiet:
        print(f"Height (input)   : {output.get('height_input_cm'):.1f} cm")
        print(f"Shoulder width   : {output.get('shoulder_width_cm'):.1f} cm")
        print(f"Chest width      : {output.get('chest_width_cm'):.1f} cm")
        print(f"Waist width      : {output.get('waist_width_cm'):.1f} cm")
        print(f"Hip width        : {output.get('hip_width_cm'):.1f} cm")
