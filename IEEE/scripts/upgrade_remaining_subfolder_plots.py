"""
Upgrades remaining 13 subfolder plots to IEEE Publication Standard.
"""
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
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_predict, StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IEEE_DIR = os.path.join(BASE_DIR, "IEEE")
IEEE_PLOTS_DIR = os.path.join(IEEE_DIR, "plots")
PRES2_IEEE_DIR = os.path.join(BASE_DIR, "presentation_2", "06-11-2026", "IEEE")
PRES2_PLOTS_DIR = os.path.join(BASE_DIR, "presentation_2", "06-11-2026", "plots")

plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Cambria', 'serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.6
plt.rcParams['grid.color'] = '#777777'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['grid.alpha'] = 0.55
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.major.size'] = 6.5
plt.rcParams['ytick.major.size'] = 6.5
plt.rcParams['xtick.major.width'] = 1.4
plt.rcParams['ytick.major.width'] = 1.4
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.titlesize'] = 17
plt.rcParams['legend.fontsize'] = 13
plt.rcParams['figure.titlesize'] = 18

FS = 190.0
df_feat = pd.read_csv(os.path.join(BASE_DIR, "notebook", "plant_time_series_features.csv"))

feature_cols = [
    "mean", "std", "var", "min", "max", "range", "median", 
    "rms", "mad", "p25", "p75", "iqr", "zcr", "skew", "kurt", 
    "peak_count", "low_freq_power", "mid_freq_power", "high_freq_power", 
    "spectral_entropy", "dominant_freq"
]

def save_both(fig, rel_path):
    p1 = os.path.join(IEEE_PLOTS_DIR, rel_path)
    p2 = os.path.join(PRES2_IEEE_DIR, "plots", rel_path)
    p3 = os.path.join(PRES2_PLOTS_DIR, rel_path)
    for p in [p1, p2, p3]:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fig.savefig(p, dpi=400, bbox_inches='tight')
        pdf_p = p.replace('.png', '.pdf')
        fig.savefig(pdf_p, dpi=400, bbox_inches='tight')
    plt.close(fig)
    print(f"  [✓ Upgraded] {rel_path}")

raw_paths = {
    'normal': ('csv/2026-08-11/plant_normal_morning_11hrs39min.csv', '#003366', 'Normal Baseline'),
    'devotional': ('categorize csv/music/devotional/plant_hanuman_chalisa_afternoon_12hrs34min17sec.csv', '#6A1B9A', 'Devotional Music'),
    'water': ('csv/2026-08-11/plant_water_morning_11hrs50min.csv', '#006633', 'Water Stimulation'),
    'dead': ('categorize csv/dead/plant_dead_control_zero_signal_morning_10hrs00min.csv', '#333333', 'Dead Control')
}

# 1. 2_psd_fft_spectrum.png
print("Generating 2_psd_fft_spectrum...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
for k, (rel_f, col, lbl) in raw_paths.items():
    df_raw = pd.read_csv(os.path.join(BASE_DIR, rel_f), nrows=3500)
    sig = df_raw["ecg"].values.astype(float) - np.mean(df_raw["ecg"].values)
    if np.std(sig) > 0:
        freqs, psd = signal.welch(sig, fs=FS, nperseg=min(512, len(sig)))
        ax1.semilogy(freqs, psd, label=lbl, color=col, linewidth=2.2)
        fft_vals = np.abs(np.fft.rfft(sig))
        fft_freqs = np.fft.rfftfreq(len(sig), d=1.0/FS)
        ax2.plot(fft_freqs[:250], fft_vals[:250], label=lbl, color=col, linewidth=1.8, alpha=0.9)
ax1.set_title("Welch Power Spectral Density (PSD)", fontsize=16, fontweight='bold', pad=12)
ax1.set_xlabel("Frequency [Hz]", fontsize=15, fontweight='bold')
ax1.set_ylabel("Power Density [$\mathrm{ADC}^2/\mathrm{Hz}$]", fontsize=15, fontweight='bold')
ax1.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
ax1.grid(True, which='both')

ax2.set_title("Low-Frequency FFT Amplitude Spectrum", fontsize=16, fontweight='bold', pad=12)
ax2.set_xlabel("Frequency [Hz]", fontsize=15, fontweight='bold')
ax2.set_ylabel("FFT Magnitude", fontsize=15, fontweight='bold')
ax2.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
ax2.grid(True)
plt.tight_layout()
save_both(fig, "01_time_series_eda_and_feature_extraction/2_psd_fft_spectrum.png")

# 2. 3_rolling_volatility.png
print("Generating 3_rolling_volatility...")
fig, ax = plt.subplots(figsize=(12, 5.8))
for k, (rel_f, col, lbl) in raw_paths.items():
    df_raw = pd.read_csv(os.path.join(BASE_DIR, rel_f), nrows=2500)
    rolling_std = pd.Series(df_raw["ecg"]).rolling(window=100).std()
    ax.plot(rolling_std.values, label=f"{lbl} (Rolling σ)", color=col, linewidth=2.2)
ax.set_title("Biopotential Volatility Over Time (Rolling Window = 100 samples)", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("Observation Sample Index", fontsize=15, fontweight='bold')
ax.set_ylabel("Rolling Standard Deviation [ADC Counts]", fontsize=15, fontweight='bold')
ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12.5)
ax.grid(True)
plt.tight_layout()
save_both(fig, "01_time_series_eda_and_feature_extraction/3_rolling_volatility.png")

# 3. 4_feature_correlation_matrix.png
print("Generating 4_feature_correlation_matrix...")
fig, ax = plt.subplots(figsize=(12, 9.5))
corr_sub = df_feat[feature_cols[:12]].corr()
sns.heatmap(corr_sub, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, cbar=True, square=True, ax=ax)
ax.set_title("Cross-Correlation Matrix of Engineered Time-Series Features", fontsize=16, fontweight='bold', pad=12)
plt.tight_layout()
save_both(fig, "01_time_series_eda_and_feature_extraction/4_feature_correlation_matrix.png")

# 4. 5_feature_distributions_violin.png
print("Generating 5_feature_distributions_violin...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5.8))
metrics = [
    ("std", "Signal Standard Deviation [σ]"), 
    ("mad", "Mean Absolute Difference (Signal Velocity)"), 
    ("spectral_entropy", "Spectral Entropy (Signal Complexity)")
]
palette_v = {"normal": "#003366", "music": "#6A1B9A", "water": "#006633", "dead": "#B22222"}
for ax, (m_col, m_title) in zip(axes, metrics):
    sns.violinplot(data=df_feat, x="main_category", y=m_col, ax=ax, palette=palette_v)
    ax.set_title(m_title, fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel("Stimulus Condition", fontsize=14, fontweight='bold')
    ax.grid(True)
plt.tight_layout()
save_both(fig, "01_time_series_eda_and_feature_extraction/5_feature_distributions_violin.png")

# 5. 02_viability_dead_vs_alive_rf/3_feature_importances.png
print("Generating 3_feature_importances...")
rf_v = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf_v.fit(df_feat[feature_cols].values, df_feat['is_alive'].values)
imp_v = rf_v.feature_importances_
ind_v = np.argsort(imp_v)[::-1][:12]

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.barh(range(12), imp_v[ind_v[:12]][::-1] * 100, color="#003366", alpha=0.88, edgecolor='black', linewidth=1.4)
ax.set_yticks(range(12))
ax.set_yticklabels([feature_cols[i] for i in ind_v[:12]][::-1], fontsize=13.5, fontweight='bold')
ax.set_xlabel("Gini Feature Importance (%)", fontsize=15, fontweight='bold')
ax.set_title("Top 12 Discriminative Feature Importances for Plant Viability Detection", fontsize=16, fontweight='bold', pad=12)
ax.grid(True, axis='x')
for i, v in enumerate(imp_v[ind_v[:12]][::-1] * 100):
    ax.text(v + 0.3, i, f"{v:.1f}%", va='center', fontsize=12.5, fontweight='bold')
plt.tight_layout()
save_both(fig, "02_viability_dead_vs_alive_rf/3_feature_importances.png")

# 6. 03_multiclass_stimulus_svm_knn/2_ovr_roc_curves.png
print("Generating 2_ovr_roc_curves...")
from sklearn.svm import SVC
from sklearn.preprocessing import label_binarize
class_labels = ["normal", "music", "water", "dead"]
display_names = ["Normal Baseline", "Acoustic Music", "Water Hydration", "Dead Control"]
y_multi = df_feat["main_category"].map({l: i for i, l in enumerate(class_labels)}).values
X_scaled = StandardScaler().fit_transform(df_feat[feature_cols].values)
svm = SVC(kernel='rbf', C=5.0, probability=True, random_state=42)
svm.fit(X_scaled, y_multi)
proba_svm = svm.predict_proba(X_scaled)

fig, ax = plt.subplots(figsize=(9.5, 6.2))
colors_ovr = ["#003366", "#6A1B9A", "#006633", "#B22222"]
for i, (c_name, color) in enumerate(zip(display_names, colors_ovr)):
    y_bin = (y_multi == i).astype(int)
    fpr, tpr, _ = roc_curve(y_bin, proba_svm[:, i])
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, color=color, lw=2.8, label=f'{c_name} (AUC = {roc_auc:.3f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1.5)
ax.set_title("One-vs-Rest (OvR) ROC Curves: Multi-Class Stimulus Classification", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("False Positive Rate", fontsize=15, fontweight='bold')
ax.set_ylabel("True Positive Rate", fontsize=15, fontweight='bold')
ax.legend(loc='lower right', framealpha=0.96, edgecolor='black', fontsize=13)
ax.grid(True)
plt.tight_layout()
save_both(fig, "03_multiclass_stimulus_svm_knn/2_ovr_roc_curves.png")

# 7. 03_multiclass_stimulus_svm_knn/4_knn_k_tuning.png
print("Generating 4_knn_k_tuning...")
k_range = range(1, 25, 2)
k_scores = []
for k in k_range:
    knn_temp = KNeighborsClassifier(n_neighbors=k, weights='distance')
    preds = cross_val_predict(knn_temp, X_scaled, y_multi, cv=3)
    k_scores.append(np.mean(preds == y_multi) * 100)

fig, ax = plt.subplots(figsize=(9.2, 5.2))
ax.plot(k_range, k_scores, marker='o', markersize=8, color='#D35400', lw=2.6, label='Distance-Weighted KNN')
ax.set_title("Hyperparameter Optimization: KNN Accuracy vs. Neighbor Count ($k$)", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("Number of Nearest Neighbors ($k$)", fontsize=15, fontweight='bold')
ax.set_ylabel("3-Fold CV Accuracy (%)", fontsize=15, fontweight='bold')
ax.grid(True)
ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
plt.tight_layout()
save_both(fig, "03_multiclass_stimulus_svm_knn/4_knn_k_tuning.png")

# 8. 04_music_genre_gradient_boosting/1_spectral_power_distributions.png
print("Generating 1_spectral_power_distributions...")
genre_map = {
    "normal": "Silence / Normal",
    "music/classical": "Classical Music",
    "music/devotional": "Devotional Music",
    "music/pop": "Pop Music"
}
music_df = df_feat[df_feat["category"].isin(genre_map.keys())].copy()
music_df["genre"] = music_df["category"].map(genre_map)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5.8))
palette_g = {"Silence / Normal": "#003366", "Classical Music": "#D35400", "Devotional Music": "#6A1B9A", "Pop Music": "#B22222"}
sns.boxplot(data=music_df, x="genre", y="low_freq_power", ax=ax1, palette=palette_g)
ax1.set_title("Low Freq Power (0.1–2 Hz)", fontsize=14, fontweight='bold')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=20, ha='right', fontsize=12, fontweight='bold')
ax1.grid(True)

sns.boxplot(data=music_df, x="genre", y="high_freq_power", ax=ax2, palette=palette_g)
ax2.set_title("High Freq Power (10–45 Hz)", fontsize=14, fontweight='bold')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=20, ha='right', fontsize=12, fontweight='bold')
ax2.grid(True)

sns.boxplot(data=music_df, x="genre", y="spectral_entropy", ax=ax3, palette=palette_g)
ax3.set_title("Spectral Entropy (Complexity)", fontsize=14, fontweight='bold')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=20, ha='right', fontsize=12, fontweight='bold')
ax3.grid(True)
plt.suptitle("Figure: Spectral Power Band Distributions Across Acoustic Genres", fontsize=16.5, fontweight='bold', y=0.98)
plt.tight_layout()
save_both(fig, "04_music_genre_gradient_boosting/1_spectral_power_distributions.png")

# 9. 04_music_genre_gradient_boosting/3_feature_weights.png
print("Generating 3_feature_weights...")
feature_cols_m = [
    "mean", "std", "var", "range", "rms", "mad", 
    "zcr", "skew", "kurt", "peak_count",
    "low_freq_power", "mid_freq_power", "high_freq_power", 
    "spectral_entropy", "dominant_freq"
]
X_m_scaled = StandardScaler().fit_transform(music_df[feature_cols_m].values)
lr_m = LogisticRegression(max_iter=1000)
lr_m.fit(X_m_scaled, music_df["genre"])
coef_mag = np.mean(np.abs(lr_m.coef_), axis=0)
ind_m = np.argsort(coef_mag)[::-1]

fig, ax = plt.subplots(figsize=(10.5, 6.2))
ax.barh(range(len(feature_cols_m)), coef_mag[ind_m][::-1], color="#6A1B9A", alpha=0.88, edgecolor='black')
ax.set_yticks(range(len(feature_cols_m)))
ax.set_yticklabels([feature_cols_m[i] for i in ind_m][::-1], fontsize=13, fontweight='bold')
ax.set_xlabel("Mean Absolute Coefficient Weight", fontsize=15, fontweight='bold')
ax.set_title("Feature Discriminative Power Across Acoustic Genres", fontsize=16, fontweight='bold', pad=12)
ax.grid(True, axis='x')
plt.tight_layout()
save_both(fig, "04_music_genre_gradient_boosting/3_feature_weights.png")

# 10. 05_circadian_rhythm_mlp_neural_network/3_mlp_training_loss.png
print("Generating 3_mlp_training_loss...")
mlp_loss = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=250, random_state=42)
mlp_loss.fit(X_scaled, df_feat["time_of_day"])
fig, ax = plt.subplots(figsize=(9.2, 5.2))
ax.plot(mlp_loss.loss_curve_, color='#006633', lw=2.8, label='Cross-Entropy Loss')
ax.set_title("MLP Neural Network Training Loss Convergence", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("Training Iterations (Epochs)", fontsize=15, fontweight='bold')
ax.set_ylabel("Loss Function Value", fontsize=15, fontweight='bold')
ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
ax.grid(True)
plt.tight_layout()
save_both(fig, "05_circadian_rhythm_mlp_neural_network/3_mlp_training_loss.png")

# 11. 05_circadian_rhythm_mlp_neural_network/4_layer_weight_activations.png
print("Generating 4_layer_weight_activations...")
weights_in = np.abs(mlp_loss.coefs_[0]).mean(axis=1)
ind_w = np.argsort(weights_in)[::-1]
fig, ax = plt.subplots(figsize=(11, 6.8))
ax.barh(range(len(feature_cols)), weights_in[ind_w][::-1], color='#D35400', alpha=0.88, edgecolor='black')
ax.set_yticks(range(len(feature_cols)))
ax.set_yticklabels([feature_cols[i] for i in ind_w][::-1], fontsize=13, fontweight='bold')
ax.set_xlabel("Mean Weight Magnitude", fontsize=15, fontweight='bold')
ax.set_title("MLP Input Layer Mean Absolute Weight Activations", fontsize=16, fontweight='bold', pad=12)
ax.grid(True, axis='x')
plt.tight_layout()
save_both(fig, "05_circadian_rhythm_mlp_neural_network/4_layer_weight_activations.png")

# 12. 06_unsupervised_anomaly_detection_isolation_forest/1_anomaly_score_distribution.png
print("Generating 1_anomaly_score_distribution...")
iso = IsolationForest(n_estimators=150, contamination=0.08, random_state=42)
iso.fit(X_scaled[df_feat["main_category"] == "normal"])
scores_all = -iso.decision_function(X_scaled)
df_feat["iso_score"] = scores_all
fig, ax = plt.subplots(figsize=(10.5, 5.8))
sns.boxplot(data=df_feat, x="main_category", y="iso_score", palette=palette_v, ax=ax)
ax.axhline(np.percentile(scores_all[df_feat["main_category"] == "normal"], 90),
           color='#B22222', linestyle='--', linewidth=2.0, label='Alarm Trigger Boundary')
ax.set_title("Isolation Forest Anomaly Score Distribution Across Stimulus Categories", fontsize=16, fontweight='bold', pad=12)
ax.set_ylabel("Anomaly Score (Higher = More Anomalous)", fontsize=15, fontweight='bold')
ax.set_xlabel("Condition", fontsize=15, fontweight='bold')
ax.legend(loc='upper left', framealpha=0.96, edgecolor='black', fontsize=12.5)
ax.grid(True)
plt.tight_layout()
save_both(fig, "06_unsupervised_anomaly_detection_isolation_forest/1_anomaly_score_distribution.png")

# 13. 06_unsupervised_anomaly_detection_isolation_forest/4_anomaly_roc_curve.png
print("Generating 4_anomaly_roc_curve...")
y_true_anomaly = (df_feat["main_category"] != "normal").astype(int)
fpr_a, tpr_a, _ = roc_curve(y_true_anomaly, scores_all)
roc_auc_a = auc(fpr_a, tpr_a)
fig, ax = plt.subplots(figsize=(8.8, 5.8))
ax.plot(fpr_a, tpr_a, color='#B22222', lw=2.8, label=f'Unsupervised Isolation Forest (AUC = {roc_auc_a:.3f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1.5)
ax.set_title("ROC Curve: Unsupervised Stimulus Anomaly Detection", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("False Alarm Rate", fontsize=15, fontweight='bold')
ax.set_ylabel("Event Detection Rate (Sensitivity)", fontsize=15, fontweight='bold')
ax.legend(loc='lower right', framealpha=0.96, edgecolor='black', fontsize=13)
ax.grid(True)
plt.tight_layout()
save_both(fig, "06_unsupervised_anomaly_detection_isolation_forest/4_anomaly_roc_curve.png")

print("\nAll 13 remaining subfolder plots successfully upgraded to IEEE publication standard!")
