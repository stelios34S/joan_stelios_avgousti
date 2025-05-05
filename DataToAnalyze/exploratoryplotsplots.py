import pandas as pd, seaborn as sns, matplotlib.pyplot as plt

rank = pd.read_csv("ranking_summary.csv", index_col=0)


# ── Clustered bar (rank-centric) ───────────────────────────────
rank.T.plot(kind="bar", figsize=(6,4), rot=0,
            color=["#de2d26", "#9ecae1", "#31a354"])
plt.ylabel("Count")
plt.title("How often each version received each rank")
plt.legend(title="Version", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("ranking_clustered.png", dpi=300)

corr = (pd.read_csv("exploratory_correlations.csv")
          .pivot(index="predictor", columns="outcome", values="correlation"))

plt.figure(figsize=(6,4))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1,
            cbar_kws=dict(label="ρ / r"))
plt.title("Exploratory correlations")
plt.tight_layout()
plt.savefig("corr_heatmap.png", dpi=300)

# ── Lollipop of significant (p<.05) only ──────────────────────
sig = (pd.read_csv("exploratory_correlations.csv")
         .query("p_value < .05")
         .assign(abs_r=lambda d: d.correlation.abs())
         .sort_values("abs_r", ascending=False))
plt.figure(figsize=(6,4))
sns.pointplot(data=sig, y="predictor", x="correlation", hue="outcome",
              join=False, palette="Set2", dodge=.4)
plt.axvline(0, color="grey", lw=1)
plt.title("Significant exploratory correlations (p < .05)")
plt.tight_layout()
plt.savefig("corr_lollipop_sig.png", dpi=300)





sns.set_theme(style="whitegrid")           # same look-and-feel as the rest
rank = pd.read_csv("ranking_summary.csv", index_col=0)

# ── 1.  CLEAN-UP COLUMN NAMES FOR A SHORT LEGEND ───────────────────────────
rank = rank.rename(columns={
        "Rank 1 (Least Comfortable)" : "Rank 1",
        "Rank 2"                     : "Rank 2",
        "Rank 3 (Most Comfortable)"  : "Rank 3"
})

# ── 2.  CLUSTERED BAR WITH NICE X-LABELS ───────────────────────────────────
ax = rank.plot(kind="bar", figsize=(6, 4), width=0.65,
               color=["#de2d26", "#9ecae1", "#31a354"], rot=0)

ax.set_xlabel("")                                  # no text under x-axis
ax.set_ylabel("Count")
ax.set_title("Comfort-rank frequencies per version")

# force the exact strings you want:
ax.set_xticklabels(["Version 1", "Version 2", "Version 3"])

ax.legend(title="Rank", bbox_to_anchor=(1.03, 1), loc="upper left")
plt.tight_layout()
plt.savefig("ranking_clustered.png", dpi=300)
plt.close()