# plots_h1_h2_seaborn.py  ---------------------------------------------
import numpy as np, pandas as pd, seaborn as sns, matplotlib.pyplot as plt
from numpy.random import default_rng
sns.set_theme(style="whitegrid")

DF = pd.read_csv("MergedData.csv")       # <- adjust path if needed

################################################################################
# Helper 1 – violin + box + strip  (returns ax)
################################################################################
def violin_box_strip(data, y, palette, fname):
    fig, ax = plt.subplots(figsize=(5,5))
    sns.violinplot(ax=ax, data=data, x="group", y=y,
                   palette=palette, inner=None, cut=0)
    sns.boxplot(ax=ax,   data=data, x="group", y=y, palette=palette,
                width=.25, showcaps=True, boxprops={'zorder':3},
                whiskerprops={'linewidth':1}, saturation=.75)
    sns.stripplot(ax=ax, data=data, x="group", y=y, color='black',
                  size=5, jitter=.18, alpha=.7, zorder=4)
    ax.set_xlabel("")
    ax.set_ylabel(y.replace("_"," ").title())
    ax.set_title(f"{y.replace('_',' ').title()} – Text vs Voice")
    fig.tight_layout()
    fig.savefig(fname, dpi=300)
    print(f"✓ saved {fname}")
    return ax

################################################################################
# Helper 2 – Gardner-Altman panel (mean diff + 95 % bootstrap CI)
################################################################################
def gardner_altman_effect(data,                # tidy DF
                          y,                   # column with the metric
                          g1="text", g2="voice",
                          n_boot=5000, seed=0,
                          fname="ga_effect.png"):
    """
    Draw a single-panel Gardner–Altman plot (effect size only).

    * data    : DataFrame with columns  [group, y]
    * y       : outcome column (str)
    * g1 / g2 : reference & comparison group labels in `data.group`
    * n_boot  : bootstrap iterations for the CI
    * seed    : RNG seed for reproducibility
    * fname   : file name for the PNG export
    """
    a = data.loc[data.group == g1, y].values
    b = data.loc[data.group == g2, y].values
    diff_obs   = b.mean() - a.mean()

    rng        = default_rng(seed)
    boot_diffs = [rng.choice(b, len(b), True).mean() -
                  rng.choice(a, len(a), True).mean()
                  for _ in range(n_boot)]
    ci_lo, ci_hi = np.percentile(boot_diffs, [2.5, 97.5])

    # ---------- single panel -------------------------------------------
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.violinplot(y=boot_diffs, ax=ax, color="lightgrey",
                   inner=None, orient="h")
    ax.scatter(diff_obs, 0, s=120, color="black", zorder=5)
    ax.hlines(0, ci_lo, ci_hi, lw=4, color="black")
    ax.axvline(0, color="grey", lw=1)
    ax.set_yticks([])
    ax.set_xlabel(f"Mean difference  ({g2} – {g1})")
    ax.set_title(f"Effect size for {y.replace('_',' ').title()}\n95 % CI")

    fig.tight_layout()
    fig.savefig(fname, dpi=300)
    print(f"✓ saved {fname}  (mean diff = {diff_obs:.2f}, "
          f"CI {ci_lo:.2f} – {ci_hi:.2f})")
    return diff_obs, ci_lo, ci_hi

################################################################################
# 1 & 2  – violin/box/strip figures
################################################################################
palette = {"text": "#3182bd", "voice": "#e6550d"}
violin_box_strip(DF, "trust_score",     palette, "fig1_violin_trust.png")
violin_box_strip(DF, "total_presses",   palette, "fig2_violin_press.png")

################################################################################
# 3 & 4  – Gardner-Altman effect-size panels
################################################################################
# Trust
gardner_altman_effect(DF, y="trust_score",
                      g1="text", g2="voice",
                      fname="GA_trust.png")

# Interventions
gardner_altman_effect(DF, y="total_presses",
                      g1="text", g2="voice",
                      fname="GA_interventions.png")