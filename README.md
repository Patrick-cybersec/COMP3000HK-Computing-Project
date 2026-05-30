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
Usage
Enroll a New User
bash
python bioguard_ml.py
Click Register New Profile

Enter username & password

Complete 3 pangram sessions (≥ 50s each)

Login & Monitor
Enter credentials → Login & Monitor

System monitors keystrokes

Lockout triggered if anomaly rate > threshold

Evaluation
bash
python evaluate_models.py
Generates ROC AUC, precision, recall, F1 scores per subject.

Admin Listener
bash
uvicorn admin_listener:app --reload --host 127.0.0.1 --port 8000
Receives alerts with structured metadata.

Ethical Considerations
Only keystroke timing data collected (no text content)

Local encrypted storage

GDPR & HK Privacy Ordinance compliance

Consent form required for all volunteers

Repository Contents
bioguard_ml.py – main client

admin_listener.py – backend listener

evaluate_models.py – evaluation script

plot_results.py – visualization

docs/consent_form.pdf – template consent form

docs/poster.pdf – showcase poster
