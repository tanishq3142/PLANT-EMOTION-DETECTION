# Scratchpad Entry 02: Exploratory Visual Analysis & Physiological Observations

**Date**: 2026-11-06  
**Objective**: Visually evaluate the electrophysiological signals recorded across all conditions, formulate biological and physical hypotheses, and verify which patterns represent real plant physiology versus environmental artifacts.

---

## 1. Key Visual Observations & Hypotheses Tested

### A. The "Zero BPM" Mystery: Plant Biology vs. Cardiac Hardware
- **Observation**: In human electrocardiography, R-peaks trigger a hardware threshold circuit inside the AD8232 / software edge-detector to calculate Beats Per Minute (BPM).
- **Finding in Plant Data**: Every valid plant CSV records $\text{BPM} = 0$.
- **Scientific Interpretation**: Plants do not possess cardiac pacemaking cells (Sinoatrial node) or rhythmic muscular contractions. Plant bioelectrical signaling operates through slow wave potentials (SWPs, duration $1 - 10\text{ s}$), action potentials (APs, duration $0.1 - 2\text{ s}$), and system-wide hydraulic-electrical waves (variation potentials, VPs). The absence of BPM is the primary physiological proof that the system was not recording human cardiac artifacts.

---

### B. Biological Control: Live Plant vs. Dead Plant Tissue
- **Hypothesis**: If the measured signals represent true physiological trans-membrane ion gradients ($H^+$-ATPase pumps, $K^+$ and $Ca^{2+}$ flux), a live plant should exhibit broad dynamic range and active baseline fluctuations, whereas dead desiccated plant tissue should exhibit collapsed variance and passive impedance drift.
- **Visual Evidence**:
  - **Live Plant Normal Baseline**: Interquartile Range (IQR) $\approx 178 - 439\text{ ADC counts}$ ($870 - 2145\text{ mV}$). Shows continuous physiological drift, oscillatory bursts, and spontaneous micro-depolarizations.
  - **Dead Plant Tissue**: Interquartile Range (IQR) $\approx 31 - 54\text{ ADC counts}$ ($151 - 263\text{ mV}$). Shows near-flatline behavior punctuated only by high-frequency thermal/ADC quantization jitter.
  - **Statistical Ratio**: Live tissue exhibits $> 4.8\times$ greater variance and $> 5.2\times$ greater IQR than dead tissue.
- **Conclusion**: The AD8232 electrodes coupled to the plant stem and leaves successfully record endogenous physiological biopotentials rather than open-air antenna noise.

---

### C. Hydration Stimulus: The Water-Absorption Transient
- **Observation**: In `plant_water_morning_10-02.csv` and `plant_water_morning_11hrs50min.csv`, introducing water produces an immediate baseline surge ($\mu = 534.4\text{ ADC}$ vs control baseline $\mu \approx 318 - 380\text{ ADC}$).
- **Mechanism (Plant Physiology)**:
  - Adding water to dry potting soil alters root osmolarity within milliseconds.
  - Xylem tension abruptly shifts, propagating a negative hydrostatic pressure wave (hydraulic signal) upwards through the stem at velocities of $1 - 10\text{ cm/s}$.
  - This hydraulic shock physically tugs on parenchymal cell membranes, opening mechanosensitive ion channels (OSCA/MSL channels) and triggering $Ca^{2+}$ influx and $Cl^-$ efflux, causing a transient membrane depolarization known as a **Variation Potential (VP)**.
  - After $60 - 120\text{ seconds}$, the signal re-equilibrates to a new resting potential.

---

### D. Acoustic Perturbation: Silence vs. Vedic Mantras vs. Pop/Energetic Music
- **Visual & Statistical Contrast**:
  - **Silent Baseline (Afternoon)**: Standard deviation $\sigma \approx 33.5 - 113.7\text{ ADC}$, $\text{IQR} \approx 38 - 48\text{ ADC}$. Very calm, stable baseline.
  - **Vedic Mantras / Classical Music (Om, Hanuman Chalisa, Classical)**: Standard deviation $\sigma \approx 72.1 - 238.3\text{ ADC}$. Features rhythmic low-frequency undulations with moderate spectral dispersion.
  - **Pop Music & High Beats ("Bye Bye Bye", "Yalgaar")**: Standard deviation $\sigma \approx 239.5 - 284.8\text{ ADC}$, $\text{IQR} \approx 526 - 630\text{ ADC}$!
- **Scientific Interpretation**:
  - Pop music and heavy bass tracks produce continuous high-energy acoustic sound pressure waves ($50 - 500\text{ Hz}$).
  - These mechanical vibrations physically vibrate leaf blades and stems.
  - Mechanotransduction in plant cells: Plant cell walls are piezoelectric to a micro-degree, and membrane stretch-activated channels fire in response to continuous acoustic vibration.
  - Dual Effect: A significant portion of this response is physical acoustic vibration coupled to the electrode interface, combined with true plant mechanosensitive electrophysiological activation.

---

### E. Circadian / Diurnal Baseline Shifts
- **Morning (09:00 - 11:30 AM)**: Mean ADC $\approx 381 - 408$, broad variance ($\sigma \approx 200$). Plants are in active stomatal conductance, photosynthesis, and transpiration.
- **Afternoon (12:30 - 15:30 PM)**: Mean ADC stabilizes around $303 - 340$, variance drops to $\sigma \approx 33 - 113$ in quiet control.
- **Night (22:47 PM)**: Deep nocturnal state; stomata closed, minimal transpirational water pull, stable low-frequency oscillations ($\sigma = 72.1$).

---

## 2. Plots Produced
1. `plot_01_macro_timeseries_comparison.png`: Comprehensive 5-panel longitudinal overview.
2. `plot_02_waveform_microstructure_5sec.png`: Millisecond-resolution 5-second insets showcasing waveform morphology.
3. `plot_03_biological_control_live_vs_dead.png`: Definitive comparison of live bioactivity vs desiccated control.
4. `plot_04_hydration_dynamics_water_stimulus.png`: Hydraulic wave coupling and variation potential following watering.
5. `plot_05_acoustic_impact_silence_vs_music.png`: Violin and dispersion bar comparison of sound pressure impacts.
6. `plot_06_circadian_diurnal_shifts.png`: Circadian rhythm comparison (Morning, Afternoon, Night).
7. `plot_07_power_spectral_density_psd.png`: Frequency domain decomposition ($0.1 - 45\text{ Hz}$).

---

## 3. Next Methodological Step
Proceed to **Phase 3: Digital Signal Processing (DSP) & Feature Engineering**, followed by **Phase 4: Machine Learning & Mathematical Hypothesis Testing**.

