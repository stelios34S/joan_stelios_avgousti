import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx - 1)*x.std()**2 + (ny - 1)*y.std()**2) / dof)
    return (x.mean() - y.mean()) / pooled_std

def run_hypothesis_tests(df):
    # Split groups
    voice = df[df['group'] == 'voice']
    text = df[df['group'] == 'text']

    # -------------------- H1: Modality → Trust Score -------------------- #
    print("\n=== H1: Modality → Trust ===")
    trust_voice = voice['trust_score'].dropna()
    trust_text = text['trust_score'].dropna()

    # Normality
    print("Shapiro-Wilk Test (Trust):")
    print("Voice:", stats.shapiro(trust_voice))
    print("Text:", stats.shapiro(trust_text))

    # Variance check
    print("Levene’s test (Trust):", stats.levene(trust_voice, trust_text))

    # T-test or Mann-Whitney
    ttest_result = stats.ttest_ind(trust_voice, trust_text, equal_var=False)
    print("T-test (Trust):", ttest_result)
    print("Cohen’s d (Trust):", cohens_d(trust_voice, trust_text))

    # -------------------- H2: Modality → Interventions -------------------- #
    print("\n=== H2: Modality → Interventions ===")
    presses_voice = voice['total_presses'].dropna()
    presses_text = text['total_presses'].dropna()

    print("Shapiro-Wilk Test (Interventions):")
    print("Voice:", stats.shapiro(presses_voice))
    print("Text:", stats.shapiro(presses_text))

    print("Levene’s test (Interventions):", stats.levene(presses_voice, presses_text))

    ttest_result = stats.ttest_ind(presses_voice, presses_text, equal_var=False)
    print("T-test (Interventions):", ttest_result)
    print("Cohen’s d (Interventions):", cohens_d(presses_voice, presses_text))

    # Optional plots
    plt.boxplot([trust_text, trust_voice], labels=['Text', 'Voice'])
    plt.title('Trust Score by Group')
    plt.ylabel('Trust Score')
    plt.show()

    plt.boxplot([presses_text, presses_voice], labels=['Text', 'Voice'])
    plt.title('Total Interventions by Group')
    plt.ylabel('Button Presses')
    plt.show()

# --- Entry Point ---
if __name__ == "__main__":
    df = pd.read_csv("MergedData.csv")
    run_hypothesis_tests(df)