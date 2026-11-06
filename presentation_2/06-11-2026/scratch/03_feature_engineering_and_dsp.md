# Scratchpad Entry 03: Digital Signal Processing (DSP) & Feature Engineering

**Date**: 2026-11-06  
**Objective**: Transform raw 10-bit analog-to-digital converter (ADC) time-series voltages into physiologically meaningful, mathematically rigorous feature vectors using sliding window segmentation.

---

## 1. Windowing Strategy & Nyquist Constraints
- **Sampling Frequency ($f_s$)**: Verified at $\approx 190.0\text{ Hz}$ across recordings.
- **Nyquist Frequency ($f_{Nyquist}$)**: $f_s / 2 \approx 95.0\text{ Hz}$.
- **Hardware Analog Bandwidth**: The AD8232 front-end employs internal operational amplifier filtering, constraining useful bioelectrical signals to $0.5 - 40\text{ Hz}$. Above $50\text{ Hz}$, electrical powerline mains interference typically dominates.
- **Window Length ($W$)**: $5.0\text{ seconds}$ ($N = 950\text{ samples}$ per window). A 5-second window is biologically optimal: it is sufficiently long to resolve low-frequency slow-wave variations down to $0.2\text{ Hz}$ while maintaining localized stationarity for acoustic and hydration responses.
- **Step Size / Overlap ($S$)**: $50\%\text{ overlap}$ ($2.5\text{ seconds}$, $475\text{ samples}$) to preserve continuous boundary dynamics without loss of transient peaks.

---

## 2. Engineered Feature Taxonomy

### A. Amplitude & Central Tendency (Baselines & Polarization)
1. **Mean ADC ($\mu$)**: Baseline resting potential / DC shift ($V_{DC} = \mu \times \frac{5000\text{ mV}}{1023}$). Reflects whole-tissue electrochemical polarization.
2. **Median ADC**: Non-parametric central tendency, resistant to sudden motion spikes or single-sample ADC dropouts.

### B. Signal Dispersion & Electrical Turbulence
3. **Standard Deviation ($\sigma$) & Variance ($\sigma^2$)**: Total AC biopotential energy. Distinguishes live, active tissue from dead tissue or quiet baseline.
4. **Interquartile Range (IQR = $Q_3 - Q_1$)**: Robust measure of non-Gaussian signal spread.
5. **Peak-to-Peak Amplitude ($V_{p-p} = V_{max} - V_{min}$)**: Maximum dynamic voltage excursion within the 5-second window.
6. **Root Mean Square (RMS)**: Total root-mean-squared power of the waveform.

### C. Waveform Morphology & Higher-Order Moments
7. **Skewness ($\gamma_1$)**: Asymmetry of depolarization vs. repolarization phases.
8. **Kurtosis ($\gamma_2$)**: Peakedness / heaviness of distribution tails. Indicates whether biopotential changes are smooth continuous oscillations or sharp pulse bursts.
9. **Mean Absolute Difference (MAD = $\frac{1}{N-1}\sum |x_{i+1} - x_i|$)**: Average velocity of voltage transition ($|\Delta V / \Delta t|$). Captures high-frequency microphonic roughness.
10. **Zero-Crossing Rate (ZCR)**: Number of sign transitions of the zero-centered signal per window, capturing oscillation frequency.
11. **Peak Count ($N_{peaks}$)**: Number of prominent spikes exceeding $\mu + 1.5\sigma$ with minimum refractory distance of $100\text{ ms}$.

### D. Frequency Domain Spectral Features (Welch Power Spectral Density)
Welch's periodogram with Hann tapering ($N_{FFT} = 256$) decomposes the power spectrum:
12. **Low-Frequency Band Power ($P_{low}$: $0.1 - 2.0\text{ Hz}$)**: Corresponds to slow wave potentials (SWPs), hydraulic pressure wave coupling, and gradual baseline re-equilibration.
13. **Mid-Frequency Band Power ($P_{mid}$: $2.0 - 10.0\text{ Hz}$)**: Intermediate biological rhythmic action potentials.
14. **High-Frequency Band Power ($P_{high}$: $10.0 - 45.0\text{ Hz}$)**: Rapid transients, acoustic mechanical vibrations, and leaf mechanotransduction.
15. **High-to-Low Power Ratio ($P_{ratio} = P_{high} / P_{low}$)**: Spectral tilt indicator. Distinguishes high-vibration pop music from low-frequency meditative mantras or baseline drift.
16. **Spectral Centroid**: Power-weighted average frequency ($\bar{f} = \frac{\sum f \cdot S(f)}{\sum S(f)}$).
17. **Spectral Entropy ($H_{spectral}$)**: Shannon entropy of the normalized power spectrum. High entropy indicates broad-band white noise / chaotic vibration; low entropy indicates discrete harmonic resonance.

---

## 3. Machine Learning Dataset Assembly
The resulting feature dataset `presentation/06-11-2026/scratch/plant_features_extracted.csv` compiles thousands of feature vectors labeled by:
- Experimental Condition Category (5 classes)
- Sub-label (Mantra, Pop, Water, Normal, Dead, etc.)
- Session ID / File source (enabling session-grouped cross-validation).

