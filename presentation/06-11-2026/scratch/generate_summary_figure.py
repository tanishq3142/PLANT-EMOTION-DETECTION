import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# Set backend
plt.style.use('default')
fig = plt.figure(figsize=(18, 11), facecolor='#0B0F19')
fig.suptitle('PLANT BIO-POTENTIAL ANALYSIS & STATE CLASSIFICATION SYSTEM\n'
             'Hardware: Arduino Uno + AD8232 Bio-Potential Front-End | Subject: Epipremnum aureum (Pothos)',
             fontsize=16, fontweight='bold', color='#FFFFFF', y=0.98)

# Paths to the 6 core plots
plot_paths = [
    ("plots/01_time_series_eda_and_feature_extraction/1_raw_waveform_comparison.png", 
     "(A) Raw Bio-Potential Waveforms Under Distinct Stimuli"),
    ("plots/02_viability_dead_vs_alive_rf/1_confusion_matrices.png", 
     "(B) Biological Viability Verification: Living vs Dead Control (100% ROC-AUC)"),
    ("plots/03_multiclass_stimulus_svm_knn/1_multiclass_confusion_matrices.png", 
     "(C) 4-Class Stimulus Classification: SVM vs KNN (94% - 95% Accuracy)"),
    ("plots/04_music_genre_gradient_boosting/4_genre_radar_profiles.png", 
     "(D) Acoustic Vibration Profiling: Leaf Mechanoreceptor Response"),
    ("plots/05_circadian_rhythm_mlp_neural_network/1_diurnal_baseline_shifts.png", 
     "(E) Circadian Rhythm: Diurnal Baseline Shifts (Morning / Afternoon / Night)"),
    ("plots/06_unsupervised_anomaly_detection_isolation_forest/3_continuous_anomaly_timeline.png", 
     "(F) Real-World Deployment: Unsupervised Smart Irrigation Trigger")
]

# We will create a 2x3 grid
for idx, (path, title) in enumerate(plot_paths):
    full_path = os.path.join("presentation/06-11-2026", path)
    ax = fig.add_subplot(2, 3, idx + 1)
    if os.path.exists(full_path):
        img = mpimg.imread(full_path)
        ax.imshow(img)
        ax.set_title(title, fontsize=11, fontweight='bold', color='#38BDF8', pad=10)
    else:
        ax.text(0.5, 0.5, f"Image not found:\n{full_path}", color='white', ha='center', va='center')
    ax.axis('off')

plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.94])
output_path = "presentation/06-11-2026/plots/00_master_summary_dashboard.png"
plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Master summary dashboard generated at: {output_path}")

