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
# ---------- 3.  LIGHT KEYWORD TAGGING  -------------------------------------
##############################################################################
# Columns with free text
TEXT_COLS = {
    'Q20_expl' : 'trust_explanation',   # “How did the explanations influence…”
    'Q21_ctrl' : 'control_buttons',     # “What was your experience with buttons…”
    'Q19_why' : 'why_ranked',        # “Why did you rank the versions this way?”
}

KW = {
    'expl_up'    : ['trust', 'safe', 'confidence', 'reassur', 'comfortable'],
    'expl_down'  : ['distrust', 'unsafe', 'confusing', 'worried', 'uncomfortable'],
    'btn_up'   : ['liked', 'helpful', 'reassur', 'good to have', 'control'],
    'btn_down'  : ['never used', 'didn\'t use', 'rarely used', 'confusing'],
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
# ---------- 5.  OPEN-ENDED EXPORT FOR MANUAL THEMES ------------------------
##############################################################################
export_cols = ['ResponseId',
               'rank_1', 'rank_2', 'rank_3',
               'trust_explanation', 'control_buttons', 'why_ranked','final_feedback'] \
             + [c for c in df.columns if any(c.startswith(p) for p in
                ('expl_up', 'expl_down', 'btn_up',
                 'btn_down'))]

df[export_cols].to_excel("open_ended_encoded.xlsx", index=False)
print("\n✔️  Saved open_ended_encoded.xlsx")


