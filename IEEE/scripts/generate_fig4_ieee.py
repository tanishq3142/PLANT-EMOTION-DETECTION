import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.tree import DecisionTreeClassifier, plot_tree

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

print("Building IEEE Figure 4: Feature Correlation Matrix & Interpretable Decision Architecture...")

# Load Feature Dataframe
feat_df = pd.read_csv("presentation_2/06-11-2026/scratch/plant_features_extracted.csv")
features = [
    'mean_adc', 'std_adc', 'var_adc', 'min_adc', 'max_adc', 'peak_to_peak',
    'median_adc', 'iqr_adc', 'rms_adc', 'skewness', 'kurtosis',
    'mean_abs_diff', 'zero_crossings', 'peak_count',
    'power_low_freq', 'power_mid_freq', 'power_high_freq',
    'power_ratio_high_low', 'spectral_centroid', 'spectral_entropy'
]
pretty_labels = [
    'Mean (μ)', 'Std. Dev. (σ)', 'Variance (σ²)', 'Min Potential', 'Max Potential', 'Peak-to-Peak',
    'Median', 'IQR', 'RMS Energy', 'Skewness (γ₁)', 'Kurtosis (γ₂)',
    'Velocity (MAD)', 'Zero Crossings', 'Peak Count',
    'Low Freq (0.1–2 Hz)', 'Mid Freq (2–10 Hz)', 'High Freq (10–45 Hz)',
    'High/Low Ratio', 'Spectral Centroid', 'Spectral Entropy'
]

fig = plt.figure(figsize=(15, 7.5))
gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.2], wspace=0.25)

# -------------------------------------------------------------
# Subplot (a): Feature Correlation Matrix Heatmap
# -------------------------------------------------------------
ax_a = fig.add_subplot(gs[0, 0])
corr = feat_df[features].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

im = sns.heatmap(corr, mask=mask, cmap='vlag', vmin=-1.0, vmax=1.0, ax=ax_a,
                 cbar_kws={'label': 'Pearson Correlation Coefficient (r)', 'shrink': 0.8},
                 square=True, linewidths=0.5, linecolor='white')
cbar = im.collections[0].colorbar
cbar.ax.tick_params(labelsize=11)
cbar.set_label('Pearson Correlation (r)', fontsize=12, labelpad=6)

ax_a.set_xticks(np.arange(len(features)) + 0.5)
ax_a.set_yticks(np.arange(len(features)) + 0.5)
ax_a.set_xticklabels(pretty_labels, fontsize=8.5, rotation=45, ha='right')
ax_a.set_yticklabels(pretty_labels, fontsize=8.5)
ax_a.tick_params(direction='out')

ax_a.text(0.5, -0.25, '(a)', transform=ax_a.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (b): Interpretable Decision Tree Architecture
# -------------------------------------------------------------
ax_b = fig.add_subplot(gs[0, 1])

# Train a shallow decision tree (depth 3) on the full feature dataset
dt = DecisionTreeClassifier(max_depth=3, random_state=42)
dt.fit(feat_df[features].fillna(0), feat_df['category'])

# Clean class labels
class_short = ['Pop Music', 'Mantra', 'Dead (Ctrl)', 'Baseline', 'Water Stim.']
plot_tree(dt, feature_names=pretty_labels, class_names=class_short,
          filled=True, rounded=True, fontsize=8, precision=1, ax=ax_b,
          proportion=True)

ax_b.text(0.5, -0.15, '(b)', transform=ax_b.transAxes, fontsize=16, fontweight='bold', ha='center')

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)

out_png = f"{FIG_DIR}/fig4_decision_rules_and_correlation_manifold.png"
out_pdf = f"{FIG_DIR}/fig4_decision_rules_and_correlation_manifold.pdf"
fig.savefig(out_png, dpi=400, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Figure 4 successfully exported to:\n  {out_png}\n  {out_pdf}")
