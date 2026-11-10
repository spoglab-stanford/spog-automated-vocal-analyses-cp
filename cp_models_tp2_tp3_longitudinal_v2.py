"""
cp_models_tp2_tp3_longitudinal_v2.py

Reproduces Table 6: CP at Timepoint 2 predicting Timepoint 3 outcomes —
articulation (GFTA-2), expressive vocabulary (EVT-2), phonological awareness
(CTOPP-2 Elision), and speech perception (SAILS).

See cp_models_common.py for the modeling details and for what changed from v1.

Usage:
    python cp_models_tp2_tp3_longitudinal_v2.py [path/to/tp2_tp3_master_with_scaled.csv]
"""
import sys
from cp_models_common import run_table

DEFAULT_MASTER = "data/tp2_tp3_master_with_scaled.csv"
OUTCOMES = [
    "GFTA_Standard",
    "EVT_Standard",
    "CTOPP_Elision_Scaled",
    "SAILS_ProportionTestCorrect",
]

if __name__ == "__main__":
    master = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MASTER
    run_table(master, OUTCOMES, "TABLE 6 — Timepoint 2 -> Timepoint 3")
