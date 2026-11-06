# Scratchpad Entry 01: Dataset Audit, Noise Elimination & Experimental Categorization

**Date**: 2026-11-06  
**Objective**: Systematically audit the raw CSV files recorded from the Arduino Uno + AD8232 ECG sensor, discard unusable/erroneous files, eliminate human/test artifacts, and categorize clean experimental sessions.

---

## 1. Initial State & Problem Formulation
- The repository contains 56 raw CSV files distributed across directories dated `2026-08-11` to `2026-10-09`.
- The measurement device is an **AD8232 analog front-end** (designed for biopotentials, primarily ECG) connected to an Arduino Uno's analog pin (A0, 10-bit ADC, $0 - 1023$ counts, corresponding to $0 - 5.0\text{ V}$, $\approx 4.887\text{ mV}$ per LSB).
- In human cardiography, the AD8232 uses internal bandpass filtering ($0.5\text{ Hz} - 40\text{ Hz}$) and detects ventricular depolarization (QRS peaks) to compute Heart Rate (BPM).
- **Fundamental Biological Fact**: Plants possess no myocardial tissue, cardiac pacemakers, or discrete circulatory pumps; plant electrophysiology relies on cell-to-cell proton/calcium flux, action potentials (APs), slow wave potentials (SWPs), and variation potentials (VPs). Consequently, the hardware's automated peak-detection algorithm yields $\text{BPM} = 0$ for almost all measurements, which is biologically accurate and expected. However, the raw biopotential ($0 - 1023$ ADC counts) fluctuates dynamically with cellular membrane impedance, trans-membrane ion gradients, mechanical perturbations, and hydration dynamics.

---

## 2. Filtering Criteria & Exclusion Rules
Per strict experimental guidelines, all testing runs, human calibrations, corrupted files, and arbitrary trials were systematically isolated and rejected:

1. **Empty / Aborted Recordings ($N < 100$ rows)**:
   - Several sessions terminated prematurely upon startup or recorded zero bytes (e.g., `plant_hwh_night`, `plant_iuhjlkk`, `plant_dead_morning_09hrs47min`, `plant_pencil_with_om`, `plant_without_attaching_electrode`).
   - *Action*: Excluded 10 empty files.

2. **Human Subjects / Calibration Recordings**:
   - `asim.csv`, `plant_human_morning_11hrs03min.csv`, `plant_sachin_morning_10hrs18min.csv`, `plant_tanishq_morning_10hrs21min.csv`, `plant_sujal_night_22hrs58min45sec.csv`.
   - *Action*: Excluded 5 human-calibrated / human-named files.

3. **Software Tests, Demos & Mock Simulations**:
   - `demo.csv`, `simulation.csv`, `2026-08-11_09-57-49.csv` (unlabelled), `plant_test_evening`, `plant_test2_evening`, `plant_test_afternoon`, `plant_tets_afternoon`.
   - *Action*: Excluded 6 synthetic/test files.

4. **Junk / Hardware Scratch / Unassigned Stimuli**:
   - `plant_na_night` (NA stimulus), `plant_pencil` (graphite test), `plant_sd_morning` (undefined), `plant_ii_morning`, `plant_iii_morning` (unlabeled trials).
   - *Action*: Excluded 9 non-experimental files.

---

## 3. Curated Experimental Dataset Summary
A total of **26 valid, high-fidelity plant experimental sessions** containing **1,275,952 continuous physiological samples** were retained. The effective sampling rate was verified at $\approx 187 - 195\text{ Hz}$ ($\Delta t \approx 5.1 - 5.3\text{ ms}$).

| Experimental Category | Session Count | Total Samples | Representative Conditions |
| :--- | :---: | :---: | :--- |
| **Normal Baseline (Control)** | 8 | 366,704 | Undisturbed morning & afternoon controls, silent baseline |
| **Water Stimulation (Hydration)** | 3 | 110,419 | Immediate and post-watering biopotential responses |
| **Acoustic: Meditative & Mantras** | 7 | 504,127 | Classical music for growth, Om mantra (night/afternoon), Hanuman Chalisa, Hare Krishna, Namami Shamisaan |
| **Acoustic: High Energy & Pop** | 5 | 269,226 | Fast percussive pop ("Bye Bye Bye"), energetic beat ("Yalgaar"), morning music |
| **Dead / Semi-Dead Plant (Control)** | 3 | 25,476 | Biologically inactive desiccated plant tissue (true negative control) |
| **Total** | **26** | **1,275,952** | High-density longitudinal plant electrophysiology dataset |

---

## 4. Next Methodological Step
Proceed to **Phase 2: Signal Preprocessing, Visual Time-Series Plotting & Exploratory Inspection**. We will generate time-series plots, zoomed waveform morphological comparisons, and frequency spectrograms to visually identify plant bioelectrical patterns under different environmental states.

