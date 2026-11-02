"""
visualize_presentation.py
=========================
Generates 8 presentation-quality plots from the plant bio-potential CSV data.

Usage:
    python visualize_presentation.py

Outputs (saved to plots/ folder):
    1_raw_waveform_comparison.png   – side-by-side waveforms for each stimulus
    2_fft_spectrum_comparison.png   – frequency spectra per stimulus class
    3_statistical_boxplot.png       – box plot of signal amplitude per class
    4_rolling_variability.png       – rolling std over time per session
    5_violin_distribution.png       – violin plots of ADC distribution per class
    6_heatmap_sessions.png          – feature heatmap across all valid sessions
    7_dead_vs_alive_panel.png       – dramatic side-by-side dead vs alive
    8_feature_radar.png             – radar chart of mean features per class

Requirements:
    pip install matplotlib numpy
"""

import csv
import glob
import math
import os
import statistics

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

CSV_GLOB = "csv/**/*.csv"
OUT_DIR = "plots"

LABEL_MAP = {
    "normal": "Baseline",
    "na": "Baseline",
    "without_music": "Baseline",
    "water": "Water",
    "with_water": "Water",
    "dead": "Dead",
    "semi_dead": "Dead",
    "partial_dead": "Dead",
    "sd": "Dead",
    "hare_krishna": "Devotional Music",
    "music_hare_krishna": "Devotional Music",
    "hanuman_chalisa": "Devotional Music",
    "plant_om_mantra": "Devotional Music",
    "om": "Devotional Music",
    "music_namami_shamisaan": "Devotional Music",
    "music_yalgaar": "Pop Music",
    "bye_bye_bye": "Pop Music",
    "plant_pop_music_bye_bye_bye": "Pop Music",
    "classical_music_for_plant_growth": "Classical Music",
}

CLASS_COLORS = {
    "Baseline":         "#4FC3F7",
    "Water":            "#81C784",
    "Dead":             "#EF5350",
    "Devotional Music": "#CE93D8",
    "Pop Music":        "#FFB74D",
    "Classical Music":  "#F06292",
}

REQUIRED_COLS = {"session_id", "elapsed_seconds", "stimulus", "ecg", "bpm"}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_all_sessions():
    sessions = []
    for path in glob.glob(CSV_GLOB, recursive=True):
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        except Exception:
            continue
        if not rows or not REQUIRED_COLS.issubset(rows[0]):
            continue
        raw_label = rows[0]["stimulus"].strip().lower()
        label = LABEL_MAP.get(raw_label)
        if label is None:
            continue
        try:
            ecg   = [float(r["ecg"])             for r in rows]
            times = [float(r["elapsed_seconds"]) for r in rows]
            bpm   = [float(r["bpm"])              for r in rows]
        except (ValueError, KeyError):
            continue
        if len(ecg) < 50:
            continue
        sessions.append({
            "path": path,
            "label": label,
            "ecg": ecg,
            "times": times,
            "bpm": bpm,
            "session_id": rows[0]["session_id"],
        })
    return sessions


def subsample(lst, n=2000):
    if len(lst) <= n:
        return lst
    step = len(lst) / n
    return [lst[int(i * step)] for i in range(n)]


def compute_features(ecg):
    if len(ecg) < 4:
        return None
    mean = statistics.fmean(ecg)
    std  = statistics.stdev(ecg)
    changes = [abs(b - a) for a, b in zip(ecg, ecg[1:])]
    return {
        "Mean":     mean,
        "Std Dev":  std,
        "Range":    max(ecg) - min(ecg),
        "Mean |Δ|": statistics.fmean(changes),
        "RMS":      math.sqrt(statistics.fmean(v * v for v in ecg)),
    }


def simple_fft_power(ecg, sample_rate, n_bins=256):
    chunk = ecg[:n_bins]
    n = len(chunk)
    mean = statistics.fmean(chunk)
    centered = [v - mean for v in chunk]
    freqs, power = [], []
    for k in range(1, n // 2 + 1):
        freq = k * sample_rate / n
        real = sum(centered[i] * math.cos(2 * math.pi * k * i / n) for i in range(n))
        imag = sum(centered[i] * math.sin(2 * math.pi * k * i / n) for i in range(n))
        freqs.append(freq)
        power.append((real * real + imag * imag) / (n * n))
    return freqs, power


def pick_one_per_class(sessions):
    best = {}
    for s in sessions:
        label = s["label"]
        if label not in best or len(s["ecg"]) > len(best[label]["ecg"]):
            best[label] = s
    return best


def rolling_std(values, window=200):
    result = []
    for i in range(len(values)):
        chunk = values[max(0, i - window):i + 1]
        result.append(statistics.stdev(chunk) if len(chunk) > 1 else 0.0)
    return result


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor":  "#0D1117",
        "axes.facecolor":    "#161B22",
        "axes.edgecolor":    "#30363D",
        "axes.labelcolor":   "#C9D1D9",
        "axes.titlecolor":   "#E6EDF3",
        "xtick.color":       "#8B949E",
        "ytick.color":       "#8B949E",
        "text.color":        "#C9D1D9",
        "grid.color":        "#21262D",
        "grid.linewidth":    0.6,
        "font.family":       "DejaVu Sans",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "legend.facecolor":  "#161B22",
        "legend.edgecolor":  "#30363D",
        "legend.labelcolor": "#C9D1D9",
    })
    return plt


# ---------------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------------

def plot_raw_waveforms(plt, sessions, out_dir):
    best = pick_one_per_class(sessions)
    classes = list(best.keys())
    n = len(classes)
    fig, axes = plt.subplots(n, 1, figsize=(14, 2.8 * n))
    if n == 1:
        axes = [axes]
    fig.suptitle("Plant Bio-Electrical Signal — Raw Waveform per Stimulus",
                 fontsize=15, fontweight="bold", color="#E6EDF3", y=1.01)
    for ax, label in zip(axes, classes):
        s = best[label]
        t = subsample(s["times"], 3000)
        e = subsample(s["ecg"],   3000)
        color = CLASS_COLORS.get(label, "#AAAAAA")
        ax.plot(t, e, color=color, linewidth=0.7, alpha=0.9)
        ax.fill_between(t, e, alpha=0.12, color=color)
        ax.set_ylabel("ADC (0–1023)", fontsize=9)
        ax.set_title(f"  {label}", loc="left", pad=4, fontsize=11, color=color)
        ax.set_ylim(-30, 1060)
        ax.grid(True, axis="y")
        ax.set_xlim(t[0], t[-1])
        ax.set_xlabel(f"Elapsed seconds (showing {t[-1]-t[0]:.0f}s)", fontsize=9)
    plt.tight_layout()
    path = os.path.join(out_dir, "1_raw_waveform_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_fft_spectra(plt, sessions, out_dir):
    best = pick_one_per_class(sessions)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title("Frequency Spectrum (FFT Power) per Stimulus Class")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (normalised)")
    for label, s in best.items():
        ecg = s["ecg"]
        times = s["times"]
        duration = times[-1] - times[0]
        if duration <= 0:
            continue
        sample_rate = (len(ecg) - 1) / duration
        chunk_size = min(512, len(ecg))
        freqs, power = simple_fft_power(ecg[:chunk_size], sample_rate, n_bins=chunk_size)
        max_p = max(power) or 1
        norm_power = [p / max_p for p in power]
        color = CLASS_COLORS.get(label, "#AAAAAA")
        ax.plot(freqs, norm_power, color=color, linewidth=1.6, label=label, alpha=0.85)
        ax.fill_between(freqs, norm_power, alpha=0.07, color=color)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="upper right")
    ax.grid(True)
    ax.axvspan(0,   0.5, alpha=0.05, color="#4FC3F7")
    ax.axvspan(0.5, 2.0, alpha=0.05, color="#81C784")
    ax.axvspan(2.0, 10,  alpha=0.05, color="#FFB74D")
    ax.text(0.25, 1.06, "Low",  ha="center", fontsize=8, color="#4FC3F7")
    ax.text(1.25, 1.06, "Mid",  ha="center", fontsize=8, color="#81C784")
    ax.text(6.0,  1.06, "High", ha="center", fontsize=8, color="#FFB74D")
    plt.tight_layout()
    path = os.path.join(out_dir, "2_fft_spectrum_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_boxplot(plt, sessions, out_dir):
    from collections import defaultdict
    by_class = defaultdict(list)
    for s in sessions:
        by_class[s["label"]].extend(subsample(s["ecg"], 1000))
    classes = list(by_class.keys())
    data    = [by_class[c] for c in classes]
    colors  = [CLASS_COLORS.get(c, "#AAAAAA") for c in classes]
    fig, ax = plt.subplots(figsize=(12, 7))
    bp = ax.boxplot(data, patch_artist=True, notch=True,
                    medianprops=dict(color="#FFFFFF", linewidth=2),
                    whiskerprops=dict(color="#8B949E"),
                    capprops=dict(color="#8B949E"),
                    flierprops=dict(marker=".", color="#8B949E", markersize=2, alpha=0.4))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_xticks(range(1, len(classes) + 1))
    ax.set_xticklabels(classes, rotation=15, ha="right")
    ax.set_ylabel("ADC Value  (0–1023)")
    ax.set_title("Signal Amplitude Distribution per Stimulus Class\n(Box = IQR · Whiskers = 1.5×IQR · White line = Median)")
    ax.grid(True, axis="y")
    plt.tight_layout()
    path = os.path.join(out_dir, "3_statistical_boxplot.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_rolling_variability(plt, sessions, out_dir):
    best = pick_one_per_class(sessions)
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_title("Signal Variability Over Time  (Rolling Std Dev, window = 100 samples)")
    ax.set_xlabel("Elapsed seconds")
    ax.set_ylabel("Rolling Std Dev  (ADC units)")
    for label, s in best.items():
        ecg   = subsample(s["ecg"],   2000)
        times = subsample(s["times"], 2000)
        rstd  = rolling_std(ecg, window=100)
        color = CLASS_COLORS.get(label, "#AAAAAA")
        ax.plot(times, rstd, color=color, linewidth=1.4, label=label, alpha=0.85)
    ax.legend(loc="upper right")
    ax.grid(True)
    ax.set_ylim(0)
    plt.tight_layout()
    path = os.path.join(out_dir, "4_rolling_variability.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_violin(plt, sessions, out_dir):
    from collections import defaultdict
    by_class = defaultdict(list)
    for s in sessions:
        by_class[s["label"]].extend(subsample(s["ecg"], 800))
    classes = sorted(by_class.keys())
    data    = [by_class[c] for c in classes]
    colors  = [CLASS_COLORS.get(c, "#AAAAAA") for c in classes]
    fig, ax = plt.subplots(figsize=(12, 7))
    parts = ax.violinplot(data, showmedians=True, showextrema=True)
    for pc, color in zip(parts["bodies"], colors):
        pc.set_facecolor(color)
        pc.set_alpha(0.65)
        pc.set_edgecolor(color)
    parts["cmedians"].set_color("#FFFFFF")
    parts["cmedians"].set_linewidth(2)
    parts["cbars"].set_color("#8B949E")
    parts["cmins"].set_color("#8B949E")
    parts["cmaxes"].set_color("#8B949E")
    ax.set_xticks(range(1, len(classes) + 1))
    ax.set_xticklabels(classes, rotation=15, ha="right")
    ax.set_ylabel("ADC Value  (0–1023)")
    ax.set_title("Violin Plot — Signal Distribution per Stimulus\n(Width = probability density · White line = median)")
    ax.grid(True, axis="y")
    plt.tight_layout()
    path = os.path.join(out_dir, "5_violin_distribution.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_feature_heatmap(plt, sessions, out_dir):
    FEAT_NAMES = ["Mean", "Std Dev", "Range", "Mean |Δ|", "RMS"]
    session_labels, session_names, matrix = [], [], []
    for s in sessions:
        feats = compute_features(s["ecg"])
        if feats is None:
            continue
        session_labels.append(s["label"])
        session_names.append(os.path.basename(s["path"])[:30])
        matrix.append([feats[f] for f in FEAT_NAMES])
    if not matrix:
        print("  Skipping heatmap — no valid sessions.")
        return
    n_feats = len(FEAT_NAMES)
    col_mins = [min(row[j] for row in matrix) for j in range(n_feats)]
    col_maxs = [max(row[j] for row in matrix) for j in range(n_feats)]
    norm = [[(row[j]-col_mins[j])/(col_maxs[j]-col_mins[j]+1e-9) for j in range(n_feats)]
            for row in matrix]
    fig, ax = plt.subplots(figsize=(max(10, n_feats * 1.6), max(8, len(norm) * 0.45)))
    import matplotlib
    cmap = matplotlib.colormaps["plasma"]
    for row_i, (row_vals, lbl, sname) in enumerate(zip(norm, session_labels, session_names)):
        for col_j, val in enumerate(row_vals):
            color = cmap(val)
            ax.add_patch(plt.Rectangle((col_j, row_i), 1, 1, color=color))
            ax.text(col_j + 0.5, row_i + 0.5, f"{val:.2f}",
                    ha="center", va="center", fontsize=7.5,
                    color="white" if val < 0.6 else "#111111")
    ax.set_xlim(0, n_feats)
    ax.set_ylim(0, len(norm))
    ax.set_xticks([j + 0.5 for j in range(n_feats)])
    ax.set_xticklabels(FEAT_NAMES, fontsize=10)
    ax.set_yticks([i + 0.5 for i in range(len(session_names))])
    ax.set_yticklabels([f"[{session_labels[i][:3].upper()}] {session_names[i]}"
                        for i in range(len(session_names))], fontsize=7.5)
    ax.set_title("Normalised Feature Heatmap Across All Sessions  (Brighter = higher relative value)")
    plt.tight_layout()
    path = os.path.join(out_dir, "6_heatmap_sessions.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_dead_vs_alive(plt, sessions, out_dir):
    dead_session  = next((s for s in sessions if s["label"] == "Dead"),     None)
    alive_session = next((s for s in sessions if s["label"] == "Baseline"), None)
    if not dead_session or not alive_session:
        print("  Skipping dead-vs-alive — missing class data.")
        return
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Dead Plant  vs.  Alive Plant — Bio-Electrical Signal Comparison",
                 fontsize=15, fontweight="bold", color="#E6EDF3")
    for ax, session, title, color in [
        (axes[0], dead_session,  "☠  Dead Plant",              "#EF5350"),
        (axes[1], alive_session, "🌿  Alive Plant (Baseline)",  "#4FC3F7"),
    ]:
        t = subsample(session["times"], 2000)
        e = subsample(session["ecg"],   2000)
        ax.plot(t, e, color=color, linewidth=0.9, alpha=0.92)
        ax.fill_between(t, e, alpha=0.15, color=color)
        feats = compute_features(session["ecg"])
        if feats:
            ax.set_xlabel(
                f"Mean={feats['Mean']:.0f}  Std={feats['Std Dev']:.0f}  Range={feats['Range']:.0f}",
                fontsize=9, color="#8B949E")
        ax.set_title(title, color=color, fontsize=13, fontweight="bold")
        ax.set_ylabel("ADC Value  (0–1023)")
        ax.set_ylim(-30, 1060)
        ax.grid(True, axis="y")
        ax.set_xlim(t[0], t[-1])
    plt.tight_layout()
    path = os.path.join(out_dir, "7_dead_vs_alive_panel.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_radar(plt, sessions, out_dir):
    from collections import defaultdict
    FEAT_NAMES = ["Mean", "Std Dev", "Range", "Mean |Δ|", "RMS"]
    by_class = defaultdict(list)
    for s in sessions:
        feats = compute_features(s["ecg"])
        if feats:
            by_class[s["label"]].append([feats[f] for f in FEAT_NAMES])
    class_means = {}
    for label, feat_rows in by_class.items():
        n_feats = len(FEAT_NAMES)
        class_means[label] = [statistics.fmean(row[j] for row in feat_rows)
                               for j in range(n_feats)]
    all_vals = [v for vals in class_means.values() for v in vals]
    global_max = max(all_vals) or 1
    norm_means = {lbl: [v / global_max for v in vals] for lbl, vals in class_means.items()}
    n_feats = len(FEAT_NAMES)
    angles = [2 * math.pi * i / n_feats for i in range(n_feats)] + [0]
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"polar": True})
    ax.set_facecolor("#161B22")
    ax.set_title("Feature Radar Chart — Mean Normalised Features per Class",
                 fontsize=13, fontweight="bold", color="#E6EDF3", pad=20)
    for label, vals in norm_means.items():
        vals_closed = vals + vals[:1]
        color = CLASS_COLORS.get(label, "#AAAAAA")
        ax.plot(angles, vals_closed, color=color, linewidth=2, label=label)
        ax.fill(angles, vals_closed, color=color, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(FEAT_NAMES, fontsize=11, color="#C9D1D9")
    ax.set_yticklabels([])
    ax.yaxis.grid(True, color="#30363D")
    ax.xaxis.grid(True, color="#30363D")
    ax.spines["polar"].set_color("#30363D")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=10)
    plt.tight_layout()
    path = os.path.join(out_dir, "8_feature_radar.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Loading sessions...")
    sessions = load_all_sessions()
    classes_found = set(s["label"] for s in sessions)
    print(f"  Found {len(sessions)} valid sessions: {classes_found}\n")
    if not sessions:
        print("ERROR: No valid sessions found. Make sure CSV_GLOB matches your data.")
        return
    plt = setup_matplotlib()
    print("Generating plots...")
    plot_raw_waveforms(plt, sessions, OUT_DIR)
    plot_fft_spectra(plt, sessions, OUT_DIR)
    plot_boxplot(plt, sessions, OUT_DIR)
    plot_rolling_variability(plt, sessions, OUT_DIR)
    plot_violin(plt, sessions, OUT_DIR)
    plot_feature_heatmap(plt, sessions, OUT_DIR)
    plot_dead_vs_alive(plt, sessions, OUT_DIR)
    plot_radar(plt, sessions, OUT_DIR)
    print(f"\nAll 8 plots saved to '{OUT_DIR}/' — ready for your presentation!")


if __name__ == "__main__":
    main()
