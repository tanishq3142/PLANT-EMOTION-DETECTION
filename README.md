# Plant Bio-potential Detection

A Python system for capturing, labeling, visualizing, and classifying plant bio-potential signals from an Arduino connected to an AD8232 sensor.

The project records experimental conditions such as water, music, touch, or baseline. It can then train a machine-learning model to recognize signal patterns associated with those labels. These predictions describe experimental plant states; they do not prove human-like emotions.

## Repository structure

```text
PLANT-EMOTION-DETECTION/
|-- main.py          # Arduino recorder and live signal display
|-- plot_csv.py      # Live/static CSV signal visualizer
|-- simulate_ecg.py  # Legacy synthetic ECG generator for display testing
|-- train_model.py   # Feature extraction, model training, evaluation, prediction
|-- overview.md      # Data dictionary and scientific/ML explanation
|-- csv/             # Recordings grouped into YYYY-MM-DD directories
`-- README.md
```

## Requirements

- Python 3.8 or newer
- Arduino and AD8232 for real recordings
- `pyserial` for Arduino communication
- `matplotlib` for graphs
- `scikit-learn` for model training and prediction

Install the Python packages:

```powershell
python -m pip install pyserial matplotlib scikit-learn
```

## 1. Capture a recording

Connect the Arduino, check its COM port, and run:

```powershell
python main.py --port COM7 --baud 9600
```

The CLI asks for the stimulus being monitored, for example:

```text
Stimulus (water, music, touch, none, etc.): water
```

The timestamp and time-of-day category are detected automatically. To skip the prompt:

```powershell
python main.py --stimulus water --port COM7 --baud 9600
```

Close the graph or press `Ctrl+C` to stop. The CSV is closed safely and stored as:

```text
csv/YYYY-MM-DD/plant_<stimulus>_<time_of_day>_<HH>hrs<MM>min<SS>sec.csv
```

Each hardware CSV contains:

| Column | Purpose |
|---|---|
| `session_id` | Identifies one complete recording session. |
| `timestamp` | Timezone-aware sample reception time. |
| `elapsed_seconds` | Monotonic time since the session started. |
| `sample_number` | Sequential sample index. |
| `stimulus` | Experimental label used for learning. |
| `time_of_day` | Automatically detected recording period. |
| `ecg` | Raw 0–1023 Arduino ADC reading. |
| `bpm` | Estimated electrical threshold-crossing rate per minute. |

See [overview.md](overview.md) for the significance and limitations of every field.

## 2. Plot a recording

```powershell
python plot_csv.py csv/2026-08-11/plant_water_morning_11hrs50min.csv
```

The plot displays raw ADC readings and estimated event rate. It also updates while another process is adding rows to the CSV.

## 3. Collect training data

Before training, collect multiple independent sessions for each label. The code requires at least two sessions per label, but reliable research needs substantially more sessions and multiple plants.

A simple balanced dataset might contain:

```text
none:   10 or more independent recordings
water:  10 or more independent recordings
music:  10 or more independent recordings
touch:  10 or more independent recordings
```

Keep the recording duration, plant conditions, sensor setup, and stimulus procedure as consistent as possible. Record a `none` baseline so the model can learn normal activity.

## 4. Train and evaluate the model

Train with all compatible CSV files under `csv/`:

```powershell
python train_model.py train --input "csv/**/*.csv" --window 10 --output plant_state_model.pkl
```

Options:

| Option | Meaning |
|---|---|
| `--input` | Recursive glob selecting training CSV files. |
| `--window` | Signal-window duration in seconds; default is 10. |
| `--test-size` | Fraction of complete sessions reserved for testing; default is 0.25. |
| `--seed` | Random seed for reproducible splitting and training. |
| `--output` | Destination for the trained model file. |

For each waveform window, `train_model.py` extracts 14 features describing amplitude, variability, rate of change, peaks, energy, trend, event rate, and frequency-band power. A balanced random forest learns combinations of those features that distinguish the stimulus labels.

Evaluation keeps complete sessions separate. Samples from one recording cannot appear in both training and testing. The CLI reports:

- Precision, recall, and F1 score
- Confusion matrix
- Most influential signal features
- Number of training and test sessions

Old three-column CSV files and simulator files are skipped because they lack `session_id`, `stimulus`, and timing metadata.

## 5. Predict a new recording

After capturing a new session, classify it with the saved model:

```powershell
python train_model.py predict plant_state_model.pkl csv/2026-08-22/new_recording.csv
```

The model predicts every signal window and reports the majority label plus the vote count. Only load model files you created or trust, because Python pickle model files can execute code when loaded.

## Simulation for graph testing

The simulator tests visualization without Arduino hardware:

```powershell
python simulate_ecg.py csv/simulation.csv --duration 60 --rate 50
```

In another terminal:

```powershell
python plot_csv.py csv/simulation.csv
```

Simulator output uses the legacy `timestamp,ecg,bpm` format. It is intended for graph testing and cannot train the new classifier because it has no real stimulus/session metadata.

## Scientific limitation

The AD8232 output is a plant bio-potential measurement influenced by physiology, electrode contact, movement, environmental electrical noise, temperature, light, and humidity. A successful classifier shows association with controlled labels; it does not by itself demonstrate consciousness or an emotion. Use repeatable protocols, unseen plants/sessions for testing, and independent validation.
