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

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Global IEEE Typography and Aesthetics for Individual Large-Format Figures
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Cambria', 'Georgia', 'serif']
plt.rcParams['mathtext.fontset'] = 'dejavuserif'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.6
plt.rcParams['grid.color'] = '#777777'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['grid.alpha'] = 0.65
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.major.size'] = 7
plt.rcParams['ytick.major.size'] = 7
plt.rcParams['xtick.major.width'] = 1.4
plt.rcParams['ytick.major.width'] = 1.4
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.labelsize'] = 16

OUT_DIR = "IEEE/figures/individual"
os.makedirs(OUT_DIR, exist_ok=True)
fs = 190.0
ADC_TO_MV = 5000.0 / 1023.0

print("Generating 14 individual high-resolution IEEE figures one by one...")

# -------------------------------------------------------------------------
# Common Data Loading
# -------------------------------------------------------------------------
live_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
baseline_path = live_path
dead_path = 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'
water_path = 'csv/2026-08-11/plant_water_morning_11hrs50min.csv'
pop_path = 'csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv'
classical_path = 'csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv'

silence_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
mantra_path = 'csv/2026-10-09/plant_plant_om_mantra_afternoon_12hrs23min38sec.csv'
yalgaar_path = 'csv/2026-10-09/plant_music_yalgaar_afternoon_13hrs16min40sec.csv'

morn_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
aft_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
night_path = 'csv/2026-08-11/plant_om_night_22hrs47min.csv'

feat_df = pd.read_csv("presentation_2/06-11-2026/scratch/plant_features_extracted.csv")

ecg_live = pd.read_csv(live_path)['ecg'].values.astype(float)
ecg_dead = pd.read_csv(dead_path)['ecg'].values.astype(float)
ecg_water = pd.read_csv(water_path)['ecg'].values.astype(float)

# =========================================================================
# FIGURE 01: Time-Domain Resting Trace (Living vs. Dead Control)
# =========================================================================
print("Exporting Fig 01: Time-Domain Resting Trace...")
fig, ax = plt.subplots(figsize=(11, 6.5))
t_50 = np.linspace(0, 50, int(50 * fs))
live_50 = ecg_live[1000:1000 + len(t_50)]
dead_50 = ecg_dead[500:500 + len(t_50)]

ax.plot(t_50, live_50, color='#003366', linewidth=2.0, label='Living Plant (Epipremnum aureum, Active Proton Pumps)')
ax.plot(t_50, dead_50, color='#b22222', linewidth=1.8, linestyle='--', label='Desiccated Dead Tissue (Negative Biological Control)')
ax.axhline(np.mean(live_50), color='#003366', linestyle=':', linewidth=1.4, label=f'Living Mean = {np.mean(live_50):.1f} ADC ({np.mean(live_50)*ADC_TO_MV:.1f} mV)')
ax.axhline(np.mean(dead_50), color='#b22222', linestyle=':', linewidth=1.4, label=f'Dead Mean = {np.mean(dead_50):.1f} ADC ({np.mean(dead_50)*ADC_TO_MV:.1f} mV)')

ax.set_xlabel('Time (Seconds)', fontsize=16, labelpad=8)
ax.set_ylabel('Biopotential (ADC Counts, 0–1023)', fontsize=16, labelpad=8)
ax.set_xlim(0, 50)
ax.set_ylim(-20, 1040)
ax.grid(True)
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12.5)
ax.set_title('Figure 1: 50-Second Continuous Resting Biopotential Trace (Living vs. Dead Control)',
             fontsize=17, fontweight='bold', pad=12)

ax_mv = ax.twinx()
ax_mv.set_ylim(-20 * ADC_TO_MV, 1040 * ADC_TO_MV)
ax_mv.set_ylabel('Voltage Potential (mV)', fontsize=15, color='#333333', labelpad=8)
ax_mv.tick_params(colors='#333333', labelsize=13)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_01_time_domain_resting_trace.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_01_time_domain_resting_trace.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 02: Waveform Micro-Structure & Depolarization Peak
# =========================================================================
print("Exporting Fig 02: Waveform Microstructure Inset...")
fig, ax = plt.subplots(figsize=(11, 6.5))
t_4 = np.linspace(0, 4.0, int(4.0 * fs))
live_4 = ecg_live[3000:3000 + len(t_4)]
dead_4 = ecg_dead[1500:1500 + len(t_4)]

ax.plot(t_4, live_4, color='#003366', linewidth=2.4, marker='o', markersize=4.5, markevery=10,
        label='Living Waveform (Action / Slow Wave Depolarization)')
ax.plot(t_4, dead_4, color='#b22222', linewidth=2.0, linestyle='-.', marker='s', markersize=4.5, markevery=10,
        label='Dead Tissue Control (Passive Quantization Jitter, Zero Flux)')

ax.set_xlabel('Window Elapsed Time (Seconds)', fontsize=16, labelpad=8)
ax.set_ylabel('Biopotential (ADC Counts)', fontsize=16, labelpad=8)
ax.set_xlim(0, 4.0)
ax.set_ylim(-20, 1040)
ax.grid(True)
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12.5)
ax.set_title('Figure 2: Millisecond-Resolution Waveform Micro-Structure & Depolarization Peak',
             fontsize=17, fontweight='bold', pad=12)

peak_idx = np.argmax(live_4)
ax.annotate('Physiological Depolarization Peak\n(Ca²⁺ Influx & Cl⁻ Efflux Across Membrane)',
            xy=(t_4[peak_idx], live_4[peak_idx]),
            xytext=(t_4[peak_idx] - 1.4, live_4[peak_idx] - 240),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontsize=12, fontweight='bold', bbox=dict(boxstyle='square,pad=0.4', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_02_waveform_microstructure_action_potential.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_02_waveform_microstructure_action_potential.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 03: Hydration Dynamics (Variation Potential Wave)
# =========================================================================
print("Exporting Fig 03: Hydration Variation Potential Trajectory...")
fig, ax = plt.subplots(figsize=(11, 6.5))
t_water = np.linspace(0, len(ecg_water)/fs, len(ecg_water))
step_w = max(1, len(t_water) // 2500)
s_w = pd.Series(ecg_water)
roll_mean = s_w.rolling(int(fs * 5), center=True).mean().values
roll_std = s_w.rolling(int(fs * 5), center=True).std().values

ax.plot(t_water[::step_w], ecg_water[::step_w], color='#88c999', alpha=0.45, linewidth=1.0, label='Raw Biopotential Samples')
ax.plot(t_water[::step_w], roll_mean[::step_w], color='#006633', linewidth=2.8, label='5-Second Rolling Mean (Variation Potential Wave)')
ax.fill_between(t_water[::step_w], (roll_mean - roll_std)[::step_w], (roll_mean + roll_std)[::step_w],
                color='#2e8b57', alpha=0.25, label='±1 Standard Deviation Envelope')

ax.axvline(25, color='#b22222', linestyle='--', linewidth=2.2, label='Hydration Onset (Water Injection at t = 25 s)')
ax.annotate('Rapid Depolarization Wave\n(Xylem Tension Release & Hydraulic Coupling)',
            xy=(28, 620), xytext=(80, 800),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontsize=12.5, fontweight='bold', bbox=dict(boxstyle='square,pad=0.4', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

ax.set_xlabel('Time Post-Stimulus (Seconds)', fontsize=16, labelpad=8)
ax.set_ylabel('Biopotential (ADC Counts)', fontsize=16, labelpad=8)
ax.set_xlim(0, 520)
ax.set_ylim(-20, 1040)
ax.grid(True)
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12.5)
ax.set_title('Figure 3: Plant Hydration Electrophysiological Response (Variation Potential Trajectory)',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_03_hydration_variation_potential_trajectory.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_03_hydration_variation_potential_trajectory.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 04: Biopotential Density & Variance Ratio (Live vs. Dead)
# =========================================================================
print("Exporting Fig 04: Biopotential Density & Variance Ratio...")
fig, ax = plt.subplots(figsize=(11, 6.5))
sample_live = np.random.choice(ecg_live, min(40000, len(ecg_live)), replace=False)
sample_dead = np.random.choice(ecg_dead, min(40000, len(ecg_dead)), replace=False)

sns.kdeplot(sample_live, ax=ax, color='#003366', linewidth=2.6,
            label=f'Living Tissue (IQR = {np.percentile(sample_live, 75) - np.percentile(sample_live, 25):.1f} ADC Counts)')
sns.kdeplot(sample_dead, ax=ax, color='#b22222', linewidth=2.6, linestyle='--',
            label=f'Dead Control (IQR = {np.percentile(sample_dead, 75) - np.percentile(sample_dead, 25):.1f} ADC Counts)')

var_ratio = np.var(sample_live) / np.var(sample_dead)
ax.text(0.05, 0.75, f'Variance Ratio:\nVar(Live) / Var(Dead) = {var_ratio:.2f}×\nLiving State: Active Ionic Turbulence\nDead Control: Passive Baseline Drift',
        transform=ax.transAxes, fontsize=13, fontweight='bold',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#ffffff', edgecolor='black', linewidth=1.4))

ax.set_xlabel('Biopotential (ADC Counts, 0–1023)', fontsize=16, labelpad=8)
ax.set_ylabel('Probability Density Function', fontsize=16, labelpad=8)
ax.set_xlim(0, 1023)
ax.grid(True)
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=13)
ax.set_title('Figure 4: Biopotential Probability Density & Variance Ratio (Live vs. Dead Control)',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_04_biopotential_density_and_variance_ratio.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_04_biopotential_density_and_variance_ratio.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 05: Power Spectral Density (PSD - Welch's Method)
# =========================================================================
print("Exporting Fig 05: Welch Power Spectral Density...")
fig, ax = plt.subplots(figsize=(11, 6.5))
conditions_psd = [
    ('Normal Baseline', baseline_path, '#003366', '-'),
    ('Water Stimulation', water_path, '#006633', '--'),
    ('Pop Music ("Bye Bye Bye")', pop_path, '#b22222', '-'),
    ('Classical Music', classical_path, '#800080', '-.'),
    ('Dead Plant Control', dead_path, '#777777', ':')
]

for label, fpath, col, ls in conditions_psd:
    df = pd.read_csv(fpath)
    sig = df['ecg'].values.astype(float)
    sig = sig - np.mean(sig)
    nperseg = min(len(sig), int(fs * 4))
    freqs, psd = signal.welch(sig, fs=fs, window='hann', nperseg=nperseg, noverlap=nperseg//2)
    mask = (freqs >= 0.1) & (freqs <= 45.0)
    ax.semilogy(freqs[mask], psd[mask], label=label, color=col, linestyle=ls, linewidth=2.2)

ax.axvspan(0.1, 2.0, color='#ffffcc', alpha=0.35, label='Slow Wave Band (0.1–2 Hz: Hydraulic Coupling)')
ax.axvspan(2.0, 10.0, color='#e0f3f8', alpha=0.35, label='Action Potential Band (2–10 Hz: Ionic Bursts)')
ax.axvspan(10.0, 45.0, color='#fee0d2', alpha=0.35, label='Acoustic/Vibration Band (10–45 Hz: Leaf Vibration)')

ax.set_xlabel('Frequency (Hz)', fontsize=16, labelpad=8)
ax.set_ylabel('Power Spectral Density (ADC²/Hz, log scale)', fontsize=16, labelpad=8)
ax.set_xlim(0.1, 45.0)
ax.grid(True, which="both")
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=11.5)
ax.set_title('Figure 5: Power Spectral Density (PSD) Analysis Across Plant Physiological States',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_05_power_spectral_density_welch.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_05_power_spectral_density_welch.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 06: Acoustic Sound Pressure Dispersion Metrics
# =========================================================================
print("Exporting Fig 06: Acoustic Dispersion Metrics...")
fig, ax = plt.subplots(figsize=(11, 6.5))
ecg_sil = pd.read_csv(silence_path)['ecg'].values.astype(float)
ecg_man = pd.read_csv(mantra_path)['ecg'].values.astype(float)
ecg_pop = pd.read_csv(pop_path)['ecg'].values.astype(float)
ecg_yal = pd.read_csv(yalgaar_path)['ecg'].values.astype(float)

stds = [np.std(ecg_sil), np.std(ecg_man), np.std(ecg_pop), np.std(ecg_yal)]
iqrs = [np.percentile(ecg_sil, 75) - np.percentile(ecg_sil, 25),
        np.percentile(ecg_man, 75) - np.percentile(ecg_man, 25),
        np.percentile(ecg_pop, 75) - np.percentile(ecg_pop, 25),
        np.percentile(ecg_yal, 75) - np.percentile(ecg_yal, 25)]

labels_ac = ['Silence (Baseline)', 'Vedic Mantra (Om)', 'Pop ("Bye Bye Bye")', 'Fast Rap ("Yalgaar")']
x_ac = np.arange(len(labels_ac))
w_ac = 0.35

bars_std = ax.bar(x_ac - w_ac/2, stds, w_ac, label='Standard Deviation (σ, Total AC Energy)',
                  color='#003366', edgecolor='black', linewidth=1.2, hatch='//')
bars_iqr = ax.bar(x_ac + w_ac/2, iqrs, w_ac, label='Interquartile Range (IQR, Non-Gaussian Spread)',
                  color='#b22222', edgecolor='black', linewidth=1.2, hatch='\\\\')

ax.set_ylabel('Dispersion Amplitude (ADC Counts)', fontsize=16, labelpad=8)
ax.set_xticks(x_ac)
ax.set_xticklabels(labels_ac, fontsize=13, fontweight='bold')
ax.set_ylim(0, 750)
ax.grid(True, axis='y')
ax.legend(loc='upper left', framealpha=1.0, edgecolor='black', fontsize=13)
ax.set_title('Figure 6: Acoustic Sound Pressure Wave Impact on Plant Biopotential Dispersion',
             fontsize=17, fontweight='bold', pad=12)

for rect in bars_std:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 12, f'{h:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
for rect in bars_iqr:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 12, f'{h:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_06_acoustic_dispersion_sound_pressure.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_06_acoustic_dispersion_sound_pressure.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 07: Circadian Diurnal Baseline Dynamics
# =========================================================================
print("Exporting Fig 07: Circadian Diurnal Baseline Dynamics...")
fig, ax = plt.subplots(figsize=(11, 6.5))
ecg_m = pd.read_csv(morn_path)['ecg'].values.astype(float)
ecg_a = pd.read_csv(aft_path)['ecg'].values.astype(float)
ecg_n = pd.read_csv(night_path)['ecg'].values.astype(float)

dur_c = 45.0
n_c = int(dur_c * fs)
t_c = np.linspace(0, dur_c, n_c)

ax.plot(t_c, ecg_m[:n_c], color='#e67e22', linewidth=1.8,
        label=f'Morning (11:39 AM, σ = {np.std(ecg_m):.1f} ADC) — Active Transpiration & Open Stomata')
ax.plot(t_c, ecg_a[:n_c], color='#006633', linewidth=1.8,
        label=f'Afternoon (03:38 PM, σ = {np.std(ecg_a):.1f} ADC) — Steady-State Sap Flow')
ax.plot(t_c, ecg_n[:n_c], color='#003366', linewidth=1.8, linestyle='--',
        label=f'Night (10:47 PM, σ = {np.std(ecg_n):.1f} ADC) — Nocturnal Stomatal Closure')

ax.set_xlabel('Time (Seconds)', fontsize=16, labelpad=8)
ax.set_ylabel('Biopotential (ADC Counts, 0–1023)', fontsize=16, labelpad=8)
ax.set_xlim(0, dur_c)
ax.set_ylim(-20, 1040)
ax.grid(True)
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12)
ax.set_title('Figure 7: Circadian & Diurnal Electrophysiological Baseline Dynamics',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_07_circadian_diurnal_dynamics.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_07_circadian_diurnal_dynamics.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 08: Spectral Energy Allocation Across Bands
# =========================================================================
print("Exporting Fig 08: Relative Spectral Energy Allocation...")
fig, ax = plt.subplots(figsize=(11, 6.5))
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
width_d = 0.52

p1 = ax.bar(x_d, low_pcts, width_d, label='Low Freq (0.1–2 Hz: Slow Wave Potential)', color='#003366', edgecolor='black', linewidth=1.2)
p2 = ax.bar(x_d, mid_pcts, width_d, bottom=low_pcts, label='Mid Freq (2–10 Hz: Action Potentials)', color='#2e8b57', edgecolor='black', linewidth=1.2)
p3 = ax.bar(x_d, high_pcts, width_d, bottom=np.array(low_pcts) + np.array(mid_pcts), label='High Freq (10–45 Hz: Acoustic Vibration)', color='#b22222', edgecolor='black', linewidth=1.2)

ax.set_ylabel('Spectral Energy Allocation (%)', fontsize=16, labelpad=8)
ax.set_xticks(x_d)
ax.set_xticklabels(display_labels, fontsize=13, fontweight='bold')
ax.set_ylim(0, 108)
ax.grid(True, axis='y')
ax.legend(loc='lower right', framealpha=1.0, edgecolor='black', fontsize=12)
ax.set_title('Figure 8: Relative Spectral Energy Allocation Across Physiological Frequency Bands',
             fontsize=17, fontweight='bold', pad=12)

ax.annotate('Acoustic High-Frequency Surge\n(>25% of Total Energy in 10–45 Hz)',
            xy=(3, 85), xytext=(1.4, 90),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontsize=12, fontweight='bold', bbox=dict(boxstyle='square,pad=0.4', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_08_spectral_energy_allocation_bands.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_08_spectral_energy_allocation_bands.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 09: The Data Leakage Dilemma Benchmark
# =========================================================================
print("Exporting Fig 09: The Data Leakage Dilemma Benchmark...")
fig, ax = plt.subplots(figsize=(11, 6.5))
model_names = ['Logistic Regression', 'K-Nearest Neighbors', 'Decision Tree', 'Random Forest', 'SVM (RBF Kernel)']
strat_acc = [84.18, 93.62, 90.18, 96.87, 90.75]
strat_err = [1.37, 1.29, 0.99, 0.55, 1.29]
group_acc = [16.81, 16.62, 27.52, 25.46, 11.05]
group_err = [12.07, 12.91, 21.39, 14.44, 13.33]

x_m = np.arange(len(model_names))
w_m = 0.35

rects_s = ax.bar(x_m - w_m/2, strat_acc, w_m, yerr=strat_err, capsize=5,
                 label='Stratified K-Fold (Naive Random Shuffle: Data Leakage Trap)',
                 color='#b22222', edgecolor='black', linewidth=1.2, hatch='//')
rects_g = ax.bar(x_m + w_m/2, group_acc, w_m, yerr=group_err, capsize=5,
                 label='Group K-Fold (Strict Leave-Session-Out: True Scientific Benchmark)',
                 color='#003366', edgecolor='black', linewidth=1.2, hatch='\\\\')

ax.axhline(20.0, color='#444444', linestyle='--', linewidth=1.8, label='Random Chance Baseline (5 Classes = 20%)')
ax.set_ylabel('Classification Accuracy (%)', fontsize=16, labelpad=8)
ax.set_xticks(x_m)
ax.set_xticklabels(model_names, fontsize=12, fontweight='bold', rotation=15, ha='right')
ax.set_ylim(0, 118)
ax.grid(True, axis='y')
ax.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=11.5)
ax.set_title('Figure 9: The Temporal Data Leakage Dilemma in Multi-Class Biopotential Classification',
             fontsize=17, fontweight='bold', pad=12)

for rect in rects_s:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
for rect in rects_g:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_09_data_leakage_dilemma_benchmark.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_09_data_leakage_dilemma_benchmark.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 10: Robust Cross-Session Generalization
# =========================================================================
print("Exporting Fig 10: Robust Cross-Session Generalization...")
fig, ax = plt.subplots(figsize=(11, 6.5))
tasks_b = ['Living Plant vs. Dead Control', 'Silence vs. Pop Music Vibration']
acc_b = [93.99, 86.35]
acc_err_b = [5.72, 5.65]
f1_b = [48.93, 81.58]
f1_err_b = [0.83, 6.53]

x_b = np.arange(len(tasks_b))
w_b = 0.32

rects_b_acc = ax.bar(x_b - w_b/2, acc_b, w_b, yerr=acc_err_b, capsize=6,
                     label='Cross-Session Accuracy (%)', color='#003366', edgecolor='black', linewidth=1.2, hatch='..')
rects_b_f1 = ax.bar(x_b + w_b/2, f1_b, w_b, yerr=f1_err_b, capsize=6,
                    label='Macro F1-Score (%)', color='#2e8b57', edgecolor='black', linewidth=1.2, hatch='xx')

ax.axhline(50.0, color='#444444', linestyle='--', linewidth=1.8, label='Binary Chance Baseline (50%)')
ax.set_ylabel('Generalization Metric on Unseen Sessions (%)', fontsize=16, labelpad=8)
ax.set_xticks(x_b)
ax.set_xticklabels(tasks_b, fontsize=14, fontweight='bold')
ax.set_ylim(0, 118)
ax.grid(True, axis='y')
ax.legend(loc='lower left', framealpha=1.0, edgecolor='black', fontsize=12.5)
ax.set_title('Figure 10: Robust Cross-Session Generalization on Unseen Recording Days',
             fontsize=17, fontweight='bold', pad=12)

for rect in rects_b_acc:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
for rect in rects_b_f1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_10_cross_session_generalization_robust.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_10_cross_session_generalization_robust.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 11: Multi-Class Confusion Matrix (Random Forest)
# =========================================================================
print("Exporting Fig 11: Multi-Class Normalized Confusion Matrix...")
fig, ax = plt.subplots(figsize=(10, 8))
features = [
    'mean_adc', 'std_adc', 'var_adc', 'min_adc', 'max_adc', 'peak_to_peak',
    'median_adc', 'iqr_adc', 'rms_adc', 'skewness', 'kurtosis',
    'mean_abs_diff', 'zero_crossings', 'peak_count',
    'power_low_freq', 'power_mid_freq', 'power_high_freq',
    'power_ratio_high_low', 'spectral_centroid', 'spectral_entropy'
]
X = feat_df[features].fillna(0).values
y = feat_df['category'].values

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.30, stratify=y, random_state=42)
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr)
X_te_s = scaler.transform(X_te)

rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf.fit(X_tr_s, y_tr)
y_pred = rf.predict(X_te_s)

categories = sorted(feat_df['category'].unique())
short_labels = ['Pop Music', 'Mantra', 'Dead (Ctrl)', 'Baseline', 'Water Stim.']
cm = confusion_matrix(y_te, y_pred, labels=categories)
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

im = ax.imshow(cm_norm, cmap='Blues', vmin=0, vmax=1.0, aspect='auto')
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=12)
cbar.set_label('Normalized Prediction Fraction', fontsize=14, labelpad=8)

ax.set_xticks(np.arange(len(short_labels)))
ax.set_yticks(np.arange(len(short_labels)))
ax.set_xticklabels(short_labels, fontsize=13, fontweight='bold', rotation=25, ha='right')
ax.set_yticklabels(short_labels, fontsize=13, fontweight='bold')
ax.set_xlabel('Predicted Plant State', fontsize=16, labelpad=8)
ax.set_ylabel('True Plant State', fontsize=16, labelpad=8)
ax.set_title('Figure 11: Multi-Class Normalized Confusion Matrix (Random Forest Classifier)',
             fontsize=17, fontweight='bold', pad=12)

for i in range(len(short_labels)):
    for j in range(len(short_labels)):
        val = cm_norm[i, j]
        color_txt = "white" if val > 0.55 else "black"
        ax.text(j, i, f"{val:.2f}\n(n={cm[i,j]})", ha='center', va='center',
                color=color_txt, fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_11_multiclass_confusion_matrix_rf.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_11_multiclass_confusion_matrix_rf.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 12: Gini Feature Importance Hierarchy
# =========================================================================
print("Exporting Fig 12: Gini Feature Importance Hierarchy...")
fig, ax = plt.subplots(figsize=(11, 6.5))
importances = rf.feature_importances_
feat_imp = pd.DataFrame({'feature': features, 'importance': importances}).sort_values('importance', ascending=True)
top_feats = feat_imp.tail(10)

pretty_names = {
    'power_low_freq': 'Low Freq Power (0.1–2 Hz: Slow Wave Dynamics)',
    'std_adc': 'Standard Deviation (σ: Total AC Energy)',
    'var_adc': 'Biopotential Variance (σ²)',
    'iqr_adc': 'Interquartile Range (IQR: Non-Gaussian Spread)',
    'mean_abs_diff': 'Signal Velocity / MAD (|ΔV/Δt|)',
    'power_high_freq': 'High Freq Power (10–45 Hz: Acoustic Vibration)',
    'peak_to_peak': 'Peak-to-Peak Amplitude (Vmax - Vmin)',
    'rms_adc': 'Root Mean Square (RMS Power)',
    'spectral_centroid': 'Spectral Centroid Frequency (f̄)',
    'power_mid_freq': 'Mid Freq Power (2–10 Hz: Action Potentials)'
}
labels_d = [pretty_names.get(f, f) for f in top_feats['feature']]

y_pos = np.arange(len(labels_d))
rects_d = ax.barh(y_pos, top_feats['importance'] * 100, color='#003366', edgecolor='black', linewidth=1.2, height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels_d, fontsize=12.5, fontweight='bold')
ax.set_xlabel('Gini Feature Importance (%)', fontsize=16, labelpad=8)
ax.set_xlim(0, 26)
ax.grid(True, axis='x')
ax.set_title('Figure 12: Gini Feature Importance Hierarchy for Plant State Discrimination',
             fontsize=17, fontweight='bold', pad=12)

for rect in rects_d:
    w_val = rect.get_width()
    ax.text(w_val + 0.4, rect.get_y() + rect.get_height()/2., f'{w_val:.1f}%', va='center', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_12_gini_feature_importance_hierarchy.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_12_gini_feature_importance_hierarchy.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 13: Feature Cross-Correlation Matrix Heatmap
# =========================================================================
print("Exporting Fig 13: Feature Cross-Correlation Matrix...")
fig, ax = plt.subplots(figsize=(12, 10))
corr = feat_df[features].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

pretty_labels_all = [
    'Mean (μ)', 'Std. Dev. (σ)', 'Variance (σ²)', 'Min Potential', 'Max Potential', 'Peak-to-Peak',
    'Median', 'IQR', 'RMS Energy', 'Skewness (γ₁)', 'Kurtosis (γ₂)',
    'Velocity (MAD)', 'Zero Crossings', 'Peak Count',
    'Low Freq (0.1–2 Hz)', 'Mid Freq (2–10 Hz)', 'High Freq (10–45 Hz)',
    'High/Low Ratio', 'Spectral Centroid', 'Spectral Entropy'
]

im = sns.heatmap(corr, mask=mask, cmap='vlag', vmin=-1.0, vmax=1.0, ax=ax,
                 cbar_kws={'label': 'Pearson Correlation Coefficient (r)', 'shrink': 0.8},
                 square=True, linewidths=0.6, linecolor='white')
cbar = im.collections[0].colorbar
cbar.ax.tick_params(labelsize=13)
cbar.set_label('Pearson Correlation Coefficient (r)', fontsize=15, labelpad=8)

ax.set_xticks(np.arange(len(features)) + 0.5)
ax.set_yticks(np.arange(len(features)) + 0.5)
ax.set_xticklabels(pretty_labels_all, fontsize=10.5, rotation=45, ha='right', fontweight='bold')
ax.set_yticklabels(pretty_labels_all, fontsize=10.5, fontweight='bold')
ax.set_title('Figure 13: Feature Cross-Correlation Matrix of Plant Electrophysiological Domain',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_13_feature_cross_correlation_matrix.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_13_feature_cross_correlation_matrix.pdf", bbox_inches='tight')
plt.close()

# =========================================================================
# FIGURE 14: Interpretable Decision Tree Rule Flowchart
# =========================================================================
print("Exporting Fig 14: Interpretable Decision Tree Flowchart...")
fig, ax = plt.subplots(figsize=(14, 7.5))
dt = DecisionTreeClassifier(max_depth=3, random_state=42)
dt.fit(feat_df[features].fillna(0), feat_df['category'])

plot_tree(dt, feature_names=pretty_labels_all, class_names=short_labels,
          filled=True, rounded=True, fontsize=10, precision=1, ax=ax,
          proportion=True)

ax.set_title('Figure 14: Interpretable Rule-Based Flowchart for Plant State Classification',
             fontsize=17, fontweight='bold', pad=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/fig_14_interpretable_decision_tree_flowchart.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/fig_14_interpretable_decision_tree_flowchart.pdf", bbox_inches='tight')
plt.close()

print("\nSuccessfully generated all 14 individual IEEE figures in high-DPI PNG and vector PDF!")
