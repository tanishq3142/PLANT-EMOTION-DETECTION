# Scratchpad 07: Experiment 4 – Circadian Rhythm & Diurnal Baseline Progression

**Date:** 06-11-2026  
**Investigator:** Lead Biophysics & Machine Learning Research Agent  
**Context:** College 7th Semester B.Tech Project Viva & Presentation Prep  

---

## 1. Botanical Biophysics: The Circadian Transpiration Engine

Living plants do not maintain a static, frozen electrical baseline. They undergo continuous diurnal rhythmic fluctuations driven by the planetary light-dark cycle:

1. **Morning ($05:00 - 12:00$):** As photosynthetic active radiation (PAR) increases, guard cell $H^+$-ATPases activate, pumping protons out to drive $K^+$ influx, opening stomata. Transpiration begins, establishing a moderate xylem sap velocity.
   - **Baseline Voltage:** Centered at $ADC \approx 360 - 390$.
2. **Afternoon ($12:00 - 17:00$):** Ambient solar radiation and ambient temperature peak. Transpirational pull generates high negative hydrostatic tension ($-0.5\text{ to } -1.5\text{ MPa}$) in the vascular bundle, driving maximum convective ion flow ($Ca^{2+}, K^+, Cl^-$).
   - **Baseline Voltage:** Significant positive depolarization upward to $ADC \approx 420 - 460$.
3. **Night ($21:00 - 05:00$):** Absence of photons closes stomata. Hydraulic transpiration collapses, leaving only slow capillary root pressure.
   - **Baseline Voltage:** Decays to its quietest, lowest nocturnal baseline at $ADC \approx 320 - 350$.

---

## 2. Deep Learning Classification: Multi-Layer Perceptron (MLP)

To test whether the 21 extracted electrophysiological features carry an endogenous circadian time stamp, we trained a deep neural network:

### Architecture:
- **Input Dimension:** 21 standardized time-series features.
- **Hidden Layer 1:** 128 neurons, ReLU activation function, $L_2$ regularization ($\alpha = 0.0001$).
- **Hidden Layer 2:** 64 neurons, ReLU activation function.
- **Output Layer:** 3 neurons with Softmax probability normalization:
  $$P(\text{Phase} = k) = \frac{e^{z_k}}{\sum_{j=1}^3 e^{z_j}}, \quad k \in \{\text{Morning}, \text{Afternoon}, \text{Night}\}$$
- **Optimizer:** Adam ($\beta_1 = 0.9, \beta_2 = 0.999$, initial learning rate $\eta = 0.001$).

---

## 3. Results & Performance

- **Overall Accuracy:** **72.0%** (more than double random chance of $33.3\%$).
- **Afternoon Class Recall:** **0.96 (96%)** — Afternoon windows are almost never misclassified due to unmistakable transpirational baseline elevation.
- **Morning vs Night Disambiguation:** 70% F1-score; minor overlap occurs during twilight dawn transitions.

---

## 4. Visual Artifacts
- Diurnal Baseline Shift Distributions: `plots/05_circadian_rhythm_mlp_neural_network/1_diurnal_baseline_shifts.png`
- Circadian Confusion Matrix: `plots/05_circadian_rhythm_mlp_neural_network/2_circadian_confusion_matrix.png`
- MLP Training Loss Convergence: `plots/05_circadian_rhythm_mlp_neural_network/3_mlp_training_loss.png`
- Neural Hidden Layer Activations: `plots/05_circadian_rhythm_mlp_neural_network/4_layer_weight_activations.png`

---

## 5. What to Say in Presentation

> *"Sir, we also investigated whether plant electrical activity changes throughout the day.  
> As shown in our diurnal plot, the plant's resting baseline voltage shifts systematically: it peaks in the afternoon ($ADC \approx 440$) and drops at night ($ADC \approx 330$).  
> Biologically, this reflects circadian stomatal conductance and transpirational ion flow through xylem vessels.  
> Our Multi-Layer Perceptron neural network detected the time of day with **72.0% accuracy** purely from electrical signal geometry."*
