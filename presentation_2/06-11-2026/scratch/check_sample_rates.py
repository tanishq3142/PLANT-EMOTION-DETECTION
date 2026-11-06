import glob
import os
import pandas as pd
import numpy as np

# Let's inspect timestamp formats, time intervals, and sampling rates across a few representative files
test_files = [
    'csv/2026-08-11/plant_normal_morning_11hrs39min.csv',
    'csv/2026-08-11/plant_water_morning_11hrs50min.csv',
    'csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv',
    'csv/2026-08-11/plant_om_night_22hrs47min.csv',
    'csv/2026-08-22/plant_normal_morning_09hrs38min.csv',
    'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv',
    'csv/2026-10-09/plant_normal_afternoon_12hrs30min04sec.csv',
    'csv/2026-10-09/plant_with_water_afternoon_15hrs48min05sec.csv',
    'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv',
    'csv/2026-10-09/plant_music_yalgaar_afternoon_13hrs16min40sec.csv',
]

for f in test_files:
    if not os.path.exists(f):
        print(f"Missing: {f}")
        continue
    df = pd.read_csv(f, nrows=100)
    print(f"\n=== File: {f} ===")
    print("Columns:", list(df.columns))
    print(df.head(3))
    
    # Check elapsed_seconds or timestamps
    if 'elapsed_seconds' in df.columns:
        dt = df['elapsed_seconds'].diff().dropna()
        median_dt = dt.median()
        sr = 1.0 / median_dt if median_dt > 0 else 0
        print(f"Elapsed seconds dt median: {median_dt:.5f} s -> Approx Sampling Rate: {sr:.1f} Hz")
    elif 'timestamp' in df.columns:
        try:
            ts = pd.to_datetime(df['timestamp'])
            dt = ts.diff().dropna().dt.total_seconds()
            median_dt = dt.median()
            sr = 1.0 / median_dt if median_dt > 0 else 0
            print(f"Timestamp dt median: {median_dt:.5f} s -> Approx Sampling Rate: {sr:.1f} Hz")
        except Exception as e:
            print("Could not parse timestamp:", e)

