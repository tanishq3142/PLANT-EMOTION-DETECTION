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

PLOT_DIR = "presentation/06-11-2026/plots"
os.makedirs(PLOT_DIR, exist_ok=True)
ADC_TO_MV = 5000.0 / 1023.0

# -------------------------------------------------------------
# PLOT 6: Circadian & Diurnal Shifts (Morning vs Afternoon vs Night)
# -------------------------------------------------------------
print("Generating Plot 6: Circadian & Diurnal Shifts...")
morn_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
aft_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
night_path = 'csv/2026-08-11/plant_om_night_22hrs47min.csv'

df_morn = pd.read_csv(morn_path)
df_aft = pd.read_csv(aft_path)
df_night = pd.read_csv(night_path)

ecg_m = df_morn['ecg'].values
ecg_a = df_aft['ecg'].values
ecg_n = df_night['ecg'].values

fig, (ax_ts, ax_kde) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={'width_ratios': [2, 1]})

# Use 45-second sample from each to ensure all arrays have enough points
fs = 190.0
dur_sec = 45.0
n_pts = int(dur_sec * fs)

t_m = np.linspace(0, dur_sec, n_pts)
t_a = np.linspace(0, dur_sec, n_pts)
t_n = np.linspace(0, dur_sec, n_pts)

ax_ts.plot(t_m, ecg_m[:n_pts], label=f'Morning (11:39 AM, SD={np.std(ecg_m):.1f}) - Active Transpiration', color='#e67e22', alpha=0.85, linewidth=0.9)
ax_ts.plot(t_a, ecg_a[:n_pts], label=f'Afternoon (03:38 PM, SD={np.std(ecg_a):.1f}) - Steady State', color='#27ae60', alpha=0.85, linewidth=0.9)
ax_ts.plot(t_n, ecg_n[:n_pts], label=f'Night (10:47 PM, SD={np.std(ecg_n):.1f}) - Resting / Stomata Closed', color='#2c3e50', alpha=0.85, linewidth=0.9)

ax_ts.set_title("[A] 45-Second Snapshot Across Diurnal Cycles", fontsize=11, fontweight='bold')
ax_ts.set_xlabel("Time (seconds)", fontsize=10, fontweight='bold')
ax_ts.set_ylabel("ADC Count (0-1023)", fontsize=10, fontweight='bold')
ax_ts.set_ylim(-20, 1050)
ax_ts.legend(loc='upper right')

# Density KDE
sns.kdeplot(ecg_m, ax=ax_kde, color='#e67e22', label='Morning', linewidth=2)
sns.kdeplot(ecg_a, ax=ax_kde, color='#27ae60', label='Afternoon', linewidth=2)
sns.kdeplot(ecg_n, ax=ax_kde, color='#2c3e50', label='Night', linewidth=2)

ax_kde.set_title("[B] Diurnal Biopotential Density", fontsize=11, fontweight='bold')
ax_kde.set_xlabel("ADC Count", fontsize=10, fontweight='bold')
ax_kde.set_ylabel("Probability Density", fontsize=10, fontweight='bold')
ax_kde.set_xlim(0, 1023)
ax_kde.legend(loc='upper right')

plt.suptitle("Circadian & Diurnal Electrophysiological Variations in Plant Signaling",
             fontsize=13, fontweight='bold', y=0.99)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_06_circadian_diurnal_shifts.png", dpi=300)
plt.close()
print("Plot 6 saved.")

# -------------------------------------------------------------
# PLOT 7: Power Spectral Density (PSD - Welch's Method)
# -------------------------------------------------------------
print("Generating Plot 7: Power Spectral Density (PSD)...")
conditions_psd = {
    'Normal Baseline': ('csv/2026-08-11/plant_normal_morning_11hrs39min.csv', '#1f77b4'),
    'Water Stimulation': ('csv/2026-08-11/plant_water_morning_11hrs50min.csv', '#2ca02c'),
    'Pop Music ("Bye Bye Bye")': ('csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv', '#d62728'),
    'Classical Music': ('csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv', '#9467bd'),
    'Dead Plant (Negative Control)': ('csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv', '#7f7f7f')
}

plt.figure(figsize=(12, 6))

for label, (fpath, col) in conditions_psd.items():
    df = pd.read_csv(fpath)
    sig = df['ecg'].values.astype(float)
    sig = sig - np.mean(sig)  # zero center
    
    # Welch PSD with 4-second Hann window (nperseg = 190 * 4 = 760)
    nperseg = min(len(sig), int(fs * 4))
    freqs, psd = signal.welch(sig, fs=fs, window='hann', nperseg=nperseg, noverlap=nperseg//2)
    
    # Restrict to 0.1 - 45 Hz (AD8232 analog bandwidth)
    mask = (freqs >= 0.1) & (freqs <= 45.0)
    plt.semilogy(freqs[mask], psd[mask], label=label, color=col, linewidth=1.8, alpha=0.9)

plt.axvspan(0.1, 2.0, color='#ffffcc', alpha=0.35, label='Low Freq (0.1-2 Hz: Slow Wave Potential)')
plt.axvspan(2.0, 10.0, color='#e0f3f8', alpha=0.35, label='Mid Freq (2-10 Hz: Action Potentials)')
plt.axvspan(10.0, 45.0, color='#fee0d2', alpha=0.35, label='High Freq (10-45 Hz: Acoustic/Burst Vibration)')

plt.title("Power Spectral Density (PSD) Analysis: Frequency Domain Signatures Across Plant States",
          fontsize=12, fontweight='bold')
plt.xlabel("Frequency (Hz)", fontsize=11, fontweight='bold')
plt.ylabel("Power Spectral Density (ADC²/Hz, log scale)", fontsize=11, fontweight='bold')
plt.xlim(0.1, 45)
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(loc='upper right', frameon=True)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_07_power_spectral_density_psd.png", dpi=300)
plt.close()
print("Plot 7 saved.")

