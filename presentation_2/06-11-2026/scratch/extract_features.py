import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import pandas as pd
import numpy as np
from scipy import signal, stats
import warnings
warnings.filterwarnings('ignore')

# Use trapezoid from scipy.integrate or np.trapezoid
try:
    from scipy.integrate import trapezoid as trapz_func
except ImportError:
    try:
        trapz_func = np.trapezoid
    except AttributeError:
        trapz_func = np.trapz

# Load curated file list
stats_df = pd.read_csv("presentation/06-11-2026/scratch/file_level_statistics.csv")

WINDOW_SEC = 5.0  # 5-second analysis windows
FS = 190.0        # ~190 Hz effective sampling rate
WINDOW_SIZE = int(WINDOW_SEC * FS)  # 950 samples
STEP_SIZE = int(WINDOW_SIZE * 0.5)  # 50% overlap for continuous feature extraction

features_list = []

print(f"Extracting 5-second window features (Window size: {WINDOW_SIZE} samples, Step: {STEP_SIZE} samples)...")

for idx, row in stats_df.iterrows():
    fpath = row['filepath']
    cat = row['category']
    sub = row['sub_label']
    fname = row['filename']
    
    try:
        df = pd.read_csv(fpath)
        ecg = df['ecg'].dropna().values.astype(float)
        
        n_samples = len(ecg)
        if n_samples < WINDOW_SIZE:
            continue
            
        n_windows = (n_samples - WINDOW_SIZE) // STEP_SIZE + 1
        
        for w_idx in range(n_windows):
            start = w_idx * STEP_SIZE
            end = start + WINDOW_SIZE
            win = ecg[start:end]
            
            # Time domain features
            mean_v = np.mean(win)
            std_v = np.std(win)
            var_v = np.var(win)
            min_v = np.min(win)
            max_v = np.max(win)
            p2p_v = max_v - min_v
            median_v = np.median(win)
            p25 = np.percentile(win, 25)
            p75 = np.percentile(win, 75)
            iqr_v = p75 - p25
            rms_v = np.sqrt(np.mean(win**2))
            skew_v = stats.skew(win)
            kurt_v = stats.kurtosis(win)
            
            # Differences
            diffs = np.diff(win)
            mad_v = np.mean(np.abs(diffs))
            
            # Zero-crossings of centered signal
            centered = win - mean_v
            zc_v = np.sum((centered[:-1] * centered[1:]) < 0)
            
            # Prominent peaks exceeding mean + 1.5*std
            peak_thresh = mean_v + 1.5 * std_v
            peaks, _ = signal.find_peaks(win, height=peak_thresh, distance=int(FS * 0.1))
            peak_count = len(peaks)
            
            # Frequency domain features via Welch PSD
            nperseg = min(len(centered), 256)
            freqs, psd = signal.welch(centered, fs=FS, window='hann', nperseg=nperseg)
            
            # Band powers
            low_mask = (freqs >= 0.1) & (freqs < 2.0)
            mid_mask = (freqs >= 2.0) & (freqs < 10.0)
            high_mask = (freqs >= 10.0) & (freqs <= 45.0)
            
            low_pow = trapz_func(psd[low_mask], freqs[low_mask]) if np.any(low_mask) else 0.0
            mid_pow = trapz_func(psd[mid_mask], freqs[mid_mask]) if np.any(mid_mask) else 0.0
            high_pow = trapz_func(psd[high_mask], freqs[high_mask]) if np.any(high_mask) else 0.0
            total_pow = low_pow + mid_pow + high_pow + 1e-12
            
            spectral_centroid = np.sum(freqs * psd) / (np.sum(psd) + 1e-12)
            
            # Spectral entropy
            psd_norm = psd / (np.sum(psd) + 1e-12)
            psd_norm = psd_norm[psd_norm > 0]
            spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm)) if len(psd_norm) > 0 else 0.0

            features_list.append({
                'session_file': fname,
                'category': cat,
                'sub_label': sub,
                'is_live': 0 if 'Dead' in cat else 1,
                'window_index': w_idx,
                'mean_adc': round(mean_v, 2),
                'std_adc': round(std_v, 2),
                'var_adc': round(var_v, 2),
                'min_adc': int(min_v),
                'max_adc': int(max_v),
                'peak_to_peak': round(p2p_v, 2),
                'median_adc': round(median_v, 2),
                'iqr_adc': round(iqr_v, 2),
                'rms_adc': round(rms_v, 2),
                'skewness': round(float(skew_v), 3),
                'kurtosis': round(float(kurt_v), 3),
                'mean_abs_diff': round(mad_v, 3),
                'zero_crossings': int(zc_v),
                'peak_count': int(peak_count),
                'power_low_freq': round(float(low_pow), 2),
                'power_mid_freq': round(float(mid_pow), 2),
                'power_high_freq': round(float(high_pow), 2),
                'power_ratio_high_low': round(float(high_pow / (low_pow + 1e-6)), 4),
                'spectral_centroid': round(float(spectral_centroid), 2),
                'spectral_entropy': round(float(spectral_entropy), 3)
            })
    except Exception as e:
        print(f"Error processing {fname}: {e}")

feat_df = pd.DataFrame(features_list)
feat_df.to_csv("presentation/06-11-2026/scratch/plant_features_extracted.csv", index=False)

print(f"\nSuccessfully extracted {len(feat_df):,} feature windows!")
print("\nFeature windows per category:")
print(feat_df['category'].value_counts())
