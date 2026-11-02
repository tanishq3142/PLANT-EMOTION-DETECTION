import csv
import glob
import os
import re

SOURCE_DIR = "csv"
TARGET_DIR = "cleaned csv"

FILENAME_REGEX = re.compile(r"^plant_(.*)_(morning|afternoon|evening|night)_(.*)\.csv$")

CLEAN_COLUMNS = ["timestamp", "stimulus", "time_of_day", "ecg"]


def get_period(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def parse_period_from_timestamp(timestamp_str: str) -> str:
    if not timestamp_str:
        return "morning"
    match = re.search(r"[T ](\d{2}):(\d{2})", timestamp_str)
    if match:
        return get_period(int(match.group(1)))
    return "morning"


def process_file(source_path: str, target_path: str):
    basename = os.path.basename(source_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    # Check filename for stimulus and time_of_day fallback
    match = FILENAME_REGEX.match(basename)
    if match:
        default_stimulus = match.group(1)
        default_time_of_day = match.group(2)
    else:
        name_without_ext = os.path.splitext(basename)[0]
        if re.match(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$", name_without_ext):
            default_stimulus = "unknown"
        else:
            default_stimulus = name_without_ext
        default_time_of_day = None

    row_count = 0
    with open(source_path, newline="", encoding="utf-8", errors="ignore") as in_fh, \
         open(target_path, "w", newline="", encoding="utf-8") as out_fh:
        reader = csv.DictReader(in_fh)
        writer = csv.DictWriter(out_fh, fieldnames=CLEAN_COLUMNS)
        writer.writeheader()

        for row in reader:
            timestamp = (row.get("timestamp") or "").strip()
            stimulus = (row.get("stimulus") or "").strip() or default_stimulus
            time_of_day = (row.get("time_of_day") or "").strip() or default_time_of_day
            if not time_of_day:
                time_of_day = parse_period_from_timestamp(timestamp)
            ecg = (row.get("ecg") or "").strip()

            writer.writerow({
                "timestamp": timestamp,
                "stimulus": stimulus,
                "time_of_day": time_of_day,
                "ecg": ecg,
            })
            row_count += 1

    return row_count


def main():
    total_files = 0
    total_rows = 0

    for root, _, files in os.walk(SOURCE_DIR):
        for file in sorted(files):
            if not file.endswith(".csv"):
                continue
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, SOURCE_DIR)
            dst_path = os.path.join(TARGET_DIR, rel_path)

            rows = process_file(src_path, dst_path)
            total_files += 1
            total_rows += rows
            print(f"[{total_files:02d}] {rel_path} -> {rows:,} rows")

    print(f"\nCompleted! Processed {total_files} files with {total_rows:,} total rows into '{TARGET_DIR}'.")


if __name__ == "__main__":
    main()

