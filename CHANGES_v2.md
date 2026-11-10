# Statistical analysis notes

The notebooks and scripts in this repository reproduce the published
**Tables 4, 5, and 6** and **Figure 3** from the `data/` masters. CP is
standardized once over the full cohort, in code, and each scaled outcome is
z-scored over its own analysis sample.

## Post-publication data correction: one child's gender covariate

One child's gender was recorded inconsistently across the analysis dataframes
(female in the Timepoint 1 dataframes, male in the Timepoint 2–3 dataframe and
in the lab's master records; male is correct). The shared `data/` files carry
the correction, so a handful of Table 4 and Table 5 cells shift in their final
digits relative to the typeset tables (e.g., Table 4 EVT-2 scaled β
0.63 → 0.62); no sign or significance level changes.

## Remaining last-digit discrepancies vs. the typeset tables

Beyond the correction above, re-runs match the typeset tables cell for cell
apart from a few final-digit rounding differences (e.g., Table 6 GFTA-2 χ²
prints as 6.59 here and 6.60 in the proof).

## Files

| File | Reproduces |
|------|-----------|
| `cp_models_common.py` | shared model-fitting / reporting (used by the `.py` drivers) |
| `cp_models_tp1_tp1_concurrent_v2.{py,ipynb}` | Table 4 |
| `cp_models_tp1_tp2_longitudinal_v2.{py,ipynb}` | Table 5 |
| `cp_models_tp2_tp3_longitudinal_v2.{py,ipynb}` | Table 6 |
| `figure3_concurrent_v2.py` | Figure 3 |

The `.ipynb` notebooks are self-contained (no import needed); the `.py` drivers
import `cp_models_common.py`. Both paths give identical results. Each script takes
the master-CSV path as a command-line argument. Requires `pandas`, `numpy`,
`statsmodels`, `scipy` (and `matplotlib` for the figure).

## Models fit (per outcome)

```
Baseline (unscaled) : OLS  outcome        ~ age + gender + maternal_ed
Expanded (unscaled) : OLS  outcome        ~ age + gender + maternal_ed + CP_scaled
Expanded (scaled)   : WLS  outcome_scaled ~ age + gender + maternal_ed + CP_scaled   (weights)
Weighted            : WLS  outcome        ~ age + gender + maternal_ed + CP_scaled   (weights)
```

CP_scaled = CP z-scored over the full cohort. outcome_scaled = outcome z-scored
over its own complete-case sample. Weights = (canonical + non-canonical clips)
normalized to mean 1. All four models for an outcome are fit on the same
complete-case sample so the likelihood-ratio tests are valid.
