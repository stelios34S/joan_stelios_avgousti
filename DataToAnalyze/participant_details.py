# table_participant_characteristics.py
# ------------------------------------------------------------
# Build “sample characteristics” table (counts & % per group)
# ------------------------------------------------------------
import pandas as pd

################################################################
# 1.  LOAD MERGED DATA (already contains the column `group`)
################################################################
DF = pd.read_csv("MergedData.csv")          # adjust path if needed

################################################################
# 2.  DERIVE AGE BANDS
################################################################
age_bins   = [17, 22, 26, 30, 35, 45]               # edges are (17,22], (22,26] …
age_labels = ["18–22", "23–26", "27–30", "31–35", "36–45"]
DF["age_band"] = pd.cut(DF["age"], bins=age_bins, labels=age_labels, right=True)
################################################################
# 3.  DEFINE VARIABLES TO TABULATE
################################################################
# column         -> nice label (1st column of the final table)
VARS = {
    "age_band"               : "Age",
    "gender"                 : "Gender",
    "av_experience"          : "Hands-free ride experience",
    "driving_experience"     : "Driving experience",
    "comfort_with_automation": "Comfort with automation (1–7)"
}

# optional re-map of raw codes to nicer strings
VALUE_LABELS = {
    "gender" : {0: "Male", 1: "Female", 2: "Other"},
    "av_experience": {0: "No", 1: "Yes"},
    "driving_experience": {1: "1", 2: "2", 3: "3", 4: "4", 5: "5"},
    "comfort_with_automation" : {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6 : "6", 7 : "7" }
}

################################################################
# 4.  HELPER THAT RETURNS n  AND  %  FOR ONE VARIABLE
################################################################
def counts_and_props(df, col, grp):
    """return Series with raw counts indexed by category,
       plus a companion Series with percentage strings"""
    counts = (
        df[df["group"] == grp][col]
        .value_counts(dropna=False, sort=False)
        .rename("n")
    )
    totals = counts.sum()
    perc   = (counts / totals * 100).round(0).astype(int).astype(str) + "%"
    return counts, perc

################################################################
# 5.  BUILD TABLE ROW BY ROW
################################################################
rows = []

for col, nice in VARS.items():
    # ensure categorical ordering is stable
    if col in VALUE_LABELS:  # we have a mapping
        categories = list(VALUE_LABELS[col])  # keys only
    else:  # no mapping: use the actual unique values
        if col == "age_band":  # keep the human-friendly order
            categories = age_labels
        else:
            categories = sorted(DF[col].dropna().unique())
    for raw_val in categories:
        label = VALUE_LABELS.get(col, {}).get(raw_val, str(raw_val))

        n_voice, p_voice = counts_and_props(DF, col, "voice")
        n_text , p_text  = counts_and_props(DF, col, "text")

        rows.append({
            "Variable"      : nice,
            "Category"      : label,
            "Voice n"       : n_voice.get(raw_val, 0),
            "Voice %"       : p_voice.get(raw_val, "0%"),
            "Text n"        : n_text.get(raw_val, 0),
            "Text %"        : p_text.get(raw_val,  "0%")
        })

################################################################
# 6.  TIDY DATAFRAME  →  LaTeX
################################################################
table_df = pd.DataFrame(rows)

# if you want \multirow-style grouping in LaTeX you can leave the
# repeated “Variable” cells blank except for the first occurrence:
table_df.loc[table_df["Variable"].duplicated(), "Variable"] = ""

# preview
print(table_df)