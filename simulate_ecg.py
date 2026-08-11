import argparse
import csv
import math
import os
import random
import time
from datetime import datetime


def simulated_ecg(sample_time, bpm):
    beat_phase = (sample_time * bpm / 60.0) % 1.0

    p_wave = 35 * math.exp(-((beat_phase - 0.18) / 0.035) ** 2)
    q_wave = -45 * math.exp(-((beat_phase - 0.29) / 0.012) ** 2)
    r_wave = 520 * math.exp(-((beat_phase - 0.31) / 0.014) ** 2)
    s_wave = -120 * math.exp(-((beat_phase - 0.34) / 0.018) ** 2)
    t_wave = 90 * math.exp(-((beat_phase - 0.56) / 0.08) ** 2)
    baseline = 512 + 8 * math.sin(sample_time * 2 * math.pi * 0.4)
    noise = random.gauss(0, 8)

    return max(0, min(1023, int(baseline + p_wave + q_wave + r_wave + s_wave + t_wave + noise)))


def simulate(output_path, duration, sample_rate):
    output_folder = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_folder, exist_ok=True)

    sample_interval = 1 / sample_rate
    start_time = time.perf_counter()
    sample_number = 0

    with open(output_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "ecg", "bpm"])
        csv_file.flush()

        print(f"Writing simulated ECG to: {output_path}")
        print("Open plot_csv.py in another terminal to view the running graph.")
        print("Press Ctrl+C to stop.")

        try:
            while duration <= 0 or time.perf_counter() - start_time < duration:
                elapsed = time.perf_counter() - start_time
                bpm = 72 + 4 * math.sin(elapsed * 2 * math.pi / 20)
                ecg = simulated_ecg(elapsed, bpm)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                writer.writerow([timestamp, ecg, round(bpm)])
                csv_file.flush()
                sample_number += 1

                next_sample = start_time + sample_number * sample_interval
                time.sleep(max(0, next_sample - time.perf_counter()))
        except KeyboardInterrupt:
            print("Simulation stopped.")


def main():
    parser = argparse.ArgumentParser(description="Generate simulated ECG data in real time.")
    parser.add_argument("output_path", help="CSV path that plot_csv.py will read")
    parser.add_argument(
        "--duration",
        type=float,
        default=60,
        help="Simulation duration in seconds; use 0 to run until stopped (default: 60)",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=50,
        help="Samples per second (default: 50)",
    )
    args = parser.parse_args()

    if args.rate <= 0:
        parser.error("--rate must be greater than zero")
    if args.duration < 0:
        parser.error("--duration cannot be negative")

    simulate(args.output_path, args.duration, args.rate)


if __name__ == "__main__":
    main()
