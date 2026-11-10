"""
figure3_concurrent_v2.py

Regenerates Figure 3 (concurrent: CP at TP1 vs GFTA-2 and EVT-2 at TP1) with the
corrected CP scaling: CP is z-scored over the FULL cohort (not the 117
GFTA-complete subset), so the EVT-2 panel now includes all 122 children and the
panel betas match the corrected Table 4 (GFTA 0.60, EVT 0.62).

Usage:
    python figure3_concurrent_v2.py <tp1_tp1_master_with_scaled.csv> [out.png]
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import to_rgba

master = sys.argv[1] if len(sys.argv) > 1 else "data/tp1_tp1_master_with_scaled.csv"
out_png = sys.argv[2] if len(sys.argv) > 2 else "figure3_concurrent_v2.png"

df = pd.read_csv(master)


def to_gender_dummy(x):
    try:
        v = float(x)
        if v in (0.0, 1.0):
            return int(v)
    except Exception:
        pass
    s = str(x).strip().lower()
    if s in ("f", "female"):
        return 1
    if s in ("m", "male"):
        return 0
    return np.nan


df["gender_dummy"] = df["gender"].apply(to_gender_dummy)
df["num_clips"] = pd.to_numeric(df["0"], errors="coerce").fillna(0) + \
                  pd.to_numeric(df["1"], errors="coerce").fillna(0)
for c in ["age_mos", "Maternal_Education_Level", "canonical_proportion"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# CORRECTED: CP z-scored over the full cohort
cohort = df["canonical_proportion"].dropna()
df["cp_scaled"] = (df["canonical_proportion"] - cohort.mean()) / cohort.std(ddof=0)
# control covariates standardized over the cohort (does not affect the CP slope)
df["age_s"] = (df["age_mos"] - df["age_mos"].mean()) / df["age_mos"].std(ddof=0)
df["med_s"] = (df["Maternal_Education_Level"] - df["Maternal_Education_Level"].mean()) / \
              df["Maternal_Education_Level"].std(ddof=0)

PRED = ["cp_scaled", "age_s", "gender_dummy", "med_s"]
OUTCOMES = [("GFTA_Standard", "A", "GFTA-2 (SS)", "#1f77b4"),
            ("EVT_Standard",  "B", "EVT-2 (SS)",  "#ffbf00")]


def fit(outcome):
    d = df.dropna(subset=[outcome, "num_clips"] + PRED).copy()
    # outcome z-scored over its own analysis sample (matches the scaled model)
    d["y_s"] = (d[outcome] - d[outcome].mean()) / d[outcome].std(ddof=0)
    w = d["num_clips"].astype(float).clip(lower=1)
    w = (w / w.mean()).values
    m = sm.WLS(d["y_s"], sm.add_constant(d[PRED]), weights=w).fit()
    return m, d


fits = {o[0]: fit(o[0]) for o in OUTCOMES}
cp_all = df["cp_scaled"].dropna()
x_lo, x_hi = float(cp_all.min()), float(cp_all.max())
cp_grid = np.linspace(x_lo, x_hi, 400)

plt.rcParams.update({"axes.labelsize": 16, "axes.labelweight": "bold",
                     "xtick.labelsize": 11, "ytick.labelsize": 11})
fig = plt.figure(figsize=(13.2, 5.6))
gs = GridSpec(1, 3, figure=fig, width_ratios=[1, 1, 0.5], wspace=0.25)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
ax_leg = fig.add_subplot(gs[0, 2]); ax_leg.axis("off")

for ax, (outcome, tag, ylab, color) in zip(axes, OUTCOMES):
    m, d = fits[outcome]
    sizes = np.clip(d["num_clips"] / 30.0, 20, 600)
    cmin, cmax = d["num_clips"].min(), d["num_clips"].max()
    denom = (cmax - cmin) if cmax > cmin else 1.0
    alphas = 0.3 + 0.7 * (d["num_clips"] - cmin) / denom
    r, g, b, _ = to_rgba(color)
    ax.scatter(d["cp_scaled"], d["y_s"], s=sizes, edgecolor="k", linewidth=0.35,
               c=[(r, g, b, float(a)) for a in alphas])
    Xp = pd.DataFrame({"const": 1.0, "cp_scaled": cp_grid,
                       "age_s": d["age_s"].mean(), "gender_dummy": d["gender_dummy"].mean(),
                       "med_s": d["med_s"].mean()})[m.params.index]
    pr = m.get_prediction(Xp).summary_frame(alpha=0.05)
    ax.plot(cp_grid, pr["mean"], color=color, linewidth=2.6)
    ax.fill_between(cp_grid, pr["mean_ci_lower"], pr["mean_ci_upper"], color=color, alpha=0.25)
    ax.set_xlabel("Canonical Proportion (Scaled)")
    ax.set_ylabel(ylab)
    ax.text(0.03, 0.92, f"({tag})", transform=ax.transAxes, fontsize=16, fontweight="bold")
    ax.text(0.05, 0.06, f"β = {m.params['cp_scaled']:.2f}", transform=ax.transAxes,
            fontsize=20, fontweight="bold")
    ax.set_xlim(x_lo, x_hi)
    q1, q99 = d["y_s"].quantile([0.01, 0.99])
    pad = 0.10 * (q99 - q1 + 1e-9)
    ax.set_ylim(float(q1 - pad), float(q99 + pad))
    ax.set_box_aspect(1)
    for s in ax.spines.values():
        s.set_visible(True); s.set_linewidth(1)
    print(f"{outcome}: N={len(d)}  beta={m.params['cp_scaled']:.3f}")

# --- Legend (clip sizes), matching the published Figures 4-5: thin boxed frame,
# no title, small dots, compact spacing, small font, comma-formatted labels ---
clip_sizes = [50, 200, 1000, 3000, 5000, 8000]
handles = [ax_leg.scatter([], [], s=np.clip(s / 70.0, 8, 130), color="gray",
                          alpha=0.7, edgecolor="k", linewidth=0.35)
           for s in clip_sizes]
labels = [f"= {s:,} clips" for s in clip_sizes]
leg = ax_leg.legend(handles, labels, loc="center left", frameon=True,
                    borderpad=0.9, labelspacing=1.2, handletextpad=0.9,
                    borderaxespad=0.0, fontsize=9)
leg.get_frame().set_edgecolor("0.6")
leg.get_frame().set_linewidth(0.8)

fig.subplots_adjust(left=0.06, right=0.995, top=0.97, bottom=0.12)
fig.savefig(out_png, dpi=300)
print("saved", out_png)
