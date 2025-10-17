import os
import re
import time
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

# ===== CONFIG =====
REPO_ID = "praveen2049/emissionapp"  # Hugging Face repo
INPUT_FOLDER = "input"
LOG_FILE = "pre1.csv"
SCAN_INTERVAL = 5  # seconds

os.makedirs(INPUT_FOLDER, exist_ok=True)

# Initialize CSV if not exists
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Filename", "DateTime", "Latitude", "Longitude"]).to_csv(LOG_FILE, index=False)

api = HfApi()

def decode_filename(filename):
    """Extract timestamp, lat, lon from filename"""
    pattern = r"(\d{8}_\d{6})_lat([\d.]+)_lon([\d.]+)"
    match = re.search(pattern, filename)
    if match:
        ts, lat, lon = match.groups()
        return ts, float(lat), float(lon)
    return None, None, None

print("🟢 Starting to scan Hugging Face Space every 5 seconds...")

while True:
    try:
        files = api.list_repo_files(repo_id=REPO_ID, repo_type="space")
        for f in files:
            if f.endswith(".jpg"):
                final_path = os.path.join(INPUT_FOLDER, os.path.basename(f))
                if not os.path.exists(final_path):
                    # Download file (may create subfolders)
                    downloaded_path = hf_hub_download(
                        repo_id=REPO_ID,
                        filename=f,
                        repo_type="space",
                        local_dir=INPUT_FOLDER,
                        local_dir_use_symlinks=False
                    )

                    # Move file to root of INPUT_FOLDER
                    if downloaded_path != final_path:
                        os.rename(downloaded_path, final_path)

                    # Remove leftover folder if empty
                    leftover_folder = os.path.dirname(downloaded_path)
                    if leftover_folder != INPUT_FOLDER and os.path.exists(leftover_folder):
                        try:
                            os.rmdir(leftover_folder)
                        except OSError:
                            pass  # Folder not empty, ignore

                    # Decode filename
                    ts, lat, lon = decode_filename(os.path.basename(f))
                    if ts is None:
                        print(f"⚠️ Skipping file with unexpected filename: {f}")
                        continue

                    # Log CSV
                    df = pd.read_csv(LOG_FILE)
                    new_entry = pd.DataFrame([{
                        "Filename": os.path.basename(f),
                        "DateTime": ts,
                        "Latitude": lat,
                        "Longitude": lon
                    }])
                    df = pd.concat([df, new_entry], ignore_index=True)
                    df.to_csv(LOG_FILE, index=False)
                    print(f"✅ Downloaded and logged {f}")
        time.sleep(SCAN_INTERVAL)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(SCAN_INTERVAL)
