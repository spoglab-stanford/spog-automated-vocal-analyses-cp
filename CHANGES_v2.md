# Statistical analysis scripts — v2

These scripts replace the modeling notebooks in the public repo
(`spoglab-stanford/spog-automated-vocal-analyses-cp`). They reproduce the
manuscript's **Tables 4, 5, and 6** from the `*_master_with_scaled.csv` files,
and they **correct a CP-standardization bug in the Timepoint 1 concurrent
analysis** (see below).

## The fix

Canonical proportion (CP) must be standardized **once over the full cohort** and
then used for every outcome. The v1 notebooks instead re-standardized CP inside
each outcome's own complete-case subset, and — for the Timepoint 1 concurrent
master — relied on a pre-stored `canonical_proportion_scaled` column that had been
computed over only the **117 GFTA-complete** children. That had two effects:

1. It put the concurrent CP coefficients on a different scale than Tables 5–6.
2. It **silently dropped the 6 EVT-2 children who lacked GFTA**, so the EVT-2
   concurrent model ran on **N = 116** instead of **122**.

v2 standardizes CP in code over the full cohort (`load_master`) and z-scores each
scaled outcome over its own analysis sample. This:

- **reproduces Tables 5 and 6** (up to the corrections and last-digit items
  listed below; their masters were already scaled over
  the full cohort), and
- **fixes Table 4** — EVT-2 concurrent now uses all 122 children, and the
  concurrent CP betas are on the same cohort scale as the rest of the paper.

R², log-likelihoods, the LRT χ², and p-values are invariant to the CP scaling
base; for GFTA-2 only the betas/SEs change, while for EVT-2 everything shifts
because the sample grows from 116 to 122.

## Corrected Table 4 (vs. the originally typeset values)

| Variable | Model | β (was → now) | SE | R² | LogLik | χ² |
|---|---|---|---|---|---|---|
| GFTA-2 | Expanded (unscaled) | 4.28 → **4.61** | 1.15 → **1.24** | .19 | −450.76 | 13.61 |
| GFTA-2 | Expanded (scaled) | 0.55 → **0.60** | 0.12 → **0.13** | .21 | −171.97 | 19.69 |
| GFTA-2 | Weighted | 7.01 → **7.55** | 1.55 → **1.67** | .21 | −469.16 | 19.69 |
| EVT-2 | Baseline | — | — | .20 → **.21** | −472.81 → **−505.14** | — |
| EVT-2 | Expanded (unscaled) | 4.99 → **5.73** | 1.37 → **1.44** | .29 → **.31** | −466.25 → **−497.38** | 13.12 → **15.52** |
| EVT-2 | Expanded (scaled) | 0.54 → **0.63** | 0.10 | .30 → **.35** | −150.66 → **−160.45** | 24.87 → **32.92** |
| EVT-2 | Weighted | 9.17 → **10.81** | 1.78 → **1.80** | .30 → **.35** | −480.14 → **−506.97** | 24.87 → **32.92** |

GFTA-2 N = 117 (unchanged); EVT-2 N = 116 → **122**. All effects remain
p < .001 (the EVT-2 effect is now slightly stronger). **Figure 3** is regenerated
accordingly (`figure3_concurrent_v2.png`; GFTA β = 0.60, EVT β = 0.62, EVT panel
now 122 points).

Tables 5 and 6 are unchanged. Two pre-existing typos in the typeset proof, also
confirmed by re-running, are corrected in the paper separately: Table 5 NWR
Baseline R² (.72 → .07) and Table 4 GFTA Weighted log-likelihood
(−479.01 → −469.16).

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
| `cp_models_tp1_tp1_concurrent_v2.{py,ipynb}` | Table 4 (corrected) |
| `cp_models_tp1_tp2_longitudinal_v2.{py,ipynb}` | Table 5 |
| `cp_models_tp2_tp3_longitudinal_v2.{py,ipynb}` | Table 6 |
| `figure3_concurrent_v2.py` | Figure 3 (corrected) |

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
