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

# Ultra-large font settings for presentation projection (100% visibility)
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
plt.rcParams['xtick.major.size'] = 6
plt.rcParams['ytick.major.size'] = 6
plt.rcParams['xtick.major.width'] = 1.4
plt.rcParams['ytick.major.width'] = 1.4
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.labelsize'] = 16

OUT_DIR = "IEEE/figures/standalone"
os.makedirs(OUT_DIR, exist_ok=True)
fs = 190.0
ADC_TO_MV = 5000.0 / 1023.0

print("Generating standalone ultra-clear presentation graphs with extra-large text...")

# -------------------------------------------------------------
# Standalone 1: Live Plant vs Dead Plant Waveform & Inset
# -------------------------------------------------------------
live_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
dead_path = 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'
ecg_live = pd.read_csv(live_path)['ecg'].values.astype(float)
ecg_dead = pd.read_csv(dead_path)['ecg'].values.astype(float)

fig, (ax_main, ax_zoom) = plt.subplots(2, 1, figsize=(12, 8.5), gridspec_kw={'height_ratios': [1.8, 1.2]})

t_30 = np.linspace(0, 30, int(30 * fs))
ax_main.plot(t_30, ecg_live[1000:1000 + len(t_30)], color='#003366', linewidth=2.0,
             label='Living Plant Tissue (Epipremnum aureum, Active Proton Pumps)')
ax_main.plot(t_30, ecg_dead[500:500 + len(t_30)], color='#b22222', linewidth=1.8, linestyle='--',
             label='Desiccated Dead Tissue (Negative Biological Control, Passive Jitter)')

ax_main.set_ylabel('Biopotential (ADC Counts)', fontsize=16, labelpad=8)
ax_main.set_xlim(0, 30)
ax_main.set_ylim(-20, 1040)
ax_main.grid(True)
ax_main.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=13)
ax_main.set_title('Figure S1: Biological Validation of Endogenous Plant Biopotentials vs. Dead Tissue',
                  fontsize=17, fontweight='bold', pad=10)

# Secondary mV axis
ax_mv = ax_main.twinx()
ax_mv.set_ylim(-20 * ADC_TO_MV, 1040 * ADC_TO_MV)
ax_mv.set_ylabel('Voltage (mV)', fontsize=15, color='#333333', labelpad=8)
ax_mv.tick_params(colors='#333333', labelsize=13)

# Zoomed 3-second inset
t_3 = np.linspace(0, 3.0, int(3.0 * fs))
ax_zoom.plot(t_3, ecg_live[3000:3000 + len(t_3)], color='#003366', linewidth=2.2, marker='o', markersize=4, markevery=10,
             label='Live Micro-Structure (Asymmetric Action/Slow Wave Depolarization)')
ax_zoom.plot(t_3, ecg_dead[1500:1500 + len(t_3)], color='#b22222', linewidth=2.0, linestyle='-.', marker='s', markersize=4, markevery=10,
             label='Dead Control (Quantization Noise, Zero Electrogenic Flux)')
ax_zoom.set_xlabel('Time (Seconds)', fontsize=16, labelpad=8)
ax_zoom.set_ylabel('ADC Counts', fontsize=16, labelpad=8)
ax_zoom.set_xlim(0, 3.0)
ax_zoom.set_ylim(-20, 1040)
ax_zoom.grid(True)
ax_zoom.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/graph1_live_vs_dead_validation.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/graph1_live_vs_dead_validation.pdf", bbox_inches='tight')
plt.close()
print("Saved graph 1.")

# -------------------------------------------------------------
# Standalone 2: Hydration Dynamics (Variation Potential Wave)
# -------------------------------------------------------------
water_path = 'csv/2026-08-11/plant_water_morning_11hrs50min.csv'
ecg_water = pd.read_csv(water_path)['ecg'].values.astype(float)
t_water = np.linspace(0, len(ecg_water)/fs, len(ecg_water))

fig, ax_w = plt.subplots(figsize=(12, 6.5))
step_w = max(1, len(t_water) // 2500)
s_w = pd.Series(ecg_water)
roll_mean = s_w.rolling(int(fs * 5), center=True).mean().values
roll_std = s_w.rolling(int(fs * 5), center=True).std().values

ax_w.plot(t_water[::step_w], ecg_water[::step_w], color='#88c999', alpha=0.45, linewidth=1.0, label='Raw Biopotential Samples')
ax_w.plot(t_water[::step_w], roll_mean[::step_w], color='#006633', linewidth=2.8, label='5-Second Rolling Mean (Variation Potential Wave)')
ax_w.fill_between(t_water[::step_w], (roll_mean - roll_std)[::step_w], (roll_mean + roll_std)[::step_w],
                  color='#2e8b57', alpha=0.25, label='±1 Standard Deviation Envelope')

ax_w.axvline(25, color='#b22222', linestyle='--', linewidth=2.2, label='Hydration Shock Onset (Water Injection)')
ax_w.annotate('Rapid Depolarization Shift\n(Xylem Tension Release & Ca²⁺ Influx)',
              xy=(28, 620), xytext=(70, 780),
              arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
              fontsize=13, fontweight='bold', bbox=dict(boxstyle='square,pad=0.4', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

ax_w.set_xlabel('Time Post-Stimulus (Seconds)', fontsize=16, labelpad=8)
ax_w.set_ylabel('Biopotential (ADC Counts)', fontsize=16, labelpad=8)
ax_w.set_xlim(0, 520)
ax_w.set_ylim(-20, 1040)
ax_w.grid(True)
ax_w.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=12.5)
ax_w.set_title('Figure S2: Plant Hydration Electrophysiological Response (Variation Potential)',
               fontsize=17, fontweight='bold', pad=10)

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/graph2_hydration_dynamics_variation_potential.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/graph2_hydration_dynamics_variation_potential.pdf", bbox_inches='tight')
plt.close()
print("Saved graph 2.")

# -------------------------------------------------------------
# Standalone 3: Acoustic Perturbation Dispersion (Silence vs Mantras vs Pop)
# -------------------------------------------------------------
silence_path = 'csv/2026-10-09/plant_without_music_afternoon_15hrs38min49sec.csv'
mantra_path = 'csv/2026-10-09/plant_plant_om_mantra_afternoon_12hrs23min38sec.csv'
pop_path = 'csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv'
yalgaar_path = 'csv/2026-10-09/plant_music_yalgaar_afternoon_13hrs16min40sec.csv'

ecg_sil = pd.read_csv(silence_path)['ecg'].values.astype(float)
ecg_man = pd.read_csv(mantra_path)['ecg'].values.astype(float)
ecg_pop = pd.read_csv(pop_path)['ecg'].values.astype(float)
ecg_yal = pd.read_csv(yalgaar_path)['ecg'].values.astype(float)

fig, ax_ac = plt.subplots(figsize=(11, 6.5))
stds = [np.std(ecg_sil), np.std(ecg_man), np.std(ecg_pop), np.std(ecg_yal)]
iqrs = [np.percentile(ecg_sil, 75) - np.percentile(ecg_sil, 25),
        np.percentile(ecg_man, 75) - np.percentile(ecg_man, 25),
        np.percentile(ecg_pop, 75) - np.percentile(ecg_pop, 25),
        np.percentile(ecg_yal, 75) - np.percentile(ecg_yal, 25)]

labels_ac = ['Silence (Baseline)', 'Vedic Mantra (Om)', 'Pop ("Bye Bye Bye")', 'Fast Rap ("Yalgaar")']
x_ac = np.arange(len(labels_ac))
w_ac = 0.35

bars_std = ax_ac.bar(x_ac - w_ac/2, stds, w_ac, label='Standard Deviation (σ, Total AC Energy)',
                     color='#003366', edgecolor='black', linewidth=1.2, hatch='//')
bars_iqr = ax_ac.bar(x_ac + w_ac/2, iqrs, w_ac, label='Interquartile Range (IQR, Non-Gaussian Spread)',
                     color='#b22222', edgecolor='black', linewidth=1.2, hatch='\\\\')

ax_ac.set_ylabel('Dispersion Metric (ADC Counts)', fontsize=16, labelpad=8)
ax_ac.set_xticks(x_ac)
ax_ac.set_xticklabels(labels_ac, fontsize=13, fontweight='bold')
ax_ac.set_ylim(0, 750)
ax_ac.grid(True, axis='y')
ax_ac.legend(loc='upper left', framealpha=1.0, edgecolor='black', fontsize=13)
ax_ac.set_title('Figure S3: Acoustic Sound Pressure Wave Impact on Plant Biopotential Dispersion',
                fontsize=16, fontweight='bold', pad=10)

for rect in bars_std:
    h = rect.get_height()
    ax_ac.text(rect.get_x() + rect.get_width()/2., h + 12, f'{h:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
for rect in bars_iqr:
    h = rect.get_height()
    ax_ac.text(rect.get_x() + rect.get_width()/2., h + 12, f'{h:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/graph3_acoustic_sound_pressure_dispersion.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/graph3_acoustic_sound_pressure_dispersion.pdf", bbox_inches='tight')
plt.close()
print("Saved graph 3.")

# -------------------------------------------------------------
# Standalone 4: Data Leakage Trap Benchmark (Stratified vs Group K-Fold)
# -------------------------------------------------------------
fig, ax_ml = plt.subplots(figsize=(11, 6.5))
model_names = ['Logistic Regression', 'K-Nearest Neighbors', 'Decision Tree', 'Random Forest', 'SVM (RBF Kernel)']
strat_acc = [84.18, 93.62, 90.18, 96.87, 90.75]
strat_err = [1.37, 1.29, 0.99, 0.55, 1.29]
group_acc = [16.81, 16.62, 27.52, 25.46, 11.05]
group_err = [12.07, 12.91, 21.39, 14.44, 13.33]

x_m = np.arange(len(model_names))
w_m = 0.35

rects_s = ax_ml.bar(x_m - w_m/2, strat_acc, w_m, yerr=strat_err, capsize=5,
                    label='Stratified K-Fold (Naive Random Shuffle: Data Leakage Trap)',
                    color='#b22222', edgecolor='black', linewidth=1.2, hatch='//')
rects_g = ax_ml.bar(x_m + w_m/2, group_acc, w_m, yerr=group_err, capsize=5,
                    label='Group K-Fold (Strict Leave-Session-Out: True Scientific Benchmark)',
                    color='#003366', edgecolor='black', linewidth=1.2, hatch='\\\\')

ax_ml.axhline(20.0, color='#444444', linestyle='--', linewidth=1.8, label='Random Chance Baseline (5 Classes = 20%)')
ax_ml.set_ylabel('Classification Accuracy (%)', fontsize=16, labelpad=8)
ax_ml.set_xticks(x_m)
ax_ml.set_xticklabels(model_names, fontsize=12, fontweight='bold', rotation=15, ha='right')
ax_ml.set_ylim(0, 118)
ax_ml.grid(True, axis='y')
ax_ml.legend(loc='upper right', framealpha=1.0, edgecolor='black', fontsize=11.5)
ax_ml.set_title('Figure S4: The Temporal Data Leakage Discovery in Plant Bio-Potential Machine Learning',
                fontsize=16, fontweight='bold', pad=10)

for rect in rects_s:
    h = rect.get_height()
    ax_ml.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
for rect in rects_g:
    h = rect.get_height()
    ax_ml.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
fig.savefig(f"{OUT_DIR}/graph4_temporal_data_leakage_discovery.png", dpi=400, bbox_inches='tight')
fig.savefig(f"{OUT_DIR}/graph4_temporal_data_leakage_discovery.pdf", bbox_inches='tight')
plt.close()
print("Saved graph 4.")

print("All standalone ultra-clear IEEE presentation graphs successfully created!")
