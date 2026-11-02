Checked Task: CSV row counts

I have enough data to give you a comprehensive analysis. Let me now write up the full ML recommendation report.

Created ml_recommendations.md

Here's the full picture — I've read every CSV file and here's my analysis and recommendations:

---

## 📊 Data Summary

You have **55 CSV files**, **~1.7 million rows** of plant biopotential (ADC) readings across 7 recording dates, with 8 columns per row (`session_id`, `timestamp`, `elapsed_seconds`, `ecg`, `bpm`, `stimulus`, `time_of_day`, `sample_number`).

---

## 🤖 6 ML Approaches (Best First)

See the full [ml_recommendations.md](file:///C:/Users/asim/.gemini/antigravity-ide/brain/abcd80f4-71eb-4df3-955f-4bd3cf9dfafa/ml_recommendations.md) — here's the summary:

| # | Approach | Readiness | Expected Accuracy |
|---|---|---|---|
| 1 | **Random Forest on 14 features** (already coded!) | ✅ Run it now | 65–80% |
| 2 | **Dead vs. Alive binary** (clearest signal split) | ✅ Best demo | **90%+** |
| 3 | **Music genre: Devotional vs. Pop vs. Silence** | ✅ Good data | 70–85% |
| 4 | **Anomaly detection** (Isolation Forest on baseline) | ✅ No labels needed | — |
| 5 | **Time-of-day prediction** (circadian analysis) | ✅ Already have labels | 60–75% |
| 6 | **1D-CNN on raw waveform** | 🔷 Need more data | — |

---

## ⚠️ #1 Thing to Do Before Training

**Clean your labels.** The same stimulus has multiple names:
- `music_yalgaar` + `bye_bye_bye` + `plant_pop_music_bye_bye_bye` → all **pop music**
- `om` + `plant_om_mantra` + `hare_krishna` + `hanuman_chalisa` → all **devotional music**  
- `normal` + `na` + `without_music` → all **baseline**

And discard junk sessions (`test`, `tets`, `asim`, `sujal`, `sachin`, etc.) — those are clearly mis-labeled experiments.

---

## 🚀 Quickest Win Right Now

```bash
python train_model.py train --input "csv/**/*.csv" --window 10 --output plant_rf_model.pkl
```

This will already run and give you a confusion matrix + feature importances for your presentation. Want me to add a label-mapping/cleaning step to `train_model.py` so it automatically merges the synonyms before training?