"""
cp_models_tp1_tp1_concurrent_v2.py

Reproduces Table 4: CP at Timepoint 1 predicting concurrent (Timepoint 1)
standardized articulation (GFTA-2) and expressive vocabulary (EVT-2).

See cp_models_common.py for the modeling details and for what changed from v1.

Usage:
    python cp_models_tp1_tp1_concurrent_v2.py [path/to/tp1_tp1_master_with_scaled.csv]
"""
import sys
from cp_models_common import run_table

DEFAULT_MASTER = "data/tp1_tp1_master_with_scaled.csv"
OUTCOMES = ["GFTA_Standard", "EVT_Standard"]

if __name__ == "__main__":
    master = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MASTER
    run_table(master, OUTCOMES, "TABLE 4 — Timepoint 1 concurrent analyses")
