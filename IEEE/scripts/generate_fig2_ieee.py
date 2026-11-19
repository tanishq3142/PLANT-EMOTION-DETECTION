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

# IEEE Publication Style Configuration
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Cambria', 'Georgia', 'serif']
plt.rcParams['mathtext.fontset'] = 'dejavuserif'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#777777'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['grid.alpha'] = 0.6
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['axes.labelsize'] = 14

FIG_DIR = "IEEE/figures"
os.makedirs(FIG_DIR, exist_ok=True)
fs = 190.0

print("Building IEEE Figure 2: Power Spectral Density & Acoustic Dynamics...")

# Data Paths
baseline_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
water_path = 'csv/2026-08-11/plant_water_morning_11hrs50min.csv'
pop_path = 'csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv'
classical_path = 'csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv'
dead_path = 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'

silence_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
mantra_path = 'csv/2026-10-09/plant_plant_om_mantra_afternoon_12hrs23min38sec.csv'
yalgaar_path = 'csv/2026-10-09/plant_music_yalgaar_afternoon_13hrs16min40sec.csv'

morn_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
aft_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
night_path = 'csv/2026-08-11/plant_om_night_22hrs47min.csv'

fig, axes = plt.subplots(2, 2, figsize=(13, 10.5))

# -------------------------------------------------------------
# Subplot (a): Welch Power Spectral Density (PSD)
# -------------------------------------------------------------
ax_a = axes[0, 0]
conditions_psd = [
    ('Normal Baseline', baseline_path, '#003366', '-'),
    ('Water Stimulation', water_path, '#006633', '--'),
    ('Pop Music ("Bye Bye Bye")', pop_path, '#b22222', '-'),
    ('Classical Music', classical_path, '#800080', '-.'),
    ('Dead Control', dead_path, '#777777', ':')
]

for label, fpath, col, ls in conditions_psd:
    df = pd.read_csv(fpath)
    sig = df['ecg'].values.astype(float)
    sig = sig - np.mean(sig)
    nperseg = min(len(sig), int(fs * 4))
    freqs, psd = signal.welch(sig, fs=fs, window='hann', nperseg=nperseg, noverlap=nperseg//2)
    mask = (freqs >= 0.1) & (freqs <= 45.0)
    ax_a.semilogy(freqs[mask], psd[mask], label=label, color=col, linestyle=ls, linewidth=2.0)

# Physiological frequency band shading
ax_a.axvspan(0.1, 2.0, color='#ffffcc', alpha=0.35, label='Slow Wave Band (0.1–2 Hz)')
ax_a.axvspan(2.0, 10.0, color='#e0f3f8', alpha=0.35, label='Action Potential Band (2–10 Hz)')
ax_a.axvspan(10.0, 45.0, color='#fee0d2', alpha=0.35, label='Acoustic/Vibration Band (10–45 Hz)')

ax_a.set_xlabel('Frequency (Hz)', fontsize=14, labelpad=6)
ax_a.set_ylabel('PSD (ADC²/Hz, log scale)', fontsize=14, labelpad=6)
ax_a.set_xlim(0.1, 45.0)
ax_a.grid(True, which="both")
ax_a.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=9.5)
ax_a.text(0.5, -0.22, '(a)', transform=ax_a.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (b): Acoustic Dispersion Metrics
# -------------------------------------------------------------
ax_b = axes[0, 1]
ecg_sil = pd.read_csv(silence_path)['ecg'].values.astype(float)
ecg_man = pd.read_csv(mantra_path)['ecg'].values.astype(float)
ecg_pop = pd.read_csv(pop_path)['ecg'].values.astype(float)
ecg_yal = pd.read_csv(yalgaar_path)['ecg'].values.astype(float)

stds = [np.std(ecg_sil), np.std(ecg_man), np.std(ecg_pop), np.std(ecg_yal)]
iqrs = [np.percentile(ecg_sil, 75) - np.percentile(ecg_sil, 25),
        np.percentile(ecg_man, 75) - np.percentile(ecg_man, 25),
        np.percentile(ecg_pop, 75) - np.percentile(ecg_pop, 25),
        np.percentile(ecg_yal, 75) - np.percentile(ecg_yal, 25)]

labels_b = ['Silence (Ctrl)', 'Vedic Mantra', 'Pop ("Bye Bye")', 'Rap ("Yalgaar")']
x_b = np.arange(len(labels_b))
w = 0.35

rects_std = ax_b.bar(x_b - w/2, stds, w, label='Standard Deviation (σ, ADC)', color='#003366', edgecolor='black', linewidth=1.0, hatch='//')
rects_iqr = ax_b.bar(x_b + w/2, iqrs, w, label='Interquartile Range (IQR, ADC)', color='#b22222', edgecolor='black', linewidth=1.0, hatch='\\\\')

ax_b.set_ylabel('Dispersion Amplitude (ADC Counts)', fontsize=14, labelpad=6)
ax_b.set_xticks(x_b)
ax_b.set_xticklabels(labels_b, fontsize=11, fontweight='normal')
ax_b.set_ylim(0, 720)
ax_b.grid(True, axis='y')
ax_b.legend(loc='upper left', framealpha=0.95, edgecolor='black', fontsize=10.5)

# Value labels atop bars
for rect in rects_std:
    h = rect.get_height()
    ax_b.text(rect.get_x() + rect.get_width()/2., h + 10, f'{h:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
for rect in rects_iqr:
    h = rect.get_height()
    ax_b.text(rect.get_x() + rect.get_width()/2., h + 10, f'{h:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax_b.text(0.5, -0.22, '(b)', transform=ax_b.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (c): Circadian Diurnal Baseline Dynamics
# -------------------------------------------------------------
ax_c = axes[1, 0]
ecg_m = pd.read_csv(morn_path)['ecg'].values.astype(float)
ecg_a = pd.read_csv(aft_path)['ecg'].values.astype(float)
ecg_n = pd.read_csv(night_path)['ecg'].values.astype(float)

dur_c = 45.0
n_c = int(dur_c * fs)
t_c = np.linspace(0, dur_c, n_c)

ax_c.plot(t_c, ecg_m[:n_c], color='#e67e22', linewidth=1.6, label=f'Morning (11:39 AM, σ={np.std(ecg_m):.1f}) - Active Transpiration')
ax_c.plot(t_c, ecg_a[:n_c], color='#006633', linewidth=1.6, label=f'Afternoon (03:38 PM, σ={np.std(ecg_a):.1f}) - Steady State')
ax_c.plot(t_c, ecg_n[:n_c], color='#003366', linewidth=1.6, linestyle='--', label=f'Night (10:47 PM, σ={np.std(ecg_n):.1f}) - Stomata Quiescent')

ax_c.set_xlabel('Time (s)', fontsize=14, labelpad=6)
ax_c.set_ylabel('Biopotential (ADC Counts)', fontsize=14, labelpad=6)
ax_c.set_xlim(0, dur_c)
ax_c.set_ylim(-20, 1040)
ax_c.grid(True)
ax_c.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=9.5)
ax_c.text(0.5, -0.22, '(c)', transform=ax_c.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (d): Relative Spectral Band Energy Allocation
# -------------------------------------------------------------
ax_d = axes[1, 1]

# Load extracted feature dataframe for clean aggregate energy fractions
feat_df = pd.read_csv("presentation_2/06-11-2026/scratch/plant_features_extracted.csv")
cat_energy = feat_df.groupby('category')[['power_low_freq', 'power_mid_freq', 'power_high_freq']].mean()

categories_d = [
    'Normal Baseline (Control)',
    'Water Stimulation',
    'Acoustic - Meditative/Mantras',
    'Acoustic - High Energy/Pop',
    'Dead / Semi-Dead Control'
]
display_labels = ['Normal (Ctrl)', 'Water Stim.', 'Meditative', 'Pop Music', 'Dead (Ctrl)']

low_pcts = []
mid_pcts = []
high_pcts = []

for c in categories_d:
    row = cat_energy.loc[c]
    tot = row['power_low_freq'] + row['power_mid_freq'] + row['power_high_freq'] + 1e-6
    low_pcts.append((row['power_low_freq'] / tot) * 100)
    mid_pcts.append((row['power_mid_freq'] / tot) * 100)
    high_pcts.append((row['power_high_freq'] / tot) * 100)

x_d = np.arange(len(display_labels))
width_d = 0.55

p1 = ax_d.bar(x_d, low_pcts, width_d, label='Low Freq (0.1–2 Hz: Slow Wave Potential)', color='#003366', edgecolor='black', linewidth=1.0)
p2 = ax_d.bar(x_d, mid_pcts, width_d, bottom=low_pcts, label='Mid Freq (2–10 Hz: Action Potentials)', color='#2e8b57', edgecolor='black', linewidth=1.0)
p3 = ax_d.bar(x_d, high_pcts, width_d, bottom=np.array(low_pcts) + np.array(mid_pcts), label='High Freq (10–45 Hz: Acoustic Vibration)', color='#b22222', edgecolor='black', linewidth=1.0)

ax_d.set_ylabel('Spectral Energy Allocation (%)', fontsize=14, labelpad=6)
ax_d.set_xticks(x_d)
ax_d.set_xticklabels(display_labels, fontsize=11, fontweight='normal')
ax_d.set_ylim(0, 105)
ax_d.grid(True, axis='y')
ax_d.legend(loc='lower right', framealpha=0.95, edgecolor='black', fontsize=9.5)

# Annotation pointing to pop high freq dominance
ax_d.annotate('High-Frequency Acoustic Spike\n(>25% Energy in 10-45 Hz)',
              xy=(3, 85), xytext=(1.2, 88),
              arrowprops=dict(facecolor='black', shrink=0.08, width=1.2, headwidth=6),
              fontsize=10.0, fontweight='bold', bbox=dict(boxstyle='square,pad=0.3', facecolor='#ffffdd', edgecolor='black'))

ax_d.text(0.5, -0.22, '(d)', transform=ax_d.transAxes, fontsize=16, fontweight='bold', ha='center')

plt.tight_layout()
plt.subplots_adjust(bottom=0.08, hspace=0.32, wspace=0.25)

out_png = f"{FIG_DIR}/fig2_spectral_and_acoustic_dynamics.png"
out_pdf = f"{FIG_DIR}/fig2_spectral_and_acoustic_dynamics.pdf"
fig.savefig(out_png, dpi=400, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Figure 2 successfully exported to:\n  {out_png}\n  {out_pdf}")
