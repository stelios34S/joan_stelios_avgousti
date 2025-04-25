import pandas as pd
from scipy.stats import pearsonr, spearmanr, shapiro

def run_exploratory_correlations(df, outcome_vars, predictor_vars):
    results = []
    for outcome in outcome_vars:
        for predictor in predictor_vars:
            x = df[predictor]
            y = df[outcome]

            if x.isnull().any() or y.isnull().any():
                continue

            # Check normality
            p_x = shapiro(x).pvalue if len(x) >= 3 and x.nunique() > 2 else 0
            p_y = shapiro(y).pvalue if len(y) >= 3 and y.nunique() > 2 else 0

            if p_x > 0.05 and p_y > 0.05:
                corr, pval = pearsonr(x, y)
                method = "Pearson"
            else:
                corr, pval = spearmanr(x, y)
                method = "Spearman"

            results.append({
                "outcome": outcome,
                "predictor": predictor,
                "method": method,
                "correlation": corr,
                "p_value": pval
            })

    return pd.DataFrame(results)
def summarize_rankings(df):
    # Step 1: Map numeric version ranks to string labels
    version_map = {1: "Version 1", 2: "Version 2", 3: "Version 3"}
    df['rank_1_label'] = df['rank_1'].astype(float).map(version_map)
    df['rank_2_label'] = df['rank_2'].astype(float).map(version_map)
    df['rank_3_label'] = df['rank_3'].astype(float).map(version_map)

    # Step 2: Count how often each version appears in each rank
    rank_counts = {
        'Rank 1 (Least Comfortable)': df['rank_1_label'].value_counts(),
        'Rank 2': df['rank_2_label'].value_counts(),
        'Rank 3 (Most Comfortable)': df['rank_3_label'].value_counts()
    }

    # Step 3: Combine into a single summary DataFrame
    versions = ['Version 1', 'Version 2', 'Version 3']
    summary_df = pd.DataFrame(index=versions)
    for rank_label, counts in rank_counts.items():
        summary_df[rank_label] = summary_df.index.map(counts).fillna(0).astype(int)

    summary_df['Total Mentions'] = summary_df.sum(axis=1)
    return summary_df


outcomes = ['trust_score', 'total_presses']
predictors = ['age','gender','driving_experience','av_experience','comfort_with_automation']  # Add others like 'driving_experience' if numeric
df = pd.read_csv("MergedData.csv")
correlation_df = run_exploratory_correlations(df, outcomes, predictors)
correlation_df.to_csv("exploratory_correlations.csv", index=False)

# Create the ranking summary
ranking_summary = summarize_rankings(df)

# Save or view it
ranking_summary.to_csv("ranking_summary.csv")