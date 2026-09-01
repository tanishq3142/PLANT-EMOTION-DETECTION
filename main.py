import argparse
import csv
import os
import re
import time
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt
import serial
from matplotlib.animation import FuncAnimation

WINDOW_SIZE = 200
FIELDS = ["session_id", "timestamp", "elapsed_seconds", "sample_number", "stimulus",
          "time_of_day", "ecg", "bpm"]


def clean_label(value):
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def get_label(prompt, supplied=None):
    value = clean_label(supplied or "")
    while not value:
        value = clean_label(input(prompt))
        if not value:
            print("A value is required.")
    return value


def period(hour):
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def arguments():
    parser = argparse.ArgumentParser(description="Record plant bio-potential data from Arduino/AD8232")
    parser.add_argument("--port", default="COM7", help="Arduino port (default: COM7)")
    parser.add_argument("--baud", type=int, default=9600, help="Serial baud rate")
    parser.add_argument("--stimulus", help="Stimulus label; skips its prompt")
    return parser.parse_args()


def main():
    args = arguments()
    stimulus = get_label("Stimulus (water, music, touch, none, etc.): ", args.stimulus)
    started_at = datetime.now().astimezone()
    time_of_day = period(started_at.hour)
    session_id = started_at.strftime("%Y%m%dT%H%M%S%z")
    folder = os.path.join("csv", started_at.strftime("%Y-%m-%d"))
    os.makedirs(folder, exist_ok=True)
    name = f"plant_{stimulus}_{time_of_day}_{started_at:%Hhrs%Mmin%Ssec}.csv"
    path = os.path.join(folder, name)

    print(f"Session: {session_id}")
    print(f"Local start: {started_at.isoformat(timespec='seconds')} ({time_of_day})")
    print(f"Saving to: {path}")

    connection = None
    output = None
    try:
        connection = serial.Serial(args.port, args.baud, timeout=1)
        time.sleep(2)
        connection.reset_input_buffer()
        output = open(path, "w", newline="", encoding="utf-8")
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        output.flush()

        samples = deque(maxlen=WINDOW_SIZE)
        values = deque(maxlen=WINDOW_SIZE)
        recent_values = deque(maxlen=30)
        peaks = deque(maxlen=10)
        state = {"number": 0, "rate": None, "previous": 0}
        monotonic_start = time.perf_counter()

        figure, axis = plt.subplots(figsize=(10, 5))
        line, = axis.plot([], [], linewidth=1.5)
        rate_text = axis.text(0.02, 0.95, "Event rate: --/min", transform=axis.transAxes, fontsize=14)
        axis.set(title=f"Plant bio-potential: {stimulus}", xlabel="Sample", ylabel="ADC count")
        axis.set_ylim(0, 1023)
        axis.grid(True)

        def update(_frame):
            while connection.in_waiting:
                try:
                    raw = connection.readline().decode("utf-8", errors="ignore").strip()
                    if not raw or raw.lower() == "nan":
                        continue
                    parts = raw.split(",")
                    ecg = int(parts[0])
                    if not 0 <= ecg <= 1023:
                        continue
                    incoming_rate = None
                    if len(parts) > 1:
                        try:
                            incoming_rate = int(parts[1])
                        except ValueError:
                            pass

                    recent_values.append(ecg)
                    threshold = max(512, min(recent_values) + (max(recent_values) - min(recent_values)) * 0.5)
                    now = time.perf_counter()
                    if state["previous"] < threshold <= ecg and (not peaks or now - peaks[-1] >= 0.25):
                        peaks.append(now)
                        if len(peaks) >= 2:
                            intervals = [b - a for a, b in zip(peaks, list(peaks)[1:])]
                            state["rate"] = round(60 / (sum(intervals) / len(intervals)))
                    state["previous"] = ecg
                    if incoming_rate is not None and incoming_rate > 0:
                        state["rate"] = incoming_rate

                    writer.writerow({
                        "session_id": session_id,
                        "timestamp": datetime.now().astimezone().isoformat(timespec="milliseconds"),
                        "elapsed_seconds": f"{now - monotonic_start:.3f}",
                        "sample_number": state["number"],
                        "stimulus": stimulus,
                        "time_of_day": time_of_day,
                        "ecg": ecg,
                        "bpm": state["rate"] or 0,
                    })
                    output.flush()
                    samples.append(state["number"])
                    values.append(ecg)
                    state["number"] += 1
                except (ValueError, IndexError):
                    continue
            line.set_data(samples, values)
            axis.set_xlim(max(0, state["number"] - WINDOW_SIZE), max(WINDOW_SIZE, state["number"]))
            rate_text.set_text(f"Event rate: {state['rate'] or 0}/min")
            return line, rate_text

        animation = FuncAnimation(figure, update, interval=20, cache_frame_data=False)
        _ = animation
        plt.show()
    except serial.SerialException as error:
        print(f"Could not open Arduino on {args.port}: {error}")
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("Recording stopped by user.")
    finally:
        if connection is not None and connection.is_open:
            connection.close()
        if output is not None:
            output.close()
        print("Recording closed safely.")


if __name__ == "__main__":
    main()
