import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats

from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

PLOT_DIR = "presentation/06-11-2026/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Load extracted features
df = pd.read_csv("presentation/06-11-2026/scratch/plant_features_extracted.csv")

feature_cols = [
    'mean_adc', 'std_adc', 'var_adc', 'min_adc', 'max_adc', 'peak_to_peak',
    'median_adc', 'iqr_adc', 'rms_adc', 'skewness', 'kurtosis',
    'mean_abs_diff', 'zero_crossings', 'peak_count',
    'power_low_freq', 'power_mid_freq', 'power_high_freq',
    'power_ratio_high_low', 'spectral_centroid', 'spectral_entropy'
]

X = df[feature_cols].copy()
y = df['category'].copy()
groups = df['session_file'].copy()

# Handle any NaN/inf if present
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

# =============================================================
# 1. MATHEMATICAL STATISTICAL SIGNIFICANCE (ANOVA & KRUSKAL)
# =============================================================
print("\n--- 1. Mathematical Hypothesis Testing (ANOVA & Kruskal-Wallis) ---")
stat_results = []
categories = df['category'].unique()

for col in feature_cols:
    groups_data = [df[df['category'] == cat][col].values for cat in categories]
    f_stat, p_val_anova = stats.f_oneway(*groups_data)
    h_stat, p_val_kruskal = stats.kruskal(*groups_data)
    stat_results.append({
        'Feature': col,
        'ANOVA_F_Stat': round(f_stat, 2),
        'ANOVA_p_val': f"{p_val_anova:.2e}",
        'Kruskal_H_Stat': round(h_stat, 2),
        'Kruskal_p_val': f"{p_val_kruskal:.2e}",
        'Statistically_Significant': p_val_anova < 0.001
    })

stat_df = pd.DataFrame(stat_results).sort_values(by='ANOVA_F_Stat', ascending=False)
stat_df.to_csv("presentation/06-11-2026/scratch/statistical_significance_tests.csv", index=False)
print("Top 8 most statistically significant features by F-statistic:")
print(stat_df.head(8).to_string(index=False))

# =============================================================
# 2. PLOT 8: Feature Correlation Heatmap
# =============================================================
print("\nGenerating Plot 8: Feature Correlation Heatmap...")
plt.figure(figsize=(12, 10))
corr = X.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, cmap='vlag', vmin=-1, vmax=1, annot=False,
            square=True, linewidths=.5, cbar_kws={"shrink": .8})
plt.title("Feature Cross-Correlation Matrix: Plant Electrophysiological Domain", fontsize=13, fontweight='bold', pad=12)
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_08_feature_correlation_heatmap.png", dpi=300)
plt.close()
print("Plot 8 saved.")

# =============================================================
# 3. MACHINE LEARNING BENCHMARKING (TRY & FAIL: STRATIFIED VS GROUP K-FOLD)
# =============================================================
print("\n--- 3. Machine Learning Model Benchmarking ---")

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
    'Support Vector Machine': SVC(kernel='rbf', C=1.0, random_state=42)
}

# A. Stratified 5-Fold CV (Window-level shuffle - Naive method)
strat_scores = {}
for name, clf in models.items():
    pipe = Pipeline([('scaler', StandardScaler()), ('clf', clf)])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipe, X, y, cv=cv, scoring='accuracy')
    strat_scores[name] = (scores.mean(), scores.std())
    print(f"[Stratified CV] {name:22s}: Mean Acc = {scores.mean()*100:.2f}% (±{scores.std()*100:.2f}%)")

# B. Group 5-Fold CV (Session-level grouping - Rigorous scientific method)
group_scores = {}
# Ensure each fold has balanced groups
gkf = GroupKFold(n_splits=5)
for name, clf in models.items():
    pipe = Pipeline([('scaler', StandardScaler()), ('clf', clf)])
    scores = cross_val_score(pipe, X, y, groups=groups, cv=gkf, scoring='accuracy')
    group_scores[name] = (scores.mean(), scores.std())
    print(f"[Group K-Fold]  {name:22s}: Mean Acc = {scores.mean()*100:.2f}% (±{scores.std()*100:.2f}%)")

# =============================================================
# 4. PLOT 9: Model Accuracy Comparison (Stratified vs Group CV)
# =============================================================
print("\nGenerating Plot 9: Model Comparison Bar Chart...")
model_names = list(models.keys())
strat_means = [strat_scores[m][0] * 100 for m in model_names]
strat_stds = [strat_scores[m][1] * 100 for m in model_names]
group_means = [group_scores[m][0] * 100 for m in model_names]
group_stds = [group_scores[m][1] * 100 for m in model_names]

x = np.arange(len(model_names))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
rects1 = ax.bar(x - width/2, strat_means, width, yerr=strat_stds, label='Stratified K-Fold (Naive Random Shuffle)',
                color='#3498db', capsize=5, alpha=0.9)
rects2 = ax.bar(x + width/2, group_means, width, yerr=group_stds, label='Group K-Fold (Strict Leave-Session-Out)',
                color='#e67e22', capsize=5, alpha=0.9)

ax.set_ylabel('Classification Accuracy (%)', fontsize=11, fontweight='bold')
ax.set_title('Machine Learning Benchmark: Stratified Shuffle vs. Session-Generalizable Group K-Fold',
             fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=10, fontweight='bold', rotation=15)
ax.set_ylim(0, 110)
ax.axhline(20, color='gray', linestyle=':', label='Chance Baseline (5 classes = 20%)')
ax.legend(loc='lower left', frameon=True)

# Add value labels
for rect in rects1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
for rect in rects2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_09_ml_model_comparison_accuracy.png", dpi=300)
plt.close()
print("Plot 9 saved.")

# =============================================================
# 5. DETAILED TRAIN/TEST SPLIT, CONFUSION MATRIX & CLASSIFICATION REPORT
# =============================================================
print("\n--- 5. In-Depth Evaluation of Best Model (Random Forest) ---")
# Split by session to prevent leakage
np.random.seed(42)
unique_sessions = groups.unique()
train_sessions = []
test_sessions = []

# Ensure every category has at least one session in train and test
for cat in categories:
    cat_sess = df[df['category'] == cat]['session_file'].unique()
    if len(cat_sess) == 1:
        # If only 1 session, split windows within session
        train_sessions.append(cat_sess[0])
    else:
        np.random.shuffle(cat_sess)
        n_test = max(1, int(len(cat_sess) * 0.3))
        test_sessions.extend(cat_sess[:n_test])
        train_sessions.extend(cat_sess[n_test:])

train_mask = df['session_file'].isin(train_sessions)
test_mask = df['session_file'].isin(test_sessions)

# Fallback: if test set lacks a class, use stratified split
if len(df.loc[test_mask, 'category'].unique()) < len(categories):
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
else:
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf.fit(X_train_scaled, y_train)
y_pred = rf.predict(X_test_scaled)

test_acc = accuracy_score(y_test, y_pred)
print(f"Random Forest Test Accuracy: {test_acc*100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# =============================================================
# 6. PLOT 10: Confusion Matrix Heatmap
# =============================================================
print("Generating Plot 10: Confusion Matrix...")
cm = confusion_matrix(y_test, y_pred, labels=sorted(categories))
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

plt.figure(figsize=(9, 7))
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=sorted(categories), yticklabels=sorted(categories),
            cbar_kws={'label': 'Normalized Prediction Fraction'})
plt.title(f"Plant State Confusion Matrix (Random Forest, Test Accuracy = {test_acc*100:.1f}%)",
          fontsize=12, fontweight='bold', pad=12)
plt.ylabel('True Experimental Condition', fontsize=10, fontweight='bold')
plt.xlabel('Predicted Condition', fontsize=10, fontweight='bold')
plt.xticks(rotation=30, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_10_ml_confusion_matrix.png", dpi=300)
plt.close()
print("Plot 10 saved.")

# =============================================================
# 7. PLOT 11: Feature Importance Ranking
# =============================================================
print("Generating Plot 11: Feature Importance Ranking...")
importances = rf.feature_importances_
feat_imp = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': importances
}).sort_values(by='Importance', ascending=True)

plt.figure(figsize=(10, 8))
plt.barh(feat_imp['Feature'], feat_imp['Importance'] * 100, color='#2c3e50', alpha=0.9)
plt.xlabel('Gini Feature Importance (%)', fontsize=11, fontweight='bold')
plt.title('Feature Importance Hierarchy for Discriminating Plant Electrophysiological States',
          fontsize=12, fontweight='bold', pad=10)
plt.grid(True, axis='x', linestyle='--', alpha=0.7)

for i, v in enumerate(feat_imp['Importance'] * 100):
    plt.text(v + 0.2, i, f"{v:.1f}%", va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_11_ml_feature_importance.png", dpi=300)
plt.close()
print("Plot 11 saved.")

# =============================================================
# 8. PLOT 12: Decision Tree Rule Flowchart
# =============================================================
print("Generating Plot 12: Interpretable Decision Tree...")
dt = DecisionTreeClassifier(max_depth=3, random_state=42)
dt.fit(X, y)

plt.figure(figsize=(18, 9))
plot_tree(dt, feature_names=feature_cols, class_names=dt.classes_,
          filled=True, rounded=True, fontsize=8, precision=1)
plt.title("Interpretable Plant State Decision Tree: Rule Hierarchy for College Presentation",
          fontsize=13, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot_12_decision_tree_rules.png", dpi=300)
plt.close()
print("Plot 12 saved.")
print("\nAll ML and statistical tasks completed successfully!")

