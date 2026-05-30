# COMP3000HK-Computing-Project
# BioGuard – Spatially Aware Keystroke Authentication

## Overview
BioGuard is a continuous authentication prototype that uses keystroke dynamics to detect impostors in real time. It combines **IsolationForest** and **OneClassSVM** anomaly detectors, supports adaptive retraining, and enforces strict lockouts with audit logging.

## Features
- Fixed‑text enrollment (pangram sessions)
- Real‑time monitoring with anomaly thresholds
- Lockout & unlock workflow
- Adaptive retraining with confirmed good samples
- Administrative listener & dashboard
- Evaluation scripts with ROC AUC, precision, recall, F1 metrics
- Privacy‑conscious design (timing data only, encrypted profiles)

## Requirements
- Python 3.11
- Dependencies: `numpy`, `pandas`, `scikit-learn`, `joblib`, `cryptography`, `pynput`, `tkinter`, `matplotlib`, `shap`, `requests`

Install:
```bash
pip install -r requirements.txt
