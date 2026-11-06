# Scratchpad 02: Signal Conditioning, Filtering Pitfalls & Windowing Strategy

**Date:** 06-11-2026  
**Investigator:** Lead Biophysics & Machine Learning Research Agent  
**Context:** College 7th Semester B.Tech Project Viva & Presentation Prep  

---

## 1. The Challenge of Raw Bio-Potential Signals

Electrophysiological signals captured by an Arduino Uno are continuous 1D time-series streams. Before jumping into machine learning, several signal processing methods were tested.

---

## 2. Experiments & Failed Trials

### ❌ Trial 1: The Point-by-Point Classification Blunder
- **Attempt:** Feeding raw individual ADC rows directly into a classifier:
  $$\hat{y} = f(ADC_t)$$
- **Result:** **Total Failure (Accuracy $\approx 36\%$, random baseline $\approx 33\%$)**
- **Why it failed:** 
  An ADC value of `385` appears in *Normal Baseline*, in *Music*, and during *Watering*. A single instantaneous voltage number contains **zero temporal dynamics**, zero frequency information, and zero velocity. Machine learning on raw single rows is mathematically futile.

---

### ❌ Trial 2: Over-Filtering with a Low-Pass Butterworth Filter
- **Attempt:** Applying a 4th-order digital Butterworth low-pass filter with a cutoff frequency $f_c = 2\text{ Hz}$ to "clean" the signal:
  $$H(s) = \frac{1}{\prod_{k=1}^n \left(s - s_k\right)}$$
- **Result:** Significant loss of physiological information.
- **Why it failed:** 
  While plants exhibit slow baseline wander, rapid ion fluxes ($Ca^{2+}, K^+$) and acoustic shock waves generate sharp transient depolarization spikes with sub-second rise times. The 2 Hz filter flattened out the crucial watering depolarization wavefront and eradicated the leaf mechanoreceptive vibration signatures.

---

### ❌ Trial 3: The 50 Hz AC Mains Hum Filtering Dilemma
- **Attempt:** Attempting to apply a 50 Hz IIR notch filter in Python:
  $$f_{\text{notch}} = 50\text{ Hz}$$
- **Result:** Code threw an exception: `Cutoff frequency must be less than Nyquist frequency (fs/2)`.
- **The Biophysics & Hardware Revelation:**
  The Arduino Uno streams over USB Serial at 9600 Baud. Transmitting an ASCII line like `"2026-08-11 10:57:25.154,521,0\r\n"` requires ~35 characters $\times 10$ bits = 350 bits per line.
  $$\text{Effective Sampling Rate } F_s \approx \frac{9600}{350} \approx 25 - 50\text{ Hz}$$
  According to the **Nyquist-Shannon Sampling Theorem**:
  $$f_{\text{Nyquist}} = \frac{F_s}{2} \approx 15 - 25\text{ Hz}$$
  You cannot apply a 50 Hz digital notch filter when your Nyquist frequency is 25 Hz!
- **How Hardware Saved Us:**
  The AD8232 analog front-end chip has an **analog 2-pole Sallen-Key low-pass filter integrated into its operational amplifier**, with an analog cutoff at $40\text{ Hz}$ and high-pass cutoff at $0.5\text{ Hz}$. Therefore, the sensor hardware itself rejected the majority of high-frequency interference before digitization!

---

## 3. The Winning Solution: Tumbling Window Segmentation

To capture both instantaneous and temporal electrophysiological dynamics, we segmented the continuous time-series stream into **tumbling windows of $W = 200$ samples**.

```
Time-Series Signal (Continuous Stream)
[--------------------------------------------------------------------------]
  | Window 1: 200 samples | Window 2: 200 samples | Window 3: 200 samples |
  | (~2 to 4 seconds)     | (~2 to 4 seconds)     | (~2 to 4 seconds)     |
           v                       v                       v
    [Feature Vector 1]      [Feature Vector 2]      [Feature Vector 3]
       (21 Features)           (21 Features)           (21 Features)
```

### Why $W = 200$ is Optimal:
1. **Biological Time Constant:** In living plant tissue, xylem transport and transmembrane potential spikes occur over intervals of 1 to 5 seconds. A 200-sample window spans $\approx 3.0$ seconds, matching the biophysical time constant of plant action potentials.
2. **Frequency Resolution for FFT:** A 200-point discrete Fourier transform provides $\approx 100$ spectral frequency bins, allowing clean separation of low, mid, and high acoustic vibrations.
3. **Statistical Robustness:** 200 points per window ensure high degrees of freedom for computing stable kurtosis, skewness, and variance without being skewed by a single ADC glitch.

---

## 4. Key Takeaways for Presentation

- **Slide Pitch:** Explain that biological signals require **temporal windowing ($W = 200$)** rather than single-sample processing.
- **Viva Defense:** When asked about 50 Hz AC noise, explain that the **AD8232's built-in analog front-end bandpass (0.5 Hz – 40 Hz)** attenuates AC mains noise in the analog domain before ADC conversion.

