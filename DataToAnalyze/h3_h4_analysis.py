# h3_h4_pipeline.py
# ------------------------------------------------------------
# 1.  Load merged data (survey  +  press counts  +  group flag)
# 2.  Derive ranking-based preference flags
# 3.  Lightweight keyword tagging
# 4.  Helper tables / exports for H-3  and  H-4
# ------------------------------------------------------------

import pandas as pd
from pathlib import Path
from scipy.stats import ttest_ind

##############################################################################
# ---------- 1. LOAD MERGED DATA --------------------------------------------
##############################################################################
MERGED_PATH = Path("MergedData.csv")          # already produced upstream
df = pd.read_csv(MERGED_PATH)

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

    df['prefers_buttons']      = df['most_comfortable'].isin([2, 3]).astype(int)
    df['prefers_explanations'] = (df['most_comfortable'] == 3).astype(int)
    return df

df = build_preference_flags(df)

##############################################################################
# ---------- 3.  LIGHT KEYWORD TAGGING  -------------------------------------
##############################################################################
# Columns with free text
TEXT_COLS = {
    'Q20_expl' : 'trust_explanation',   # “How did the explanations influence…”
    'Q21_ctrl' : 'control_buttons',     # “What was your experience with buttons…”
    'Q18_why' : 'why_ranked',        # “Why did you rank the versions this way?”
}

KW = {
    'trust_up'    : ['trust', 'safe', 'confidence', 'reassur', 'comfortable'],
    'trust_down'  : ['distrust', 'unsafe', 'confusing', 'worried', 'uncomfortable'],
    'liked_btn'   : ['liked', 'helpful', 'reassur', 'good to have', 'control'],
    'unused_btn'  : ['never used', 'didn\'t use', 'rarely used', 'confusing'],
    'pressed_often': ['pressed a lot', 'kept pressing', 'many times', 'spam'],
}

def tag_keyword_flags(df: pd.DataFrame,
                      text_col: str,
                      tag_prefix: str,
                      keyword_list: list[str]) -> None:
    """
    Adds Boolean column  f'{tag_prefix}_{text_col}' .
    Example:  tag_keyword_flags(df, 'control_buttons', 'liked_btn', KW['liked_btn'])
    """
    colflag = f'{tag_prefix}_{text_col}'
    df[colflag] = df[text_col].str.lower().fillna('').apply(
        lambda txt: any(kw in txt for kw in keyword_list)
    )

# run tags
for tag, kw_list in KW.items():
    for _, col in TEXT_COLS.items():
        tag_keyword_flags(df, col, tag, kw_list)

##############################################################################
# ---------- 4.  TABLES / EXPORTS FOR H-3   &   H-4  -------------------------
##############################################################################
def h3_tables(df: pd.DataFrame):
    """H-3  (Control buttons → Trust)."""
    # descriptives
    print("\n=== Trust score by prefers_buttons ===")
    print(df.groupby('prefers_buttons')['trust_score'].describe())


    # qualitative counts
    liked   = df.filter(like='liked_btn_Q21_ctrl').any(axis=1).sum()
    unused  = df.filter(like='unused_btn_Q21_ctrl').any(axis=1).sum()
    print(f"\nParticipants explicitly *liking* buttons    : {liked}")
    print(f"Participants saying they *never used* buttons: {unused}")

def h4_tables(df: pd.DataFrame):
    """H-4  (Explanations → Trust)."""
    print("\n=== Trust score by prefers_explanations ===")
    print(df.groupby('prefers_explanations')['trust_score'].describe())

    expl_up   = df.filter(like='trust_up_Q20_expl').any(axis=1).sum()
    expl_down = df.filter(like='trust_down_Q20_expl').any(axis=1).sum()
    print(f"\nTrust ↑ because of explanations: {expl_up}")
    print(f"Trust ↓ / confusion            : {expl_down}")

    # Any relationship with actual button-press behaviour?
    print("\n=== total_presses by prefers_explanations ===")
    print(df.groupby('prefers_explanations')['total_presses'].describe())

##############################################################################
# ---------- 5.  OPEN-ENDED EXPORT FOR MANUAL THEMES ------------------------
##############################################################################
export_cols = ['ResponseId',
               'rank_1', 'rank_2', 'rank_3',
               'trust_explanation', 'control_buttons', 'final_feedback'] \
             + [c for c in df.columns if any(c.startswith(p) for p in
                ('trust_up', 'trust_down', 'liked_btn',
                 'unused_btn','pressed_often'))]

df[export_cols].to_excel("open_ended_for_manual_coding.xlsx", index=False)
print("\n✔️  Saved open_ended_for_manual_coding.xlsx")

##############################################################################
# ---------- 6.  RUN & PRINT -------------------------------------------------
##############################################################################
h3_tables(df)
h4_tables(df)
