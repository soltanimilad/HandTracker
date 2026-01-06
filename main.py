import cv2
import numpy as np
import mediapipe as mp
import uvicorn
import os
import urllib.request
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# --- CONFIGURATION ---
MODEL_PATH = 'hand_landmarker.task'
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
FINGER_NAMES = {4: "Thumb", 8: "Index", 12: "Middle", 16: "Ring", 20: "Pinky"}


# --- SETUP & LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Download model if missing
    if not os.path.exists(MODEL_PATH):
        print("Downloading MediaPipe model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    # Initialize MediaPipe
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.IMAGE
    )
    app.state.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
    yield
    app.state.landmarker.close()


app = FastAPI(lifespan=lifespan)

# --- CORS SETUP ---
# This allows your Django frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your Django URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/get-landmarks")
async def get_landmarks(file: UploadFile = File(...)):
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        h, w, _ = img.shape
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)

        # Detect landmarks
        result = app.state.landmarker.detect(mp_image)

        if not result.hand_landmarks:
            return {"hands": [], "width": w, "height": h}

        hand_data = []
        for hand in result.hand_landmarks:
            fingers = []
            for idx, name in FINGER_NAMES.items():
                fingers.append({
                    "name": name,
                    "x": hand[idx].x * w,
                    "y": hand[idx].y * h
                })
            hand_data.append(fingers)

        return {"hands": hand_data, "width": w, "height": h}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)