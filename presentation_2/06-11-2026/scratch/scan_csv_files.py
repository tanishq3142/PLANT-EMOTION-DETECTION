import os
import glob
import pandas as pd

csv_files = glob.glob('csv/**/*.csv', recursive=True)
print(f'Total CSV files found: {len(csv_files)}')

data_inventory = []
for f in sorted(csv_files):
    fname = os.path.basename(f)
    try:
        df = pd.read_csv(f, nrows=5)
        total_rows = sum(1 for _ in open(f, 'rb')) - 1
        data_inventory.append({
            'path': f,
            'file': fname,
            'rows': total_rows,
            'columns': list(df.columns)
        })
    except Exception as e:
        data_inventory.append({
            'path': f,
            'file': fname,
            'rows': 0,
            'columns': [],
            'error': str(e)
        })

print("\n--- CSV Inventory ---")
for item in data_inventory:
    col_str = ", ".join(item['columns']) if item['columns'] else item.get('error', 'empty')
    print(f"{item['path']} | Rows: {item['rows']} | Cols: {col_str}")

