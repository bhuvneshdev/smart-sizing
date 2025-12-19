# Smart Sizing

Single-image body width estimation using MediaPipe Pose.

## Features
- Height-based pixel scaling (nose–ankle segments with head offset).
- Shoulder, hip, multi-slice torso widths (waist=min slice, chest=upper slice adj).
- Landmark visibility aggregated to confidence score.
- Structured result dict with slice data.
- Optional annotation rendering.
- Evaluation harness for dataset calibration.
- **NEW**: REST API for both direct MediaPipe and SAM2+MediaPipe measurements

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Core Usage
```python
from measure_person import measure_person
res = measure_person("images/person1.jpg", real_height_cm=180, draw=False, verbose=True)
print(res)
```

Result keys: `shoulder_width_cm, hip_width_cm, waist_width_cm, chest_width_cm, confidence, torso_slice_widths_cm, pixel_to_cm`.

## API Usage

Start the REST API server:
```bash
python api.py
# or
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /` - API information
- `POST /measure_person` - Direct MediaPipe measurement
- `POST /measure_person_sam2` - SAM2 segmentation + MediaPipe measurement
- `GET /docs` - Interactive API documentation

### Example API Usage

```python
import requests

# Test the API
files = {'file': open('person.jpg', 'rb')}
data = {'height_cm': 183}

# Direct measurement
response = requests.post('http://localhost:8000/measure_person', files=files, data=data)
print(response.json())

# SAM2 + measurement
response = requests.post('http://localhost:8000/measure_person_sam2', files=files, data=data)
print(response.json())
```

See `API_README.md` for detailed API documentation and `test_api.py` for testing examples.

## Method Comparison

Two measurement approaches are available:

### `measure_person` (Direct MediaPipe)
- **Pros**: Fast (~1-2 seconds), simple, works on any image
- **Cons**: Sensitive to background clutter, may include non-person elements
- **Best for**: Clean images, quick measurements, development/testing

### `measure_person_sam2` (SAM2 + MediaPipe)
- **Pros**: Accurate, handles complex backgrounds, isolates person
- **Cons**: Slower (~10-30 seconds), requires SAM2 model
- **Best for**: Busy scenes, professional measurements, higher accuracy needs

See `METHOD_COMPARISON.md` for detailed comparison and `demo_comparison.py` to test both methods on the same image.

## Evaluation / Calibration
Prepare a CSV (UTF-8) named e.g. `ground_truth.csv` with columns:
```
filename,height_cm,shoulder_cm,waist_cm,chest_cm,hip_cm
person1.jpg,180,46.0,78.0,94.0,38.0
person2.jpg,172,42.5,70.0,88.0,36.5
...
```
Columns after `height_cm` are optional; missing values are ignored for error metrics.
Place images in a directory (e.g. `images/`).

Run evaluation:
```bash
python evaluate_measurements.py --images images --csv ground_truth.csv --out results.csv
```
This will:
- Run `measure_person` per image.
- Compute error metrics (MAE, MAPE where ground truth exists).
- Save per-image predictions + errors to `results.csv`.
- Print aggregate summary.

## Error Metrics
- MAE (cm) per dimension.
- MAPE (%) per dimension (skips zero or missing ground truth).
- Confidence average.

## Improving Accuracy
1. Collect 30–50 samples with tape-measured dimensions.
2. Export predictions with `--save-slices` (future extension) for modeling.
3. Fit regression: true_waist ~ min_slice + shoulder_width + hip_width.
4. Replace heuristic chest/waist adjustments with learned coefficients.
5. Consider perspective correction if pitch/yaw detected via 3D landmarks.

## Command-Line Reference
```bash
python evaluate_measurements.py -h
```

## Uncertainty (Future)
You can add jitter-based Monte Carlo: perturb landmark pixel coords ±1–2 px multiple runs to estimate std dev of widths.

## Disclaimer
Not medical grade; clothing, posture, lens distortion, and perspective affect accuracy. Calibrate for your camera & setup.
