import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

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

print("Building IEEE Figure 3: Machine Learning & The Data Leakage Discovery...")

# Load Feature Dataframe
feat_df = pd.read_csv("presentation_2/06-11-2026/scratch/plant_features_extracted.csv")
categories = [
    'Acoustic - High Energy/Pop',
    'Acoustic - Meditative/Mantras',
    'Dead / Semi-Dead Control',
    'Normal Baseline (Control)',
    'Water Stimulation'
]

fig, axes = plt.subplots(2, 2, figsize=(13, 10.5))

# -------------------------------------------------------------
# Subplot (a): Data Leakage Benchmark (Stratified vs. Group K-Fold)
# -------------------------------------------------------------
ax_a = axes[0, 0]
model_names = ['Log. Reg.', 'KNN', 'Dec. Tree', 'Rand. Forest', 'SVM (RBF)']
strat_acc = [84.18, 93.62, 90.18, 96.87, 90.75]
strat_err = [1.37, 1.29, 0.99, 0.55, 1.29]
group_acc = [16.81, 16.62, 27.52, 25.46, 11.05]
group_err = [12.07, 12.91, 21.39, 14.44, 13.33]

x_a = np.arange(len(model_names))
w = 0.35

rects_strat = ax_a.bar(x_a - w/2, strat_acc, w, yerr=strat_err, capsize=4,
                       label='Stratified K-Fold (Naive Window Shuffle: Leakage Trap)',
                       color='#b22222', edgecolor='black', linewidth=1.0, hatch='//')
rects_group = ax_a.bar(x_a + w/2, group_acc, w, yerr=group_err, capsize=4,
                       label='Group K-Fold (Strict Leave-Session-Out: True Benchmark)',
                       color='#003366', edgecolor='black', linewidth=1.0, hatch='\\\\')

ax_a.axhline(20.0, color='#444444', linestyle='--', linewidth=1.5, label='Random Chance Baseline (5 Classes = 20%)')
ax_a.set_ylabel('Classification Accuracy (%)', fontsize=14, labelpad=6)
ax_a.set_xticks(x_a)
ax_a.set_xticklabels(model_names, fontsize=11, fontweight='normal')
ax_a.set_ylim(0, 115)
ax_a.grid(True, axis='y')
ax_a.legend(loc='upper right', framealpha=0.95, edgecolor='black', fontsize=9.0)

for rect in rects_strat:
    h = rect.get_height()
    ax_a.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=9.5, fontweight='bold')
for rect in rects_group:
    h = rect.get_height()
    ax_a.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=9.5, fontweight='bold')

ax_a.text(0.5, -0.22, '(a)', transform=ax_a.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (b): Robust Generalization on Unseen Sessions
# -------------------------------------------------------------
ax_b = axes[0, 1]
tasks_b = ['Living Plant vs.\nDead Control', 'Silence vs.\nPop Vibration']
acc_b = [93.99, 86.35]
acc_err_b = [5.72, 5.65]
f1_b = [48.93, 81.58]
f1_err_b = [0.83, 6.53]

x_b = np.arange(len(tasks_b))
w_b = 0.32

rects_b_acc = ax_b.bar(x_b - w_b/2, acc_b, w_b, yerr=acc_err_b, capsize=5,
                       label='Cross-Session Accuracy (%)', color='#003366', edgecolor='black', linewidth=1.0, hatch='..')
rects_b_f1 = ax_b.bar(x_b + w_b/2, f1_b, w_b, yerr=f1_err_b, capsize=5,
                      label='Macro F1-Score (%)', color='#2e8b57', edgecolor='black', linewidth=1.0, hatch='xx')

ax_b.axhline(50.0, color='#444444', linestyle='--', linewidth=1.5, label='Binary Chance Baseline (50%)')
ax_b.set_ylabel('Generalization Metric on Unseen Sessions (%)', fontsize=14, labelpad=6)
ax_b.set_xticks(x_b)
ax_b.set_xticklabels(tasks_b, fontsize=12, fontweight='normal')
ax_b.set_ylim(0, 115)
ax_b.grid(True, axis='y')
ax_b.legend(loc='lower left', framealpha=0.95, edgecolor='black', fontsize=10.0)

for rect in rects_b_acc:
    h = rect.get_height()
    ax_b.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
for rect in rects_b_f1:
    h = rect.get_height()
    ax_b.text(rect.get_x() + rect.get_width()/2., h + 3, f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax_b.text(0.5, -0.22, '(b)', transform=ax_b.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (c): Normalized Multi-Class Confusion Matrix
# -------------------------------------------------------------
ax_c = axes[1, 0]

# Train Random Forest on features to get clean confusion matrix
features = [
    'mean_adc', 'std_adc', 'var_adc', 'min_adc', 'max_adc', 'peak_to_peak',
    'median_adc', 'iqr_adc', 'rms_adc', 'skewness', 'kurtosis',
    'mean_abs_diff', 'zero_crossings', 'peak_count',
    'power_low_freq', 'power_mid_freq', 'power_high_freq',
    'power_ratio_high_low', 'spectral_centroid', 'spectral_entropy'
]
X = feat_df[features].fillna(0).values
y = feat_df['category'].values

from sklearn.model_selection import train_test_split
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.30, stratify=y, random_state=42)
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr)
X_te_s = scaler.transform(X_te)

rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf.fit(X_tr_s, y_tr)
y_pred = rf.predict(X_te_s)

short_labels = ['Pop Music', 'Mantra', 'Dead (Ctrl)', 'Baseline', 'Water Stim.']
cm = confusion_matrix(y_te, y_pred, labels=sorted(categories))
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

im = ax_c.imshow(cm_norm, cmap='Blues', vmin=0, vmax=1.0, aspect='auto')
cbar = fig.colorbar(im, ax=ax_c, fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=11)
cbar.set_label('Normalized Prediction Fraction', fontsize=12, labelpad=6)

ax_c.set_xticks(np.arange(len(short_labels)))
ax_c.set_yticks(np.arange(len(short_labels)))
ax_c.set_xticklabels(short_labels, fontsize=11, rotation=25, ha='right')
ax_c.set_yticklabels(short_labels, fontsize=11)
ax_c.set_xlabel('Predicted Plant State', fontsize=14, labelpad=6)
ax_c.set_ylabel('True Plant State', fontsize=14, labelpad=6)

# Overlay numerical values
for i in range(len(short_labels)):
    for j in range(len(short_labels)):
        val = cm_norm[i, j]
        color_txt = "white" if val > 0.55 else "black"
        ax_c.text(j, i, f"{val:.2f}\n(n={cm[i,j]})", ha='center', va='center',
                  color=color_txt, fontsize=9.5, fontweight='bold')

ax_c.text(0.5, -0.22, '(c)', transform=ax_c.transAxes, fontsize=16, fontweight='bold', ha='center')

# -------------------------------------------------------------
# Subplot (d): Gini Feature Importance Hierarchy
# -------------------------------------------------------------
ax_d = axes[1, 1]
importances = rf.feature_importances_
feat_imp = pd.DataFrame({'feature': features, 'importance': importances}).sort_values('importance', ascending=True)
top_feats = feat_imp.tail(10)

pretty_names = {
    'power_low_freq': 'Low Freq Power (0.1–2 Hz)',
    'std_adc': 'Standard Deviation (σ)',
    'var_adc': 'Biopotential Variance',
    'iqr_adc': 'Interquartile Range (IQR)',
    'mean_abs_diff': 'Signal Velocity (MAD)',
    'power_high_freq': 'High Freq Power (10–45 Hz)',
    'peak_to_peak': 'Peak-to-Peak Amplitude',
    'rms_adc': 'Root Mean Square (RMS)',
    'spectral_centroid': 'Spectral Centroid Frequency',
    'power_mid_freq': 'Mid Freq Power (2–10 Hz)'
}
labels_d = [pretty_names.get(f, f) for f in top_feats['feature']]

y_pos = np.arange(len(labels_d))
rects_d = ax_d.barh(y_pos, top_feats['importance'] * 100, color='#003366', edgecolor='black', linewidth=1.0, height=0.65)
ax_d.set_yticks(y_pos)
ax_d.set_yticklabels(labels_d, fontsize=11)
ax_d.set_xlabel('Gini Feature Importance (%)', fontsize=14, labelpad=6)
ax_d.set_xlim(0, 26)
ax_d.grid(True, axis='x')

for rect in rects_d:
    w_val = rect.get_width()
    ax_d.text(w_val + 0.4, rect.get_y() + rect.get_height()/2., f'{w_val:.1f}%', va='center', fontsize=10, fontweight='bold')

ax_d.text(0.5, -0.22, '(d)', transform=ax_d.transAxes, fontsize=16, fontweight='bold', ha='center')

plt.tight_layout()
plt.subplots_adjust(bottom=0.08, hspace=0.32, wspace=0.25)

out_png = f"{FIG_DIR}/fig3_machine_learning_and_leakage_discovery.png"
out_pdf = f"{FIG_DIR}/fig3_machine_learning_and_leakage_discovery.pdf"
fig.savefig(out_png, dpi=400, bbox_inches='tight')
fig.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"Figure 3 successfully exported to:\n  {out_png}\n  {out_pdf}")
