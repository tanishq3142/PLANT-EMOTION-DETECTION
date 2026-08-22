# Plant Bio-potential Dataset Overview

This project records ADC readings from an AD8232 connected to an Arduino and electrodes placed on a plant. Each CSV row contains the sensor reading plus the experimental context needed to interpret it.

> Scientific note: the AD8232 is an analogue biopotential front end designed for ECG applications. On a plant this is a bio-potential signal, not a medical ECG. The `bpm` value is an estimated electrical-event rate, not a demonstrated plant heartbeat.

## Data dictionary

| Column | Format / unit | Meaning and significance |
|---|---|---|
| `session_id` | `YYYYMMDDTHHMMSS+HHMM` | Unique recording ID. Groups all rows from one uninterrupted experiment. |
| `timestamp` | ISO 8601, milliseconds and UTC offset | Local computer time when Python receives the reading. Aligns data with experimental events and preserves timezone. It is reception time, not exact ADC conversion time. |
| `elapsed_seconds` | Monotonic seconds | Time since recording began. Enables robust duration and interval calculations even if the system clock changes. |
| `sample_number` | Integer from 0 | Sequential observation number. Useful for plotting and spotting missing data. |
| `stimulus` | Normalized text | Condition entered at launch, such as `water`, `music`, `touch`, or `none`. This is the supervised-learning label; use consistent names. |
| `time_of_day` | Category | Period inferred from local start time. Helps investigate circadian/environmental effects; use the exact timestamp for precise comparisons. |
| `ecg` | ADC count, usually 0–1023 | Raw Arduino/AD8232 reading. It preserves the waveform for later filtering and feature extraction. It is not voltage until calibrated. |
| `bpm` | Events/minute; 0 until estimated | Recent upward threshold-crossing rate, or the second value sent by Arduino. It is algorithm-dependent and sensitive to noise/movement. |

## Automatic file organization

Files are stored in `csv/YYYY-MM-DD/` as:

```text
plant_<stimulus>_<time_of_day>_<HH>hrs<MM>min<SS>sec.csv
```

The exact timestamp and labels are stored in every row, so analysis need not parse filenames. Time periods are morning 05:00–11:59, afternoon 12:00–16:59, evening 17:00–20:59, and night 21:00–04:59.

## Experimental guidance

- Capture a `none` baseline before each stimulus with unchanged placement.
- Keep labels consistent (always `water`, rather than mixing `water` and `watering`).
- Keep electrodes/leads fixed; motion, mains noise, and poor contact can mimic biological changes.
- Also track plant ID/species, water quantity, music frequency/volume, temperature, humidity, light, and electrode spacing in a lab notebook; these can become future CLI fields.
- Repeat conditions across plants and sessions. A waveform change alone does not establish an emotion without controlled experiments and validated labels.
- Check the operating-system clock and timezone before every recording.

## How these signals can support future state or "emotion" detection

The sensor does not directly measure an emotion. It measures changing electrical activity and noise at the plant-electrode interface. A future model can learn whether repeatable signal patterns are associated with carefully defined plant states—for example `baseline`, `recently_watered`, `dehydration_stress`, `touch_response`, or `music_exposure`. These measurable labels are more defensible than human terms such as happy, sad, or afraid.

### Significance of the captured signal

The raw `ecg` series is the most valuable measurement because a response may appear as a change in baseline level, a rapid spike, a slow variation, altered signal variability, or a change in frequency content. Keeping the raw series allows future algorithms to extract features that are not known at collection time.

The `bpm` series compresses threshold crossings into an event rate. It may help identify periods with more or fewer large electrical changes, but it loses waveform detail and can react to noise. It should be treated as one candidate feature, never as the only evidence of state.

The timestamps and elapsed time show when a response starts, how long it lasts, and how quickly it follows a stimulus. `stimulus` supplies the target label, while `time_of_day` helps the model separate a stimulus response from ordinary daily variation. `session_id` prevents samples from the same experiment being accidentally split across training and testing data.

### Suggested machine-learning workflow

1. Record several minutes of `none` baseline, then apply exactly one documented stimulus and continue recording. Repeat the protocol across many independent sessions and plants.
2. Remove obvious disconnections and motion artefacts, then filter mains interference and slow baseline drift without overwriting the original CSV.
3. Divide each session into fixed time windows, such as 5–30 seconds.
4. Extract features from each window: mean and median level, standard deviation, peak count and size, slope, signal energy, zero-crossing rate, event-rate statistics, and frequency-band power from an FFT or wavelet transform.
5. Train an initial interpretable classifier, such as logistic regression or random forest, to predict the defined stimulus/state. Later, enough clean data may support a 1-D CNN or recurrent model using waveform windows directly.
6. Split training and testing by whole `session_id` and preferably by plant. Never randomly mix rows from one recording across both sets, because that produces misleadingly high accuracy.
7. Report a confusion matrix, precision, recall, F1 score, and performance on plants/sessions the model has never seen.

A useful result is not merely detecting which stimulus was scheduled. The stronger goal is showing that the model recognizes a repeatable physiological response better than it recognizes recording date, plant identity, electrode contact, room noise, or time of day.

## Implemented learning pipeline

[`train_model.py`](train_model.py) implements the first reproducible model. It reads all CSV recordings, groups samples by `session_id`, cuts each waveform into configurable windows (10 seconds by default), and represents every window with these numerical features:

| Feature group | What the model can learn from it |
|---|---|
| Mean, median, minimum, maximum, and range | Baseline shifts and overall response amplitude. |
| Standard deviation and root-mean-square level | Signal variability and total activity/energy. |
| Mean absolute change and slope | How rapidly the potential changes and whether it trends upward or downward. |
| Peak count and mean event rate | Frequency of prominent transient responses. |
| Low-, mid-, and high-frequency power | Whether slow variations, medium oscillations, or rapid/noisy changes dominate. |

A balanced random forest receives these feature vectors together with their `stimulus` labels. During training, its decision trees repeatedly find feature thresholds that best separate labels. For example, some trees might learn that `water` windows often have greater slow-frequency power after watering, while other trees use variability or peak count. Hundreds of trees vote on the final class, which is more robust than relying on one threshold.

The script holds out complete sessions independently within every label. This matters because adjacent windows from one recording are extremely similar; random row splitting would let the model memorize a session and give falsely optimistic test scores. The output includes precision, recall, F1 score, a confusion matrix, and feature importance values. The saved model can then vote across all windows of a new recording.

### Commands

Install the training dependency:

```bash
python -m pip install scikit-learn
```

Train and evaluate:

```bash
python train_model.py train --input "csv/**/*.csv" --window 10 --output plant_state_model.pkl
```

Predict a new complete recording:

```bash
python train_model.py predict plant_state_model.pkl path/to/new_recording.csv
```

At least two independent sessions per label are required by the code; in practice, many more sessions and multiple plants are needed. Old three-column CSV files are skipped because they do not contain the stimulus and session metadata required for supervised training. A prediction means “this waveform resembles recordings with this experimental label,” not proof that the plant experienced a conscious emotion.
