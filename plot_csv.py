import argparse
import csv
import os

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def load_csv(filepath):
    timestamps = []
    ecg_values = []
    bpm_values = []

    with open(filepath, "r", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        required_columns = {"timestamp", "ecg", "bpm"}
        if not required_columns.issubset(reader.fieldnames or set()):
            raise ValueError("CSV must contain timestamp, ecg, and bpm columns.")

        for row_number, row in enumerate(reader, start=2):
            try:
                timestamps.append(row["timestamp"])
                ecg_values.append(float(row["ecg"]))
                bpm_values.append(float(row["bpm"]))
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid data on CSV row {row_number}.") from error

    return timestamps, ecg_values, bpm_values

def plot_csv(filepath):
    figure, ecg_axis = plt.subplots(figsize=(12, 6))
    bpm_axis = ecg_axis.twinx()

    ecg_line, = ecg_axis.plot([], [], color="tab:blue", linewidth=1.2, label="ECG")
    bpm_line, = bpm_axis.plot([], [], color="tab:red", linewidth=1.2, label="BPM")

    ecg_axis.set_title(f"ECG and BPM - {os.path.basename(filepath)}")
    ecg_axis.set_xlabel("Sample")
    ecg_axis.set_ylabel("ECG / ADC", color="tab:blue")
    bpm_axis.set_ylabel("BPM", color="tab:red")
    ecg_axis.set_ylim(0, 1023)
    ecg_axis.set_xlim(0, 1)
    ecg_axis.grid(True, alpha=0.3)

    lines = [ecg_line, bpm_line]
    ecg_axis.legend(lines, [line.get_label() for line in lines], loc="upper right")

    def update(_frame):
        _, ecg_values, bpm_values = load_csv(filepath)
        samples = list(range(len(ecg_values)))

        ecg_line.set_data(samples, ecg_values)
        bpm_line.set_data(samples, bpm_values)

        if samples:
            ecg_axis.set_xlim(0, max(1, len(samples) - 1))

            bpm_min = min(bpm_values)
            bpm_max = max(bpm_values)
            bpm_margin = max(5, (bpm_max - bpm_min) * 0.1)
            bpm_axis.set_ylim(bpm_min - bpm_margin, bpm_max + bpm_margin)

        return ecg_line, bpm_line

    animation = FuncAnimation(
        figure,
        update,
        interval=100,
        cache_frame_data=False,
    )

    figure.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot ECG and BPM data from a plant recording CSV file."
    )
    parser.add_argument("csv_path", help="Path to the recording CSV file")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_path):
        parser.error(f"CSV file not found: {args.csv_path}")

    try:
        plot_csv(args.csv_path)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
