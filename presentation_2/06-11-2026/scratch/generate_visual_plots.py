import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import signal

# Style setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

PLOT_DIR = "presentation/06-11-2026/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# ADC to millivolts conversion factor (10-bit ADC, 0-1023 mapped to 0-5000 mV)
ADC_TO_MV = 5000.0 / 1023.0

print("Generating Plot 1: Macro Time-Series Comparison Across 5 Experimental States...")

# Representative files for macro comparison
macro_files = {
    'Normal Baseline': 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv',
    'Water Stimulation': 'csv/2026-08-11/plant_water_morning_11hrs50min.csv',
    'Acoustic (Classical/Mantra)': 'csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv',
    'Acoustic (Pop / High Beat)': 'csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv',
    'Dead Plant (Negative Control)': 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'
}

fig, axes = plt.subplots(5, 1, figsize=(14, 12), sharex=False)
colors = ['#1f77b4', '#2ca02c', '#9467bd', '#d62728', '#7f7f7f']

for idx, (label, fpath) in enumerate(macro_files.items()):
    ax = axes[idx]
    df = pd.read_csv(fpath)
    ecg = df['ecg'].values
    
    # Time vector
    if 'elapsed_seconds' in df.columns:
        t = df['elapsed_seconds'].values
    else:
        t = np.linspace(0, len(ecg)/190.0, len(ecg))
        
    # Subsample if too large for clean rasterization
    step = max(1, len(t) // 3000)
    t_sub = t[::step]
    ecg_sub = ecg[::step]
    
    ax.plot(t_sub, ecg_sub, color=colors[idx], linewidth=0.8, alpha=0.9, label=label)
    ax.set_ylabel("ADC Counts (0-1023)", fontsize=9, fontweight='bold')
    ax.set_ylim(-20, 1050)
    ax.set_title(f"[{chr(65+idx)}] {label} (File: {os.path.basename(fpath)}, N={len(ecg):,}, Duration={t[-1]:.1f}s)",
                 fontsize=11, fontweight='bold', loc='left', pad=4)
    ax.axhline(512, color='black', linestyle=':', alpha=0.4, label='ADC Midpoint (~2.5V)')
    
    # Secondary y-axis for millivolts
    ax_mv = ax.twinx()
    ax_mv.set_ylim(-20 * ADC_TO_MV, 1050 * ADC_TO_MV)
    ax_mv.set_ylabel("Voltage (mV)", fontsize=9, color='#555555')
    ax_mv.tick_params(colors='#555555')
    
    # Annotations of key statistics
    mean_val = np.mean(ecg)
    std_val = np.std(ecg)
    ax.text(0.98, 0.82, f"Mean: {mean_val:.1f} | SD: {std_val:.1f}",
            transform=ax.transAxes, fontsize=10, ha='right',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#cccccc', alpha=0.9))

axes[-1].set_xlabel("Time (seconds)", fontsize=11, fontweight='bold')
plt.suptitle("Macro Time-Series Comparison: Plant Electrophysiological Signals Across Conditions",
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_01_macro_timeseries_comparison.png", dpi=300)
plt.close()

print("Plot 1 saved successfully.")

