import pandas as pd
import numpy as np
import os

DATA_DIR = "data"

for fn in os.listdir(DATA_DIR):
    if fn.endswith(".csv"):
        path = os.path.join(DATA_DIR, fn)

        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(f"Skipping {fn}: could not read CSV ({e})")
            continue

        # Detect format: 3-column or 5-column
        if all(col in df.columns for col in ["event", "key", "time"]):
            # New/collector format with header
            event_col, key_col, time_col = "event", "key", "time"
        elif df.shape[1] == 3:
            # Old format without header (assume order: event,key,time)
            df.columns = ["event", "key", "time"]
            event_col, key_col, time_col = "event", "key", "time"
        else:
            print(f"Skipping {fn}: unexpected columns {list(df.columns)}")
            continue

        press_times = {}
        vectors = []
        last_release_time = None
        last_hand_zone = None

        def get_zone(key: str):
            key = key.lower()
            if any(c in key for c in "qwertasdfgzxcvb"):
                return 1
            if any(c in key for c in "yuiophjklnm"):
                return 2
            return 0

        for _, row in df.iterrows():
            event = row[event_col]
            key = str(row[key_col])
            t = float(row[time_col])

            if event == "press":
                press_times[key] = t
            elif event == "release" and key in press_times:
                hold_time = t - press_times.pop(key)
                flight_time = 0.0
                if last_release_time is not None:
                    flight_time = min(t - last_release_time, 2.0)

                zone = get_zone(key)
                if last_hand_zone in [1, 2] and zone in [1, 2]:
                    hand_transition = 1.0 if last_hand_zone == zone else 0.0
                else:
                    hand_transition = 0.5

                last_release_time = t
                last_hand_zone = zone

                if hold_time < 1.0:  # filter out long presses
                    vectors.append([hold_time, flight_time, hand_transition])

        arr = np.array(vectors)
        npy_path = os.path.join(DATA_DIR, fn.replace(".csv", ".npy"))
        np.save(npy_path, arr)

        # Save a label file alongside
        label = 1 if "imp" in fn.lower() or "impostor" in fn.lower() else 0
        with open(npy_path.replace(".npy", ".label"), "w") as f:
            f.write(str(label))

        print(f"Converted {fn} -> {npy_path} with {len(arr)} samples, label={label}")
