# Automated Vocal Analyses Over Child-Centered Recordings to Predict Speech-Language Development

This repo is associated with the paper "Connecting preschoolers’ spontaneous speech patterns to future language skills: A three-year concurrent and longitudinal cohort study of canonical proportion as a
developmental index"

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

## 2. Modeling and Statistical Analysis
### 2.1 cp_models.ipynb
- includes mutliple linear regression models and statistical analysis for canonical proportion as predictor of the following speech-language measures
    - GFTA-2
    - PPVT-4
    - CTOPP-2
    - Real Word Repetition Accuracy
    - Nonword Repetition Accuracy
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
 
## Procedure

To apply this dataflow:

1. Run script 1.1 on naturalistic raw audio recording with corresponding .its file.
2. Run script 1.2 and chop the vocalizations into 500ms clips so the model can process.
3. Use deep learning model to classify clips into respective labels.
4. Calculate canonical proportion for each child based on output (Canonical Proportion = Canonical/(Canonical + Non-Canonical))
5. Use speech-language scores and canonical proportion measures to fit statistical models using script 2.1.

