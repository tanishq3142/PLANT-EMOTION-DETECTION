import os
import csv
import re
import time
import serial
from datetime import datetime
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ===========================
# Configuration
# ===========================

PORT = "COM7"
BAUD_RATE = 9600
WINDOW_SIZE = 200

# ===========================
# Create output folder
# ===========================

stimulus = input("What stimulus are you adding (for example, water, poison, or music)? ").strip().lower()
stimulus = re.sub(r"[^a-z0-9]+", "_", stimulus).strip("_")

while not stimulus:
    stimulus = input("Please enter a stimulus: ").strip().lower()
    stimulus = re.sub(r"[^a-z0-9]+", "_", stimulus).strip("_")

while True:
    time_of_day = input("Time of day (morning, afternoon, or night): ").strip().lower()
    if time_of_day in {"morning", "afternoon", "night"}:
        break
    print("Please enter morning, afternoon, or night.")

while True:
    recording_time_text = input("Time (24-hour format, HH:MM): ").strip()
    try:
        recording_time = datetime.strptime(recording_time_text, "%H:%M")
        break
    except ValueError:
        print("Please enter the time in 24-hour format, for example 10:13.")

start_time = datetime.now()
date_folder = start_time.strftime("%Y-%m-%d")
output_folder = os.path.join("csv", date_folder)
os.makedirs(output_folder, exist_ok=True)

filename = (
    f"plant_{stimulus}_{time_of_day}_"
    f"{recording_time.strftime('%H')}hrs{recording_time.strftime('%M')}min.csv"
)
filepath = os.path.join(output_folder, filename)

csv_file = open(filepath, "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["timestamp", "ecg", "bpm"])

print(f"Saving to: {filepath}")

# ===========================
# Connect to Arduino
# ===========================

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)

# Clear old data
ser.reset_input_buffer()

# ===========================
# Graph setup
# ===========================

x = deque(maxlen=WINDOW_SIZE)
y = deque(maxlen=WINDOW_SIZE)

sample = 0
current_bpm = None
bpm_peak_times = deque(maxlen=10)
ecgs_for_threshold = deque(maxlen=30)
last_ecg = 0

fig, ax = plt.subplots(figsize=(10, 5))

line, = ax.plot([], [], lw=1.5)

bpm_text = ax.text(
    0.02,
    0.95,
    "BPM: --",
    transform=ax.transAxes,
    fontsize=14,
)

ax.set_title("Live ECG")
ax.set_xlabel("Sample")
ax.set_ylabel("ADC")
ax.set_ylim(0, 1023)
ax.grid(True)

# ===========================
# Update
# ===========================

def update(frame):
    global sample, current_bpm, last_ecg

    while ser.in_waiting:

        try:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()

            if not raw:
                continue

            if raw == "NaN":
                continue

            parts = raw.split(",")

            ecg = int(parts[0])

            if len(parts) > 1:
                try:
                    incoming_bpm = int(parts[1])
                except Exception:
                    incoming_bpm = None
            else:
                incoming_bpm = None

            ecgs_for_threshold.append(ecg)
            threshold = max(512, min(ecgs_for_threshold) + (max(ecgs_for_threshold) - min(ecgs_for_threshold)) * 0.5)

            if last_ecg < threshold <= ecg:
                bpm_peak_times.append(time.time())
                if len(bpm_peak_times) >= 2:
                    intervals = [
                        bpm_peak_times[i] - bpm_peak_times[i - 1]
                        for i in range(1, len(bpm_peak_times))
                    ]
                    avg_interval = sum(intervals) / len(intervals)
                    current_bpm = int(round(60.0 / avg_interval))

            last_ecg = ecg

            if incoming_bpm:
                current_bpm = incoming_bpm

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            writer.writerow([timestamp, ecg, current_bpm or 0])
            csv_file.flush()

            x.append(sample)
            y.append(ecg)

            sample += 1

        except Exception:
            continue

    line.set_data(x, y)

    ax.set_xlim(max(0, sample - WINDOW_SIZE), sample)

    bpm_text.set_text(f"BPM: {current_bpm if current_bpm is not None else 0}")

    return line, bpm_text


ani = FuncAnimation(
    fig,
    update,
    interval=20,
    cache_frame_data=False,
)

try:
    plt.show()

finally:
    print("Closing...")

    ser.close()
    csv_file.close()

    print("CSV saved.")