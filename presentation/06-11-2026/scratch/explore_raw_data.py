import os
import glob
import pandas as pd
import numpy as np

csv_files = glob.glob("csv/**/*.csv", recursive=True)
print(f"Total raw CSV files found: {len(csv_files)}")

records = []
corrupted_files = []

for f in csv_files:
    try:
        # Check first line for header
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            first_line = fp.readline()
        
        df = pd.read_csv(f, on_bad_lines='skip')
        rows, cols = df.shape
        col_names = list(df.columns)
        
        stimulus = df['stimulus'].iloc[0] if 'stimulus' in df.columns and len(df) > 0 else 'UNKNOWN'
        time_of_day = df['time_of_day'].iloc[0] if 'time_of_day' in df.columns and len(df) > 0 else 'UNKNOWN'
        
        ecg_min = df['ecg'].min() if 'ecg' in df.columns and len(df) > 0 else np.nan
        ecg_max = df['ecg'].max() if 'ecg' in df.columns and len(df) > 0 else np.nan
        ecg_mean = df['ecg'].mean() if 'ecg' in df.columns and len(df) > 0 else np.nan
        ecg_std = df['ecg'].std() if 'ecg' in df.columns and len(df) > 0 else np.nan
        
        # Duration from elapsed_seconds or timestamp
        duration_sec = 0.0
        if 'elapsed_seconds' in df.columns and len(df) > 0:
            duration_sec = df['elapsed_seconds'].iloc[-1] - df['elapsed_seconds'].iloc[0]
            
        sample_rate = len(df) / duration_sec if duration_sec > 0 else 0
        
        records.append({
            'file': f,
            'rows': rows,
            'cols': cols,
            'stimulus': str(stimulus).strip().lower(),
            'time_of_day': str(time_of_day).strip().lower(),
            'ecg_min': ecg_min,
            'ecg_max': ecg_max,
            'ecg_mean': ecg_mean,
            'ecg_std': ecg_std,
            'duration_sec': duration_sec,
            'sample_rate_hz': sample_rate
        })
    except Exception as e:
        corrupted_files.append((f, str(e)))

audit_df = pd.DataFrame(records)
print("\n--- Summary by Stimulus Label ---")
stim_summary = audit_df.groupby('stimulus').agg(
    file_count=('file', 'count'),
    total_rows=('rows', 'sum'),
    mean_duration=('duration_sec', 'mean'),
    avg_ecg=('ecg_mean', 'mean'),
    avg_std=('ecg_std', 'mean')
).reset_index()
print(stim_summary.to_string())

print("\n--- Summary by Time of Day ---")
tod_summary = audit_df.groupby('time_of_day').agg(
    file_count=('file', 'count'),
    total_rows=('rows', 'sum')
).reset_index()
print(tod_summary.to_string())

print(f"\nCorrupted/Unreadable files: {len(corrupted_files)}")
for cf, err in corrupted_files:
    print(f"  {cf}: {err}")

# Save audit results
audit_df.to_csv("presentation/06-11-2026/scratch/raw_data_audit.csv", index=False)
print("\nAudit saved to presentation/06-11-2026/scratch/raw_data_audit.csv")

