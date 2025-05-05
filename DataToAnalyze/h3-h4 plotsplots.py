# plots_h3_h4.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

################################################################################
# 1.  LOAD DATA (themes_with_outcomes.csv from your previous step)
################################################################################
DF = pd.read_csv("themes_with_outcomes.csv")          # path as needed
sns.set_theme(style="whitegrid")

################################################################################
# 2.  NICE COLOUR PALETTE  (positive = green, neutral = grey, mixed = orange,
#                            negative = red — tweak as you like)
################################################################################
pal = {"positive": "#31a354",
       "neutral" : "#bdbdbd",
       "mixed"   : "#fd8d3c",
       "negative": "#de2d26"}

################################################################################
# 3.  HELPER – violin + slim box + strip in **one** axis
################################################################################
def combo_violin(ax, data, x, y):
    sns.violinplot(ax=ax, data=data, x=x, y=y,
                   palette=pal, inner=None, cut=0)
    sns.boxplot(ax=ax, data=data, x=x, y=y,
                palette=pal, width=.25, showcaps=True,
                boxprops={'zorder':3}, whiskerprops={'linewidth':1})
    sns.stripplot(ax=ax, data=data, x=x, y=y,
                  color='black', size=5, jitter=.18, alpha=.7, zorder=4)
    ax.set_xlabel("")
    ax.set_ylabel(y.replace("_", " ").title())

################################################################################
# 4.  -----  H-3  (Button themes)   -------------------------------------------
################################################################################
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharex=True)

combo_violin(ax1, DF, "btn_theme", "trust_score")
ax1.set_title("H-3 · Trust Score  by  Button Theme")

combo_violin(ax2, DF, "btn_theme", "total_presses")
ax2.set_title("H-3 · Total Presses  by  Button Theme")
ax2.set_ylabel("Button presses (Trial 3)")

fig1.tight_layout()
fig1.savefig("H3_buttons_violinplots.png", dpi=300)

################################################################################
# 5.  -----  H-4  (Explanation themes)  ---------------------------------------
################################################################################
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 5), sharex=True)

combo_violin(ax3, DF, "expl_theme", "trust_score")
ax3.set_title("H-4 · Trust Score  by  Explanation Theme")

combo_violin(ax4, DF, "expl_theme", "total_presses")
ax4.set_title("H-4 · Total Presses  by  Explanation Theme")
ax4.set_ylabel("Button presses (Trial 3)")

fig2.tight_layout()
fig2.savefig("H4_expl_violinplots.png", dpi=300)

################################################################################
# 6.  OPTIONAL BAR-PLOT – Triangulation (H-4)
#     What % of each self-report theme actually ranked Version-3 highest?
################################################################################
# Need the “prefers_explanations_and_buttons” flag – merge in if missing
TRI_FILE = Path("themes_with_outcomes.csv")   # <-- contains the flag
if TRI_FILE.exists():
    DF = pd.read_csv(TRI_FILE)

    bar_data = (DF.groupby("expl_theme")["prefers_explanations_and_buttons"]
                  .mean()               # proportion
                  .reset_index(name="pct"))
    bar_data["pct"] *= 100              # convert to %

    plt.figure(figsize=(6,4))
    sns.barplot(data=bar_data, x="expl_theme", y="pct",
                palette=pal,
                order=["positive","neutral","mixed","negative"])
    plt.ylabel("% who ranked Control + Explanations highest")
    plt.xlabel("Explanation theme (self-reported)")
    plt.title("Triangulation check – H4")
    plt.ylim(0,100)
    plt.tight_layout()
    plt.savefig("H4_triangulation_bar.png", dpi=300)
    print("✓ saved H4_triangulation_bar.png")
else:
    print("⚠  themes_with_outcomes.csv not found – skipped bar-plot")

print("✓ Graphs saved:")
print("  • H3_buttons_violinplots.png")
print("  • H4_expl_violinplots.png")
print("  • H4_triangulation_bar.png  (if ranking flag was available)")
