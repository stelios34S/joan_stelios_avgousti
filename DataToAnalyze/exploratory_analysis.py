import pandas as pd
from scipy.stats import pearsonr, spearmanr, shapiro

def run_exploratory_correlations(df, outcome_vars, predictor_vars):
    results = []
    print(df)
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

outcomes = ['trust_score', 'total_presses']
predictors = ['age','gender','driving_experience','av_experience','comfort_with_automation']  # Add others like 'driving_experience' if numeric
df = pd.read_csv("MergedData.csv")
correlation_df = run_exploratory_correlations(df, outcomes, predictors)
correlation_df.to_csv("exploratory_correlations.csv", index=False)