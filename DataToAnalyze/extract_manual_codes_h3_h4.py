# h3_h4_manual_only.py
import pandas as pd
from pathlib import Path
from scipy.stats import ttest_ind

#POSITIVE, NEGATIVE, MIX, NEUTRAL
MERGED   = Path("MergedData.csv")          # numeric stuff
CODED_XL = Path("open_ended_encoded.xlsx")   # you added btn_theme / expl_theme

##############################################################################
# ---------- EXTRA:  Pair-wise rank preferences -----------------------------
##############################################################################
def pairwise_pref_counts(df):
    """
    Return a Series where index is 'V1>V2', 'V1>V3', 'V2>V3' etc.
    E.g.,  V1>V2  means Version-1 ranked **more comfortable** than Version-2
    (i.e., lower numeric rank number → smaller = less comfort, higher = more comfort).
    """
    counts = {
        'V1_over_V2': 0,
        'V1_over_V3': 0,
        'V2_over_V3': 0,
        'V2_over_V1': 0,
        'V3_over_V1': 0,
        'V3_over_V2': 0,
    }

    for _, row in df[['rank_1', 'rank_2', 'rank_3']].iterrows():
        # build a dict {version:rank_position}
        rankdict = {row['rank_1']: 1,
                    row['rank_2']: 2,
                    row['rank_3']: 3}

        # compare every pair
        if rankdict[1] > rankdict[2]:
            counts['V1_over_V2'] += 1
        else:
            counts['V2_over_V1'] += 1

        if rankdict[1] > rankdict[3]:
            counts['V1_over_V3'] += 1
        else:
            counts['V3_over_V1'] += 1

        if rankdict[2] > rankdict[3]:
            counts['V2_over_V3'] += 1
        else:
            counts['V3_over_V2'] += 1

    return pd.Series(counts)
##############################################################################
# ---------- 2.  PREFERENCE FLAGS FROM RANKS --------------------------------
##############################################################################
def build_preference_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns:
        most_comfortable           (value 1 / 2 / 3)
        prefers_buttons            (1 if version 2 or 3 was top-ranked)
        prefers_explanations       (1 if version 3 was top-ranked)
    """
    # rank_3  ==  participant’s “most comfortable” choice
    df['most_comfortable'] = df['rank_3']
    df['prefers_nothing'] =  (df['most_comfortable']== 1).astype(int)
    df['prefers_buttons'] = (df['most_comfortable']== 2).astype(int)
    df['prefers_explanations_and_buttons'] = (df['most_comfortable'] == 3).astype(int)
    return df






# 1. Merge -------------------------------------------------------------------
df_num   = pd.read_csv(MERGED)
df = build_preference_flags(df_num)
pair_counts = pairwise_pref_counts(df)
print("\n=== Pair-wise ranking preferences ===")
print(pair_counts)
df_code  = pd.read_excel(CODED_XL)[['ResponseId', 'btn_theme', 'expl_theme']]
df       = df.merge(df_code, on='ResponseId', how='left')

# 2. Helper: quick summary ----------------------------------------------------
def theme_descriptives(df, theme_col, outcome_cols):
    print(f"\n=== {theme_col} frequencies ===")
    print(df[theme_col].value_counts(dropna=False))

    for outcome in outcome_cols:
        print(f"\n{outcome} by {theme_col}")
        print(df.groupby(theme_col)[outcome].agg(['count','mean','std']))

        # optional: collapse to pos vs non-pos
        pos  = df[df[theme_col] == 'positive'][outcome]
        nonp = df[df[theme_col] != 'positive'][outcome]
        if len(pos) > 1 and len(nonp) > 1:
            t,p = ttest_ind(pos, nonp, equal_var=False, nan_policy='omit')
            print(f"   ‣ t-test  positive vs others:   t={t:.2f},  p={p:.3f}")

# 3. Run summaries -----------------------------------------------------------
OUTCOMES = ['trust_score', 'total_presses']

print("\n#################  H-3  (Buttons)  #################")
theme_descriptives(df, 'btn_theme', OUTCOMES)

print("\n################  H-4  (Explanations)  #############")
theme_descriptives(df, 'expl_theme', OUTCOMES)

# 4. Export tidy sheet for plots --------------------------------------------
export_cols = ['ResponseId',
               'btn_theme','expl_theme',
               'prefers_explanations_and_buttons',      # ▶ add this
               'trust_score','total_presses']
df[export_cols].to_csv("themes_with_outcomes.csv", index=False)
print("\n✔️ Saved themes_with_outcomes.csv – ready for plots or further stats")

############################################################
#  TRIANGULATION  –  revised
############################################################

def triangulate_h3(df):
    """H-3  Buttons → Trust  (self-report vs behaviour/attitude)"""
    print("\n=========== H-3  (Buttons) ===========")

    # (A)  Trust by button-theme
    print("\nTrust-score by btn_theme")
    print(df.groupby('btn_theme')['trust_score']
            .agg(['count','mean','std']))

    # (B)  Press count by button-theme
    print("\nPress-count by btn_theme")
    print(df.groupby('btn_theme')['total_presses']
            .agg(['count','mean','std']))

def triangulate_h4(df):
    """H-4  Explanations → Trust  (self-report × ranking × outcomes)"""
    print("\n=========== H-4  (Explanations) ==========")

    # 1.  Self-report theme  ×  ranking flag
    tab = pd.crosstab(df['expl_theme'],
                      df['prefers_explanations_and_buttons'],
                      dropna=False)
    print("\nSelf-report theme  ×  Ranked Version-3 highest")
    print(tab)

    # 2.  Outcomes split by expl_theme
    for outcome in ['trust_score', 'total_presses']:
        print(f"\n{outcome} by expl_theme")
        print(df.groupby('expl_theme')[outcome]
                .agg(['count','mean','std']))

############################################################
#  run
############################################################
triangulate_h3(df)
triangulate_h4(df)
