# convert_cmu.py
import pandas as pd, numpy as np, os

DATA_FILE = "public_dataset/DSL-StrongPasswordData.csv"
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_FILE)

# Drop metadata
feature_cols = [c for c in df.columns if not c.lower().startswith("subject") and not c.lower().startswith("session")]

vectors = []
for _, row in df.iterrows():
    values = row[feature_cols].astype(float)

    # Average hold times (columns starting with "H.")
    hold = np.mean([v for c, v in zip(feature_cols, values) if c.startswith("H.")])

    # Average digraph/flight times (columns starting with "DD." or "UD.")
    flight = np.mean([v for c, v in zip(feature_cols, values) if c.startswith("DD.") or c.startswith("UD.")])

    # Placeholder hand transition
    hand = 0.5

    vectors.append([hold, flight, hand])

arr = np.array(vectors)
npy_path = os.path.join(OUT_DIR, "cmu_impostor.npy")
np.save(npy_path, arr)

with open(npy_path.replace(".npy", ".label"), "w") as f:
    f.write("1")

print(f"Converted CMU dataset -> {npy_path} with {arr.shape[0]} samples, {arr.shape[1]} features, label=1")
