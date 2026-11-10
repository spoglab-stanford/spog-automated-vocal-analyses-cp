# Automated Vocal Analyses Over Child-Centered Recordings to Predict Speech-Language Development

This repo is associated with the paper:

Ott, C., & Cychosz, M. (2026). Connecting preschoolers’ spontaneous speech patterns to future language skills: A 3-year concurrent and longitudinal cohort study of canonical proportion as a developmental index. *Journal of Speech, Language, and Hearing Research, 69*, 4232–4250. https://doi.org/10.1044/2026_JSLHR-25-00938  

## Overview

Daylong (~16 hour) naturalistic child speech audio recordings (N=155, the exact # varied by time point) of children at age 3 and 4 were chopped into 500ms clips based on vocalization timestamps, then processed through a deep learning model to classify each clip into their respective category (0: canonical, 1: non-canonical, 2: crying, 3: laughing, 4: junk). After classification, statistical analyses were run to determine canonical proportion as a predictor of various speech-language assessments of the same children concurrently and 1 year later at 4 and 5. For more information on model architecture, please see Zhang et al. (2025) *Proceedings of Interspeech*. For more information on the dataset (which is too large to share publicly on this platform, but is available for re-use), please contact author directly. 

Key Terms:
CHN = Key Child Near vocalization
.its = output file generated from naturalistic daylong recording

The following files were used for preprocessing of audio and statistical analysis: 

## 1. Audio Preprocessing 
### 1.1 get_CHN_clips.py
- takes in raw audio and retrieves CHN clips based on timestamps in the .its file for the corresponding recording

### 1.2 chop_CHN_clips.py
- chops each CHN clip into a 500ms bit, appending any remainder <200ms onto the last utterance
- stores metadata of all utterances
    - unique utterance id
    - recording + CHN clip it came from
    - child_id
    - age(mos)
    - duration of clip

## 2. Data

The `data/` directory contains the three analysis dataframes ("masters"), one per analysis. Each row is one child at one timepoint:

- `data/tp1_tp1_master_with_scaled.csv` — Timepoint 1 concurrent analysis (Table 4)
- `data/tp1_tp2_master_with_scaled.csv` — Timepoint 1 → Timepoint 2 longitudinal analysis (Table 5)
- `data/tp2_tp3_master_with_scaled.csv` — Timepoint 2 → Timepoint 3 longitudinal analysis (Table 6)

Columns:
- `child_id` — study-specific pseudonymous ID (`cp001`–`cp154`), consistent for the same child across the three files. These IDs are specific to this release and are not used in any other dataset.
- `0`, `1` — number of 500ms clips classified canonical (0) and non-canonical (1); `num_clips` = canonical + non-canonical, the CP denominator (used as the model weight)
- `age_mos`, `gender`, `Maternal_Education_Level` — demographic covariates
- `canonical_proportion` — CP = canonical / (canonical + non-canonical)
- assessment columns (`GFTA_Standard`, `EVT_Standard`, `PPVT_Standard`, `CTOPP_Elision_Scaled`, `avg_rwr_accuracy`, `avg_nwr_accuracy`, `SAILS_ProportionTestCorrect`) — scores available at that analysis's outcome timepoint
- `*_scaled` columns, where present — pre-computed z-scored versions; the analysis code standardizes CP and outcomes in code (see `CHANGES_v2.md`) and does not rely on these

Raw audio and clip-level classifier outputs are not included due to size (~1M+ clips); contact the authors.

## 3. Modeling and Statistical Analysis
The `cp_models_*_v2.ipynb` notebooks contain multiple linear regression models and statistical analysis for canonical proportion (CP) at Timepoint X as predictor of speech-language measures at Timepoint Y. They reproduce the paper's Tables 4, 5, and 6 from the `data/` masters; shared code lives in `cp_models_common.py`, and `CHANGES_v2.md` documents how these v2 notebooks differ from the originally posted v1 notebooks (a CP-standardization correction that was incorporated into the published Table 4 at proofs).

Run each notebook top to bottom from the repository root, or equivalently:

```
jupyter nbconvert --to notebook --execute cp_models_tp1_tp1_concurrent_v2.ipynb
```

Requirements: Python 3 with `pandas`, `numpy`, `statsmodels`, `scipy`, and `jupyter` (plus `matplotlib` and `scikit-learn` for the figure script and visuals notebooks). Each notebook also exists as a command-line script (`python cp_models_tp1_tp1_concurrent_v2.py [path/to/master.csv]`); the scripts import `cp_models_common.py` and print the same tables.

All analyses adhere to the following format:
- Baseline model
    - demographic variables as predictors
        - maternal education
        - gender
        - age
- Expanded (Unscaled) model
    - adds CP as an additional predictor
- Weighted (Unscaled) model
    - weights based on number of canonical and non-canonical clips contributing to the calculation of canonical proportion
    - higher weight is given to more clips contributing
- Scaled model
    - centers and scaled outcome variable to interpret results relative to each other
 
Models were created for ALL speech-language assessments that were available at that specific timepoint.

### 3.1 cp_models_tp1_tp1_concurrent_v2.ipynb (paper Table 4)
- At Timepoint 1 on Timepoint 1, models were created for the following speech/language assessments:
    - GFTA-2
    - EVT-2
 
### 3.2 cp_models_tp1_tp2_longitudinal_v2.ipynb (paper Table 5)
- At Timepoint 1 on Timepoint 2, models were created for the following speech/language assessments:
    - PPVT-4
    - CTOPP-2
    - Real Word Repetition Accuracy
    - Nonword Repetition Accuracy

### 3.3 cp_models_tp2_tp3_longitudinal_v2.ipynb (paper Table 6)
- At Timepoint 2 on Timepoint 3, models were created for the following speech/language assessments:
    - GFTA-2
    - EVT-2
    - CTOPP-2
    - SAILS
 
## 4. Data Visualizations

- `figure3_concurrent_v2.py` — generates the paper's Figure 3 (Timepoint 1 concurrent weighted scatterplots, GFTA-2 and EVT-2) from `data/tp1_tp1_master_with_scaled.csv`: `python figure3_concurrent_v2.py`
- `tp1_tp2_visuals.ipynb` — Timepoint 1 → Timepoint 2 weighted scatterplots (PPVT-4, CTOPP-2, Real Word Repetition, Nonword Repetition)
- `tp2_tp3_visuals.ipynb` — Timepoint 2 → Timepoint 3 weighted scatterplots (GFTA-2, EVT-2, CTOPP-2, SAILS)

The visuals notebooks read the `data/` masters directly (see paper for figures).

## Procedure

To apply this dataflow:

1. **Extract CHN Clips** — run `get_CHN_clips.py`  
   - Extracts child vocalization clips from raw daylong audio using timestamps from the `.its` file.  
   - **Input:** raw audio + `.its` file  
   - **Output:** CHN audio clips + metadata  

2. **Chop Clips Into 500ms Segments** — run `chop_CHN_clips.py`  
   - Splits each CHN clip into 500ms utterances and stores clip-level metadata.  
   - **Input:** CHN clips  
   - **Output:** 500ms utterances + metadata  

3. **Classify Utterances** — apply deep learning model  
   - Assigns a label to each utterance (canonical / non-canonical / other).  
   - **Input:** 500ms utterances  
   - **Output:** classification labels per utterance  

4. **Compute Canonical Proportion (CP)** — compute using classifier output  
   - Calculate CP per child per timepoint: CP = Canonical / (Canonical + Non-Canonical).  
   - **Input:** utterance-level labels  
   - **Output:** CP values per child per timepoint  

5. **Fit Statistical Models** — run appropriate `cp_models_*_v2` notebook  
   - Tests CP as predictor of speech-language outcomes (baseline, expanded, weighted, scaled models).  
   - **Input:** CP values + assessment scores (the `data/` masters)  
   - **Output:** regression model results (paper Tables 4–6)  

6. **Create Visualizations** — run `figure3_concurrent_v2.py` or the matching `tp*_tp*_visuals.ipynb` notebook  
   - Generates weighted scatterplots.  
   - **Input:** the `data/` masters  
   - **Output:** publication-ready visualizations  

Steps 1–4 require the raw audio and are included for transparency; steps 5–6 are fully reproducible from this repository alone.

