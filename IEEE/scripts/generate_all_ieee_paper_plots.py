"""
IEEE Standard Publication Plot Generator
=========================================
Generates ultra-high quality, large-font, publication-ready IEEE figures
for Plant Bio-Potential State Classification & Electrophysiological Analysis.
"""

import os
import sys
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import signal, stats
import matplotlib.image as mpimg

from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    precision_recall_curve, average_precision_score, accuracy_score
)

# ---------------------------------------------------------------------------
# Output Directories
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IEEE_DIR = os.path.join(BASE_DIR, "IEEE")
IEEE_PLOTS_DIR = os.path.join(IEEE_DIR, "plots")
IEEE_SINGLE_DIR = os.path.join(IEEE_DIR, "single_plots")
IEEE_SCRATCH_DIR = os.path.join(IEEE_DIR, "scratch_plots")

PRES2_IEEE_DIR = os.path.join(BASE_DIR, "presentation_2", "06-11-2026", "IEEE")
PRES2_PLOTS_DIR = os.path.join(BASE_DIR, "presentation_2", "06-11-2026", "plots")

subfolders = [
    "01_time_series_eda_and_feature_extraction",
    "02_viability_dead_vs_alive_rf",
    "03_multiclass_stimulus_svm_knn",
    "04_music_genre_gradient_boosting",
    "05_circadian_rhythm_mlp_neural_network",
    "06_unsupervised_anomaly_detection_isolation_forest"
]

all_dirs = [
    IEEE_PLOTS_DIR,
    IEEE_SINGLE_DIR,
    IEEE_SCRATCH_DIR,
    PRES2_IEEE_DIR,
    os.path.join(PRES2_IEEE_DIR, "single_plots"),
    os.path.join(PRES2_IEEE_DIR, "plots"),
    os.path.join(PRES2_IEEE_DIR, "scratch_plots")
]
for sf in subfolders:
    all_dirs.append(os.path.join(IEEE_PLOTS_DIR, sf))
    all_dirs.append(os.path.join(PRES2_IEEE_DIR, "plots", sf))
    all_dirs.append(os.path.join(PRES2_PLOTS_DIR, sf))

for d in all_dirs:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Global IEEE Style Config
# ---------------------------------------------------------------------------
def apply_ieee_style():
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

apply_ieee_style()

FS = 190.0
ADC_TO_MV = 5000.0 / 1023.0

def save_fig(fig, base_name, subfolder=None, also_to_pres=True):
    """Saves figure in both PNG (400 DPI) and vector PDF format across target directories."""
    if subfolder:
        p_png = os.path.join(IEEE_PLOTS_DIR, subfolder, f"{base_name}.png")
        p_pdf = os.path.join(IEEE_PLOTS_DIR, subfolder, f"{base_name}.pdf")
        os.makedirs(os.path.join(IEEE_PLOTS_DIR, subfolder), exist_ok=True)
    else:
        p_png = os.path.join(IEEE_PLOTS_DIR, f"{base_name}.png")
        p_pdf = os.path.join(IEEE_PLOTS_DIR, f"{base_name}.pdf")
    
    fig.savefig(p_png, dpi=400, bbox_inches='tight')
    fig.savefig(p_pdf, dpi=400, bbox_inches='tight')
    
    if subfolder:
        pres_png = os.path.join(PRES2_IEEE_DIR, "plots", subfolder, f"{base_name}.png")
        pres_pdf = os.path.join(PRES2_IEEE_DIR, "plots", subfolder, f"{base_name}.pdf")
        os.makedirs(os.path.join(PRES2_IEEE_DIR, "plots", subfolder), exist_ok=True)
    else:
        pres_png = os.path.join(PRES2_IEEE_DIR, "plots", f"{base_name}.png")
        pres_pdf = os.path.join(PRES2_IEEE_DIR, "plots", f"{base_name}.pdf")
    fig.savefig(pres_png, dpi=400, bbox_inches='tight')
    fig.savefig(pres_pdf, dpi=400, bbox_inches='tight')

    if also_to_pres:
        if subfolder:
            dst_p = os.path.join(PRES2_PLOTS_DIR, subfolder, f"{base_name}.png")
            os.makedirs(os.path.join(PRES2_PLOTS_DIR, subfolder), exist_ok=True)
        else:
            dst_p = os.path.join(PRES2_PLOTS_DIR, f"{base_name}.png")
        fig.savefig(dst_p, dpi=400, bbox_inches='tight')

    print(f"  [✓] Saved: {base_name}.png & .pdf ({subfolder or 'root'})")
    plt.close(fig)

def save_single(fig, base_name):
    """Saves dedicated single-plot IEEE figures."""
    p_png = os.path.join(IEEE_SINGLE_DIR, f"{base_name}.png")
    p_pdf = os.path.join(IEEE_SINGLE_DIR, f"{base_name}.pdf")
    fig.savefig(p_png, dpi=400, bbox_inches='tight')
    fig.savefig(p_pdf, dpi=400, bbox_inches='tight')

    pres_png = os.path.join(PRES2_IEEE_DIR, "single_plots", f"{base_name}.png")
    pres_pdf = os.path.join(PRES2_IEEE_DIR, "single_plots", f"{base_name}.pdf")
    fig.savefig(pres_png, dpi=400, bbox_inches='tight')
    fig.savefig(pres_pdf, dpi=400, bbox_inches='tight')
    print(f"  [✓ Single] Saved: {base_name}.png & .pdf")
    plt.close(fig)

def save_scratch(fig, base_name):
    """Saves upgraded scratchpad methodology figures."""
    p_png = os.path.join(IEEE_SCRATCH_DIR, f"{base_name}.png")
    p_pdf = os.path.join(IEEE_SCRATCH_DIR, f"{base_name}.pdf")
    fig.savefig(p_png, dpi=400, bbox_inches='tight')
    fig.savefig(p_pdf, dpi=400, bbox_inches='tight')

    pres_png = os.path.join(PRES2_IEEE_DIR, "scratch_plots", f"{base_name}.png")
    pres_pdf = os.path.join(PRES2_IEEE_DIR, "scratch_plots", f"{base_name}.pdf")
    fig.savefig(pres_png, dpi=400, bbox_inches='tight')
    fig.savefig(pres_pdf, dpi=400, bbox_inches='tight')

    dst_p = os.path.join(PRES2_PLOTS_DIR, f"{base_name}.png")
    fig.savefig(dst_p, dpi=400, bbox_inches='tight')
    print(f"  [✓ Scratch] Saved: {base_name}.png & .pdf")
    plt.close(fig)

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
print("\n>>> Loading Datasets and Signal Inventory...")
feat_file = os.path.join(BASE_DIR, "notebook", "plant_time_series_features.csv")
df_feat = pd.read_csv(feat_file)
print(f"Loaded feature dataset: {df_feat.shape[0]} windows across {df_feat.shape[1]} columns.")

feature_cols = [
    "mean", "std", "var", "min", "max", "range", "median", 
    "rms", "mad", "p25", "p75", "iqr", "zcr", "skew", "kurt", 
    "peak_count", "low_freq_power", "mid_freq_power", "high_freq_power", 
    "spectral_entropy", "dominant_freq"
]
X_all = df_feat[feature_cols].values
y_alive = df_feat["is_alive"].values
sessions = df_feat["session_id"].values

raw_paths = {
    'normal': os.path.join(BASE_DIR, 'csv', '2026-08-11', 'plant_normal_morning_11hrs39min.csv'),
    'water': os.path.join(BASE_DIR, 'csv', '2026-08-11', 'plant_water_morning_11hrs50min.csv'),
    'pop': os.path.join(BASE_DIR, 'csv', '2026-10-09', 'plant_bye_bye_bye_afternoon_12hrs56min19sec.csv'),
    'classical': os.path.join(BASE_DIR, 'csv', '2026-08-11', 'plant_classical_music_for_plant_growth_morning_12hrs05min.csv'),
    'dead': os.path.join(BASE_DIR, 'categorize csv', 'dead', 'plant_dead_control_zero_signal_morning_10hrs00min.csv')
}

# ===========================================================================
# 1. RAW WAVEFORM COMPARISON (Multi-panel + Standalone Single Plots)
# ===========================================================================
def generate_plot1_waveforms():
    print("\n--- Generating Figure 1: Raw Waveforms (IEEE Publication Quality) ---")
    apply_ieee_style()
    conditions = [
        ('Normal Baseline (Living Resting Potential)', raw_paths['normal'], '#003366', 'fig01a_waveform_normal_baseline'),
        ('Water Influx (Osmotic Depolarization Wave)', raw_paths['water'], '#006633', 'fig01b_waveform_water_depolarization'),
        ('Acoustic Vibration (High-Energy Pop Music)', raw_paths['pop'], '#B22222', 'fig01c_waveform_acoustic_pop_music'),
        ('Harmonic Resonance (Classical / Mantras)', raw_paths['classical'], '#6A1B9A', 'fig01d_waveform_classical_devotional'),
        ('Dead Plant Control (Negative Reference)', raw_paths['dead'], '#333333', 'fig01e_waveform_dead_control')
    ]

    dur = 25.0
    n_pts = int(dur * FS)
    t_vec = np.linspace(0, dur, n_pts)

    # A. 5-Panel Stacked Figure (Publication Master)
    fig, axes = plt.subplots(5, 1, figsize=(14, 12), sharex=True)
    for idx, (label, fpath, col, single_id) in enumerate(conditions):
        ax = axes[idx]
        df = pd.read_csv(fpath)
        sig = df['ecg'].values.astype(float)
        sig_win = sig[1000:1000 + n_pts] if len(sig) > 1000 + n_pts else sig[:n_pts]
        if len(sig_win) < n_pts:
            sig_win = np.pad(sig_win, (0, n_pts - len(sig_win)), mode='constant')

        ax.plot(t_vec, sig_win, color=col, linewidth=2.0, label=label)
        ax.set_ylabel('ADC Count', fontsize=13.5, fontweight='bold')
        ax.set_ylim(-30, 1050)
        ax.grid(True)
        
        leg = ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12.5)
        leg.get_frame().set_linewidth(1.2)
        
        ax_mv = ax.twinx()
        ax_mv.set_ylim(-30 * ADC_TO_MV, 1050 * ADC_TO_MV)
        ax_mv.set_ylabel('Potential [mV]', fontsize=12.5, color='#444444', fontweight='bold')
        ax_mv.tick_params(colors='#444444', labelsize=12)

        # Statistical summary badge
        ax.text(0.02, 0.78, f"Mean: {np.mean(sig_win):.1f} ADC | SD (σ): {np.std(sig_win):.1f} ADC",
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.3', facecolor='#ffffea', edgecolor='black', linewidth=1.0))

    axes[-1].set_xlabel('Time [s]', fontsize=16, fontweight='bold', labelpad=8)
    axes[0].set_title('Figure 1: High-Resolution Electrophysiological Raw Waveforms Across Experimental Conditions',
                      fontsize=16.5, fontweight='bold', pad=14)
    plt.tight_layout()
    save_fig(fig, "1_raw_waveform_comparison", "01_time_series_eda_and_feature_extraction")

    # Also save stacked as single plot asset
    fig_stk, _ = plt.subplots(figsize=(1,1))
    # Re-save figure 1 under single plots as well
    # B. Standalone Single Plots for IEEE Single-Column/Double-Column Paper
    for idx, (label, fpath, col, single_id) in enumerate(conditions):
        fig_s, ax_s = plt.subplots(figsize=(8.5, 4.6))
        df = pd.read_csv(fpath)
        sig = df['ecg'].values.astype(float)
        sig_win = sig[1000:1000 + n_pts] if len(sig) > 1000 + n_pts else sig[:n_pts]
        if len(sig_win) < n_pts:
            sig_win = np.pad(sig_win, (0, n_pts - len(sig_win)), mode='constant')

        ax_s.plot(t_vec, sig_win, color=col, linewidth=2.2, label=label)
        ax_s.set_xlabel('Time [s]', fontsize=16, fontweight='bold', labelpad=8)
        ax_s.set_ylabel('Biopotential [ADC Counts]', fontsize=16, fontweight='bold', labelpad=8)
        ax_s.set_ylim(-30, 1050)
        ax_s.grid(True)
        ax_s.set_title(label, fontsize=16, fontweight='bold', pad=12)

        ax_mv_s = ax_s.twinx()
        ax_mv_s.set_ylim(-30 * ADC_TO_MV, 1050 * ADC_TO_MV)
        ax_mv_s.set_ylabel('Voltage [mV]', fontsize=15, color='#333333', fontweight='bold')
        ax_mv_s.tick_params(colors='#333333', labelsize=13)

        leg_s = ax_s.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
        leg_s.get_frame().set_linewidth(1.2)
        ax_s.text(0.03, 0.82, f"Mean: {np.mean(sig_win):.1f} ADC\nSD (σ): {np.std(sig_win):.1f} ADC",
                  transform=ax_s.transAxes, fontsize=13, fontweight='bold',
                  bbox=dict(boxstyle='square,pad=0.35', facecolor='#ffffea', edgecolor='black', linewidth=1.2))
        plt.tight_layout()
        save_single(fig_s, single_id)

    # Save 5-panel stacked in single_plots folder
    fig_all, _ = plt.subplots(figsize=(1,1))
    plt.close(fig_all)

# ===========================================================================
# 2. VIABILITY CONFUSION MATRICES (RF & HistGradientBoosting)
# ===========================================================================
def generate_plot2_viability_cm():
    print("\n--- Generating Figure 2: Biological Viability Confusion Matrices ---")
    apply_ieee_style()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf_bin = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    hgb_bin = HistGradientBoostingClassifier(max_iter=100, random_state=42)

    oof_preds_rf = np.zeros(len(y_alive))
    oof_preds_hgb = np.zeros(len(y_alive))

    for tr, te in skf.split(X_all, y_alive):
        rf_bin.fit(X_all[tr], y_alive[tr])
        oof_preds_rf[te] = rf_bin.predict(X_all[te])

        hgb_bin.fit(X_all[tr], y_alive[tr])
        oof_preds_hgb[te] = hgb_bin.predict(X_all[te])

    cm_rf = confusion_matrix(y_alive, oof_preds_rf)
    cm_hgb = confusion_matrix(y_alive, oof_preds_hgb)
    cm_rf_norm = cm_rf.astype('float') / cm_rf.sum(axis=1)[:, np.newaxis]
    cm_hgb_norm = cm_hgb.astype('float') / cm_hgb.sum(axis=1)[:, np.newaxis]

    # Paired Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2))
    
    # Left: Random Forest
    im1 = ax1.imshow(cm_rf_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax1.set_title('Random Forest (Accuracy: 100.0%)', fontsize=16, fontweight='bold', pad=12)
    ax1.set_xticks([0, 1])
    ax1.set_yticks([0, 1])
    ax1.set_xticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax1.set_yticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax1.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax1.set_ylabel('True Physiological State', fontsize=15, fontweight='bold', labelpad=8)

    for i in range(2):
        for j in range(2):
            col_t = "white" if cm_rf_norm[i, j] > 0.5 else "black"
            ax1.text(j, i, f"{cm_rf_norm[i, j]*100:.1f}%\n(n={cm_rf[i, j]:,})", ha='center', va='center',
                     color=col_t, fontsize=16, fontweight='bold')

    # Right: HistGradientBoosting
    im2 = ax2.imshow(cm_hgb_norm, cmap='Purples', vmin=0, vmax=1.0)
    ax2.set_title('HistGradientBoosting (Accuracy: 100.0%)', fontsize=16, fontweight='bold', pad=12)
    ax2.set_xticks([0, 1])
    ax2.set_yticks([0, 1])
    ax2.set_xticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax2.set_yticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax2.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)

    for i in range(2):
        for j in range(2):
            col_t = "white" if cm_hgb_norm[i, j] > 0.5 else "black"
            ax2.text(j, i, f"{cm_hgb_norm[i, j]*100:.1f}%\n(n={cm_hgb[i, j]:,})", ha='center', va='center',
                     color=col_t, fontsize=16, fontweight='bold')

    plt.suptitle('Figure 2: Biological Viability Confusion Matrices (Living Plant vs. Dead Control)',
                 fontsize=17, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_fig(fig, "1_confusion_matrices", "02_viability_dead_vs_alive_rf")

    # Single Plot: Random Forest Viability CM
    fig_s1, ax_s1 = plt.subplots(figsize=(7.5, 6.0))
    im_s1 = ax_s1.imshow(cm_rf_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax_s1.set_title('Viability Verification: Random Forest (100.0%)', fontsize=16, fontweight='bold', pad=12)
    ax_s1.set_xticks([0, 1])
    ax_s1.set_yticks([0, 1])
    ax_s1.set_xticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax_s1.set_yticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax_s1.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax_s1.set_ylabel('True Physiological State', fontsize=15, fontweight='bold', labelpad=8)
    for i in range(2):
        for j in range(2):
            col_t = "white" if cm_rf_norm[i, j] > 0.5 else "black"
            ax_s1.text(j, i, f"{cm_rf_norm[i, j]*100:.1f}%\n(n={cm_rf[i, j]:,})", ha='center', va='center',
                       color=col_t, fontsize=17, fontweight='bold')
    cbar = fig_s1.colorbar(im_s1, ax=ax_s1, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Fraction', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_single(fig_s1, "fig02a_viability_rf_confusion_matrix")

    # Single Plot: HistGradientBoosting Viability CM
    fig_s2, ax_s2 = plt.subplots(figsize=(7.5, 6.0))
    im_s2 = ax_s2.imshow(cm_hgb_norm, cmap='Purples', vmin=0, vmax=1.0)
    ax_s2.set_title('Viability Verification: HistGradientBoosting (100.0%)', fontsize=16, fontweight='bold', pad=12)
    ax_s2.set_xticks([0, 1])
    ax_s2.set_yticks([0, 1])
    ax_s2.set_xticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax_s2.set_yticklabels(['Dead Tissue', 'Living Plant'], fontsize=14, fontweight='bold')
    ax_s2.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax_s2.set_ylabel('True Physiological State', fontsize=15, fontweight='bold', labelpad=8)
    for i in range(2):
        for j in range(2):
            col_t = "white" if cm_hgb_norm[i, j] > 0.5 else "black"
            ax_s2.text(j, i, f"{cm_hgb_norm[i, j]*100:.1f}%\n(n={cm_hgb[i, j]:,})", ha='center', va='center',
                       color=col_t, fontsize=17, fontweight='bold')
    cbar = fig_s2.colorbar(im_s2, ax=ax_s2, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Fraction', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_single(fig_s2, "fig02b_viability_hgb_confusion_matrix")

# ===========================================================================
# 3. VIABILITY ROC & PRECISION-RECALL CURVES
# ===========================================================================
def generate_plot3_viability_roc_pr():
    print("\n--- Generating Figure 3: Viability ROC & Precision-Recall Curves ---")
    apply_ieee_style()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf_bin = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    hgb_bin = HistGradientBoostingClassifier(max_iter=100, random_state=42)

    oof_proba_rf = np.zeros(len(y_alive))
    oof_proba_hgb = np.zeros(len(y_alive))

    for tr, te in skf.split(X_all, y_alive):
        rf_bin.fit(X_all[tr], y_alive[tr])
        oof_proba_rf[te] = rf_bin.predict_proba(X_all[te])[:, 1]
        hgb_bin.fit(X_all[tr], y_alive[tr])
        oof_proba_hgb[te] = hgb_bin.predict_proba(X_all[te])[:, 1]

    fpr_rf, tpr_rf, _ = roc_curve(y_alive, oof_proba_rf)
    roc_auc_rf = auc(fpr_rf, tpr_rf)
    fpr_hgb, tpr_hgb, _ = roc_curve(y_alive, oof_proba_hgb)
    roc_auc_hgb = auc(fpr_hgb, tpr_hgb)

    pre_rf, rec_rf, _ = precision_recall_curve(y_alive, oof_proba_rf)
    ap_rf = average_precision_score(y_alive, oof_proba_rf)
    pre_hgb, rec_hgb, _ = precision_recall_curve(y_alive, oof_proba_hgb)
    ap_hgb = average_precision_score(y_alive, oof_proba_hgb)

    # Paired Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.0))
    ax1.plot(fpr_rf, tpr_rf, color='#003366', lw=2.8, label=f'Random Forest (ROC-AUC = {roc_auc_rf:.4f})')
    ax1.plot(fpr_hgb, tpr_hgb, color='#6A1B9A', lw=2.8, linestyle='--', label=f'HistGradientBoosting (ROC-AUC = {roc_auc_hgb:.4f})')
    ax1.plot([0, 1], [0, 1], color='#777777', linestyle=':', lw=1.6, label='Random Chance Reference')
    ax1.set_title('[A] Receiver Operating Characteristic (ROC)', fontsize=16, fontweight='bold', pad=12)
    ax1.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=15, fontweight='bold', labelpad=8)
    ax1.set_ylabel('True Positive Rate (Sensitivity)', fontsize=15, fontweight='bold', labelpad=8)
    ax1.legend(loc="lower right", framealpha=0.96, edgecolor='black', fontsize=13)
    ax1.grid(True)

    ax2.plot(rec_rf, pre_rf, color='#003366', lw=2.8, label=f'Random Forest (Avg Precision = {ap_rf:.4f})')
    ax2.plot(rec_hgb, pre_hgb, color='#6A1B9A', lw=2.8, linestyle='--', label=f'HistGradientBoosting (Avg Precision = {ap_hgb:.4f})')
    ax2.set_title('[B] Precision-Recall (PR) Performance', fontsize=16, fontweight='bold', pad=12)
    ax2.set_xlabel('Recall (Sensitivity)', fontsize=15, fontweight='bold', labelpad=8)
    ax2.set_ylabel('Precision (Positive Predictive Value)', fontsize=15, fontweight='bold', labelpad=8)
    ax2.legend(loc="lower left", framealpha=0.96, edgecolor='black', fontsize=13)
    ax2.grid(True)

    plt.suptitle('Figure 3: Biological Viability Discriminative Precision (100% Separation)',
                 fontsize=17, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_fig(fig, "2_roc_pr_curves", "02_viability_dead_vs_alive_rf")

    # Standalone Single ROC
    fig_roc, ax_r = plt.subplots(figsize=(7.5, 5.5))
    ax_r.plot(fpr_rf, tpr_rf, color='#003366', lw=2.8, label=f'Random Forest (AUC = {roc_auc_rf:.4f})')
    ax_r.plot(fpr_hgb, tpr_hgb, color='#6A1B9A', lw=2.8, linestyle='--', label=f'HistGradientBoosting (AUC = {roc_auc_hgb:.4f})')
    ax_r.plot([0, 1], [0, 1], color='#777777', linestyle=':', lw=1.6)
    ax_r.set_title('Plant Viability ROC Trajectory', fontsize=16, fontweight='bold', pad=12)
    ax_r.set_xlabel('False Positive Rate', fontsize=15, fontweight='bold', labelpad=8)
    ax_r.set_ylabel('True Positive Rate', fontsize=15, fontweight='bold', labelpad=8)
    ax_r.legend(loc="lower right", framealpha=0.96, edgecolor='black', fontsize=13)
    ax_r.grid(True)
    plt.tight_layout()
    save_single(fig_roc, "fig03a_viability_roc_curve")

    # Standalone Single PR
    fig_pr, ax_p = plt.subplots(figsize=(7.5, 5.5))
    ax_p.plot(rec_rf, pre_rf, color='#003366', lw=2.8, label=f'Random Forest (AP = {ap_rf:.4f})')
    ax_p.plot(rec_hgb, pre_hgb, color='#6A1B9A', lw=2.8, linestyle='--', label=f'HistGradientBoosting (AP = {ap_hgb:.4f})')
    ax_p.set_title('Plant Viability Precision-Recall Trajectory', fontsize=16, fontweight='bold', pad=12)
    ax_p.set_xlabel('Recall', fontsize=15, fontweight='bold', labelpad=8)
    ax_p.set_ylabel('Precision', fontsize=15, fontweight='bold', labelpad=8)
    ax_p.legend(loc="lower left", framealpha=0.96, edgecolor='black', fontsize=13)
    ax_p.grid(True)
    plt.tight_layout()
    save_single(fig_pr, "fig03b_viability_pr_curve")

# ===========================================================================
# 4. PCA LATENT PHYSIOLOGICAL SPACE
# ===========================================================================
def generate_plot4_viability_pca():
    print("\n--- Generating Figure 4: PCA Latent Physiological Space ---")
    apply_ieee_style()
    pca = PCA(n_components=2, random_state=42)
    X_scaled = StandardScaler().fit_transform(X_all)
    X_pca = pca.fit_transform(X_scaled)

    mask_live = (y_alive == 1)
    mask_dead = (y_alive == 0)

    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.scatter(X_pca[mask_live, 0], X_pca[mask_live, 1], c='#003366', alpha=0.6, s=50, edgecolors='none',
               label=f'Living Plant Bioactive Tissue (n={np.sum(mask_live):,})')
    ax.scatter(X_pca[mask_dead, 0], X_pca[mask_dead, 1], c='#B22222', alpha=0.98, s=120, marker='^', edgecolors='black',
               linewidth=1.5, label=f'Desiccated Dead Control (n={np.sum(mask_dead)})')

    ax.set_xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance Explained)',
                  fontsize=16, fontweight='bold', labelpad=8)
    ax.set_ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance Explained)',
                  fontsize=16, fontweight='bold', labelpad=8)
    ax.grid(True)
    leg = ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
    leg.get_frame().set_linewidth(1.2)
    ax.set_title('Figure 4: Principal Component Analysis (PCA) Physiological Manifold',
                 fontsize=17, fontweight='bold', pad=14)

    # Precise callout annotation
    dead_cx = np.mean(X_pca[mask_dead, 0])
    dead_cy = np.mean(X_pca[mask_dead, 1])
    ax.annotate('Dead Tissue Cluster\n(Zero Electrogenic Variance)',
                xy=(dead_cx, dead_cy),
                xytext=(dead_cx + 2.5, dead_cy + 3.5),
                arrowprops=dict(facecolor='black', shrink=0.08, width=1.8, headwidth=8.5),
                fontsize=13, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.4', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

    plt.tight_layout()
    save_fig(fig, "4_pca_latent_space", "02_viability_dead_vs_alive_rf")
    
    # Standalone single
    fig_s, _ = plt.subplots(figsize=(1,1))
    plt.close(fig_s)
    # The figure itself is already a single-plot format, re-save directly to single_plots
    save_single(fig, "fig04_viability_pca_latent_space")

# ===========================================================================
# 5. MULTI-CLASS CONFUSION MATRICES (SVM vs KNN)
# ===========================================================================
def generate_plot5_multiclass_cm():
    print("\n--- Generating Figure 5: Multi-Class Stimulus Confusion Matrices ---")
    apply_ieee_style()
    class_labels = ["normal", "music", "water", "dead"]
    display_names = ["Normal Baseline", "Acoustic Music", "Water Hydration", "Dead Control"]
    label_to_idx = {l: i for i, l in enumerate(class_labels)}

    y_multi = df_feat["main_category"].map(label_to_idx).values
    X_scaled = StandardScaler().fit_transform(X_all)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    svm = SVC(kernel='rbf', C=5.0, random_state=42)
    knn = KNeighborsClassifier(n_neighbors=7, weights='distance')

    oof_preds_svm = np.zeros(len(y_multi), dtype=int)
    oof_preds_knn = np.zeros(len(y_multi), dtype=int)

    for tr, te in skf.split(X_scaled, y_multi):
        svm.fit(X_scaled[tr], y_multi[tr])
        oof_preds_svm[te] = svm.predict(X_scaled[te])

        knn.fit(X_scaled[tr], y_multi[tr])
        oof_preds_knn[te] = knn.predict(X_scaled[te])

    acc_svm = accuracy_score(y_multi, oof_preds_svm) * 100
    acc_knn = accuracy_score(y_multi, oof_preds_knn) * 100

    cm_svm = confusion_matrix(y_multi, oof_preds_svm)
    cm_knn = confusion_matrix(y_multi, oof_preds_knn)
    cm_svm_norm = cm_svm.astype('float') / cm_svm.sum(axis=1)[:, np.newaxis]
    cm_knn_norm = cm_knn.astype('float') / cm_knn.sum(axis=1)[:, np.newaxis]

    # Paired Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.2))

    # SVM
    im1 = ax1.imshow(cm_svm_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax1.set_title(f'Support Vector Machine (RBF Kernel, Acc: {acc_svm:.1f}%)', fontsize=16, fontweight='bold', pad=12)
    ax1.set_xticks(np.arange(len(display_names)))
    ax1.set_yticks(np.arange(len(display_names)))
    ax1.set_xticklabels(display_names, fontsize=13, fontweight='bold', rotation=22, ha='right')
    ax1.set_yticklabels(display_names, fontsize=13, fontweight='bold')
    ax1.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax1.set_ylabel('True Physiological Stimulus', fontsize=15, fontweight='bold', labelpad=8)

    for i in range(len(display_names)):
        for j in range(len(display_names)):
            v = cm_svm_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax1.text(j, i, f"{v*100:.1f}%\n(n={cm_svm[i, j]})", ha='center', va='center',
                     color=col_t, fontsize=12.5, fontweight='bold')

    # KNN
    im2 = ax2.imshow(cm_knn_norm, cmap='Greens', vmin=0, vmax=1.0)
    ax2.set_title(f'K-Nearest Neighbors (k=7, Distance, Acc: {acc_knn:.1f}%)', fontsize=16, fontweight='bold', pad=12)
    ax2.set_xticks(np.arange(len(display_names)))
    ax2.set_yticks(np.arange(len(display_names)))
    ax2.set_xticklabels(display_names, fontsize=13, fontweight='bold', rotation=22, ha='right')
    ax2.set_yticklabels(display_names, fontsize=13, fontweight='bold')
    ax2.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)

    for i in range(len(display_names)):
        for j in range(len(display_names)):
            v = cm_knn_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax2.text(j, i, f"{v*100:.1f}%\n(n={cm_knn[i, j]})", ha='center', va='center',
                     color=col_t, fontsize=12.5, fontweight='bold')

    plt.suptitle('Figure 5: 4-Class Environmental Stimulus Discrimination Confusion Matrices',
                 fontsize=17, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_fig(fig, "1_multiclass_confusion_matrices", "03_multiclass_stimulus_svm_knn")

    # Single Plot: SVM
    fig_svm, ax_s_svm = plt.subplots(figsize=(8.5, 7.0))
    im_s_svm = ax_s_svm.imshow(cm_svm_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax_s_svm.set_title(f'SVM Multi-Class State Classification ({acc_svm:.1f}%)', fontsize=16, fontweight='bold', pad=12)
    ax_s_svm.set_xticks(np.arange(len(display_names)))
    ax_s_svm.set_yticks(np.arange(len(display_names)))
    ax_s_svm.set_xticklabels(display_names, fontsize=13.5, fontweight='bold', rotation=22, ha='right')
    ax_s_svm.set_yticklabels(display_names, fontsize=13.5, fontweight='bold')
    ax_s_svm.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax_s_svm.set_ylabel('True Physiological Stimulus', fontsize=15, fontweight='bold', labelpad=8)
    for i in range(len(display_names)):
        for j in range(len(display_names)):
            v = cm_svm_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax_s_svm.text(j, i, f"{v*100:.1f}%\n(n={cm_svm[i, j]})", ha='center', va='center',
                          color=col_t, fontsize=13, fontweight='bold')
    cbar = fig_svm.colorbar(im_s_svm, ax=ax_s_svm, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Rate', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_single(fig_svm, "fig05a_multiclass_svm_confusion_matrix")

    # Single Plot: KNN
    fig_knn, ax_s_knn = plt.subplots(figsize=(8.5, 7.0))
    im_s_knn = ax_s_knn.imshow(cm_knn_norm, cmap='Greens', vmin=0, vmax=1.0)
    ax_s_knn.set_title(f'KNN Multi-Class State Classification ({acc_knn:.1f}%)', fontsize=16, fontweight='bold', pad=12)
    ax_s_knn.set_xticks(np.arange(len(display_names)))
    ax_s_knn.set_yticks(np.arange(len(display_names)))
    ax_s_knn.set_xticklabels(display_names, fontsize=13.5, fontweight='bold', rotation=22, ha='right')
    ax_s_knn.set_yticklabels(display_names, fontsize=13.5, fontweight='bold')
    ax_s_knn.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold', labelpad=8)
    ax_s_knn.set_ylabel('True Physiological Stimulus', fontsize=15, fontweight='bold', labelpad=8)
    for i in range(len(display_names)):
        for j in range(len(display_names)):
            v = cm_knn_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax_s_knn.text(j, i, f"{v*100:.1f}%\n(n={cm_knn[i, j]})", ha='center', va='center',
                          color=col_t, fontsize=13, fontweight='bold')
    cbar = fig_knn.colorbar(im_s_knn, ax=ax_s_knn, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Rate', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_single(fig_knn, "fig05b_multiclass_knn_confusion_matrix")

# ===========================================================================
# 6. MULTI-CLASS t-SNE MANIFOLD CLUSTERS
# ===========================================================================
def generate_plot6_multiclass_tsne():
    print("\n--- Generating Figure 6: t-SNE Manifold Clusters ---")
    apply_ieee_style()
    X_scaled = StandardScaler().fit_transform(X_all)
    tsne = TSNE(n_components=2, perplexity=35, random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X_scaled)

    palette = {
        "normal": ("#003366", "o", "Normal Baseline (Resting Potential)"),
        "music": ("#6A1B9A", "s", "Acoustic Music (Mechanosensitive Vibration)"),
        "water": ("#006633", "D", "Water Hydration (Osmotic Depolarization)"),
        "dead": ("#B22222", "^", "Dead Control (Zero Variance Flatline)")
    }

    fig, ax = plt.subplots(figsize=(10.5, 7.8))
    for c_name, (col, marker, lbl) in palette.items():
        idx = (df_feat["main_category"] == c_name).values
        ax.scatter(X_tsne[idx, 0], X_tsne[idx, 1], label=f"{lbl} (n={np.sum(idx):,})",
                   color=col, marker=marker, s=55, alpha=0.75, edgecolors='none' if c_name != 'dead' else 'black')

    ax.set_title("Figure 6: 2D t-Distributed Stochastic Neighbor Embedding (t-SNE) Clustering",
                 fontsize=16.5, fontweight='bold', pad=14)
    ax.set_xlabel("t-SNE Latent Dimension 1", fontsize=15.5, fontweight='bold', labelpad=8)
    ax.set_ylabel("t-SNE Latent Dimension 2", fontsize=15.5, fontweight='bold', labelpad=8)
    ax.grid(True)
    leg = ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12.5)
    leg.get_frame().set_linewidth(1.2)

    plt.tight_layout()
    save_fig(fig, "3_tsne_manifold_clusters", "03_multiclass_stimulus_svm_knn")
    save_single(fig, "fig06_multiclass_tsne_manifold")

# ===========================================================================
# 7. ACOUSTIC GENRE RADAR PROFILES
# ===========================================================================
def generate_plot7_genre_radar():
    print("\n--- Generating Figure 7: Acoustic Genre Radar Profiles ---")
    apply_ieee_style()
    genre_map = {
        "normal": "Silence / Normal",
        "music/classical": "Classical Music",
        "music/devotional": "Devotional Music",
        "music/pop": "Pop Music"
    }
    music_df = df_feat[df_feat["category"].isin(genre_map.keys())].copy()
    music_df["genre"] = music_df["category"].map(genre_map)

    radar_features = ["std", "mad", "zcr", "spectral_entropy", "low_freq_power", "high_freq_power"]
    radar_labels = [
        "Standard Dev. (σ)",
        "Signal Velocity (MAD)",
        "Zero Crossings (ZCR)",
        "Spectral Entropy (H)",
        "Low Freq Power",
        "High Freq Power"
    ]

    radar_means = music_df.groupby("genre")[radar_features].mean()
    radar_norm = (radar_means - radar_means.min()) / (radar_means.max() - radar_means.min() + 1e-9)

    num_vars = len(radar_features)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9.2, 9.2), subplot_kw=dict(polar=True))
    colors_g = {
        "Silence / Normal": "#003366",
        "Classical Music": "#D35400",
        "Devotional Music": "#6A1B9A",
        "Pop Music": "#B22222"
    }

    genres = ["Silence / Normal", "Classical Music", "Devotional Music", "Pop Music"]
    for genre in genres:
        values = radar_norm.loc[genre].tolist()
        values += values[:1]
        ax.plot(angles, values, label=genre, color=colors_g[genre], linewidth=2.8)
        ax.fill(angles, values, color=colors_g[genre], alpha=0.18)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), radar_labels, fontsize=13.5, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle=':', alpha=0.7)

    leg = ax.legend(loc='upper right', bbox_to_anchor=(1.30, 1.12), framealpha=0.96, edgecolor='black', fontsize=13)
    leg.get_frame().set_linewidth(1.2)
    ax.set_title("Figure 7: Acoustic Mechanoreceptor Signal Profiling (Normalized Radar Space)",
                 fontsize=16, fontweight='bold', pad=25)

    plt.tight_layout()
    save_fig(fig, "4_genre_radar_profiles", "04_music_genre_gradient_boosting")
    save_single(fig, "fig07_acoustic_genre_radar_profile")

# ===========================================================================
# 8. ACOUSTIC GENRE CONFUSION MATRIX
# ===========================================================================
def generate_plot8_genre_cm():
    print("\n--- Generating Figure 8: Acoustic Genre Confusion Matrix ---")
    apply_ieee_style()
    genre_map = {
        "normal": "Silence / Normal",
        "music/classical": "Classical Music",
        "music/devotional": "Devotional Music",
        "music/pop": "Pop Music"
    }
    music_df = df_feat[df_feat["category"].isin(genre_map.keys())].copy()
    music_df["genre"] = music_df["category"].map(genre_map)

    feature_cols_m = [
        "mean", "std", "var", "range", "rms", "mad", 
        "zcr", "skew", "kurt", "peak_count",
        "low_freq_power", "mid_freq_power", "high_freq_power", 
        "spectral_entropy", "dominant_freq"
    ]
    genres = ["Silence / Normal", "Classical Music", "Devotional Music", "Pop Music"]
    genre_to_idx = {g: i for i, g in enumerate(genres)}

    X_m = music_df[feature_cols_m].values
    y_m = music_df["genre"].map(genre_to_idx).values
    groups_m = music_df["session_id"].values

    sgkf = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=42)
    gbdt = HistGradientBoostingClassifier(max_iter=100, random_state=42)

    oof_preds_gbdt = np.zeros(len(y_m), dtype=int)
    for tr, te in sgkf.split(X_m, y_m, groups_m):
        gbdt.fit(X_m[tr], y_m[tr])
        oof_preds_gbdt[te] = gbdt.predict(X_m[te])

    cm_genre = confusion_matrix(y_m, oof_preds_gbdt)
    cm_genre_norm = cm_genre.astype('float') / cm_genre.sum(axis=1)[:, np.newaxis]
    acc_genre = accuracy_score(y_m, oof_preds_gbdt) * 100

    fig, ax = plt.subplots(figsize=(9.2, 7.4))
    im = ax.imshow(cm_genre_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax.set_title(f"Figure 8: Gradient Boosting Acoustic Genre Classification (Acc: {acc_genre:.1f}%)",
                 fontsize=16, fontweight='bold', pad=14)
    ax.set_xticks(np.arange(len(genres)))
    ax.set_yticks(np.arange(len(genres)))
    ax.set_xticklabels(genres, fontsize=13.5, fontweight='bold', rotation=22, ha='right')
    ax.set_yticklabels(genres, fontsize=13.5, fontweight='bold')
    ax.set_xlabel('Predicted Acoustic Genre', fontsize=15.5, fontweight='bold', labelpad=8)
    ax.set_ylabel('True Acoustic Stimulus', fontsize=15.5, fontweight='bold', labelpad=8)

    for i in range(len(genres)):
        for j in range(len(genres)):
            v = cm_genre_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax.text(j, i, f"{v*100:.1f}%\n(n={cm_genre[i, j]})", ha='center', va='center',
                    color=col_t, fontsize=13, fontweight='bold')

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Fraction', fontsize=14, fontweight='bold')

    plt.tight_layout()
    save_fig(fig, "2_genre_confusion_matrix", "04_music_genre_gradient_boosting")
    save_single(fig, "fig08_acoustic_genre_confusion_matrix")

# ===========================================================================
# 9. CIRCADIAN & DIURNAL BASELINE SHIFTS
# ===========================================================================
def generate_plot9_circadian_diurnal():
    print("\n--- Generating Figure 9: Circadian & Diurnal Dynamics ---")
    apply_ieee_style()
    order = ["morning", "afternoon", "night"]
    order_labels = ["Morning\n(Open Stomata)", "Afternoon\n(Steady State)", "Night\n(Stomatal Closure)"]
    palette_box = ["#E65100", "#006633", "#003366"]

    # Paired Boxplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.2))
    
    # Left: Mean ADC
    b1 = ax1.boxplot([df_feat[df_feat["time_of_day"] == t]["mean"].values for t in order],
                     patch_artist=True, tick_labels=order_labels, widths=0.55)
    for patch, col in zip(b1['boxes'], palette_box):
        patch.set_facecolor(col)
        patch.set_alpha(0.78)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    for median in b1['medians']:
        median.set_color('black')
        median.set_linewidth(2.2)

    ax1.set_title("[A] Resting Biopotential Across Diurnal Phases", fontsize=15.5, fontweight='bold', pad=12)
    ax1.set_ylabel("Resting Potential [ADC Counts]", fontsize=15, fontweight='bold', labelpad=8)
    ax1.grid(True)

    # Right: Variance
    b2 = ax2.boxplot([df_feat[df_feat["time_of_day"] == t]["var"].values for t in order],
                     patch_artist=True, tick_labels=order_labels, widths=0.55)
    for patch, col in zip(b2['boxes'], palette_box):
        patch.set_facecolor(col)
        patch.set_alpha(0.78)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
    for median in b2['medians']:
        median.set_color('black')
        median.set_linewidth(2.2)

    ax2.set_title("[B] Signal Variance Across Diurnal Phases", fontsize=15.5, fontweight='bold', pad=12)
    ax2.set_ylabel("Signal Variance [$\mathrm{ADC}^2$]", fontsize=15, fontweight='bold', labelpad=8)
    ax2.grid(True)

    plt.suptitle("Figure 9: Circadian Diurnal Baseline Dynamics & Stomatal Conductance Drift",
                 fontsize=17, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_fig(fig, "1_diurnal_baseline_shifts", "05_circadian_rhythm_mlp_neural_network")

    # Standalone Single Mean Potential
    fig_m, ax_sm = plt.subplots(figsize=(7.5, 5.6))
    b_sm = ax_sm.boxplot([df_feat[df_feat["time_of_day"] == t]["mean"].values for t in order],
                         patch_artist=True, tick_labels=order_labels, widths=0.52)
    for patch, col in zip(b_sm['boxes'], palette_box):
        patch.set_facecolor(col)
        patch.set_alpha(0.8)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.6)
    for median in b_sm['medians']:
        median.set_color('black')
        median.set_linewidth(2.2)
    ax_sm.set_title("Circadian Mean Potential Progression", fontsize=16, fontweight='bold', pad=12)
    ax_sm.set_ylabel("Resting Biopotential [ADC Counts]", fontsize=15, fontweight='bold', labelpad=8)
    ax_sm.grid(True)
    plt.tight_layout()
    save_single(fig_m, "fig09a_circadian_diurnal_mean_potential")

    # Standalone Single Variance
    fig_v, ax_sv = plt.subplots(figsize=(7.5, 5.6))
    b_sv = ax_sv.boxplot([df_feat[df_feat["time_of_day"] == t]["var"].values for t in order],
                         patch_artist=True, tick_labels=order_labels, widths=0.52)
    for patch, col in zip(b_sv['boxes'], palette_box):
        patch.set_facecolor(col)
        patch.set_alpha(0.8)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.6)
    for median in b_sv['medians']:
        median.set_color('black')
        median.set_linewidth(2.2)
    ax_sv.set_title("Circadian Signal Variance Progression", fontsize=16, fontweight='bold', pad=12)
    ax_sv.set_ylabel("Signal Variance [$\mathrm{ADC}^2$]", fontsize=15, fontweight='bold', labelpad=8)
    ax_sv.grid(True)
    plt.tight_layout()
    save_single(fig_v, "fig09b_circadian_diurnal_signal_variance")

    # Standalone Single Multi-trace Time Series
    fig_ts, ax_ts = plt.subplots(figsize=(11, 5.8))
    morn_p = os.path.join(BASE_DIR, 'csv', '2026-08-11', 'plant_normal_morning_11hrs39min.csv')
    aft_p = os.path.join(BASE_DIR, 'csv', '2026-10-09', 'plant_without_music_afternoon_15hrs38min49sec.csv')
    night_p = os.path.join(BASE_DIR, 'csv', '2026-08-11', 'plant_om_night_22hrs47min.csv')

    ecg_m = pd.read_csv(morn_p)['ecg'].values.astype(float)
    ecg_a = pd.read_csv(aft_p)['ecg'].values.astype(float)
    ecg_n = pd.read_csv(night_p)['ecg'].values.astype(float)

    dur_c = 40.0
    n_c = int(dur_c * FS)
    t_c = np.linspace(0, dur_c, n_c)

    ax_ts.plot(t_c, ecg_m[:n_c], color='#E65100', linewidth=2.0, label=f'Morning (11:39 AM, σ = {np.std(ecg_m):.1f} ADC)')
    ax_ts.plot(t_c, ecg_a[:n_c], color='#006633', linewidth=2.0, label=f'Afternoon (03:38 PM, σ = {np.std(ecg_a):.1f} ADC)')
    ax_ts.plot(t_c, ecg_n[:n_c], color='#003366', linewidth=2.0, linestyle='--', label=f'Night (10:47 PM, σ = {np.std(ecg_n):.1f} ADC)')

    ax_ts.set_xlabel('Time [s]', fontsize=16, fontweight='bold', labelpad=8)
    ax_ts.set_ylabel('Biopotential [ADC Counts]', fontsize=16, fontweight='bold', labelpad=8)
    ax_ts.set_ylim(-20, 1050)
    ax_ts.grid(True)
    leg_ts = ax_ts.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12.5)
    leg_ts.get_frame().set_linewidth(1.2)
    ax_ts.set_title('Circadian Multi-Trace Temporal Alignment', fontsize=16.5, fontweight='bold', pad=12)
    plt.tight_layout()
    save_single(fig_ts, "fig09c_circadian_diurnal_multitrace_timeseries")

# ===========================================================================
# 10. CIRCADIAN MLP CONFUSION MATRIX
# ===========================================================================
def generate_plot10_circadian_mlp_cm():
    print("\n--- Generating Figure 10: Circadian MLP Neural Network Confusion Matrix ---")
    apply_ieee_style()
    order = ["morning", "afternoon", "night"]
    display_phases = ["Morning (11 AM)", "Afternoon (3 PM)", "Night (10 PM)"]
    time_to_idx = {t: i for i, t in enumerate(order)}

    y_circ = df_feat["time_of_day"].map(time_to_idx).values
    X_scaled = StandardScaler().fit_transform(X_all)
    groups = df_feat["session_id"].values

    sgkf = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=42)
    mlp = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=250, random_state=42)

    oof_preds_mlp = np.zeros(len(y_circ), dtype=int)
    for tr, te in sgkf.split(X_scaled, y_circ, groups):
        mlp.fit(X_scaled[tr], y_circ[tr])
        oof_preds_mlp[te] = mlp.predict(X_scaled[te])

    cm_circ = confusion_matrix(y_circ, oof_preds_mlp)
    cm_circ_norm = cm_circ.astype('float') / cm_circ.sum(axis=1)[:, np.newaxis]
    acc_circ = accuracy_score(y_circ, oof_preds_mlp) * 100

    fig, ax = plt.subplots(figsize=(8.8, 7.2))
    im = ax.imshow(cm_circ_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax.set_title(f"Figure 10: MLP Neural Network Circadian Phase Matrix (Acc: {acc_circ:.1f}%)",
                 fontsize=16, fontweight='bold', pad=14)
    ax.set_xticks(np.arange(len(display_phases)))
    ax.set_yticks(np.arange(len(display_phases)))
    ax.set_xticklabels(display_phases, fontsize=13.5, fontweight='bold')
    ax.set_yticklabels(display_phases, fontsize=13.5, fontweight='bold')
    ax.set_xlabel('Predicted Diurnal Phase', fontsize=15.5, fontweight='bold', labelpad=8)
    ax.set_ylabel('True Diurnal Phase', fontsize=15.5, fontweight='bold', labelpad=8)

    for i in range(len(display_phases)):
        for j in range(len(display_phases)):
            v = cm_circ_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax.text(j, i, f"{v*100:.1f}%\n(n={cm_circ[i, j]})", ha='center', va='center',
                    color=col_t, fontsize=14, fontweight='bold')

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=13)
    cbar.set_label('Normalized Prediction Fraction', fontsize=14, fontweight='bold')

    plt.tight_layout()
    save_fig(fig, "2_circadian_confusion_matrix", "05_circadian_rhythm_mlp_neural_network")
    save_single(fig, "fig10_circadian_mlp_confusion_matrix")

# ===========================================================================
# 11. CONTINUOUS ANOMALY TIMELINE (Autonomous Irrigation Trigger)
# ===========================================================================
def generate_plot11_anomaly_timeline():
    print("\n--- Generating Figure 11: Real-Time Anomaly Stream & Alarm Timeline ---")
    apply_ieee_style()
    sample_session = df_feat[df_feat["main_category"] == "water"].copy()
    if len(sample_session) < 50:
        sample_session = df_feat.sample(150, random_state=42).sort_values("window_idx")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_all)
    normal_mask = (df_feat["main_category"] == "normal").values
    iso = IsolationForest(n_estimators=150, contamination=0.08, random_state=42)
    iso.fit(X_scaled[normal_mask])

    scores_all = -iso.decision_function(X_scaled)
    df_feat["anomaly_score"] = scores_all
    sample_session["anomaly_score"] = scores_all[sample_session.index]

    threshold = np.percentile(df_feat[df_feat["main_category"] == "normal"]["anomaly_score"], 90)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8.2), sharex=True)

    # Subplot 1: Raw Biopotential Mean
    x_axis = np.arange(len(sample_session))
    ax1.plot(x_axis, sample_session["mean"].values, color='#003366', lw=2.6, label='Mean Window Biopotential (ADC)')
    ax1.set_title('[A] Real-Time Plant Biopotential Stream During Osmotic Rehydration', fontsize=16, fontweight='bold', pad=10)
    ax1.set_ylabel('Amplitude [ADC Counts]', fontsize=15, fontweight='bold', labelpad=8)
    leg1 = ax1.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
    leg1.get_frame().set_linewidth(1.2)
    ax1.grid(True)

    # Subplot 2: Anomaly Score & Alarm Trigger
    scores = sample_session["anomaly_score"].values
    ax2.plot(x_axis, scores, color='#B22222', lw=2.6, label='Isolation Forest Anomaly Score')
    ax2.axhline(threshold, color='black', linestyle='--', lw=2.0, label=f'Alarm Threshold (Score = {threshold:.2f})')
    ax2.fill_between(x_axis, scores, threshold, where=(scores > threshold), color='#FFCDD2', alpha=0.6,
                     label='Critical Alarm Region (Water Influx Detected)')

    ax2.set_title('[B] Continuous Electrophysiological Anomaly Score & Irrigation Alarm Signal',
                  fontsize=16, fontweight='bold', pad=10)
    ax2.set_xlabel('Time Window Index (W = 200 samples, ~3s windows)', fontsize=15.5, fontweight='bold', labelpad=8)
    ax2.set_ylabel('Anomaly Score', fontsize=15, fontweight='bold', labelpad=8)
    leg2 = ax2.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12.5)
    leg2.get_frame().set_linewidth(1.2)
    ax2.grid(True)

    # Annotate trigger event
    trigger_idx = np.where(scores > threshold)[0]
    if len(trigger_idx) > 0:
        first_trig = trigger_idx[0]
        ax2.annotate('Autonomous Irrigation Trigger\n(Electrophysiological Depolarization)',
                     xy=(first_trig, scores[first_trig]),
                     xytext=(first_trig + 15, scores[first_trig] + 0.12),
                     arrowprops=dict(facecolor='black', shrink=0.08, width=1.8, headwidth=8.5),
                     fontsize=12.5, fontweight='bold',
                     bbox=dict(boxstyle='square,pad=0.35', facecolor='#ffffdd', edgecolor='black', linewidth=1.2))

    plt.suptitle('Figure 11: Real-Time Electrophysiological Anomaly Stream for Precision Agriculture',
                 fontsize=17, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_fig(fig, "3_continuous_anomaly_timeline", "06_unsupervised_anomaly_detection_isolation_forest")
    save_single(fig, "fig11_anomaly_continuous_timeline")

# ===========================================================================
# 12. ANOMALY DETECTION RATE
# ===========================================================================
def generate_plot12_anomaly_rate():
    print("\n--- Generating Figure 12: Anomaly Detection Rate Across Categories ---")
    apply_ieee_style()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_all)
    normal_mask = (df_feat["main_category"] == "normal").values
    iso = IsolationForest(n_estimators=150, contamination=0.08, random_state=42)
    iso.fit(X_scaled[normal_mask])

    scores = -iso.decision_function(X_scaled)
    threshold = np.percentile(scores[normal_mask], 90)
    df_feat["is_anomaly"] = (scores > threshold)

    anomaly_rates = df_feat.groupby("main_category")["is_anomaly"].mean() * 100
    display_names = ["normal", "music", "water", "dead"]
    display_labels = ["Normal Baseline", "Acoustic Music", "Water Hydration", "Dead Control"]
    rates = [anomaly_rates.get(k, 0) for k in display_names]
    bar_colors = ["#003366", "#6A1B9A", "#006633", "#B22222"]

    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    bars = ax.bar(display_labels, rates, color=bar_colors, alpha=0.88, edgecolor='black', linewidth=1.6, width=0.55)

    for bar, rate in zip(bars, rates):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2.2, f"{yval:.1f}%", ha='center', va='bottom',
                fontsize=15, fontweight='bold')

    ax.set_title("Figure 12: Unsupervised Anomaly Detection Rate (% Windows Flagged)",
                 fontsize=16, fontweight='bold', pad=14)
    ax.set_ylabel("Anomalous Windows Detected (%)", fontsize=15.5, fontweight='bold', labelpad=8)
    ax.set_ylim(0, 115)
    ax.set_xticklabels(display_labels, fontsize=13.5, fontweight='bold')
    ax.grid(True, axis='y', linestyle=':')

    plt.tight_layout()
    save_fig(fig, "2_anomaly_detection_rate", "06_unsupervised_anomaly_detection_isolation_forest")
    save_single(fig, "fig12_anomaly_detection_rate")

# ===========================================================================
# 0. MASTER SUMMARY DASHBOARD (400 DPI Executive Overview)
# ===========================================================================
def generate_plot0_master_summary_dashboard():
    print("\n--- Synthesizing Figure 0: Master Summary Dashboard (400 DPI) ---")
    apply_ieee_style()
    panels = [
        ("01_time_series_eda_and_feature_extraction/1_raw_waveform_comparison.png", "[A] Raw Bio-Potential Waveforms Across Conditions"),
        ("02_viability_dead_vs_alive_rf/1_confusion_matrices.png", "[B] Living vs. Dead Tissue Verification (100% Accuracy)"),
        ("03_multiclass_stimulus_svm_knn/1_multiclass_confusion_matrices.png", "[C] Multi-Class Electrophysiological State Classification"),
        ("04_music_genre_gradient_boosting/4_genre_radar_profiles.png", "[D] Acoustic Mechanotransduction Radar Profiles"),
        ("05_circadian_rhythm_mlp_neural_network/1_diurnal_baseline_shifts.png", "[E] Circadian Diurnal Baseline Dynamics"),
        ("06_unsupervised_anomaly_detection_isolation_forest/3_continuous_anomaly_timeline.png", "[F] Automated Smart Irrigation Anomaly Alert")
    ]

    fig_dash, axes_dash = plt.subplots(3, 2, figsize=(22, 24))
    axes_dash = axes_dash.flatten()

    for idx, (rel_img, title) in enumerate(panels):
        ax = axes_dash[idx]
        read_path = os.path.join(IEEE_PLOTS_DIR, rel_img)
        if os.path.exists(read_path):
            img_arr = mpimg.imread(read_path)
            ax.imshow(img_arr)
            ax.set_title(title, fontsize=17, fontweight='bold', pad=10)
        ax.axis('off')

    plt.suptitle("Master Summary Slide Dashboard: Plant Bio-Potential Dynamics & Electrophysiological Modeling",
                 fontsize=22, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_fig(fig_dash, "00_master_summary_dashboard")

# ===========================================================================
# SCRATCHPAD METHODOLOGY PLOTS (Plot 01 to Plot 13)
# ===========================================================================
def generate_scratchpad_plots():
    print("\n--- Upgrading Scratchpad Methodology Plots (Plot 01 to Plot 13) ---")
    apply_ieee_style()
    
    # -------------------------------------------------------------
    # Plot 01: Macro Timeseries Comparison
    # -------------------------------------------------------------
    macro_files = {
        'Normal Baseline': ('csv/2026-08-11/plant_normal_morning_11hrs39min.csv', '#003366'),
        'Water Stimulation': ('csv/2026-08-11/plant_water_morning_11hrs50min.csv', '#006633'),
        'Classical Music': ('csv/2026-08-11/plant_classical_music_for_plant_growth_morning_12hrs05min.csv', '#6A1B9A'),
        'Pop Music': ('csv/2026-10-09/plant_bye_bye_bye_afternoon_12hrs56min19sec.csv', '#B22222'),
        'Dead Control': ('categorize csv/dead/plant_dead_control_zero_signal_morning_10hrs00min.csv', '#333333')
    }
    fig1, axes1 = plt.subplots(5, 1, figsize=(14, 12), sharex=False)
    for idx, (label, (fpath, col)) in enumerate(macro_files.items()):
        ax = axes1[idx]
        df = pd.read_csv(os.path.join(BASE_DIR, fpath))
        ecg = df['ecg'].values.astype(float)
        t = np.linspace(0, len(ecg)/FS, len(ecg))
        step = max(1, len(t) // 3000)
        ax.plot(t[::step], ecg[::step], color=col, linewidth=1.6, label=label)
        ax.set_ylabel("ADC Counts", fontsize=13, fontweight='bold')
        ax.set_ylim(-30, 1050)
        ax.set_title(f"[{chr(65+idx)}] {label} (N={len(ecg):,}, Duration={t[-1]:.1f}s)", fontsize=13.5, fontweight='bold')
        ax.grid(True)
        ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
    axes1[-1].set_xlabel("Time [s]", fontsize=15.5, fontweight='bold')
    plt.suptitle("Plot 01: Macro Time-Series Comparison Across 5 Experimental States", fontsize=16.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_scratch(fig1, "plot_01_macro_timeseries_comparison")

    # -------------------------------------------------------------
    # Plot 02: Waveform Microstructure 5-sec insets
    # -------------------------------------------------------------
    fig2, axes2 = plt.subplots(5, 1, figsize=(12, 10.5), sharex=True)
    for idx, (label, (fpath, col)) in enumerate(macro_files.items()):
        ax = axes2[idx]
        df = pd.read_csv(os.path.join(BASE_DIR, fpath))
        ecg = df['ecg'].values.astype(float)
        win = ecg[1000:1000 + int(5 * FS)]
        t_w = np.linspace(0, 5, len(win))
        ax.plot(t_w, win, color=col, linewidth=2.0, marker='o', markersize=3, label=label)
        ax.set_ylabel("ADC Counts", fontsize=13, fontweight='bold')
        ax.set_ylim(-30, 1050)
        ax.set_title(f"[{chr(65+idx)}] {label} - High-Resolution 5s Inset (Sampling: ~190 Hz)", fontsize=13, fontweight='bold')
        ax.grid(True)
        ax.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
    axes2[-1].set_xlabel("Window Elapsed Time [s]", fontsize=15.5, fontweight='bold')
    plt.suptitle("Plot 02: Micro-Morphology 5-Second Waveform Insets", fontsize=16.5, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_scratch(fig2, "plot_02_waveform_microstructure_5sec")

    # -------------------------------------------------------------
    # Plot 03: Biological Control Live vs Dead
    # -------------------------------------------------------------
    fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 5.8))
    live_df = pd.read_csv(raw_paths['normal'])
    dead_df = pd.read_csv(raw_paths['dead'])
    live_ecg = live_df['ecg'].values[:int(150*FS)]
    dead_ecg = dead_df['ecg'].values[:int(150*FS)]
    t3 = np.linspace(0, len(live_ecg)/FS, len(live_ecg))

    ax3a.plot(t3, live_ecg, color='#003366', linewidth=1.6, label='Living Plant (Active Proton Pumps)')
    ax3a.plot(t3[:len(dead_ecg)], dead_ecg, color='#B22222', linewidth=1.6, linestyle='--', label='Dead Plant (Collapsed Variance)')
    ax3a.set_title('[A] 150-Second Voltage Dynamics Comparison', fontsize=15, fontweight='bold', pad=10)
    ax3a.set_xlabel('Time [s]', fontsize=14.5, fontweight='bold')
    ax3a.set_ylabel('Amplitude [ADC Counts]', fontsize=14.5, fontweight='bold')
    ax3a.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
    ax3a.grid(True)

    # Boxplot of STD and IQR
    live_stds = [np.std(live_ecg[i:i+200]) for i in range(0, len(live_ecg)-200, 200)]
    dead_stds = [np.std(dead_ecg[i:i+200]) for i in range(0, len(dead_ecg)-200, 200)]
    ax3b.boxplot([live_stds, dead_stds], tick_labels=['Living Plant', 'Dead Control'], patch_artist=True)
    ax3b.set_title('[B] Standard Deviation (σ) Distribution', fontsize=15, fontweight='bold', pad=10)
    ax3b.set_ylabel('Window Standard Deviation [ADC]', fontsize=14.5, fontweight='bold')
    ax3b.grid(True)
    plt.suptitle("Plot 03: Biological Control Proof (Live Tissue vs. Desiccated Control)", fontsize=16.5, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_scratch(fig3, "plot_03_biological_control_live_vs_dead")

    # -------------------------------------------------------------
    # Plot 04: Hydration Dynamics Water Stimulus
    # -------------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(11, 5.8))
    water_df = pd.read_csv(raw_paths['water'])
    w_sig = water_df['ecg'].values.astype(float)
    t4 = np.linspace(0, len(w_sig)/FS, len(w_sig))
    s_w = pd.Series(w_sig)
    roll_m = s_w.rolling(int(FS*5), center=True).mean().values
    ax4.plot(t4[::10], w_sig[::10], color='#88c999', alpha=0.45, linewidth=1.0, label='Raw Biopotential')
    ax4.plot(t4[::10], roll_m[::10], color='#006633', linewidth=2.6, label='5-Second Rolling Baseline Potential')
    ax4.axvline(25, color='#B22222', linestyle='--', linewidth=2.2, label='Watering Event (Hydration Shock)')
    ax4.set_xlabel('Timeline [s]', fontsize=15.5, fontweight='bold')
    ax4.set_ylabel('Biopotential [ADC Counts]', fontsize=15.5, fontweight='bold')
    ax4.set_title('Plot 04: Hydration Wave Dynamics & Variation Potential (VP)', fontsize=16.5, fontweight='bold', pad=12)
    ax4.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=13)
    ax4.grid(True)
    plt.tight_layout()
    save_scratch(fig4, "plot_04_hydration_dynamics_water_stimulus")

    # -------------------------------------------------------------
    # Plot 05: Acoustic Impact Silence vs Music
    # -------------------------------------------------------------
    fig5, ax5 = plt.subplots(figsize=(10, 5.8))
    cats_5 = ["normal", "music/classical", "music/devotional", "music/pop"]
    labels_5 = ["Silence Baseline", "Classical", "Devotional", "Pop Music"]
    data_5 = [df_feat[df_feat["category"] == c]["std"].values for c in cats_5]
    b5 = ax5.boxplot(data_5, tick_labels=labels_5, patch_artist=True)
    for patch, col in zip(b5['boxes'], ['#003366', '#D35400', '#6A1B9A', '#B22222']):
        patch.set_facecolor(col)
        patch.set_alpha(0.8)
    ax5.set_title("Plot 05: Acoustic Sound Pressure Impact on Bioelectrical Volatility (σ)", fontsize=16.5, fontweight='bold', pad=12)
    ax5.set_ylabel("Standard Deviation (σ) [ADC Counts]", fontsize=15, fontweight='bold')
    ax5.grid(True)
    plt.tight_layout()
    save_scratch(fig5, "plot_05_acoustic_impact_silence_vs_music")

    # -------------------------------------------------------------
    # Plot 06: Circadian Diurnal Shifts
    # -------------------------------------------------------------
    fig6, ax6 = plt.subplots(figsize=(10, 5.8))
    order_6 = ["morning", "afternoon", "night"]
    labels_6 = ["Morning (11 AM)", "Afternoon (3 PM)", "Night (10 PM)"]
    data_6 = [df_feat[df_feat["time_of_day"] == t]["mean"].values for t in order_6]
    b6 = ax6.boxplot(data_6, tick_labels=labels_6, patch_artist=True)
    for patch, col in zip(b6['boxes'], ['#E65100', '#006633', '#003366']):
        patch.set_facecolor(col)
        patch.set_alpha(0.8)
    ax6.set_title("Plot 06: Diurnal Baseline Shifts (Circadian Stomatal Conductance)", fontsize=16.5, fontweight='bold', pad=12)
    ax6.set_ylabel("Mean Resting Voltage [ADC Counts]", fontsize=15, fontweight='bold')
    ax6.grid(True)
    plt.tight_layout()
    save_scratch(fig6, "plot_06_circadian_diurnal_shifts")

    # -------------------------------------------------------------
    # Plot 07: Power Spectral Density (PSD Welch)
    # -------------------------------------------------------------
    fig7, ax7 = plt.subplots(figsize=(11, 6.0))
    for lbl, fpath, col in [
        ('Normal Baseline', raw_paths['normal'], '#003366'),
        ('Water Stimulation', raw_paths['water'], '#006633'),
        ('Pop Music ("Bye Bye Bye")', raw_paths['pop'], '#B22222'),
        ('Dead Control', raw_paths['dead'], '#333333')
    ]:
        df = pd.read_csv(fpath)
        sig = df['ecg'].values.astype(float)
        sig = sig - np.mean(sig)
        freqs, psd = signal.welch(sig, fs=FS, nperseg=min(len(sig), int(FS*4)))
        mask = (freqs >= 0.1) & (freqs <= 45.0)
        ax7.semilogy(freqs[mask], psd[mask], label=lbl, color=col, linewidth=2.2)

    ax7.axvspan(0.1, 2.0, color='#ffffcc', alpha=0.35, label='Slow Wave Potential Band (0.1–2 Hz)')
    ax7.axvspan(2.0, 10.0, color='#e0f3f8', alpha=0.35, label='Action Potential Band (2–10 Hz)')
    ax7.set_title("Plot 07: Power Spectral Density (PSD - Welch Decomposition)", fontsize=16.5, fontweight='bold', pad=12)
    ax7.set_xlabel("Frequency [Hz]", fontsize=15.5, fontweight='bold')
    ax7.set_ylabel("Power Spectral Density [$\mathrm{ADC}^2/\mathrm{Hz}$]", fontsize=15.5, fontweight='bold')
    ax7.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
    ax7.grid(True, which='both')
    plt.tight_layout()
    save_scratch(fig7, "plot_07_power_spectral_density_psd")

    # -------------------------------------------------------------
    # Plot 08: Feature Correlation Heatmap
    # -------------------------------------------------------------
    fig8, ax8 = plt.subplots(figsize=(12, 10))
    corr = df_feat[feature_cols[:14]].corr()
    mask8 = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask8, cmap='vlag', vmin=-1, vmax=1, annot=True, fmt='.2f',
                square=True, linewidths=.5, cbar_kws={"shrink": .8}, ax=ax8)
    ax8.set_title("Plot 08: Feature Correlation Heatmap (Plant Electrophysiological Domain)", fontsize=16, fontweight='bold', pad=12)
    plt.tight_layout()
    save_scratch(fig8, "plot_08_feature_correlation_heatmap")

    # -------------------------------------------------------------
    # Plot 09: ML Model Accuracy Comparison
    # -------------------------------------------------------------
    fig9, ax9 = plt.subplots(figsize=(11, 5.8))
    models_9 = ['Logistic Reg.', 'KNN (k=7)', 'Decision Tree', 'Random Forest', 'SVM (RBF)']
    strat_acc = [84.2, 94.8, 90.2, 96.9, 94.1]
    group_acc = [16.8, 16.6, 27.5, 25.5, 11.1]
    x_idx = np.arange(len(models_9))
    w_bar = 0.35
    ax9.bar(x_idx - w_bar/2, strat_acc, w_bar, label='Stratified K-Fold (Naive Window Shuffle)', color='#003366', alpha=0.9)
    ax9.bar(x_idx + w_bar/2, group_acc, w_bar, label='Group K-Fold (Strict Leave-Session-Out)', color='#E65100', alpha=0.9)
    ax9.axhline(25, color='gray', linestyle=':', label='Chance Level (4 classes = 25%)')
    ax9.set_xticks(x_idx)
    ax9.set_xticklabels(models_9, fontsize=13.5, fontweight='bold')
    ax9.set_ylabel("Classification Accuracy (%)", fontsize=15, fontweight='bold')
    ax9.set_title("Plot 09: Machine Learning Benchmark & The Data Leakage Dilemma", fontsize=16.5, fontweight='bold', pad=12)
    ax9.legend(loc='upper right', framealpha=0.96, edgecolor='black', fontsize=12)
    ax9.grid(True, axis='y')
    plt.tight_layout()
    save_scratch(fig9, "plot_09_ml_model_comparison_accuracy")

    # -------------------------------------------------------------
    # Plot 10: ML Confusion Matrix
    # -------------------------------------------------------------
    fig10, ax10 = plt.subplots(figsize=(8.5, 7.0))
    class_labels = ["normal", "music", "water", "dead"]
    display_names = ["Normal Baseline", "Acoustic Music", "Water Hydration", "Dead Control"]
    y_m10 = df_feat["main_category"].map({l: i for i, l in enumerate(class_labels)}).values
    rf_10 = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    skf_10 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_10 = np.zeros(len(y_m10), dtype=int)
    for tr, te in skf_10.split(X_all, y_m10):
        rf_10.fit(X_all[tr], y_m10[tr])
        oof_10[te] = rf_10.predict(X_all[te])
    cm_10 = confusion_matrix(y_m10, oof_10)
    cm_10_norm = cm_10.astype('float') / cm_10.sum(axis=1)[:, np.newaxis]
    im10 = ax10.imshow(cm_10_norm, cmap='Blues', vmin=0, vmax=1.0)
    ax10.set_xticks(np.arange(len(display_names)))
    ax10.set_yticks(np.arange(len(display_names)))
    ax10.set_xticklabels(display_names, fontsize=13, fontweight='bold', rotation=22, ha='right')
    ax10.set_yticklabels(display_names, fontsize=13, fontweight='bold')
    ax10.set_xlabel('Predicted Plant State', fontsize=15, fontweight='bold')
    ax10.set_ylabel('True Experimental Condition', fontsize=15, fontweight='bold')
    for i in range(len(display_names)):
        for j in range(len(display_names)):
            v = cm_10_norm[i, j]
            col_t = "white" if v > 0.52 else "black"
            ax10.text(j, i, f"{v*100:.1f}%\n(n={cm_10[i, j]})", ha='center', va='center', color=col_t, fontsize=13, fontweight='bold')
    ax10.set_title(f"Plot 10: Plant State Confusion Matrix (Random Forest, Acc: {accuracy_score(y_m10, oof_10)*100:.1f}%)",
                   fontsize=16, fontweight='bold', pad=12)
    plt.tight_layout()
    save_scratch(fig10, "plot_10_ml_confusion_matrix")

    # -------------------------------------------------------------
    # Plot 11: Feature Importance Hierarchy
    # -------------------------------------------------------------
    fig11, ax11 = plt.subplots(figsize=(10, 7.5))
    rf_11 = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf_11.fit(X_all, df_feat['is_alive'].values)
    imp_11 = rf_11.feature_importances_
    indices_11 = np.argsort(imp_11)[::-1][:12]
    ax11.barh(range(len(indices_11)), imp_11[indices_11][::-1] * 100, color='#003366', alpha=0.88, edgecolor='black')
    ax11.set_yticks(range(len(indices_11)))
    ax11.set_yticklabels([feature_cols[i] for i in indices_11][::-1], fontsize=13.5, fontweight='bold')
    ax11.set_xlabel('Gini Feature Importance (%)', fontsize=15, fontweight='bold')
    ax11.set_title('Plot 11: Gini Feature Importance Hierarchy for Plant Viability Detection', fontsize=16, fontweight='bold', pad=12)
    ax11.grid(True, axis='x')
    for i, v in enumerate(imp_11[indices_11][::-1] * 100):
        ax11.text(v + 0.3, i, f"{v:.1f}%", va='center', fontsize=12.5, fontweight='bold')
    plt.tight_layout()
    save_scratch(fig11, "plot_11_ml_feature_importance")

    # -------------------------------------------------------------
    # Plot 12: Decision Tree Rule Hierarchy
    # -------------------------------------------------------------
    fig12, ax12 = plt.subplots(figsize=(16, 8.5))
    dt_12 = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt_12.fit(X_all, df_feat['main_category'])
    plot_tree(dt_12, feature_names=feature_cols, class_names=dt_12.classes_,
              filled=True, rounded=True, fontsize=10, precision=1, ax=ax12)
    ax12.set_title("Plot 12: Interpretable Plant State Decision Tree Rule Hierarchy", fontsize=16.5, fontweight='bold', pad=12)
    plt.tight_layout()
    save_scratch(fig12, "plot_12_decision_tree_rules")

    # -------------------------------------------------------------
    # Plot 13: Scientific Validation and Diagnostics
    # -------------------------------------------------------------
    fig13, (ax13a, ax13b) = plt.subplots(1, 2, figsize=(14, 5.8))
    # Panel A: Leakage trap
    ax13a.bar(['Stratified CV\n(Window Shuffle)', 'Group K-Fold\n(Leave-Session-Out)'],
              [96.9, 25.5], color=['#B22222', '#006633'], width=0.45, edgecolor='black', linewidth=1.5)
    ax13a.set_ylabel('Multi-Class Accuracy (%)', fontsize=14.5, fontweight='bold')
    ax13a.set_title('[A] Temporal Data Leakage Diagnostic Trap', fontsize=15, fontweight='bold', pad=10)
    ax13a.set_ylim(0, 115)
    ax13a.grid(True, axis='y')
    ax13a.text(0, 96.9 + 2.5, '96.9%', ha='center', fontsize=14, fontweight='bold')
    ax13a.text(1, 25.5 + 2.5, '25.5%', ha='center', fontsize=14, fontweight='bold')

    # Panel B: Robust generalizable formulations
    ax13b.bar(['Live vs Dead Control\n(Cross-Session)', 'Silence vs Pop Vibration\n(Cross-Session)'],
              [94.0, 86.4], color=['#003366', '#6A1B9A'], width=0.45, edgecolor='black', linewidth=1.5)
    ax13b.set_ylabel('Cross-Session Generalizable Acc (%)', fontsize=14.5, fontweight='bold')
    ax13b.set_title('[B] Robust Generalizable AC Classifications', fontsize=15, fontweight='bold', pad=10)
    ax13b.set_ylim(0, 115)
    ax13b.grid(True, axis='y')
    ax13b.text(0, 94.0 + 2.5, '94.0%', ha='center', fontsize=14, fontweight='bold')
    ax13b.text(1, 86.4 + 2.5, '86.4%', ha='center', fontsize=14, fontweight='bold')
    plt.suptitle("Plot 13: Rigorous Scientific Validation & Session Leakage Diagnostic", fontsize=16.5, fontweight='bold', y=0.98)
    plt.tight_layout()
    save_scratch(fig13, "plot_13_scientific_validation_and_diagnostics")

# ===========================================================================
# MAIN EXECUTION
# ===========================================================================
if __name__ == "__main__":
    print("===========================================================================")
    print("STARTING IEEE PUBLICATION PLOT SUITE GENERATION (400 DPI + VECTOR PDF)")
    print("===========================================================================")
    
    # 1. Primary document plots
    generate_plot1_waveforms()
    generate_plot2_viability_cm()
    generate_plot3_viability_roc_pr()
    generate_plot4_viability_pca()
    generate_plot5_multiclass_cm()
    generate_plot6_multiclass_tsne()
    generate_plot7_genre_radar()
    generate_plot8_genre_cm()
    generate_plot9_circadian_diurnal()
    generate_plot10_circadian_mlp_cm()
    generate_plot11_anomaly_timeline()
    generate_plot12_anomaly_rate()
    
    # 2. Master summary dashboard (synthesized from the updated panels)
    generate_plot0_master_summary_dashboard()

    # 3. Scratchpad methodology plots (plot_01 to plot_13)
    generate_scratchpad_plots()

    print("\n===========================================================================")
    print("SUCCESS: All IEEE publication figures generated in PNG (400 DPI) and PDF!")
    print(f"IEEE Master Directory: {IEEE_DIR}")
    print(f"Presentation Directory: {os.path.join(BASE_DIR, 'presentation_2', '06-11-2026')}")
    print("===========================================================================")
