from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from io import BytesIO
from PIL import Image
import random

app = FastAPI()

class ImageRequest(BaseModel):
    image_url: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/predict")
def predict(req: ImageRequest):
    image_url = req.image_url
    if not image_url:
        raise HTTPException(status_code=400, detail="image_url required")

    try:
        r = requests.get(image_url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch image: {e}")

    try:
        img = Image.open(BytesIO(r.content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not open image: {e}")

    pixels = list(img.getdata())
    avg_brightness = sum([sum(px)/3 for px in pixels]) / len(pixels)

    if avg_brightness > 120:
        prediction = "Healthy"
        confidence = 0.9
    else:
        prediction = "Disease Detected"
        confidence = 0.85

    return {"prediction": prediction, "confidence": confidence}
