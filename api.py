"""
Person Measurement API using FastAPI.

Provides two measurement endpoints:
1. /measure_person - Direct MediaPipe measurement
2. /measure_person_sam2 - SAM2 segmentation + MediaPipe measurement

Usage:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""

import io
import sys
from typing import Optional
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import measurement functions
from measure_person import measure_person as measure_person_basic

# Try to import SAM2 functions (optional)
try:
    from measure_person_sam2 import segment_person_sam2, measure_person_image
    SAM2_AVAILABLE = True
except ImportError:
    print("⚠️  SAM2 not available - SAM2 endpoints will return error")
    SAM2_AVAILABLE = False
    segment_person_sam2 = None
    measure_person_image = None

app = FastAPI(
    title="Person Measurement API",
    description="API for measuring person body dimensions using MediaPipe Pose and SAM2 segmentation",
    version="1.0.0"
)

class MeasurementResponse(BaseModel):
    ok: bool
    error: Optional[str] = None
    height_input_cm: Optional[float] = None
    pixel_to_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    hip_width_cm: Optional[float] = None
    waist_width_cm: Optional[float] = None
    chest_width_cm: Optional[float] = None
    torso_slice_widths_cm: Optional[list] = None
    slice_fracs: Optional[list] = None
    visibility: Optional[dict] = None

def image_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert uploaded image bytes to OpenCV format."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image format")
    return img

@app.post("/measure_person", response_model=MeasurementResponse)
async def measure_person_endpoint(
    file: UploadFile = File(...),
    height_cm: float = Form(..., description="Known subject height in centimeters")
):
    """
    Measure person dimensions using MediaPipe Pose directly.

    - **file**: Image file (JPEG, PNG, etc.)
    - **height_cm**: Known height of the person in centimeters
    """
    try:
        # Read image
        image_bytes = await file.read()
        img = image_to_cv2(image_bytes)

        # Save temporarily for measure_person function (it expects a file path)
        temp_path = f"/tmp/temp_{file.filename}"
        cv2.imwrite(temp_path, img)

        # Measure
        result = measure_person_basic(
            image_path=temp_path,
            real_height_cm=height_cm,
            draw=False,  # Don't show plots in API
            verbose=False,  # Don't print to console
            return_image=False  # Don't return image data
        )

        # Clean up temp file
        import os
        os.remove(temp_path)

        return MeasurementResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Measurement failed: {str(e)}")

@app.post("/measure_person_sam2", response_model=MeasurementResponse)
async def measure_person_sam2_endpoint(
    file: UploadFile = File(...),
    height_cm: float = Form(..., description="Known subject height in centimeters")
):
    """
    Measure person dimensions using SAM2 segmentation + MediaPipe Pose.

    - **file**: Image file (JPEG, PNG, etc.)
    - **height_cm**: Known height of the person in centimeters
    """
    if not SAM2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="SAM2 is not available on this deployment. Use /measure_person endpoint instead."
        )

    try:
        # Read image
        image_bytes = await file.read()
        img = image_to_cv2(image_bytes)

        # Save temporarily for SAM2 function (it expects a file path)
        temp_path = f"/tmp/temp_{file.filename}"
        cv2.imwrite(temp_path, img)

        # Segment with SAM2
        segmented_img = segment_person_sam2(temp_path)

        # Measure with MediaPipe
        result = measure_person_image(
            segmented_img,
            real_height_cm=height_cm,
            draw=False,  # Don't show plots in API
            verbose=False  # Don't print to console
        )

        # Clean up temp file
        import os
        os.remove(temp_path)

        if result is None:
            return MeasurementResponse(ok=False, error="No person detected in segmented image")

        # Convert result to match the expected format
        formatted_result = {
            "ok": True,
            "height_input_cm": height_cm,
            "pixel_to_cm": result.get("px_to_cm"),
            "shoulder_width_cm": result.get("shoulder_width_cm"),
            "hip_width_cm": result.get("hip_bone_width_cm"),  # Note: different key name
            "waist_width_cm": result.get("waist_width_cm"),
            "chest_width_cm": result.get("chest_width_cm"),
            "torso_slice_widths_cm": result.get("slice_widths_cm"),
            "slice_fracs": [0.30, 0.40, 0.50, 0.60, 0.70],  # Default slice fractions
        }

        return MeasurementResponse(**formatted_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAM2 measurement failed: {str(e)}")

@app.get("/")
async def root():
    """API information and available endpoints."""
    endpoints = {
        "/measure_person": "Direct MediaPipe measurement",
        "/docs": "Interactive API documentation"
    }

    if SAM2_AVAILABLE:
        endpoints["/measure_person_sam2"] = "SAM2 segmentation + MediaPipe measurement"
    else:
        endpoints["/measure_person_sam2"] = "SAM2 segmentation + MediaPipe measurement (NOT AVAILABLE)"

    return {
        "message": "Person Measurement API",
        "endpoints": endpoints,
        "sam2_available": SAM2_AVAILABLE,
        "usage": "Upload an image with known height to get body measurements"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)