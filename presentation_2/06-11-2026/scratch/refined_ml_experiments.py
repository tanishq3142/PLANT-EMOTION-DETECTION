import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score

PLOT_DIR = "presentation/06-11-2026/plots"
df = pd.read_csv("presentation/06-11-2026/scratch/plant_features_extracted.csv")

ac_features = [
    'std_adc', 'iqr_adc', 'peak_to_peak', 'mean_abs_diff', 'kurtosis', 'skewness',
    'power_low_freq', 'power_mid_freq', 'power_high_freq', 'spectral_centroid', 'spectral_entropy'
]

# -------------------------------------------------------------
# EXPERIMENT A: Live vs Dead Plant Classification (StratifiedGroupKFold)
# -------------------------------------------------------------
print("--- Experiment A: Live Plant vs. Dead Plant ---")
X_bin = df[ac_features]
y_bin = df['is_live']
groups_bin = df['session_file']

pipe_bin = Pipeline([('scaler', StandardScaler()),
                     ('rf', RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))])

sgkf_3 = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)
scores_bin_acc = cross_val_score(pipe_bin, X_bin, y_bin, groups=groups_bin, cv=sgkf_3, scoring='accuracy')
scores_bin_f1 = cross_val_score(pipe_bin, X_bin, y_bin, groups=groups_bin, cv=sgkf_3, scoring='f1_macro')

print(f"Live vs Dead (Unseen Sessions, 3 Folds):")
print(f"Accuracy: {scores_bin_acc.mean()*100:.2f}% (±{scores_bin_acc.std()*100:.2f}%)")
print(f"Macro F1: {scores_bin_f1.mean()*100:.2f}% (±{scores_bin_f1.std()*100:.2f}%)")

# -------------------------------------------------------------
# EXPERIMENT B: Silent Baseline vs. Pop Music Vibration
# -------------------------------------------------------------
print("\n--- Experiment B: Silent Baseline vs. Pop Music Vibration ---")
mask_music = df['category'].isin(['Normal Baseline (Control)', 'Acoustic - High Energy/Pop'])
df_music = df[mask_music].copy()

X_m = df_music[ac_features]
y_m = (df_music['category'] == 'Acoustic - High Energy/Pop').astype(int)
groups_m = df_music['session_file']

pipe_m = Pipeline([('scaler', StandardScaler()),
                   ('rf', RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))])

sgkf_m = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)
scores_m_acc = cross_val_score(pipe_m, X_m, y_m, groups=groups_m, cv=sgkf_m, scoring='accuracy')
scores_m_f1 = cross_val_score(pipe_m, X_m, y_m, groups=groups_m, cv=sgkf_m, scoring='f1_macro')

print(f"Silence vs Pop Music (Unseen Sessions, 3 Folds):")
print(f"Accuracy: {scores_m_acc.mean()*100:.2f}% (±{scores_m_acc.std()*100:.2f}%)")
print(f"Macro F1: {scores_m_f1.mean()*100:.2f}% (±{scores_m_f1.std()*100:.2f}%)")

# -------------------------------------------------------------
# RE-GENERATE PLOT 13: Clean and Robust Visualization
# -------------------------------------------------------------
print("\nRe-generating Plot 13 with clean Macro-F1 and Accuracy...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Subplot 1: The Leakage Effect
cv_types = ['Stratified K-Fold\n(Window-Level Shuffle)', 'Group K-Fold\n(Leave-Session-Out)']
rf_compare = [96.87, 25.46]
colors = ['#e74c3c', '#27ae60']

bars = ax1.bar(cv_types, rf_compare, color=colors, width=0.45)
ax1.set_ylabel('Random Forest Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_ylim(0, 110)
ax1.set_title('[A] The Data Leakage Trap in Multi-Class Biopotentials', fontsize=11, fontweight='bold')
ax1.axhline(20, color='gray', linestyle=':', label='Chance Baseline (5 classes = 20%)')
ax1.legend(loc='upper right')

for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 3, f"{h:.1f}%", ha='center', fontweight='bold', fontsize=10)

ax1.text(0.5, 0.45, "Window Shuffle leaks session DC offset!\nGroup K-Fold evaluates genuine cross-session generalization.",
         transform=ax1.transAxes, ha='center', fontsize=9,
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffdd', edgecolor='#cccccc'))

# Subplot 2: Robust Targeted Classifications
robust_tasks = ['Live Plant vs.\nDead Control', 'Silence vs.\nPop Vibration']
robust_accs = [scores_bin_acc.mean() * 100, scores_m_acc.mean() * 100]
robust_f1s = [scores_bin_f1.mean() * 100, scores_m_f1.mean() * 100]

x_r = np.arange(len(robust_tasks))
w = 0.35

rects_a = ax2.bar(x_r - w/2, robust_accs, w, label='Accuracy on Unseen Sessions (%)', color='#2980b9')
rects_f = ax2.bar(x_r + w/2, robust_f1s, w, label='Macro F1-Score (%)', color='#8e44ad')
ax2.set_ylabel('Generalization Performance (%)', fontsize=11, fontweight='bold')
ax2.set_ylim(0, 110)
ax2.set_xticks(x_r)
ax2.set_xticklabels(robust_tasks, fontsize=10, fontweight='bold')
ax2.set_title('[B] Robust Physical Classifications Across Unseen Sessions', fontsize=11, fontweight='bold')
ax2.axhline(50, color='gray', linestyle=':', label='Chance Baseline (Binary = 50%)')
ax2.legend(loc='lower left')

for rect in rects_a:
    h = rect.get_height()
    ax2.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.1f}%", ha='center', fontweight='bold', fontsize=9)
for rect in rects_f:
    h = rect.get_height()
    ax2.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.1f}%", ha='center', fontweight='bold', fontsize=9)

plt.suptitle("Rigorous Scientific Evaluation: Data Leakage Discovery & Generalizable Classifications",
             fontsize=13, fontweight='bold', y=0.99)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_13_scientific_validation_and_diagnostics.png", dpi=300)
plt.close()
print("Plot 13 regenerated successfully!")
