import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ===== CONFIG =====
CSV1 = "pre1.csv"
CSV2 = "pre2.csv"
NUM_ROWS = 10
LAT_CENTER = 30.767
LON_CENTER = 76.575

os.makedirs("output", exist_ok=True)

def random_coordinates(center_lat, center_lon, spread=0.02):
    lat = center_lat + np.random.uniform(-spread, spread)
    lon = center_lon + np.random.uniform(-spread, spread)
    return round(lat, 5), round(lon, 5)

def random_timestamp():
    now = datetime.now()
    delta = timedelta(hours=random.randint(0,24), minutes=random.randint(0,59))
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")

def random_wind_speed():
    return round(random.uniform(5, 25), 1)  # km/h typical

def random_num_boxes():
    return random.randint(1,5)  # Emission severity

# Generate pre1.csv
rows1 = []
for i in range(NUM_ROWS):
    lat, lon = random_coordinates(LAT_CENTER, LON_CENTER)
    ts = random_timestamp()
    rows1.append({
        "Filename": f"{ts.replace(' ','_')}_lat{lat}_lon{lon}.jpg",
        "DateTime": ts,
        "Latitude": lat,
        "Longitude": lon,
        "Num_Boxes": random_num_boxes(),
        "WindSpeed_kmh": random_wind_speed()
    })
df1 = pd.DataFrame(rows1)
df1.to_csv(CSV1, index=False)
print(f"{CSV1} generated with {NUM_ROWS} rows.")

# Generate pre2.csv
rows2 = []
for i in range(NUM_ROWS):
    lat, lon = random_coordinates(LAT_CENTER, LON_CENTER)
    ts = random_timestamp()
    rows2.append({
        "Filename": f"{ts.replace(' ','_')}_lat{lat}_lon{lon}.jpg",
        "DateTime": ts,
        "Latitude": lat,
        "Longitude": lon,
        "Num_Boxes": random_num_boxes(),
        "WindSpeed_kmh": random_wind_speed()
    })
df2 = pd.DataFrame(rows2)
df2.to_csv(CSV2, index=False)
print(f"{CSV2} generated with {NUM_ROWS} rows.")
