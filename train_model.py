"""Train and use a plant-state classifier from recorder CSV files.

The model learns from statistical and frequency features calculated over waveform
windows. It predicts experimental labels (the `stimulus` CSV column), not literal
human emotions.
"""

import argparse
import csv
import glob
import math
import os
import pickle
import random
import statistics
from collections import Counter, defaultdict


FEATURE_NAMES = [
    "mean", "standard_deviation", "minimum", "maximum", "range", "median",
    "mean_absolute_change", "root_mean_square", "slope", "peak_count",
    "event_rate_mean", "low_frequency_power", "mid_frequency_power",
    "high_frequency_power",
]


def load_session(path):
    with open(path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    required = {"session_id", "elapsed_seconds", "stimulus", "ecg", "bpm"}
    if not rows or not required.issubset(rows[0]):
        return None
    try:
        return {
            "path": path,
            "session_id": rows[0]["session_id"],
            "label": rows[0]["stimulus"],
            "time": [float(row["elapsed_seconds"]) for row in rows],
            "signal": [float(row["ecg"]) for row in rows],
            "rate": [float(row["bpm"]) for row in rows],
        }
    except (KeyError, TypeError, ValueError):
        return None


def band_power(values, sample_rate, low_hz, high_hz):
    """Simple periodogram band power without requiring NumPy."""
    centered = [value - statistics.fmean(values) for value in values]
    count = len(centered)
    power = 0.0
    for frequency_index in range(1, count // 2 + 1):
        frequency = frequency_index * sample_rate / count
        if low_hz <= frequency < high_hz:
            real = sum(value * math.cos(2 * math.pi * frequency_index * i / count)
                       for i, value in enumerate(centered))
            imaginary = -sum(value * math.sin(2 * math.pi * frequency_index * i / count)
                             for i, value in enumerate(centered))
            power += (real * real + imaginary * imaginary) / (count * count)
    return power


def extract_features(times, values, rates):
    if len(values) < 4:
        return None
    duration = times[-1] - times[0]
    if duration <= 0:
        return None
    sample_rate = (len(values) - 1) / duration
    changes = [b - a for a, b in zip(values, values[1:])]
    mean = statistics.fmean(values)
    deviation = statistics.stdev(values)
    peak_threshold = mean + deviation
    peaks = sum(values[i - 1] < values[i] >= values[i + 1] and values[i] > peak_threshold
                for i in range(1, len(values) - 1))
    valid_rates = [rate for rate in rates if rate > 0]
    nyquist = sample_rate / 2
    return [
        mean,
        deviation,
        min(values),
        max(values),
        max(values) - min(values),
        statistics.median(values),
        statistics.fmean(abs(change) for change in changes),
        math.sqrt(statistics.fmean(value * value for value in values)),
        (values[-1] - values[0]) / duration,
        peaks,
        statistics.fmean(valid_rates) if valid_rates else 0.0,
        band_power(values, sample_rate, 0.0, min(0.5, nyquist)),
        band_power(values, sample_rate, 0.5, min(2.0, nyquist)),
        band_power(values, sample_rate, 2.0, min(10.0, nyquist)),
    ]


def window_session(session, window_seconds):
    windows = []
    start = 0
    while start < len(session["time"]):
        end_time = session["time"][start] + window_seconds
        end = start
        while end < len(session["time"]) and session["time"][end] < end_time:
            end += 1
        features = extract_features(
            session["time"][start:end], session["signal"][start:end], session["rate"][start:end]
        )
        if features is not None:
            windows.append(features)
        start = end
    return windows


def collect_dataset(input_pattern, window_seconds):
    sessions = []
    skipped = 0
    for path in glob.glob(input_pattern, recursive=True):
        session = load_session(path)
        if session is None:
            skipped += 1
            continue
        session["features"] = window_session(session, window_seconds)
        if session["features"]:
            sessions.append(session)
    return sessions, skipped


def split_by_session(sessions, test_fraction, seed):
    features, labels, groups = [], [], []
    sessions_by_label = defaultdict(list)
    for session in sessions:
        features.extend(session["features"])
        labels.extend([session["label"]] * len(session["features"]))
        groups.extend([session["session_id"]] * len(session["features"]))
        sessions_by_label[session["label"]].append(session["session_id"])

    # Keep every label represented on both sides of the session-level split.
    generator = random.Random(seed)
    test_groups = set()
    for session_ids in sessions_by_label.values():
        generator.shuffle(session_ids)
        test_count = max(1, min(len(session_ids) - 1, round(len(session_ids) * test_fraction)))
        test_groups.update(session_ids[:test_count])
    train_indexes = [i for i, group in enumerate(groups) if group not in test_groups]
    test_indexes = [i for i, group in enumerate(groups) if group in test_groups]
    return features, labels, groups, train_indexes, test_indexes


def train(args):
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError as error:
        raise SystemExit("Install the ML dependency: python -m pip install scikit-learn") from error

    sessions, skipped = collect_dataset(args.input, args.window)
    label_sessions = Counter(session["label"] for session in sessions)
    if len(label_sessions) < 2:
        raise SystemExit("Need at least two stimulus labels in the new CSV format.")
    if any(count < 2 for count in label_sessions.values()):
        raise SystemExit("Need at least two independent recording sessions for every stimulus label.")

    features, labels, groups, train_i, test_i = split_by_session(sessions, args.test_size, args.seed)
    x_train = [features[i] for i in train_i]
    y_train = [labels[i] for i in train_i]
    x_test = [features[i] for i in test_i]
    y_test = [labels[i] for i in test_i]
    model = RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=args.seed, n_jobs=-1
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(f"Loaded {len(sessions)} sessions and {len(features)} windows; skipped {skipped} legacy/invalid files.")
    print(f"Training sessions: {len(set(groups[i] for i in train_i))}; test sessions: {len(set(groups[i] for i in test_i))}")
    print("\nClassification report:\n", classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix (rows=true, columns=predicted):")
    print(model.classes_)
    print(confusion_matrix(y_test, predictions, labels=model.classes_))
    print("\nMost influential features:")
    for name, importance in sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name}: {importance:.4f}")

    artifact = {"model": model, "feature_names": FEATURE_NAMES, "window_seconds": args.window}
    with open(args.output, "wb") as destination:
        pickle.dump(artifact, destination)
    print(f"Saved model to {args.output}")


def predict(args):
    with open(args.model, "rb") as source:
        artifact = pickle.load(source)
    session = load_session(args.csv_path)
    if session is None:
        raise SystemExit("Prediction CSV is empty or does not use the new recorder schema.")
    windows = window_session(session, artifact["window_seconds"])
    if not windows:
        raise SystemExit("Recording is too short to create a valid window.")
    predictions = artifact["model"].predict(windows)
    counts = Counter(predictions)
    label, votes = counts.most_common(1)[0]
    print(f"Predicted state/stimulus: {label} ({votes}/{len(predictions)} windows)")
    print("Window votes:", dict(counts))


def main():
    parser = argparse.ArgumentParser(description="Train or use a plant bio-potential classifier")
    subparsers = parser.add_subparsers(dest="command", required=True)
    train_parser = subparsers.add_parser("train", help="Train and evaluate a model")
    train_parser.add_argument("--input", default="csv/**/*.csv", help="Recursive CSV glob")
    train_parser.add_argument("--window", type=float, default=10.0, help="Window length in seconds")
    train_parser.add_argument("--test-size", type=float, default=0.25, help="Fraction of sessions held out")
    train_parser.add_argument("--seed", type=int, default=42)
    train_parser.add_argument("--output", default="plant_state_model.pkl")
    train_parser.set_defaults(action=train)
    predict_parser = subparsers.add_parser("predict", help="Classify a recording")
    predict_parser.add_argument("model")
    predict_parser.add_argument("csv_path")
    predict_parser.set_defaults(action=predict)
    args = parser.parse_args()
    if args.command == "train" and (args.window <= 0 or not 0 < args.test_size < 1):
        parser.error("--window must be positive and --test-size must be between 0 and 1")
    args.action(args)


if __name__ == "__main__":
    main()
