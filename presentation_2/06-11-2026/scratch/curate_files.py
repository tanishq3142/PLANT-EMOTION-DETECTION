import os
import glob
import re
import pandas as pd

# Keywords to exclude
EXCLUDE_KEYWORDS = [
    'sachin', 'tanishq', 'sujal', 'asim',  # human names
    'test', 'tets', 'demo', 'simulation',   # testing / demo
    'na_', '_na',                           # unassigned / NA
    'iuhjlkk', 'pencil', 'sd_', 'sd.',      # invalid / junk
    '2026-08-11_09-57-49'                   # unlabelled
]

def should_exclude(filepath):
    base = os.path.basename(filepath).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in base:
            return True, f"Matched exclude keyword: {kw}"
    return False, ""

def classify_file(filepath):
    base = os.path.basename(filepath).lower()
    
    # 1. Dead plant
    if 'dead' in base:
        if 'semi_dead' in base or 'partial_dead' in base:
            return 'Dead/Semi-Dead Plant', 'Semi-Dead'
        return 'Dead/Semi-Dead Plant', 'Dead'
        
    # 2. Water stimulus
    if 'water' in base:
        return 'Water Stimulation', 'Water'
        
    # 3. Acoustic / Music stimulus
    if any(m in base for m in ['classical', 'om', 'hanuman', 'hare_krishna', 'namami']):
        return 'Acoustic - Meditative / Classical', base.split('_')[1] if len(base.split('_')) > 1 else 'Meditative'
    if any(m in base for m in ['bye_bye_bye', 'yalgaar', 'music_morning']):
        return 'Acoustic - High Energy / Pop', base.split('_')[1] if len(base.split('_')) > 1 else 'High Energy'
        
    # 4. Normal / Control
    if 'normal' in base or 'without_music' in base:
        return 'Normal / Baseline Control', 'Normal Baseline'
        
    return 'Other', 'Other'

all_files = glob.glob('csv/**/*.csv', recursive=True)
curated = []
rejected = []

for f in sorted(all_files):
    fname = os.path.basename(f)
    try:
        row_count = sum(1 for _ in open(f, 'rb')) - 1
    except Exception as e:
        rejected.append((f, f"Read error: {e}"))
        continue
        
    if row_count < 100:
        rejected.append((f, f"Empty or too few rows ({row_count} rows)"))
        continue
        
    excl, reason = should_exclude(f)
    if excl:
        rejected.append((f, f"Excluded: {reason} ({row_count} rows)"))
        continue
        
    category, condition = classify_file(f)
    curated.append({
        'path': f,
        'filename': fname,
        'rows': row_count,
        'category': category,
        'condition': condition
    })

print(f"Total files: {len(all_files)}")
print(f"Curated valid experimental files: {len(curated)}")
print(f"Rejected / excluded files: {len(rejected)}")

print("\n=== REJECTED FILES ===")
for path, reason in rejected:
    print(f"[-] {path}: {reason}")

print("\n=== CURATED EXPERIMENTAL FILES ===")
curated_df = pd.DataFrame(curated)
for cat, group in curated_df.groupby('category'):
    print(f"\n--- Category: {cat} ({len(group)} files, {group['rows'].sum():,} total samples) ---")
    for _, row in group.iterrows():
        print(f"  [+] {row['filename']} ({row['rows']:,} rows)")

curated_df.to_csv("presentation/06-11-2026/scratch/curated_dataset_inventory.csv", index=False)

