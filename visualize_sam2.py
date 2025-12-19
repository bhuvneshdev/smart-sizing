#!/usr/bin/env python3
"""
Visual demonstration of SAM2 segmentation process
"""

import cv2
import numpy as np
from measure_person_sam2 import segment_person_sam2

def visualize_sam2_process(image_path):
    """Show the SAM2 segmentation steps visually."""

    print("🔍 SAM2 Segmentation Process Visualization")
    print("=" * 50)

    # Load original image
    original = cv2.imread(image_path)
    if original is None:
        print(f"❌ Could not load image: {image_path}")
        return

    h, w = original.shape[:2]
    print(f"📸 Original image: {w}x{h} pixels")

    # Show point sampling strategy
    print("\n🎯 Point Sampling Strategy:")
    print("  1. Center point: ({}, {})".format(w//2, h//2))
    print("  2. Upper body: ({}, {})".format(w//2, h//3))
    print("  3. Middle body: ({}, {})".format(w//2, h//2))
    print("  4. Lower body: ({}, {})".format(w//2, 2*h//3))

    # Run segmentation
    print("\n🔄 Running SAM2 segmentation...")
    try:
        cropped = segment_person_sam2(image_path)

        if cropped is not original:  # Segmentation succeeded
            crop_h, crop_w = cropped.shape[:2]
            print("✅ Segmentation successful!")
            print(f"   Cropped image: {crop_w}x{crop_h} pixels")
            print(".1f")
            print(".1f")

            # Show what was removed
            removed_pixels = (h * w) - (crop_h * crop_w)
            removed_percent = (removed_pixels / (h * w)) * 100
            print(".1f"
        else:
            print("⚠️  Segmentation failed, using original image")

    except Exception as e:
        print(f"❌ Segmentation error: {e}")

    print("\n🎨 Process Summary:")
    print("   Input Image → SAM2 Model → Point Prompts → Mask Generation")
    print("   → Best Mask Selection → Bounding Box → Cropped Person")
    print("   → MediaPipe Pose → Body Measurements")

def explain_sam2_conceptually():
    """Explain SAM2 concepts in simple terms."""

    print("\n🧠 SAM2 Conceptual Explanation")
    print("=" * 50)

    print("""
🤖 SAM2 is like an intelligent "object detective" that can:

   📍 POINT PROMPTS: "Hey, what's this object at pixel (x,y)?"
   🎯 SAM2: "Let me find the boundaries of that object!"

   📦 MASK GENERATION: Creates precise outlines around objects
   🏆 BEST MASK SELECTION: Chooses the most likely person mask
   ✂️ CROPPING: Cuts out just the person from the background

   Think of it as:
   - You point at a person in a crowd
   - SAM2 draws a perfect outline around just that person
   - Everything else (background, other people, objects) gets removed
   - MediaPipe then measures the clean, isolated person

   This is why SAM2 + MediaPipe works better than MediaPipe alone!
   """)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python visualize_sam2.py <image_path>")
        print("Example: python visualize_sam2.py person.jpg")
        explain_sam2_conceptually()
        sys.exit(1)

    image_path = sys.argv[1]
    visualize_sam2_process(image_path)
    explain_sam2_conceptually()