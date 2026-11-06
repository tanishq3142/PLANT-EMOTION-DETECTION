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
# PLOT 2: Waveform Micro-Structure & 5-Second Insets
# -------------------------------------------------------------
print("Generating Plot 2: Waveform Micro-Structure (5-second zoomed insets)...")
files_p2 = {
    'Normal Baseline': ('csv/2026-08-11/plant_normal_morning_11hrs39min.csv', '#1f77b4', 100),
    'Water Stimulation': ('csv/2026-08-11/plant_water_morning_11hrs50min.csv', '#2ca02c', 50),
    'Classical Music': ('csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv', '#9467bd', 80),
    'Pop Music': ('csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv', '#d62728', 120),
    'Dead Plant': ('csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv', '#7f7f7f', 40)
}

fig, axes = plt.subplots(5, 1, figsize=(12, 10), sharex=True)

for idx, (label, (fpath, col, start_sec)) in enumerate(files_p2.items()):
    ax = axes[idx]
    df = pd.read_csv(fpath)
    ecg = df['ecg'].values
    
    if 'elapsed_seconds' in df.columns:
        t = df['elapsed_seconds'].values
    else:
        t = np.linspace(0, len(ecg)/190.0, len(ecg))
        
    mask = (t >= start_sec) & (t <= start_sec + 5.0)
    t_win = t[mask] - start_sec
    ecg_win = ecg[mask]
    
    ax.plot(t_win, ecg_win, color=col, linewidth=1.3, marker='o', markersize=2, label=label)
    ax.set_ylabel("ADC Count", fontsize=9, fontweight='bold')
    ax.set_ylim(-20, 1050)
    ax.set_title(f"[{chr(65+idx)}] {label} - High-Resolution 5s Window ({len(ecg_win)} points, ~190 Hz)",
                 fontsize=10, fontweight='bold', loc='left')
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Secondary mV axis
    ax_mv = ax.twinx()
    ax_mv.set_ylim(-20 * ADC_TO_MV, 1050 * ADC_TO_MV)
    ax_mv.set_ylabel("mV", fontsize=8, color='#666666')
    ax_mv.tick_params(colors='#666666')
    
    # Local window stats
    win_std = np.std(ecg_win) if len(ecg_win) > 0 else 0
    win_p2p = (np.max(ecg_win) - np.min(ecg_win)) if len(ecg_win) > 0 else 0
    ax.text(0.98, 0.80, f"Local SD: {win_std:.1f} | Peak-to-Peak: {win_p2p} counts ({win_p2p*ADC_TO_MV:.1f} mV)",
            transform=ax.transAxes, fontsize=9, ha='right',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#dddddd', alpha=0.9))

axes[-1].set_xlabel("Window Elapsed Time (seconds)", fontsize=11, fontweight='bold')
plt.suptitle("Micro-Morphology: 5-Second Physiological Waveform Insets Across Experimental Conditions",
             fontsize=13, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_02_waveform_microstructure_5sec.png", dpi=300)
plt.close()
print("Plot 2 saved.")

# -------------------------------------------------------------
# PLOT 3: Biological Negative Control: Live Plant vs Dead Plant
# -------------------------------------------------------------
print("Generating Plot 3: Biological Negative Control (Live Plant vs Dead Plant)...")
live_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
dead_path = 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'

df_live = pd.read_csv(live_path)
df_dead = pd.read_csv(dead_path)

live_ecg = df_live['ecg'].values
dead_ecg = df_dead['ecg'].values

# Common duration of 200 seconds
t_live = np.linspace(0, len(live_ecg)/190.0, len(live_ecg))
t_dead = np.linspace(0, len(dead_ecg)/52.0, len(dead_ecg))

fig = plt.figure(figsize=(13, 8))
gs = fig.add_gridspec(2, 2, width_ratios=[2, 1])

# Panel A: Live plant time series
ax1 = fig.add_subplot(gs[0, 0])
mask_l = t_live <= 200
ax1.plot(t_live[mask_l], live_ecg[mask_l], color='#1f77b4', linewidth=0.7, alpha=0.85)
ax1.set_title("Live Plant: Normal Physiological Baseline (Active Trans-membrane Flux)",
              fontsize=11, fontweight='bold')
ax1.set_ylabel("ADC Counts (0-1023)", fontsize=9, fontweight='bold')
ax1.set_ylim(-10, 1040)
ax1.axhline(np.mean(live_ecg), color='navy', linestyle='--', label=f'Mean = {np.mean(live_ecg):.1f}')
ax1.legend(loc='upper right')

# Panel B: Dead plant time series
ax2 = fig.add_subplot(gs[1, 0])
mask_d = t_dead <= 200
ax2.plot(t_dead[mask_d], dead_ecg[mask_d], color='#7f7f7f', linewidth=0.7, alpha=0.85)
ax2.set_title("Dead Plant Tissue: Desiccated Negative Control (Passive Thermal Drift Only)",
              fontsize=11, fontweight='bold')
ax2.set_ylabel("ADC Counts (0-1023)", fontsize=9, fontweight='bold')
ax2.set_xlabel("Time (seconds)", fontsize=10, fontweight='bold')
ax2.set_ylim(-10, 1040)
ax2.axhline(np.mean(dead_ecg), color='black', linestyle='--', label=f'Mean = {np.mean(dead_ecg):.1f}')
ax2.legend(loc='upper right')

# Panel C: Distribution Comparison (KDE & Boxplot)
ax3 = fig.add_subplot(gs[:, 1])
sample_live = np.random.choice(live_ecg, min(50000, len(live_ecg)), replace=False)
sample_dead = np.random.choice(dead_ecg, min(50000, len(dead_ecg)), replace=False)

comp_df = pd.DataFrame({
    'Voltage (mV)': np.concatenate([sample_live * ADC_TO_MV, sample_dead * ADC_TO_MV]),
    'Tissue State': ['Live Plant (Physiological)'] * len(sample_live) + ['Dead Plant (Desiccated)'] * len(sample_dead)
})

sns.boxplot(data=comp_df, x='Tissue State', y='Voltage (mV)', palette=['#1f77b4', '#7f7f7f'], ax=ax3, width=0.4)
sns.stripplot(data=comp_df.sample(2000, random_state=42), x='Tissue State', y='Voltage (mV)',
              palette=['#1f77b4', '#7f7f7f'], ax=ax3, alpha=0.15, jitter=0.2, size=3)

live_iqr = np.percentile(live_ecg, 75) - np.percentile(live_ecg, 25)
dead_iqr = np.percentile(dead_ecg, 75) - np.percentile(dead_ecg, 25)

ax3.set_title("Biopotential Dispersion Comparison", fontsize=11, fontweight='bold')
ax3.text(0.05, 0.05, f"Live IQR: {live_iqr:.1f} ADC ({live_iqr*ADC_TO_MV:.1f} mV)\nDead IQR: {dead_iqr:.1f} ADC ({dead_iqr*ADC_TO_MV:.1f} mV)\nVariance Ratio: {(np.var(live_ecg)/np.var(dead_ecg)):.2f}x",
         transform=ax3.transAxes, fontsize=10, bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffea', edgecolor='#bbbbbb'))

plt.suptitle("Validation of Biological Biopotentials: Live Plant vs. Dead Plant Tissue",
             fontsize=13, fontweight='bold', y=0.99)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_03_biological_control_live_vs_dead.png", dpi=300)
plt.close()
print("Plot 3 saved.")

# -------------------------------------------------------------
# PLOT 4: Hydration Dynamics (Water Stimulation Response)
# -------------------------------------------------------------
print("Generating Plot 4: Hydration Dynamics...")
water_path = 'csv/2026-08-11/plant_water_morning_11hrs50min.csv'
df_w = pd.read_csv(water_path)
ecg_w = df_w['ecg'].values
t_w = np.linspace(0, len(ecg_w)/189.85, len(ecg_w))

fig, (ax_full, ax_zoom) = plt.subplots(2, 1, figsize=(12, 7))

# Full trace with rolling average
step_w = max(1, len(t_w) // 2500)
ax_full.plot(t_w[::step_w], ecg_w[::step_w], color='#a1d99b', alpha=0.5, label='Raw ADC (Subsampled)')

# Compute rolling mean and std to show variation potential
rolling_win = 190 * 5  # 5-second rolling window
s_ecg = pd.Series(ecg_w)
roll_mean = s_ecg.rolling(rolling_win, center=True).mean().values
roll_std = s_ecg.rolling(rolling_win, center=True).std().values

ax_full.plot(t_w[::step_w], roll_mean[::step_w], color='#006d2c', linewidth=2.0, label='5-Second Rolling Mean (Trend)')
ax_full.fill_between(t_w[::step_w], (roll_mean - roll_std)[::step_w], (roll_mean + roll_std)[::step_w],
                     color='#31a354', alpha=0.2, label='±1 SD Envelope')

ax_full.set_ylabel("ADC Count", fontsize=9, fontweight='bold')
ax_full.set_ylim(-20, 1050)
ax_full.set_title("[A] Complete Water Stimulus Trajectory (537 Seconds / ~9 Minutes)",
                  fontsize=11, fontweight='bold', loc='left')
ax_full.legend(loc='upper right')

# Zoomed 30-second window during initial water absorption (e.g. t = 20s to 50s)
mask_z = (t_w >= 15) & (t_w <= 65)
ax_zoom.plot(t_w[mask_z] - 15, ecg_w[mask_z], color='#2ca02c', linewidth=1.2, label='Transient Response')
ax_zoom.set_xlabel("Time from Hydration Perturbation (seconds)", fontsize=10, fontweight='bold')
ax_zoom.set_ylabel("ADC Count", fontsize=9, fontweight='bold')
ax_zoom.set_ylim(-20, 1050)
ax_zoom.set_title("[B] High-Resolution 50-Second Transient: Rapid Depolarization / Hydraulic Wave Coupling",
                  fontsize=11, fontweight='bold', loc='left')
ax_zoom.axvline(15, color='darkred', linestyle='--', linewidth=1.5, label='Hydration Onset Transient')
ax_zoom.legend(loc='upper right')

plt.suptitle("Electrophysiological Response to Hydration: Variation Potential & Transpiration Dynamics",
             fontsize=13, fontweight='bold', y=0.99)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_04_hydration_dynamics_water_stimulus.png", dpi=300)
plt.close()
print("Plot 4 saved.")

# -------------------------------------------------------------
# PLOT 5: Acoustic Stimulus Response: Silence vs Mantras vs Pop
# -------------------------------------------------------------
print("Generating Plot 5: Acoustic Stimulus Comparison...")
silence_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
pop_path = 'csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv'
mantra_path = 'csv/2026-10-09/plant_plant_om_mantra_afternoon_12hrs23min38sec.csv'
yalgaar_path = 'csv/2026-10-09/plant_music_yalgaar_afternoon_13hrs16min40sec.csv'

ecg_sil = pd.read_csv(silence_path)['ecg'].values
ecg_pop = pd.read_csv(pop_path)['ecg'].values
ecg_man = pd.read_csv(mantra_path)['ecg'].values
ecg_yal = pd.read_csv(yalgaar_path)['ecg'].values

fig, (ax_box, ax_var) = plt.subplots(1, 2, figsize=(13, 6))

# Prepare DataFrame for Seaborn
data_acoustic = pd.DataFrame({
    'Signal ADC': np.concatenate([ecg_sil, ecg_man, ecg_pop, ecg_yal]),
    'Stimulus': (['Silent Baseline'] * len(ecg_sil) +
                 ['Vedic Mantra (Om)'] * len(ecg_man) +
                 ['Pop ("Bye Bye Bye")'] * len(ecg_pop) +
                 ['High Beat ("Yalgaar")'] * len(ecg_yal))
})

palette = {'Silent Baseline': '#3498db', 'Vedic Mantra (Om)': '#9b59b6',
           'Pop ("Bye Bye Bye")': '#e74c3c', 'High Beat ("Yalgaar")': '#e67e22'}

sns.violinplot(data=data_acoustic, x='Stimulus', y='Signal ADC', palette=palette, ax=ax_box, cut=0, inner='quartile')
ax_box.set_title("[A] Biopotential Amplitude Distributions Across Acoustic Stimuli", fontsize=11, fontweight='bold')
ax_box.set_ylabel("ADC Counts (0-1023)", fontsize=10, fontweight='bold')
ax_box.set_ylim(-30, 1050)

# Variance / SD comparison bar chart
stds = [np.std(ecg_sil), np.std(ecg_man), np.std(ecg_pop), np.std(ecg_yal)]
iqrs = [np.percentile(ecg_sil, 75) - np.percentile(ecg_sil, 25),
        np.percentile(ecg_man, 75) - np.percentile(ecg_man, 25),
        np.percentile(ecg_pop, 75) - np.percentile(ecg_pop, 25),
        np.percentile(ecg_yal, 75) - np.percentile(ecg_yal, 25)]
labels = ['Silent Baseline', 'Vedic Mantra', 'Pop Music', 'High Beat']
x = np.arange(len(labels))
width = 0.35

ax_var.bar(x - width/2, stds, width, label='Standard Deviation (ADC)', color='#2980b9')
ax_var.bar(x + width/2, iqrs, width, label='Interquartile Range (ADC)', color='#d35400')
ax_var.set_xticks(x)
ax_var.set_xticklabels(labels, fontsize=10, fontweight='bold')
ax_var.set_ylabel("Signal Dispersion Metric (ADC Counts)", fontsize=10, fontweight='bold')
ax_var.set_title("[B] Mechanical Acoustic Perturbation: Dispersion Metrics", fontsize=11, fontweight='bold')
ax_var.legend(loc='upper left')

for i in range(len(labels)):
    ax_var.text(x[i] - width/2, stds[i] + 5, f"{stds[i]:.1f}", ha='center', fontsize=9, fontweight='bold')
    ax_var.text(x[i] + width/2, iqrs[i] + 5, f"{iqrs[i]:.1f}", ha='center', fontsize=9, fontweight='bold')

plt.suptitle("Acoustic Perturbation Effect: Plant Biopotential Response to Sound Waves",
             fontsize=13, fontweight='bold', y=0.99)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_05_acoustic_impact_silence_vs_music.png", dpi=300)
plt.close()
print("Plot 5 saved.")

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

# 60s sample from each
fs = 190.0
n_pts = int(60 * fs)
t_60 = np.linspace(0, 60, n_pts)

ax_ts.plot(t_60, ecg_m[:n_pts], label='Morning (11:39 AM) - Transpiration Active', color='#f39c12', alpha=0.8, linewidth=0.9)
ax_ts.plot(t_60, ecg_a[:n_pts], label='Afternoon (03:38 PM) - Steady State', color='#27ae60', alpha=0.8, linewidth=0.9)
ax_ts.plot(t_60, ecg_n[:n_pts], label='Night (10:47 PM) - Stomata Closed / Resting', color='#2c3e50', alpha=0.8, linewidth=0.9)

ax_ts.set_title("[A] 60-Second Snapshot Across Diurnal Cycles", fontsize=11, fontweight='bold')
ax_ts.set_xlabel("Time (seconds)", fontsize=10, fontweight='bold')
ax_ts.set_ylabel("ADC Count (0-1023)", fontsize=10, fontweight='bold')
ax_ts.set_ylim(-20, 1050)
ax_ts.legend(loc='upper right')

# Density KDE
sns.kdeplot(ecg_m, ax=ax_kde, color='#f39c12', label=f'Morning (SD={np.std(ecg_m):.1f})', linewidth=2)
sns.kdeplot(ecg_a, ax=ax_kde, color='#27ae60', label=f'Afternoon (SD={np.std(ecg_a):.1f})', linewidth=2)
sns.kdeplot(ecg_n, ax=ax_kde, color='#2c3e50', label=f'Night (SD={np.std(ecg_n):.1f})', linewidth=2)

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
# Compare: Baseline, Water, Pop Music, Classical Music, Dead Plant
fs = 190.0

conditions_psd = {
    'Normal Baseline': ('csv/2026-08-11/plant_normal_morning_11hrs39min.csv', '#1f77b4'),
    'Water Stimulation': ('csv/2026-08-11/plant_water_morning_11hrs50min.csv', '#2ca02c'),
    'Pop Music (Bye Bye Bye)': ('csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv', '#d62728'),
    'Classical Music': ('csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv', '#9467bd'),
    'Dead Plant': ('csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv', '#7f7f7f')
}

plt.figure(figsize=(11, 6))

for label, (fpath, col) in conditions_psd.items():
    df = pd.read_csv(fpath)
    sig = df['ecg'].values.astype(float)
    sig = sig - np.mean(sig)  # zero center
    
    # Welch PSD with 5-second Hann window (nperseg = 190 * 5 = 950)
    nperseg = min(len(sig), int(fs * 4))
    freqs, psd = signal.welch(sig, fs=fs, window='hann', nperseg=nperseg, noverlap=nperseg//2)
    
    # Restrict to 0.1 - 45 Hz (AD8232 analog bandwidth)
    mask = (freqs >= 0.1) & (freqs <= 45.0)
    plt.semilogy(freqs[mask], psd[mask], label=label, color=col, linewidth=1.8, alpha=0.85)

plt.axvspan(0.1, 2.0, color='#ffffcc', alpha=0.3, label='Low Freq (0.1-2 Hz: Slow Wave Potential)')
plt.axvspan(2.0, 10.0, color='#e0f3f8', alpha=0.3, label='Mid Freq (2-10 Hz: Action Potentials)')
plt.axvspan(10.0, 45.0, color='#fee0d2', alpha=0.3, label='High Freq (10-45 Hz: Acoustic/Burst Vibration)')

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

