# Smart Sizing API Documentation

## How It Works

The Smart Sizing system measures body dimensions in three steps:

### Step 1: Detect Body Landmarks
**MediaPipe Pose** - an AI model from Google - identifies 33 key points on your body: shoulders, hips, knees, ankles, and more. Think of it like putting dots at every joint. For each landmark, we capture:
- **Position**: x, y pixel coordinates
- **Visibility score**: 0.0-1.0 confidence (is this joint visible?)

### Step 2: Calibrate the Scale (Pixel to CM Conversion)
Here's the magic: we use your **actual height as a reference point**. 

**Formula:**
```
pixel_to_cm = known_height_cm / (height_pixels × 1.04)
```

*Note: The 1.04 factor corrects for head tilt and posture variation (~4% difference between nose-to-ankle distance and true height)*

**Example:**
- You're 180 cm tall
- Your height spans 2000 pixels in the photo
- Calculation: 180 / (2000 × 1.04) ≈ 0.086
- Result: 1 pixel = 0.086 centimeters

### Step 3: Measure Widths
We measure your width at five different points along your torso: chest, ribcage, waist, and hips. Each measurement is converted using the calibration factor:

```
width_cm = width_pixels × pixel_to_cm
```

These measurements map directly to clothing sizes.

### Optional: SAM2 Background Removal
For complex backgrounds (outdoor photos, busy environments), we have an optional **SAM2 mode**:
- **SAM2** (Meta's Segment Anything 2) first isolates the person using 3 point prompts (head, torso, legs)
- Then we apply the same measurement process
- Slower (3-5 seconds) but more accurate in real-world conditions

---

## API Overview

The Smart Sizing system provides two REST API endpoints for measuring person body dimensions from images.

---

## Endpoint 1: `/measure_person`

### Purpose
Direct body measurement using **MediaPipe Pose only** (no segmentation)

### When to Use
- Quick measurements without background removal
- When the person is already isolated/cropped
- For speed (faster, no SAM2 processing)

### MediaPipe Pose - What It Does

**MediaPipe Pose** is Google's lightweight pose estimation solution that detects human body landmarks in real-time.

**How it works:**
- Lightweight neural network optimized for real-time performance
- Detects 33 body joints: shoulders, elbows, wrists, hips, knees, ankles, etc.
- For each landmark provides:
  - **Position**: x, y pixel coordinates
  - **Visibility score**: 0.0-1.0 confidence (is this joint visible?)
  - **Presence score**: likelihood the joint exists

**In our system:**
- Detects: nose, shoulders, hips, ankles (key points for measurement)
- Uses nose-to-ankle distance to calibrate pixel-to-centimeter conversion
- Calculates 5 body width measurements from shoulders to hips
- Visibility scores (0.999 = very confident, 0.8 = less confident)
- Returns results in ~1-2 seconds

---

## Endpoint 2: `/measure_person_sam2`

### Purpose
Body measurement with **SAM2 segmentation + MediaPipe Pose** (better accuracy)

### When to Use
- Need accurate measurements regardless of background
- Person has complex background
- Want the cropped image for inspection
- Better accuracy is priority over speed

### SAM2 (Segment Anything 2) - What It Does

**SAM2** is Meta's universal image segmentation model that intelligently detects and isolates objects in images.

**How it works:**
- Takes an image and point prompts as input (3 points: head, torso, legs)
- Deep learning model trained on millions of images understands object boundaries
- Generates a segmentation mask (binary image: 1 = person, 0 = background)
- Returns multiple mask options with confidence scores
- Selects the mask with highest confidence

**In our system:**
- Uses 3 point prompts at different heights (head, torso, legs) for full-body detection
- Removes background clutter automatically
- Crops image to just the person for cleaner analysis
- Saves cropped image for inspection/debugging
- Works with any background (outdoor, cluttered, etc.)
- Returns results in ~3-5 seconds
- Pre-processes image before MediaPipe for improved accuracy

### Processing Flow
1. **SAM2 Segmentation** - Detects person with 3 point prompts (head, torso, legs)
2. **Generate Cropped Image** - Removes background, isolates person
3. **MediaPipe Pose** - Detects landmarks on clean cropped image
4. **Calculate Measurements** - Converts pixels to centimeters using height calibration

---

## Error Handling

**400 Bad Request** - Invalid image or missing parameters
```json
{"detail": "Invalid image format"}
```

**500 Internal Server Error** - Processing failed
```json
{"detail": "Measurement failed: {error message}"}
```

**503 Service Unavailable** - SAM2 not available
```json
{"detail": "SAM2 is not available on this deployment. Use /measure_person endpoint instead."}
```
