import pandas as pd, numpy as np, os

DATA_FILE = "public_dataset/DSL-StrongPasswordData.csv"
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_FILE)

# Identify subject column
subject_col = "subject"  # adjust if dataset uses different name

# Drop metadata columns
feature_cols = [c for c in df.columns if not c.lower().startswith("subject") and not c.lower().startswith("session")]

def extract_features(row):
    values = row[feature_cols].astype(float)
    hold = np.mean([v for c, v in zip(feature_cols, values) if c.startswith("H.")])
    flight = np.mean([v for c, v in zip(feature_cols, values) if c.startswith("DD.") or c.startswith("UD.")])
    hand = 0.5  # placeholder
    return [hold, flight, hand]

# Partition by subject
subjects = df[subject_col].unique()

for subj in subjects:
    genuine_rows = df[df[subject_col] == subj]
    impostor_rows = df[df[subject_col] != subj]

    genuine_vectors = np.array([extract_features(r) for _, r in genuine_rows.iterrows()])
    impostor_vectors = np.array([extract_features(r) for _, r in impostor_rows.iterrows()])

    # Save genuine
    np.save(os.path.join(OUT_DIR, f"cmu_subject{subj}_genuine.npy"), genuine_vectors)
    with open(os.path.join(OUT_DIR, f"cmu_subject{subj}_genuine.label"), "w") as f:
        f.write("0")

    # Save impostor
    np.save(os.path.join(OUT_DIR, f"cmu_subject{subj}_impostor.npy"), impostor_vectors)
    with open(os.path.join(OUT_DIR, f"cmu_subject{subj}_impostor.label"), "w") as f:
        f.write("1")

    print(f"Created account for subject {subj}: {len(genuine_vectors)} genuine, {len(impostor_vectors)} impostor samples")
