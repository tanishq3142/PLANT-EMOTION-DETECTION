# Scratchpad 03: Feature Engineering, Spectral Decomposition & Ablation Trials

**Date:** 06-11-2026  
**Investigator:** Lead Biophysics & Machine Learning Research Agent  
**Context:** College 7th Semester B.Tech Project Viva & Presentation Prep  

---

## 1. Feature Representation Space

A continuous physiological time-series window of length $W = 200$ samples:
$$X = [x_1, x_2, \dots, x_{200}], \quad x_i \in [0, 1023]$$
must be mapped into a compact, discriminative mathematical vector:
$$\vec{\phi}(X) \in \mathbb{R}^{21}$$

We formulated 4 distinct mathematical families of features:

### Family A: Central Tendency & Amplitude
1. **Mean ($\mu$):** $\mu = \frac{1}{W}\sum_{i=1}^{W} x_i$ (Captures slow DC baseline potential)
2. **Median:** Robust midpoint resisting single-sample impulse spikes.
3. **Minimum & Maximum:** Peak voltage boundaries.
4. **Range:** Peak-to-Peak voltage span: $R = x_{\max} - x_{\min}$.
5. **Percentiles ($P_{25}, P_{75}$):** First and third quartile boundaries.
6. **Interquartile Range ($IQR$):** $IQR = P_{75} - P_{25}$ (Non-parametric spread measure).

### Family B: Dispersion & Distribution Shape
7. **Standard Deviation ($\sigma$):** $\sigma = \sqrt{\frac{1}{W-1}\sum_{i=1}^{W}(x_i - \mu)^2}$ (Measure of electrical volatility).
8. **Variance ($\sigma^2$):** Square of standard deviation.
9. **Root Mean Square (RMS):** $\text{RMS} = \sqrt{\frac{1}{W}\sum_{i=1}^{W} x_i^2}$ (Overall signal power including DC component).
10. **Skewness ($S$):** Third standardized moment:
    $$S = \frac{\frac{1}{W}\sum_{i=1}^{W}(x_i - \mu)^3}{\sigma^3}$$
    Reflects directional asymmetry in ion channel depolarization vs. repolarization.
11. **Kurtosis ($K$):** Fourth standardized moment:
    $$K = \frac{\frac{1}{W}\sum_{i=1}^{W}(x_i - \mu)^4}{\sigma^4} - 3$$
    Indicates whether the signal is prone to sudden, outlier-like action potential bursts.

### Family C: Signal Kinematics & Transition Dynamics
12. **Mean Absolute Difference (MAD / Signal Velocity):**
    $$\text{MAD} = \frac{1}{W-1}\sum_{i=1}^{W-1} |x_{i+1} - x_i|$$
    Crucial feature measuring the instantaneous slew rate of ionic depolarization.
13. **Zero-Crossing Rate (ZCR):** Number of times the AC-coupled signal ($x_i - \mu$) crosses the zero axis.
14. **Local Peak Count:** Number of local maxima exceeding $\mu + 1.0\sigma$.

### Family D: Spectral & Frequency Energy (FFT)
Using the Discrete Fourier Transform (DFT):
$$X_k = \sum_{n=0}^{W-1} x_n e^{-j \frac{2\pi}{W} k n}$$
Power Spectral Density (PSD): $P_k = |X_k|^2$.
15. **Low-Frequency Band Power:** $\sum P_k$ for $f \in [0, 0.25 f_{\text{Nyq}}]$.
16. **Mid-Frequency Band Power:** $\sum P_k$ for $f \in [0.25, 0.50 f_{\text{Nyq}}]$.
17. **High-Frequency Band Power:** $\sum P_k$ for $f \in [0.50, 1.0 f_{\text{Nyq}}]$.
18. **Dominant Frequency Index:** $k^* = \arg\max_k P_k$.
19. **Spectral Entropy ($H_{\text{spec}}$):**
    $$p_k = \frac{P_k}{\sum P_j}, \quad H_{\text{spec}} = -\sum_{k} p_k \log_2(p_k)$$
    Quantifies the disorder / complexity of the acoustic or metabolic vibration.

---

## 2. Experimental Trials & Feature Ablation

### ❌ Trial A: Complex Continuous Wavelet Transform (CWT)
- **Attempt:** Tested Morlet wavelet scalograms for time-frequency multi-resolution analysis.
- **Outcome:** Computational bottleneck! Computing CWT on 1.7 million rows took over 25 minutes, generated high-dimensional image matrices, and caused severe overfitting in small validation sets.
- **Decision:** Abandoned CWT. Discrete Fourier Transform (FFT) spectral bands and Spectral Entropy achieved equivalent discriminative accuracy in 0.8 seconds.

### ⚠️ Multicollinearity Check
- A correlation analysis (`plot/01_time_series_eda_and_feature_extraction/4_feature_correlation_matrix.png`) revealed:
  - $\rho(\sigma, \sigma^2) = 0.98$ (Variance is an exact non-linear duplicate of Standard Deviation).
  - $\rho(\mu, \text{Median}) = 0.96$ during steady baseline, but drops to $0.74$ during sudden watering surges.
- **Decision:** Tree-based models (Random Forest, Gradient Boosting) are naturally invariant to monotonic feature collinearity. For linear models (SVM, KNN), feature normalization with `StandardScaler` was applied:
  $$z = \frac{x - \mu}{\sigma}$$

---

## 3. Results of Feature Extraction

The transformation produced `plant_time_series_features.csv`:
- **Dimensions:** 3,529 windows $\times 27$ columns (21 numeric features + metadata).
- **Target Variables:**
  - `is_alive`: Binary flag ($1 = \text{Living}, 0 = \text{Dead}$).
  - `main_category`: 4 classes (`normal`, `music`, `water`, `dead`).
  - `category`: 7 granular classes (`normal`, `devotional`, `pop`, `classical`, `general`, `water`, `dead`).
  - `time_of_day`: 3 circadian phases (`morning`, `afternoon`, `night`).

This feature matrix serves as the standardized foundation for all subsequent machine learning experiments.

