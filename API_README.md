# Person Measurement API

This API provides two methods for measuring person body dimensions from images:

1. **Direct MediaPipe**: Uses MediaPipe Pose directly on the uploaded image
2. **SAM2 + MediaPipe**: First segments the person using Meta's SAM2, then measures with MediaPipe

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python api.py
```

Or with uvicorn directly:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### GET /
Returns API information and available endpoints.

### POST /measure_person
Direct MediaPipe measurement.

**Parameters:**
- `file`: Image file (JPEG, PNG, etc.)
- `height_cm`: Known height of the person in centimeters

### POST /measure_person_sam2
SAM2 segmentation + MediaPipe measurement.

**Parameters:**
- `file`: Image file (JPEG, PNG, etc.)
- `height_cm`: Known height of the person in centimeters

## Usage Examples

### Using curl

```bash
# Direct MediaPipe measurement
curl -X POST "http://localhost:8000/measure_person" \
  -F "file=@person.jpg" \
  -F "height_cm=183"

# SAM2 + MediaPipe measurement
curl -X POST "http://localhost:8000/measure_person_sam2" \
  -F "file=@person.jpg" \
  -F "height_cm=183"
```

### Using Python requests

```python
import requests

# Direct measurement
files = {'file': open('person.jpg', 'rb')}
data = {'height_cm': 183}
response = requests.post('http://localhost:8000/measure_person', files=files, data=data)
print(response.json())

# SAM2 measurement
response = requests.post('http://localhost:8000/measure_person_sam2', files=files, data=data)
print(response.json())
```

## Response Format

```json
{
  "ok": true,
  "height_input_cm": 183.0,
  "pixel_to_cm": 0.123,
  "shoulder_width_cm": 45.2,
  "hip_width_cm": 38.1,
  "waist_width_cm": 32.5,
  "chest_width_cm": 46.8,
  "torso_slice_widths_cm": [46.8, 42.3, 38.9, 35.6, 32.5],
  "slice_fracs": [0.3, 0.4, 0.5, 0.6, 0.7]
}
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with testing capabilities.