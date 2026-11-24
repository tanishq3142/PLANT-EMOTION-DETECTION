"""Save one signal waveform image for each categorized CSV recording."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
PLOT_SAMPLE_LIMIT = 1000


def load_signal(csv_path, signal_column):
    values = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or signal_column not in reader.fieldnames:
            raise ValueError(
                f"{csv_path}: missing required signal column '{signal_column}'."
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                values.append(float(row[signal_column]))
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{csv_path}: invalid '{signal_column}' value on row {row_number}."
                ) from error

    return values


def save_signal_plot(csv_path, output_path, class_name, signal_column, values):
    plotted_values = values[:PLOT_SAMPLE_LIMIT]
    figure, axis = plt.subplots(figsize=(12, 4))
    axis.plot(
        range(len(plotted_values)), plotted_values, color="tab:blue", linewidth=0.8
    )
    title = f"{class_name} - {csv_path.stem}"
    if len(values) > PLOT_SAMPLE_LIMIT:
        title += f" (first {PLOT_SAMPLE_LIMIT:,} of {len(values):,} samples)"
    axis.set_title(title)
    axis.set_xlabel("Sample")
    axis.set_ylabel(signal_column.upper() if signal_column == "ecg" else signal_column)
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def generate_plots(input_dir, output_dir, signal_column):
    csv_paths = sorted(input_dir.rglob("*.csv"))
    if not csv_paths:
        raise ValueError(f"No CSV files found under: {input_dir}")

    plotted = 0
    skipped = 0
    for csv_path in csv_paths:
        values = load_signal(csv_path, signal_column)
        if not values:
            print(f"Skipping empty recording: {csv_path}")
            skipped += 1
            continue

        relative_path = csv_path.relative_to(input_dir)
        output_path = (output_dir / relative_path).with_suffix(".png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        class_name = " / ".join(relative_path.parts[:-1])
        save_signal_plot(
            csv_path, output_path, class_name, signal_column, values
        )
        print(f"Saved: {output_path}")
        plotted += 1

    print(f"Created {plotted} plot(s); skipped {skipped} empty CSV file(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Create a signal plot image for each categorized CSV recording."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=SCRIPT_DIR / "categorize csv",
        help="Folder containing class-organized CSV files (default: categorize csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SCRIPT_DIR / "categorize csv plots",
        help="Folder for the generated PNG images (default: categorize csv plots)",
    )
    parser.add_argument(
        "--signal-column",
        default="ecg",
        help="CSV column to plot (default: ecg)",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Input folder not found: {args.input_dir}")

    try:
        generate_plots(args.input_dir, args.output_dir, args.signal_column)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
