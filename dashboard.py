import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from datetime import datetime
import requests
from urllib.parse import urlencode
import threading
import time

# ==== CONFIG ====
OUTPUT_FOLDER = "output"
CSV_FILES = ["pre1.csv", "pre2.csv"]
DEFAULT_LAT, DEFAULT_LON = 30.767, 76.575
AUTO_REFRESH_INTERVAL = 5  # seconds

# Telegram Bot Config
TELEGRAM_TOKEN = "7328348344:AAHEksEEEWd4n_BtUkQKauHE0WuUq5nZARQ"
CHAT_ID = "-4941624831"
TRACK_FILE = "alerted_hotspots.txt"

# Open-Meteo Config
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_PARAMS = {
    "current_weather": "true",
    "wind_speed_unit": "kmh",
    "latitude": None,
    "longitude": None
}

# ==== FUNCTIONS ====
def send_telegram_alert(message):
    """Send a message via Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print("⚠️ Telegram error:", res.text)
    except Exception as e:
        print("⚠️ Telegram exception:", e)

def load_alerted_hotspots():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_alerted_hotspot(fname):
    with open(TRACK_FILE, "a") as f:
        f.write(f"{fname}\n")

def fetch_wind(lat, lon):
    """Fetch current wind data from Open-Meteo."""
    params = OPEN_METEO_PARAMS.copy()
    params["latitude"] = lat
    params["longitude"] = lon
    url = OPEN_METEO_BASE + "?" + urlencode(params)
    try:
        resp = requests.get(url, timeout=5).json()
        cw = resp.get("current_weather")
        if cw:
            speed = cw.get("windspeed")
            direction = cw.get("winddirection")
            return speed, direction
    except Exception as e:
        print("⚠️ Wind fetch error:", e)
    return None, None

def check_and_alert():
    """Continuously check CSVs for new hotspots and send Telegram alerts."""
    print("🟢 Background alert thread started...")
    while True:
        df_list = []
        for csv_file in CSV_FILES:
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
                df_list.append(df)

        if df_list:
            df_all = pd.concat(df_list, ignore_index=True)
            alerted = load_alerted_hotspots()

            for _, row in df_all.iterrows():
                fname = str(row.get("Filename", ""))
                if not fname or fname in alerted:
                    continue

                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                dt = row["DateTime"]

                wind_speed, wind_dir = fetch_wind(lat, lon)
                wind_speed_str = f"{wind_speed:.1f} km/h" if wind_speed else "N/A"
                wind_dir_str = f"{wind_dir:.1f}°" if wind_dir else "N/A"
                maps_link = f"https://maps.google.com/?q={lat},{lon}"

                message = (
                    "🚨 <b>Alert</b> 🚨\n"
                    "<b>Event:</b> Emission Detected\n"
                    "<b>Device ID:</b> Node_01\n"
                    f"<b>Time:</b> {dt}\n"
                    f"<b>Location:</b> {lat}° N, {lon}° E\n"
                    f"<b>Google Maps:</b> <a href='{maps_link}'>View Location</a>\n"
                    f"<b>Wind Direction:</b> {wind_dir_str}\n"
                    f"<b>Wind Speed:</b> {wind_speed_str}\n"
                )

                send_telegram_alert(message)
                print(f"✅ Alert sent for {fname}")
                save_alerted_hotspot(fname)

        time.sleep(10)  # check every 10 seconds


# ==== START BACKGROUND THREAD ====
if "alert_thread_started" not in st.session_state:
    st.session_state.alert_thread_started = True
    threading.Thread(target=check_and_alert, daemon=True).start()

# ==== STREAMLIT DASHBOARD ====
st.set_page_config(page_title="Emission Dashboard", layout="wide", page_icon="🌍")
st.title("🌍 Emission Monitoring Dashboard")

# ==== AUTO REFRESH ====
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
elif (datetime.now() - st.session_state.last_refresh).seconds > AUTO_REFRESH_INTERVAL:
    st.session_state.last_refresh = datetime.now()
    st.experimental_rerun()

# ==== LOAD DATA ====
df_list = []
for csv_file in CSV_FILES:
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
        df_list.append(df)
if df_list:
    df_all = pd.concat(df_list, ignore_index=True)
else:
    df_all = pd.DataFrame(columns=["Filename", "DateTime", "Latitude", "Longitude", "Num_Boxes", "WindSpeed_kmh"])

# ==== LAYOUT ====
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# ==== PANEL 1: Recent Output Images ====
with col1:
    st.subheader("📷 Recent Smoke Detections")
    if os.path.exists(OUTPUT_FOLDER):
        image_files = sorted(
            [os.path.join(OUTPUT_FOLDER, f) for f in os.listdir(OUTPUT_FOLDER) if f.lower().endswith((".jpg", ".png"))],
            key=os.path.getmtime, reverse=True
        )
        if image_files:
            n_images = min(len(image_files), 4)
            cols_img = st.columns(n_images)
            for i, img_path in enumerate(image_files[:n_images]):
                with cols_img[i]:
                    st.image(img_path, use_container_width=True)
        else:
            st.info("No output images yet.")
    else:
        st.warning("Output folder not found.")

# ==== PANEL 2: Geo Hotspot Map with Wind Arrows ====
with col2:
    st.subheader("🌍 Emission Hotspots Map")
    if not df_all.empty:
        df_map = df_all.groupby(["Latitude", "Longitude"]).size().reset_index(name="Count")
        fig_map = go.Figure()

        # Red hotspot circles
        fig_map.add_trace(go.Scattermapbox(
            lat=df_map["Latitude"],
            lon=df_map["Longitude"],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=df_map["Count"] * 25,
                color="red",
                opacity=0.7,
                symbol="circle"
            ),
            text=df_map["Count"],
            hoverinfo="text+lat+lon",
            name="Hotspots"
        ))

        # Fetch live wind data
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={DEFAULT_LAT}&longitude={DEFAULT_LON}&current_weather=true"
            resp = requests.get(url, timeout=5).json()
            wind_speed = resp["current_weather"]["windspeed"]
            wind_dir = resp["current_weather"]["winddirection"]

            # Draw arrow from hotspot center
            scale = 0.0015
            for _, row in df_map.iterrows():
                lat0, lon0 = row["Latitude"], row["Longitude"]
                rad = np.deg2rad(wind_dir)
                lat1 = lat0 + scale * np.cos(rad)
                lon1 = lon0 + scale * np.sin(rad)

                # Line + Arrow
                fig_map.add_trace(go.Scattermapbox(
                    lat=[lat0, lat1],
                    lon=[lon0, lon1],
                    mode="lines+markers",
                    line=dict(color="blue", width=6),
                    marker=dict(size=18, color="blue", symbol="triangle"),
                    showlegend=False
                ))
        except Exception:
            st.warning("⚠️ Could not fetch wind data")

        fig_map.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=15,
            mapbox_center={"lat": DEFAULT_LAT, "lon": DEFAULT_LON},
            margin={"l":0, "r":0, "t":0, "b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No hotspot data yet.")

# ==== PANEL 3: Emission Severity vs Wind Speed ====
with col3:
    st.subheader("📊 Emission Severity vs Wind Speed")
    if not df_all.empty and "Num_Boxes" in df_all.columns and "WindSpeed_kmh" in df_all.columns:
        df_corr = df_all.dropna(subset=["Num_Boxes", "WindSpeed_kmh"])
        if not df_corr.empty:
            fig_corr = px.scatter(df_corr, x="WindSpeed_kmh", y="Num_Boxes",
                                  title="Emission Severity vs Wind Speed")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("No valid correlation data yet.")
    else:
        st.info("No emission or wind speed data available.")

# ==== PANEL 4: Emission Count over Time ====
with col4:
    st.subheader("📈 Emission Count Over Time")
    if not df_all.empty:
        df_time = df_all.groupby(df_all["DateTime"].dt.hour).size().reset_index(name="Count")
        if not df_time.empty:
            fig_time = px.bar(df_time, x="DateTime", y="Count", text="Count", title="Emissions per Hour")
            fig_time.update_traces(textposition="outside")
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No time-series data yet.")
    else:
        st.info("No emission data yet.")

st.divider()
st.markdown("© 2025 Emission Monitoring System | Powered by AI + IoT + Open Meteo")
