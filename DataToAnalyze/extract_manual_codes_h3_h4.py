# h3_h4_manual_only.py
import pandas as pd
from pathlib import Path
from scipy.stats import ttest_ind

#POSITIVE, NEGATIVE, MIX, NEUTRAL
MERGED   = Path("MergedData.csv")          # numeric stuff
CODED_XL = Path("open_ended_coded.xlsx")   # you added btn_theme / expl_theme

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
df[['ResponseId','btn_theme','expl_theme']+OUTCOMES]\
  .to_csv("themes_with_outcomes.csv", index=False)
print("\n✔️ Saved themes_with_outcomes.csv – ready for plots or further stats")

# ------------------------------------------------------------
# 5. TRIANGULATION – do the three signals agree?
#    *   SELF-REPORT  →  btn_theme / expl_theme
#    *   STATED CHOICE → “most_comfortable” derived from ranks
#    *   BEHAVIOUR     → total_presses
# ------------------------------------------------------------

# def triangulate(df):
#     """
#     Creates simple crosstabs + correlations that show how well the
#     three sources of evidence line up for Buttons (H-3) and
#     Explanations (H-4).
#
#     • Self-report:      btn_theme / expl_theme  (coded by you)
#     • Stated preference: prefers_buttons / prefers_explanations_and_buttons
#     • Behaviour:        total_presses
#     """
#     # -------- H-3 : buttons ---------------------------------
#     print("\n=========== TRIANGULATION  –  H-3 (Buttons) ===========")
#
#     # (A)  Self-report  ×  Ranking
#     tab_btn = pd.crosstab(df['btn_theme'],
#                           df['prefers_buttons'],
#                           dropna=False)
#     print("\nSelf-report theme  ×  Ranked-buttons-best")
#     print(tab_btn)
#
#     # (B)  Self-report  ×  Behaviour
#     print("\nButton theme  →  mean press count")
#     print(df.groupby('btn_theme')['total_presses'].agg(['count','mean','std']))
#
#     # -------- H-4 : explanations ----------------------------
#     print("\n=========== TRIANGULATION  –  H-4 (Explanations) ======")
#
#     tab_expl = pd.crosstab(df['expl_theme'],
#                            df['prefers_explanations_and_buttons'],
#                            dropna=False)
#     print("\nSelf-report theme  ×  Ranked-explanations-best")
#     print(tab_expl)
#
#     print("\nExplanation theme  →  mean trust score")
#     print(df.groupby('expl_theme')['trust_score'].agg(['count','mean','std']))
#
#     # -------- Optional flags for quick inspection -----------
#     mismatch_btn = df[(df['btn_theme']=='positive') &
#                       (df['prefers_buttons']==0)]
#     if not mismatch_btn.empty:
#         print(f"\n⚠️  {len(mismatch_btn)} people PRAISED buttons but did NOT rank a "
#               "button version highest:")
#         print(mismatch_btn['ResponseId'].tolist())
#
#     mismatch_expl = df[(df['expl_theme']=='positive') &
#                        (df['prefers_explanations_and_buttons']==0)]
#     if not mismatch_expl.empty:
#         print(f"\n⚠️  {len(mismatch_expl)} people PRAISED explanations but did NOT rank "
#               "Version-3 highest:")
#         print(mismatch_expl['ResponseId'].tolist())


def triangulate(df):
    """
    Show how SELF-REPORT themes, STATED preference (ranking)
    and BEHAVIOUR (presses) line-up.

    • Buttons (H-3)   →  btn_theme   vs  prefers_buttons
    • Explan. (H-4)   →  expl_theme  vs  prefers_expl&btn
    """

    ##################################################################
    # Helper that prints a 2×2 grid with behaviour stats in each cell
    ##################################################################
    def grid(theme_col, pref_flag, behaviour, metric_name):

        print(f"\n=========== {metric_name.upper()}  ×  SELF vs RANK  –  {theme_col} ==========")

        # build 2×2 frame
        grid_df = (
            df
            .groupby([theme_col, pref_flag])[behaviour]
            .agg(['count', 'mean', 'std'])       # behaviour descriptives
            .reset_index()
            .pivot(index=theme_col, columns=pref_flag)
            .reindex(index=['positive','negative','neutral','mixed'])      # nice row order
        )

        # nicer column headers    e.g.   (count,0) → “count|NoPref”
        grid_df.columns = [f"{stat}|{'Pref' if pref else 'NoPref'}"
                           for stat, pref in grid_df.columns]

        print(grid_df.fillna('-'))

        # -------- Flag mismatches more clearly -----------------------
        mismatch = df[(df[theme_col]=='positive') & (df[pref_flag]==0)]
        if not mismatch.empty:
            print(f"\n⚠  {len(mismatch)} participants called it *positive* "
                  f"but did NOT rank that version highest:")
            print("   " + ", ".join(mismatch['ResponseId']))

    # ---------- H-3 : BUTTONS ---------------------------------------
    grid('btn_theme',  'prefers_explanations_and_buttons',                # self vs stated
         'total_presses', 'Press-count')
    grid('btn_theme',  'prefers_explanations_and_buttons',                # self vs stated
         'trust_score', 'Trust-Score')

    # ---------- H-4 : EXPLANATIONS ----------------------------------
    grid('expl_theme', 'prefers_explanations_and_buttons',
         'total_presses',  'Press-count')
    grid('expl_theme', 'prefers_explanations_and_buttons',
         'trust_score',  'Trust-score')

# ------------------------------------------------------------
# 6.  Run triangulation and finish
# ------------------------------------------------------------
triangulate(df)
