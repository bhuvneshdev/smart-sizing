# Comparison: measure_person vs measure_person_sam2

## 📊 **Key Differences**

| Aspect | `measure_person` | `measure_person_sam2` |
|--------|------------------|----------------------|
| **Input Processing** | Direct image | SAM2 segmentation → crop → measure |
| **Dependencies** | MediaPipe only | MediaPipe + SAM2 + PyTorch |
| **Speed** | ⚡ Fast (~1-2 seconds) | 🐌 Slower (~10-30 seconds) |
| **Accuracy** | Good for clean images | Better for complex backgrounds |
| **Robustness** | Sensitive to background clutter | Handles complex scenes better |
| **Output** | Direct measurements | Cropped image + measurements |

## 🔄 **Workflow Comparison**

### `measure_person` (Direct Approach)
```
Input Image → MediaPipe Pose → Landmark Detection → Measurements
```

### `measure_person_sam2` (Segmentation Approach)
```
Input Image → SAM2 Segmentation → Person Mask → Crop to Person → MediaPipe Pose → Measurements
```

## 🎯 **When to Use Each**

### Use `measure_person` when:
- ✅ Clean, simple backgrounds
- ✅ Person is the main subject
- ✅ Speed is important
- ✅ Limited computational resources
- ✅ Testing/development

### Use `measure_person_sam2` when:
- ✅ Complex backgrounds (crowds, objects, busy scenes)
- ✅ Person partially obscured
- ✅ Higher accuracy needed
- ✅ Professional measurements
- ✅ Can afford longer processing time

## 📈 **Technical Details**

### SAM2 Segmentation Process:
1. **Point Sampling**: Tests center and multiple body positions
2. **Mask Generation**: Creates multiple segmentation masks
3. **Best Mask Selection**: Chooses largest valid mask (>10% of image)
4. **Bounding Box**: Calculates tight crop with padding
5. **Image Cropping**: Isolates person from background

### Measurement Process (Both):
1. **Pose Detection**: MediaPipe finds 33 body landmarks
2. **Height Scaling**: Uses nose-to-ankle distance with 4% head offset
3. **Width Calculations**: Shoulder, hip, and torso slice measurements
4. **Heuristics**: Waist = min slice, Chest = upper slice × 1.03

## 🧪 **Example Results**

For a person in a busy street scene:

**`measure_person`**: Might detect background objects as part of measurements
**`measure_person_sam2`**: Isolates only the person, more accurate measurements

## ⚙️ **Configuration**

Both use:
- MediaPipe Pose model complexity: 2
- Minimum detection confidence: 0.7
- 5 torso slices (30%, 40%, 50%, 60%, 70% from shoulders to hips)

## 🚀 **API Endpoints**

Your FastAPI server provides both:
- `POST /measure_person` - Direct MediaPipe
- `POST /measure_person_sam2` - SAM2 + MediaPipe

Choose based on your image complexity and speed requirements!