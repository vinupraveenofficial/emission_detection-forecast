EMISSION HOTSPOT DETECTION AND FORECAST
AI + IoT + Open Meteo Powered Emission Monitoring System

OVERVIEW
This project provides a complete end-to-end emission monitoring solution that detects, logs, and visualizes emission hotspots (such as smoke, fire, or industrial emissions) using computer vision, IoT sensors, and live weather data.

It integrates real-time smoke detection using YOLOv8, live wind and weather data from Open Meteo, and Telegram-based alerts for fast incident response.

FEATURES

Automatic image and metadata ingestion from Hugging Face Spaces

IoT simulation for emission event generation

YOLOv8-based smoke detection pipeline

Streamlit dashboard with live visualization

Wind direction and speed overlay on emission map

Telegram group alerts for new emission detections

Historical CSV data logging (pre1.csv, pre2.csv)

PROJECT STRUCTURE
app.py - Gradio uploader for Hugging Face Space
downloader.py - Downloads data and logs to pre1.csv
iot_simulator.py - Simulated IoT data generator
detect_smoke.py - YOLOv8 emission detector
dashboard.py - Streamlit dashboard and Telegram alert system
pre1.csv - Uploaded emission data log
pre2.csv - Simulated IoT emission data log
input/ - Input images for detection
output/ - YOLO-processed emission images
alerted_hotspots.txt - Stores filenames already alerted
best(3).pt - YOLOv8 trained model
requirements.txt - Dependency list
README.md - Documentation

MODULE DESCRIPTIONS

Downloader (from Hugging Face)
File: downloader.py
Periodically checks for new uploads from your Hugging Face Space and logs them into pre1.csv.

IoT Node Simulator
File: iot_simulator.py
Simulates IoT-based emission nodes with mock location and sensor data. Logs events into pre2.csv and stores image files in the input/ folder.

Smoke Detection (YOLOv8)
File: detect_smoke.py
Detects emissions in images from input/ using YOLOv8 and stores processed detections in output/.

Streamlit Dashboard and Telegram Alerts
File: dashboard.py
Displays an interactive dashboard with:

Latest emission detections

Geospatial map with emission hotspots

Live wind overlays from Open Meteo

Graphs showing emission frequency and correlation

Telegram alert system with live weather context

TELEGRAM ALERT INTEGRATION

Step 1: Create a Telegram Bot
Open Telegram and search for @BotFather.
Run /newbot and follow the setup prompts.
You’ll receive a token that looks like:
7328348344:AAHEksEEEWd4n_BtUkQKauHE0WuUq5nZARQ

Step 2: Add Bot to a Group
Create a new Telegram group (for example, “Emission Alerts”).
Add your bot as a member and promote it to Admin.

Step 3: Retrieve Group Chat ID
Use a small Python script to get your group chat ID and note the “chat”: { "id": -XXXXXXXXXX } value.
Use this ID in the CHAT_ID variable in dashboard.py.

ALERT MESSAGE EXAMPLE

🚨 Alert 🚨
Event: Emission Detected
Device ID: Node_01
Time: 2025-10-17 14:35:21
Location: 12.9716° N, 77.5946° E
Google Maps: https://maps.google.com/?q=12.9716,77.5946
