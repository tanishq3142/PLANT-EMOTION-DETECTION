# Plant Electrophysiology — Signal Overview

## What Signals Are We Storing?

Each CSV recording captures three columns per sample:

| Column      | Description                                                         | Unit / Format               |
|-------------|---------------------------------------------------------------------|-----------------------------|
| `timestamp` | The exact date and time the sample was taken                        | `YYYY-MM-DD HH:MM:SS.mmm`  |
| `ecg`       | Raw electrical signal read from the plant via the AD8232 sensor     | 0 – 1023 (10-bit ADC value) |
| `bpm`       | Beats-per-minute derived from peak-to-peak intervals in the signal  | Integer                     |

In addition, the **filename** itself encodes important metadata:

```
plant_<stimulus>_<time_of_day>_<HH>hrs<MM>min.csv
```

- **stimulus** — what external factor was applied (e.g. water, music, touch, poison).
- **time_of_day** — morning, afternoon, or night (auto-detected from system clock).
- **recording time** — hour and minute when the session started.

---

## Why Is Each Signal Important?

### 1. Timestamp

Precise timestamps let us:

- **Reconstruct the exact timeline** of a recording session.
- **Calculate real sample rates** — the interval between consecutive timestamps reveals how fast the Arduino was actually sampling.
- **Align multiple recordings** taken on the same day or across days, so we can compare how a plant responded at different times.

### 2. ECG (Raw Electrical Signal)

Plants generate measurable electrical signals called **action potentials** and **variation potentials**. These signals are analogous (though not identical) to animal ECG signals. Storing the raw ADC value is important because:

- **It captures the plant's electrical response** to stimuli in real time. Wounding, watering, touch, light changes, sound vibrations, and chemical exposure all produce distinct electrical patterns.
- **Raw data preserves full fidelity.** Post-processing (filtering, FFT, wavelet analysis) can always be applied later, but if we only stored derived metrics we would lose the ability to re-analyse with better algorithms in the future.
- **Pattern recognition and machine learning** models need large amounts of raw waveform data to learn the difference between, for example, a "happy" watered plant and a "stressed" plant exposed to a toxin.

### 3. BPM (Beats Per Minute)

The BPM value estimates how frequently the plant's electrical signal crosses a dynamic threshold — essentially how often the plant "pulses." This matters because:

- **Rhythmic activity varies with plant health.** A steady, consistent rhythm often correlates with a plant in homeostasis, while erratic or accelerated rhythms can indicate stress.
- **It provides a quick summary metric.** While the raw ECG is rich, BPM gives an at-a-glance indicator that is easy to plot, compare, and discuss.
- **It enables cross-session comparison.** Comparing average BPM across different stimuli or times of day reveals broad trends without needing to inspect every waveform sample.

---

## Why Store Stimulus and Time-of-Day?

### Stimulus

Different stimuli trigger different electrical responses in plants:

| Stimulus  | Expected Response                                                        |
|-----------|--------------------------------------------------------------------------|
| Water     | Gradual change as turgor pressure shifts and ion channels activate        |
| Music     | Subtle rhythmic modulation; some studies suggest frequency-dependent effects |
| Touch     | Rapid action potentials (especially in sensitive species)                 |
| Poison    | Prolonged variation potentials as the plant mounts a stress response      |

By labelling each recording with its stimulus, the dataset becomes a **supervised dataset** — we know both the input (stimulus) and the output (electrical signal), which is exactly what we need to train classifiers.

### Time of Day

Plants have **circadian rhythms** that influence their electrical activity:

- **Morning** — photosynthesis ramps up, stomata open, ion transport increases.
- **Afternoon** — peak metabolic activity; electrical baselines may be higher.
- **Night** — reduced metabolic rate; signals tend to be quieter and more regular.

Recording the time of day ensures we can **control for circadian effects** when comparing stimuli. A stress response measured at night might look very different from the same stress response measured at midday.

---

## Summary

By storing **timestamp**, **raw ECG**, and **BPM** — together with **stimulus** and **time-of-day** metadata — we build a rich, labelled dataset that supports:

1. **Exploratory analysis** — visualise how plants respond to different inputs.
2. **Statistical comparison** — test whether specific stimuli produce significantly different signals.
3. **Machine learning** — train models to classify plant "emotions" (stress, comfort, stimulation) from electrical waveforms.
4. **Reproducibility** — every recording carries enough context to be understood and reused months or years later.
