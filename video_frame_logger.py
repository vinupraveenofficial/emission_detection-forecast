import cv2
import os
import time
import pandas as pd
from datetime import datetime
import random

# ===== CONFIG =====
VIDEO_FILE = "video.mp4"  # Replace with your video file
INPUT_FOLDER = "input"
LOG_FILE = "pre2.csv"
FRAME_INTERVAL = 2  # seconds
LAT_RANGE = (30.75, 30.78)  # around Chandigarh University
LON_RANGE = (76.57, 76.58)
MQ_MIN, MQ_MAX = 200, 800  # example MQ sensor reading range

os.makedirs(INPUT_FOLDER, exist_ok=True)

# Initialize CSV if not exists
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Filename", "DateTime", "Latitude", "Longitude", "MQ_Reading"]).to_csv(LOG_FILE, index=False)

# Open video
cap = cv2.VideoCapture(VIDEO_FILE)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

print(f"🟢 Video opened: {VIDEO_FILE}, duration: {duration:.2f}s, fps: {fps:.2f}")

frame_number = 0
next_capture_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_time_sec = frame_number / fps

    if current_time_sec >= next_capture_time:
        # Timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Random coordinates near Chandigarh University
        lat = round(random.uniform(*LAT_RANGE), 5)
        lon = round(random.uniform(*LON_RANGE), 5)
        # Random MQ reading
        mq = random.randint(MQ_MIN, MQ_MAX)

        # Filename encoding all info
        filename = f"{ts}_lat{lat}_lon{lon}_mq{mq}.jpg"
        save_path = os.path.join(INPUT_FOLDER, filename)

        # Save frame
        cv2.imwrite(save_path, frame)

        # Log CSV
        df = pd.read_csv(LOG_FILE)
        new_entry = pd.DataFrame([{
            "Filename": filename,
            "DateTime": ts,
            "Latitude": lat,
            "Longitude": lon,
            "MQ_Reading": mq
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)

        print(f"✅ Saved frame: {filename}")
        next_capture_time += FRAME_INTERVAL

    frame_number += 1

cap.release()
print("🟢 Video processing complete.")
