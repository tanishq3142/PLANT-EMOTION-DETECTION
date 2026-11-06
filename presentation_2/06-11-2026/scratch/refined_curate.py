import os
import glob
import re
import pandas as pd

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
            return 'Dead / Semi-Dead (Control)', 'Semi-Dead', row_count
        return 'Dead / Semi-Dead (Control)', 'Dead', row_count

    # B. Water Stimulus (Hydration shock / transpiration response)
    if 'water' in fname:
        return 'Water Stimulation', 'Water', row_count

    # C. Acoustic - Meditative / Classical / Mantras
    if any(k in fname for k in ['classical', 'om', 'hanuman', 'krishna', 'namami']):
        return 'Acoustic - Meditative / Mantras', fname.split('_')[1], row_count

    # D. Acoustic - Energetic / Pop / High Beat
    if any(k in fname for k in ['bye_bye_bye', 'yalgaar', 'music_morning']):
        return 'Acoustic - High Energy / Pop', fname.split('_')[1], row_count

    # E. Baseline / Normal Control
    if 'normal' in fname or 'without_music' in fname:
        return 'Normal Baseline (Control)', 'Normal', row_count

    return 'Other Plant', 'Other', row_count

files = sorted(glob.glob('csv/**/*.csv', recursive=True))
valid_list = []
rejected_list = []

for f in files:
    res = classify_and_filter(f)
    if res[0] == 'REJECT':
        rejected_list.append((f, res[1], res[2]))
    else:
        valid_list.append({
            'path': f,
            'filename': os.path.basename(f),
            'category': res[0],
            'sub_label': res[1],
            'rows': res[2]
        })

print(f"Total files: {len(files)}")
print(f"Valid curated plant experiments: {len(valid_list)}")
print(f"Rejected files: {len(rejected_list)}")

print("\n--- Curated Experiments by Category ---")
v_df = pd.DataFrame(valid_list)
for cat, grp in v_df.groupby('category'):
    print(f"\n[{cat}] -> {len(grp)} files, {grp['rows'].sum():,} total rows")
    for _, r in grp.iterrows():
        print(f"   * {r['filename']} ({r['rows']:,} rows, sub_label: {r['sub_label']})")

print("\n--- Rejected Files Summary ---")
for p, reason, r in rejected_list:
    print(f"   x {os.path.basename(p)}: {reason} ({r} rows)")

