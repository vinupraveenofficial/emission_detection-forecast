import os
from ultralytics import YOLO
import cv2

# ===== CONFIG =====
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
MODEL_PATH = "best(3).pt"
TARGET_CLASSES = ["smoke", "fire"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO(MODEL_PATH)

# Process images
image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

print(f"🟢 Processing {len(image_files)} images from {INPUT_FOLDER}...")

for filename in image_files:
    input_path = os.path.join(INPUT_FOLDER, filename)
    img = cv2.imread(input_path)
    if img is None:
        print(f"⚠️ Failed to read {filename}")
        continue

    results = model.predict(source=input_path, save=False, verbose=False)
    if len(results) == 0 or results[0].boxes is None:
        print(f"❌ No detections in {filename}")
        continue

    boxes = results[0].boxes
    annotated_img = img.copy()
    detected = False

    for box in boxes:
        try:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            if cls_name in TARGET_CLASSES:
                detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Draw bounding box only
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        except Exception:
            continue

    if detected:
        # Save only if smoke/fire detected
        out_path = os.path.join(OUTPUT_FOLDER, filename)
        cv2.imwrite(out_path, annotated_img)
        print(f"✅ Smoke detected, saved: {filename}")
    else:
        print(f"❌ No smoke/fire detected in {filename}")

print("🟢 All images processed.")
