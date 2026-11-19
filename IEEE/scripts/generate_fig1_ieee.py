import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

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

ADC_TO_MV = 5000.0 / 1023.0
FIG_DIR = "IEEE/figures"
os.makedirs(FIG_DIR, exist_ok=True)

print("Building IEEE Figure 1: Time-Domain Biopotential Dynamics & Biological Viability...")

# Data Paths
live_path = 'csv/2026-08-11/plant_normal_morning_11hrs39min.csv'
dead_path = 'csv/2026-09-22/plant_dead_morning_09hrs49min39sec.csv'
water_path = 'csv/2026-08-11/plant_water_morning_11hrs50min.csv'

df_live = pd.read_csv(live_path)
df_dead = pd.read_csv(dead_path)
df_water = pd.read_csv(water_path)

ecg_live = df_live['ecg'].values.astype(float)
ecg_dead = df_dead['ecg'].values.astype(float)
ecg_water = df_water['ecg'].values.astype(float)

fs = 190.0
fig, axes = plt.subplots(2, 2, figsize=(13, 10.5))

# -------------------------------------------------------------
# Subplot (a): 50-Second Raw Electrophysiological Baseline
# -------------------------------------------------------------
ax_a = axes[0, 0]
t_50 = np.linspace(0, 50, int(50 * fs))
live_50 = ecg_live[1000:1000 + len(t_50)]
dead_50 = ecg_dead[500:500 + len(t_50)]

ax_a.plot(t_50, live_50, color='#003366', linewidth=1.6, label='Living Plant (Epipremnum aureum)')
ax_a.plot(t_50, dead_50, color='#888888', linewidth=1.4, linestyle='--', label='Desiccated Dead Tissue (Control)')
ax_a.axhline(np.mean(live_50), color='#003366', linestyle=':', alpha=0.7, label=f'Live Mean = {np.mean(live_50):.1f}')
ax_a.axhline(np.mean(dead_50), color='#444444', linestyle=':', alpha=0.7, label=f'Dead Mean = {np.mean(dead_50):.1f}')

ax_a.set_xlabel('Time (s)', fontsize=14, labelpad=6)
ax_a.set_ylabel('Biopotential (ADC Counts)', fontsize=14, labelpad=6)
ax_a.set_xlim(0, 50)
ax_a.set_ylim(-20, 1040)
ax_a.grid(True)
ax_a.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=10.5)

# Secondary axis for Voltage (mV)
ax_a_mv = ax_a.twinx()
ax_a_mv.set_ylim(-20 * ADC_TO_MV, 1040 * ADC_TO_MV)
ax_a_mv.set_ylabel('Potential (mV)', fontsize=13, color='#444444', labelpad=6)
ax_a_mv.tick_params(colors='#444444', labelsize=11)

ax_a.text(0.5, -0.22, '(a)', transform=ax_a.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (b): 4-Second Micro-Structure Inset
# -------------------------------------------------------------
ax_b = axes[0, 1]
t_4 = np.linspace(0, 4.0, int(4.0 * fs))
live_4 = ecg_live[3000:3000 + len(t_4)]
dead_4 = ecg_dead[1500:1500 + len(t_4)]

ax_b.plot(t_4, live_4, color='#003366', linewidth=2.0, marker='o', markersize=3, markevery=15,
          label='Living Waveform (Action/Slow Potential)')
ax_b.plot(t_4, dead_4, color='#b22222', linewidth=1.8, linestyle='-.', marker='s', markersize=3, markevery=15,
          label='Dead Control (Passive Quantization Jitter)')

ax_b.set_xlabel('Window Elapsed Time (s)', fontsize=14, labelpad=6)
ax_b.set_ylabel('Biopotential (ADC Counts)', fontsize=14, labelpad=6)
ax_b.set_xlim(0, 4.0)
ax_b.set_ylim(-20, 1040)
ax_b.grid(True)
ax_b.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=10.5)

# Annotation for physiological depolarization
peak_idx = np.argmax(live_4)
ax_b.annotate('Depolarization Peak\n(Ca²⁺/Cl⁻ Ion Efflux)',
              xy=(t_4[peak_idx], live_4[peak_idx]),
              xytext=(t_4[peak_idx] - 1.5, live_4[peak_idx] - 220),
              arrowprops=dict(facecolor='black', shrink=0.08, width=1.2, headwidth=6),
              fontsize=10.5, fontweight='bold', bbox=dict(boxstyle='square,pad=0.3', facecolor='#ffffdd', edgecolor='black'))

ax_b.text(0.5, -0.22, '(b)', transform=ax_b.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (c): Hydration Dynamics & Variation Potential (VP)
# -------------------------------------------------------------
ax_c = axes[1, 0]
t_water = np.linspace(0, len(ecg_water)/fs, len(ecg_water))
step = max(1, len(t_water) // 2000)

s_w = pd.Series(ecg_water)
roll_mean = s_w.rolling(int(fs * 4), center=True).mean().values
roll_std = s_w.rolling(int(fs * 4), center=True).std().values

ax_c.plot(t_water[::step], ecg_water[::step], color='#88c999', alpha=0.45, linewidth=0.8, label='Raw Biopotential (Subsampled)')
ax_c.plot(t_water[::step], roll_mean[::step], color='#006633', linewidth=2.2, label='4-s Rolling Mean (Variation Potential Trend)')
ax_c.fill_between(t_water[::step], (roll_mean - roll_std)[::step], (roll_mean + roll_std)[::step],
                  color='#2e8b57', alpha=0.25, label='±1 Standard Deviation Envelope')

ax_c.axvline(25, color='#b22222', linestyle='--', linewidth=1.8, label='Hydration Onset (Water Injection)')
ax_c.set_xlabel('Time Post-Stimulus (s)', fontsize=14, labelpad=6)
ax_c.set_ylabel('Biopotential (ADC Counts)', fontsize=14, labelpad=6)
ax_c.set_xlim(0, 520)
ax_c.set_ylim(-20, 1040)
ax_c.grid(True)
ax_c.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=10.0)

ax_c.text(0.5, -0.22, '(c)', transform=ax_c.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (d): Statistical Density and IQR Dispersion
# -------------------------------------------------------------
ax_d = axes[1, 1]

sample_live = np.random.choice(ecg_live, min(30000, len(ecg_live)), replace=False)
sample_dead = np.random.choice(ecg_dead, min(30000, len(ecg_dead)), replace=False)

sns.kdeplot(sample_live, ax=ax_d, color='#003366', linewidth=2.2, label=f'Living Tissue (IQR = {np.percentile(sample_live, 75) - np.percentile(sample_live, 25):.1f} ADC)')
sns.kdeplot(sample_dead, ax=ax_d, color='#b22222', linewidth=2.2, linestyle='--', label=f'Dead Control (IQR = {np.percentile(sample_dead, 75) - np.percentile(sample_dead, 25):.1f} ADC)')

ax_d.set_xlabel('Biopotential (ADC Counts)', fontsize=14, labelpad=6)
ax_d.set_ylabel('Probability Density Function', fontsize=14, labelpad=6)
ax_d.set_xlim(0, 1023)
ax_d.grid(True)
ax_d.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=10.5)

# Annotate variance ratio
var_ratio = np.var(sample_live) / np.var(sample_dead)
ax_d.text(0.06, 0.78, f'Variance Ratio:\nVar(Live) / Var(Dead) = {var_ratio:.2f}×\nLiving Dispersion: Active\nDead Dispersion: Passive Drift',
          transform=ax_d.transAxes, fontsize=11, fontweight='normal',
          bbox=dict(boxstyle='square,pad=0.4', facecolor='white', edgecolor='black', linewidth=1.0))

ax_d.text(0.5, -0.22, '(d)', transform=ax_d.transAxes, fontsize=16, fontweight='bold', ha='center')

plt.tight_layout()
plt.subplots_adjust(bottom=0.08, hspace=0.32, wspace=0.25)

# Save high-res PNG and PDF vector
out_png = f"{FIG_DIR}/fig1_time_domain_and_viability.png"
out_pdf = f"{FIG_DIR}/fig1_time_domain_and_viability.pdf"
fig.savefig(out_png, dpi=400, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Figure 1 successfully exported to:\n  {out_png}\n  {out_pdf}")
