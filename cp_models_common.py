"""
cp_models_common.py  (v2)

Shared model-fitting and reporting utilities for the canonical-proportion (CP)
regression analyses reported in Tables 4-6 of the manuscript.

WHAT CHANGED FROM v1 (why this file exists)
-------------------------------------------
The original per-timepoint notebooks recomputed the CP z-score *inside each
outcome's own complete-case subset* (e.g. they did
    cp_z = (cp - cp.mean()) / cp.std()
after dropping rows missing that outcome). Because every outcome drops a
different set of rows, that produced a different CP standard deviation per model,
and CP coefficients that do NOT match the intended cohort-standardized analysis.

This module standardizes CP **once per timepoint over the full cohort** (every
child with a CP value in that master), computed here in code rather than read
from a pre-stored column. The scaled outcome (used by the scaled-outcome model)
is z-scored over each outcome's own complete-case analysis sample.

Note on the concurrent (Timepoint 1) master: a pre-stored
`canonical_proportion_scaled` column in that file had been computed over only the
117 GFTA-complete children, which (a) shifted the concurrent CP betas and (b)
silently dropped the 6 EVT-2 children who lacked GFTA from the EVT-2 model
(N = 116 instead of 122). Computing the scaling in code over the full cohort
fixes both: the EVT-2 concurrent model now uses all 122 children and the
concurrent CP betas are on the same cohort-level scale as Tables 5-6. The
Timepoint 1->2 and 2->3 masters were already scaled over their full cohorts, so
their results are unchanged.

Quantities that are invariant to how CP is scaled (R^2, log-likelihood, the LRT
chi-square, and all p-values) are unaffected by the scaling base; only the
reported CP beta/SE shift (and, for EVT-2 concurrent, everything shifts because
the sample grows from 116 to 122).

MODELS (per outcome), matching the manuscript
---------------------------------------------
  Baseline (unscaled) : OLS  outcome ~ age + gender + maternal_ed
  Expanded (unscaled) : OLS  outcome ~ age + gender + maternal_ed + CP_scaled
  Expanded (scaled)   : WLS  outcome_scaled ~ ... + CP_scaled   (weights = clips)
  Weighted            : WLS  outcome ~ ... + CP_scaled          (weights = clips)

Weights = number of canonical + non-canonical clips contributing to CP, normalized
to mean 1. Rescaling the demographic covariates does not change the CP coefficient
or any reported fit statistic, so covariates are left in raw units for clarity.

All four models for a given outcome are fit on the SAME complete-case sample so
the likelihood-ratio tests are valid.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2

COVARIATES = ["age_mos", "gender_dummy", "Maternal_Education_Level"]
CP = "cp_scaled"  # cohort-standardized CP, computed in load_master()


def to_gender_dummy(x):
    """Female = 1, Male = 0. Accepts 'M'/'F', 'male'/'female', or numeric 0/1."""
    try:
        v = float(x)
        if v in (0.0, 1.0):
            return int(v)
    except (TypeError, ValueError):
        pass
    s = str(x).strip().lower()
    if s in ("f", "female"):
        return 1
    if s in ("m", "male"):
        return 0
    return np.nan


def load_master(path):
    """Load a master CSV; add gender_dummy, num_clips, and cohort-scaled CP."""
    df = pd.read_csv(path)
    df["gender_dummy"] = df["gender"].apply(to_gender_dummy)
    # num_clips = canonical + non-canonical clips (CP denominator). Some masters
    # store it; the concurrent master keeps the per-class counts in columns 0..4.
    if "num_clips" not in df.columns:
        df["num_clips"] = df[["0", "1"]].astype(float).sum(axis=1)
    # Standardize CP ONCE over the full cohort (every child with a CP value),
    # ddof=0. This is computed here rather than read from a pre-stored column so
    # the scaling base is always the full cohort (see module docstring).
    cohort = df["canonical_proportion"].dropna()
    df["cp_scaled"] = (df["canonical_proportion"] - cohort.mean()) / cohort.std(ddof=0)
    return df


def _lrt(restricted, full):
    """Likelihood-ratio test of `full` vs nested `restricted`."""
    stat = 2.0 * (full.llf - restricted.llf)
    ddf = int(full.df_model - restricted.df_model)
    return stat, ddf, chi2.sf(stat, ddf)


def _ols(y, X):
    return sm.OLS(y, sm.add_constant(X)).fit()


def _wls(y, X, w):
    return sm.WLS(y, sm.add_constant(X), weights=w).fit()


def fit_outcome(df, outcome):
    """
    Fit all four models for one outcome and return a list of result dicts
    (one per model row) plus the analysis N.
    """
    needed = [outcome] + COVARIATES + [CP, "num_clips"]
    d = df.dropna(subset=needed).copy()
    n = len(d)

    # scaled outcome (for the scaled-outcome model): z-scored over this outcome's
    # own complete-case analysis sample, ddof=0.
    scaled_outcome = "__outcome_scaled__"
    d[scaled_outcome] = (d[outcome] - d[outcome].mean()) / d[outcome].std(ddof=0)

    # weights: clips normalized to mean 1 (guard against any non-positive)
    w = d["num_clips"].astype(float).clip(lower=1)
    w = (w / w.mean()).values

    Xb = d[COVARIATES]
    Xe = d[COVARIATES + [CP]]

    # --- unweighted (OLS): baseline + expanded, raw outcome ---
    ols_base = _ols(d[outcome], Xb)
    ols_exp = _ols(d[outcome], Xe)
    chi_u, df_u, p_u = _lrt(ols_base, ols_exp)

    # --- weighted (WLS): baseline + expanded, raw outcome ---
    wls_base = _wls(d[outcome], Xb, w)
    wls_exp = _wls(d[outcome], Xe, w)
    chi_w, df_w, p_w = _lrt(wls_base, wls_exp)

    # --- weighted + scaled outcome (WLS): baseline + expanded ---
    sca_base = _wls(d[scaled_outcome], Xb, w)
    sca_exp = _wls(d[scaled_outcome], Xe, w)
    chi_s, df_s, p_s = _lrt(sca_base, sca_exp)

    def row(model, fit, base_fit=None, lrt=None, show_cp=True):
        out = {
            "Variable": outcome,
            "Model": model,
            "beta": fit.params[CP] if show_cp else np.nan,
            "SE": fit.bse[CP] if show_cp else np.nan,
            "p": fit.pvalues[CP] if show_cp else np.nan,
            "R2": fit.rsquared,
            "LogLik": fit.llf,
            "chi2": np.nan,
            "p_LRT": np.nan,
        }
        if lrt is not None:
            out["chi2"], _, out["p_LRT"] = lrt
        return out

    return [
        row("Baseline (unscaled)", ols_base, show_cp=False),
        row("Expanded (unscaled)", ols_exp, lrt=(chi_u, df_u, p_u)),
        row("Expanded (scaled)", sca_exp, lrt=(chi_s, df_s, p_s)),
        row("Weighted", wls_exp, lrt=(chi_w, df_w, p_w)),
    ], n


def _fmt_p(p):
    if pd.isna(p):
        return "—"
    return "<.001" if p < 0.001 else f"{p:.3f}".lstrip("0")


def _stars(p):
    if pd.isna(p):
        return ""
    return "***" if p <= 0.001 else "**" if p <= 0.01 else "*" if p <= 0.05 else ""


def run_table(path, outcomes, table_label):
    """Fit every outcome for one timepoint and print a Table-4/5/6-style summary."""
    df = load_master(path)
    print(f"\n{'='*78}\n{table_label}\nsource: {path}\n{'='*78}")
    header = f"{'Variable':<22}{'Model':<20}{'beta':>7}{'SE':>7}{'p':>8}{'R2':>6}{'LogLik':>10}{'chi2':>8}{'p(LRT)':>9}"
    print(header)
    print("-" * len(header))
    rows_all = []
    for outcome in outcomes:
        rows, n = fit_outcome(df, outcome)
        print(f"# {outcome}  (N = {n})")
        for r in rows:
            b = "—" if pd.isna(r["beta"]) else f"{r['beta']:.2f}"
            se = "—" if pd.isna(r["SE"]) else f"{r['SE']:.2f}"
            p = _fmt_p(r["p"]) + _stars(r["p"])
            chi = "—" if pd.isna(r["chi2"]) else f"{r['chi2']:.2f}"
            plrt = (_fmt_p(r["p_LRT"]) + _stars(r["p_LRT"])) if not pd.isna(r["p_LRT"]) else "—"
            print(f"{'':<22}{r['Model']:<20}{b:>7}{se:>7}{p:>8}{r['R2']:>6.2f}{r['LogLik']:>10.2f}{chi:>8}{plrt:>9}")
            rr = dict(r); rr["N"] = n
            rows_all.append(rr)
    return pd.DataFrame(rows_all)
