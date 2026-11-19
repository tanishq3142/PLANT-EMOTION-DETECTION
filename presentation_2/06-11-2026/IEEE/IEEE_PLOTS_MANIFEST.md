# IEEE Publication Figures: Plant Electrophysiology & Bio-Potential State Classification

**Publication Standard Applied:**
- **Typography:** Times New Roman (Serif), Bold, Scaled 14–18 pt (guaranteed 100% legibility when zoomed or printed in IEEE two-column papers).
- **Linewidths:** 2.0 – 2.8 pt with high-contrast color palette (Navy `#003366`, Crimson `#B22222`, Forest Green `#006633`, Purple `#6A1B9A`, Amber `#D35400`).
- **Spines & Ticks:** 1.6 pt solid black enclosing boundary, inward-facing ticks (`direction='in'`), ticks on all 4 borders.
- **Physical Units:** Fully qualified with brackets on all axes (`Time [s]`, `Amplitude [ADC Counts]`, `Potential [mV]`, `Frequency [Hz]`, `Power Density [$\text{ADC}^2/\text{Hz}$]`).
- **Formats Available:**
  - **PNG:** Rendered at **400 DPI** (Ultra-high resolution raster).
  - **PDF:** Camera-ready **Vector format** for IEEE LaTeX / Overleaf documents.

---

## 🗺️ Master Mapping: `06-11-2026.md` Figures to IEEE Assets

| `06-11-2026.md` Reference | Figure Type | IEEE Composite / Paired Path | Dedicated Standalone Single-Plot Path (For Single-Column Paper) |
| :--- | :--- | :--- | :--- |
| **Figure 0** (`plots/00_master_summary_dashboard.png`) | 6-Panel Executive Dashboard | `IEEE/plots/00_master_summary_dashboard.png` | *Composite Overview* |
| **Figure 1.1** (`plots/01_.../1_raw_waveform_comparison.png`) | Raw Waveforms Across Conditions | `IEEE/plots/01_time_series_eda_and_feature_extraction/1_raw_waveform_comparison.png` | `IEEE/single_plots/fig01a_waveform_normal_baseline.png`<br>`IEEE/single_plots/fig01b_waveform_water_depolarization.png`<br>`IEEE/single_plots/fig01c_waveform_acoustic_pop_music.png`<br>`IEEE/single_plots/fig01d_waveform_classical_devotional.png`<br>`IEEE/single_plots/fig01e_waveform_dead_control.png` |
| **Figure 1.2** (`plots/02_.../1_confusion_matrices.png`) | Viability Verification (Live vs Dead) | `IEEE/plots/02_viability_dead_vs_alive_rf/1_confusion_matrices.png` | `IEEE/single_plots/fig02a_viability_rf_confusion_matrix.png`<br>`IEEE/single_plots/fig02b_viability_hgb_confusion_matrix.png` |
| **Slide 4** (`plots/02_.../2_roc_pr_curves.png`) | Viability ROC & Precision-Recall Curves | `IEEE/plots/02_viability_dead_vs_alive_rf/2_roc_pr_curves.png` | `IEEE/single_plots/fig03a_viability_roc_curve.png`<br>`IEEE/single_plots/fig03b_viability_pr_curve.png` |
| **Figure 1.3** (`plots/02_.../4_pca_latent_space.png`) | 2D PCA Physiological Latent Space | `IEEE/plots/02_viability_dead_vs_alive_rf/4_pca_latent_space.png` | `IEEE/single_plots/fig04_viability_pca_latent_space.png` |
| **Figure 2.1** (`plots/03_.../1_multiclass_confusion_matrices.png`) | 4-Class Stimulus Matrix (SVM vs KNN) | `IEEE/plots/03_multiclass_stimulus_svm_knn/1_multiclass_confusion_matrices.png` | `IEEE/single_plots/fig05a_multiclass_svm_confusion_matrix.png`<br>`IEEE/single_plots/fig05b_multiclass_knn_confusion_matrix.png` |
| **Figure 2.2** (`plots/03_.../3_tsne_manifold_clusters.png`) | 2D t-SNE Non-Linear Manifold | `IEEE/plots/03_multiclass_stimulus_svm_knn/3_tsne_manifold_clusters.png` | `IEEE/single_plots/fig06_multiclass_tsne_manifold.png` |
| **Figure 3.1** (`plots/04_.../4_genre_radar_profiles.png`) | 6D Acoustic Mechanoreceptor Radar | `IEEE/plots/04_music_genre_gradient_boosting/4_genre_radar_profiles.png` | `IEEE/single_plots/fig07_acoustic_genre_radar_profile.png` |
| **Figure 3.2** (`plots/04_.../2_genre_confusion_matrix.png`) | Acoustic Music Genre GBDT Matrix | `IEEE/plots/04_music_genre_gradient_boosting/2_genre_confusion_matrix.png` | `IEEE/single_plots/fig08_acoustic_genre_confusion_matrix.png` |
| **Figure 4.1** (`plots/05_.../1_diurnal_baseline_shifts.png`) | Diurnal Baseline Dynamics (Stomata) | `IEEE/plots/05_circadian_rhythm_mlp_neural_network/1_diurnal_baseline_shifts.png` | `IEEE/single_plots/fig09a_circadian_diurnal_mean_potential.png`<br>`IEEE/single_plots/fig09b_circadian_diurnal_signal_variance.png`<br>`IEEE/single_plots/fig09c_circadian_diurnal_multitrace_timeseries.png` |
| **Figure 4.2** (`plots/05_.../2_circadian_confusion_matrix.png`) | Circadian Phase MLP Matrix | `IEEE/plots/05_circadian_rhythm_mlp_neural_network/2_circadian_confusion_matrix.png` | `IEEE/single_plots/fig10_circadian_mlp_confusion_matrix.png` |
| **Figure 5.1** (`plots/06_.../3_continuous_anomaly_timeline.png`) | Continuous Timeline & Irrigation Alarm | `IEEE/plots/06_unsupervised_anomaly_detection_isolation_forest/3_continuous_anomaly_timeline.png` | `IEEE/single_plots/fig11_anomaly_continuous_timeline.png` |
| **Figure 5.2** (`plots/06_.../2_anomaly_detection_rate.png`) | Autonomous Anomaly Detection Rates | `IEEE/plots/06_unsupervised_anomaly_detection_isolation_forest/2_anomaly_detection_rate.png` | `IEEE/single_plots/fig12_anomaly_detection_rate.png` |

---

## 🔬 Upgraded Scratchpad Methodology Plots (`IEEE/scratch_plots/`)

All 13 exploratory visual & experimental figures from `presentation_2/06-11-2026/scratch/` are also rendered with identical IEEE large-font typography:

1. `plot_01_macro_timeseries_comparison.png` & `.pdf`: Comprehensive 5-panel longitudinal trace.
2. `plot_02_waveform_microstructure_5sec.png` & `.pdf`: Millisecond-resolution 5-second zoomed insets.
3. `plot_03_biological_control_live_vs_dead.png` & `.pdf`: Proof of biological active pumping vs desiccated zero variance.
4. `plot_04_hydration_dynamics_water_stimulus.png` & `.pdf`: Hydraulic wave coupling and variation potential (VP).
5. `plot_05_acoustic_impact_silence_vs_music.png` & `.pdf`: Sound pressure dispersion boxplot.
6. `plot_06_circadian_diurnal_shifts.png` & `.pdf`: Diurnal baseline shift boxplot.
7. `plot_07_power_spectral_density_psd.png` & `.pdf`: Welch spectral density decomposition ($0.1 - 45\text{ Hz}$).
8. `plot_08_feature_correlation_heatmap.png` & `.pdf`: Feature cross-correlation matrix with values.
9. `plot_09_ml_model_comparison_accuracy.png` & `.pdf`: Stratified vs Group K-Fold cross-validation comparison.
10. `plot_10_ml_confusion_matrix.png` & `.pdf`: Multi-class Random Forest confusion matrix with sample counts.
11. `plot_11_ml_feature_importance.png` & `.pdf`: Top 12 Gini importance hierarchy.
12. `plot_12_decision_tree_rules.png` & `.pdf`: Interpretable decision tree flow hierarchy.
13. `plot_13_scientific_validation_and_diagnostics.png` & `.pdf`: Rigorous session leakage diagnostic and robust generalizable AC models.

---

## 📂 Directory Layout
- **Root IEEE Directory:** `c:\Users\asim\projects\others\PLANT-EMOTION-DETECTION\IEEE\`
- **Mirror Presentation IEEE Directory:** `c:\Users\asim\projects\others\PLANT-EMOTION-DETECTION\presentation_2\06-11-2026\IEEE\`
- **Direct Markdown Presentation Plots:** `c:\Users\asim\projects\others\PLANT-EMOTION-DETECTION\presentation_2\06-11-2026\plots\` (directly updated for `06-11-2026.md`)
