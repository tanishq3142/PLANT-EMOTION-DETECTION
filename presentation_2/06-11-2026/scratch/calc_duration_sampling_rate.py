import pandas as pd
import glob

files = [
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

for f in files:
    df = pd.read_csv(f)
    n = len(df)
    if 'elapsed_seconds' in df.columns:
        dur = df['elapsed_seconds'].iloc[-1] - df['elapsed_seconds'].iloc[0]
        sr = n / dur if dur > 0 else 0
        print(f"{f} | N={n} | Duration={dur:.2f}s | Sample Rate={sr:.2f} Hz")
    elif 'timestamp' in df.columns:
        t0 = pd.to_datetime(df['timestamp'].iloc[0])
        t1 = pd.to_datetime(df['timestamp'].iloc[-1])
        dur = (t1 - t0).total_seconds()
        sr = n / dur if dur > 0 else 0
        print(f"{f} | N={n} | Duration={dur:.2f}s | Sample Rate={sr:.2f} Hz")

