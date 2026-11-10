"""
cp_models_tp1_tp2_longitudinal_v2.py

Reproduces Table 5: CP at Timepoint 1 predicting Timepoint 2 outcomes —
receptive vocabulary (PPVT-4), phonological awareness (CTOPP-2 Elision),
lexical-phonological access (real-word repetition), and phonological working
memory (nonword repetition).

See cp_models_common.py for the modeling details and for what changed from v1.

Usage:
    python cp_models_tp1_tp2_longitudinal_v2.py [path/to/tp1_tp2_master_with_scaled.csv]
"""
import sys
from cp_models_common import run_table

DEFAULT_MASTER = "data/tp1_tp2_master_with_scaled.csv"
OUTCOMES = [
    "PPVT_Standard",
    "CTOPP_Elision_Scaled",
    "avg_rwr_accuracy",
    "avg_nwr_accuracy",
]

if __name__ == "__main__":
    master = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MASTER
    run_table(master, OUTCOMES, "TABLE 5 — Timepoint 1 -> Timepoint 2")
