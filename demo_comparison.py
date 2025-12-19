#!/usr/bin/env python3
"""
Demo script showing the difference between measure_person and measure_person_sam2
"""

import cv2
import numpy as np
from measure_person import measure_person
from measure_person_sam2 import segment_person_sam2, measure_person_image

def demo_comparison(image_path, height_cm=180):
    """Demonstrate both measurement approaches on the same image."""

    print("=" * 60)
    print("PERSON MEASUREMENT METHOD COMPARISON")
    print("=" * 60)

    print(f"\n📸 Testing image: {image_path}")
    print(f"📏 Known height: {height_cm} cm")

    # Method 1: Direct MediaPipe
    print("\n" + "🔹" * 30)
    print("METHOD 1: Direct MediaPipe (measure_person)")
    print("🔹" * 30)

    try:
        result1 = measure_person(
            image_path=image_path,
            real_height_cm=height_cm,
            draw=False,  # Don't show plots in demo
            verbose=True
        )

        if result1.get("ok"):
            print("✅ Success!")
            print(f"   Shoulder width: {result1['shoulder_width_cm']:.1f} cm")
            print(f"   Chest width:    {result1['chest_width_cm']:.1f} cm")
            print(f"   Waist width:    {result1['waist_width_cm']:.1f} cm")
            print(f"   Hip width:      {result1['hip_width_cm']:.1f} cm")
        else:
            print(f"❌ Failed: {result1.get('error')}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Method 2: SAM2 + MediaPipe
    print("\n" + "🤖" * 30)
    print("METHOD 2: SAM2 Segmentation + MediaPipe (measure_person_sam2)")
    print("🤖" * 30)

    try:
        print("🔄 Step 1: Segmenting person with SAM2...")
        segmented_img = segment_person_sam2(image_path)

        print("🔄 Step 2: Measuring with MediaPipe...")
        result2 = measure_person_image(
            segmented_img,
            real_height_cm=height_cm,
            draw=False,  # Don't show plots in demo
            verbose=True
        )

        if result2:
            print("✅ Success!")
            print(f"   Shoulder width: {result2['shoulder_width_cm']:.1f} cm")
            print(f"   Chest width:    {result2['chest_width_cm']:.1f} cm")
            print(f"   Waist width:    {result2['waist_width_cm']:.1f} cm")
            print(f"   Hip width:      {result2['hip_bone_width_cm']:.1f} cm")
        else:
            print("❌ Failed: No person detected in segmented image")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Comparison
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)

    if result1.get("ok") and result2:
        diff_shoulder = abs(result1['shoulder_width_cm'] - result2['shoulder_width_cm'])
        diff_waist = abs(result1['waist_width_cm'] - result2['waist_width_cm'])

        print("Shoulder width difference: {:.1f} cm".format(diff_shoulder))
        print("Waist width difference:    {:.1f} cm".format(diff_waist))

        if diff_shoulder > 5 or diff_waist > 5:
            print("⚠️  Large differences suggest background interference in direct method")
        else:
            print("✅ Measurements are consistent between methods")

    print("\n💡 Key Insights:")
    print("   • Direct method is faster but may include background")
    print("   • SAM2 method is slower but more accurate for complex scenes")
    print("   • Choose based on image complexity and speed requirements")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python demo_comparison.py <image_path> [height_cm]")
        print("Example: python demo_comparison.py person.jpg 183")
        sys.exit(1)

    image_path = sys.argv[1]
    height_cm = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0

    demo_comparison(image_path, height_cm)