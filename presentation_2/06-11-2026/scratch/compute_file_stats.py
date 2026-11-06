import os
import glob
import re
import pandas as pd
import numpy as np

def classify_and_filter(filepath):
    fname = os.path.basename(filepath).lower()
    
    # 0. Check row count
    try:
        row_count = sum(1 for _ in open(filepath, 'rb')) - 1
    except Exception as e:
        return 'REJECT', f"Read error: {e}", 0
        
    if row_count < 100:
        return 'REJECT', f"Empty/too short ({row_count} rows)", row_count

    # 1. Human names or human subjects
    if re.search(r'(_|^)(asim|sachin|tanishq|sujal|human)(_|\.)', fname):
        return 'REJECT', 'Human name / human subject recording', row_count

    # 2. Test / demo / simulation
    if re.search(r'(_|^)(test\d*|tets\d*|demo|simulation)(_|\.)', fname):
        return 'REJECT', 'Test / Demo / Simulation recording', row_count

    # 3. NA or unassigned / invalid arbitrary code
    if re.search(r'(_|^)(na|pencil|sd|iuhjlkk|hwh|ii|iii)(_|\.)', fname):
        return 'REJECT', 'Unassigned / NA / Hardware artifact / Pencil', row_count
        
    if re.match(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$', fname):
        return 'REJECT', 'Unlabelled timestamp-only file', row_count

    # Categorization of valid plant experiments:
    # A. Dead / Semi-Dead Plant (Biological negative control)
    if 'dead' in fname:
        if 'semi_dead' in fname or 'partial_dead' in fname:
            return 'Dead / Semi-Dead Control', 'Semi-Dead', row_count
        return 'Dead / Semi-Dead Control', 'Dead', row_count

    # B. Water Stimulus (Hydration shock / transpiration response)
    if 'water' in fname:
        return 'Water Stimulation', 'Water', row_count

    # C. Acoustic - Meditative / Classical / Mantras
    if any(k in fname for k in ['classical', 'om', 'hanuman', 'krishna', 'namami']):
        sub = 'Meditative/Mantra'
        if 'classical' in fname: sub = 'Classical'
        elif 'om' in fname: sub = 'Om Mantra'
        elif 'hanuman' in fname: sub = 'Hanuman Chalisa'
        elif 'krishna' in fname: sub = 'Hare Krishna'
        elif 'namami' in fname: sub = 'Namami Shamisaan'
        return 'Acoustic - Meditative/Mantras', sub, row_count

    # D. Acoustic - Energetic / Pop / High Beat
    if any(k in fname for k in ['bye_bye_bye', 'yalgaar', 'music_morning']):
        sub = 'Pop/High-Energy'
        if 'bye_bye_bye' in fname: sub = 'Pop (Bye Bye Bye)'
        elif 'yalgaar' in fname: sub = 'High Beat (Yalgaar)'
        elif 'music_morning' in fname: sub = 'Morning Music'
        return 'Acoustic - High Energy/Pop', sub, row_count

    # E. Baseline / Normal Control
    if 'normal' in fname or 'without_music' in fname:
        return 'Normal Baseline (Control)', 'Normal Baseline', row_count

    return 'Other Plant', 'Other', row_count

files = sorted(glob.glob('csv/**/*.csv', recursive=True))
valid_list = []
stats = []

for f in files:
    cat, sub, count = classify_and_filter(f)
    if cat == 'REJECT':
        continue
    
    # Process dataframe
    df = pd.read_csv(f)
    ecg = df['ecg'].dropna().values
    
    # Duration and sampling rate
    if 'elapsed_seconds' in df.columns:
        dur = df['elapsed_seconds'].iloc[-1] - df['elapsed_seconds'].iloc[0]
        sr = len(ecg) / dur if dur > 0 else 0
    elif 'timestamp' in df.columns:
        try:
            t0 = pd.to_datetime(df['timestamp'].iloc[0])
            t1 = pd.to_datetime(df['timestamp'].iloc[-1])
            dur = (t1 - t0).total_seconds()
            sr = len(ecg) / dur if dur > 0 else 0
        except:
            dur = len(ecg) / 190.0
            sr = 190.0
    else:
        dur = len(ecg) / 190.0
        sr = 190.0

    stat_dict = {
        'filepath': f,
        'filename': os.path.basename(f),
        'category': cat,
        'sub_label': sub,
        'sample_count': len(ecg),
        'duration_sec': round(dur, 2),
        'sample_rate_hz': round(sr, 1),
        'mean_adc': round(float(np.mean(ecg)), 2),
        'std_adc': round(float(np.std(ecg)), 2),
        'min_adc': int(np.min(ecg)),
        'max_adc': int(np.max(ecg)),
        'median_adc': round(float(np.median(ecg)), 2),
        'rms_adc': round(float(np.sqrt(np.mean(ecg**2))), 2),
        'p25_adc': round(float(np.percentile(ecg, 25)), 2),
        'p75_adc': round(float(np.percentile(ecg, 75)), 2),
        'iqr_adc': round(float(np.percentile(ecg, 75) - np.percentile(ecg, 25)), 2)
    }
    stats.append(stat_dict)

stats_df = pd.DataFrame(stats)
stats_df.to_csv("presentation/06-11-2026/scratch/file_level_statistics.csv", index=False)
stats_df[['filepath', 'filename', 'category', 'sub_label', 'sample_count']].to_csv(
    "presentation/06-11-2026/scratch/curated_dataset_inventory.csv", index=False
)

print(f"Total curated files: {len(stats_df)}")
for cat, grp in stats_df.groupby('category'):
    print(f"\n[{cat}] ({len(grp)} files, {grp['sample_count'].sum():,} samples):")
    print(grp[['filename', 'sub_label', 'duration_sec', 'mean_adc', 'std_adc', 'iqr_adc']].to_string(index=False))
