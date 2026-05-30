import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc, precision_score, recall_score, f1_score
from sklearn.utils import resample
import pandas as pd

def balance_dataset(X, y):
    X_gen = X[y == 0]; y_gen = y[y == 0]
    X_imp = X[y == 1]; y_imp = y[y == 1]

    if len(y_imp) > len(y_gen):
        X_imp_down, y_imp_down = resample(
            X_imp, y_imp,
            replace=False,
            n_samples=len(y_gen),
            random_state=42
        )
    else:
        X_imp_down, y_imp_down = X_imp, y_imp

    X_bal = np.vstack([X_gen, X_imp_down])
    y_bal = np.concatenate([y_gen, y_imp_down])
    return X_bal, y_bal

def evaluate_subject(X, y, subj_id):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_scores = model.predict_proba(X_test)[:,1]

    fpr, tpr, thresholds = roc_curve(y_test, y_scores)
    roc_auc = auc(fpr, tpr)

    eer_idx = np.argmin(np.abs(1 - tpr - fpr))
    optimal_threshold = thresholds[eer_idx]

    y_pred = (y_scores >= optimal_threshold).astype(int)

    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    return {
        "Subject": subj_id,
        "ROC AUC": round(roc_auc, 3),
        "Precision": round(prec, 3),
        "Recall": round(rec, 3),
        "F1": round(f1, 3),
        "Threshold": round(optimal_threshold, 3)
    }

def main():
    folder = "data"
    results = []

    # Load global CMU impostors once
    cmu_imp_path = os.path.join(folder, "cmu_impostor.npy")
    cmu_impostors = None
    if os.path.exists(cmu_imp_path):
        cmu_impostors = np.load(cmu_imp_path)

    for fn in os.listdir(folder):
        if fn.endswith("_genuine.npy"):
            base = fn.replace("_genuine.npy", "")
            g_path = os.path.join(folder, f"{base}_genuine.npy")
            i_path = os.path.join(folder, f"{base}_impostor.npy")

            X_g = np.load(g_path); y_g = np.zeros(len(X_g))

            # Local impostors
            if os.path.exists(i_path):
                X_i_local = np.load(i_path)
            else:
                X_i_local = np.empty((0, X_g.shape[1]))

            # Global impostors (local + CMU)
            impostors = []
            if len(X_i_local) > 0:
                impostors.append(X_i_local)
            if cmu_impostors is not None:
                impostors.append(cmu_impostors)

            if impostors:
                X_i_global = np.vstack(impostors)
                y_i_global = np.ones(len(X_i_global))

                # Local evaluation
                if len(X_i_local) > 0:
                    X_local = np.vstack([X_g, X_i_local])
                    y_local = np.concatenate([y_g, np.ones(len(X_i_local))])
                    X_local, y_local = balance_dataset(X_local, y_local)
                    results.append(evaluate_subject(X_local, y_local, base + "_local"))

                # Global evaluation
                X_global = np.vstack([X_g, X_i_global])
                y_global = np.concatenate([y_g, y_i_global])
                X_global, y_global = balance_dataset(X_global, y_global)
                results.append(evaluate_subject(X_global, y_global, base + "_global"))

    # Print results
    print("\n=== Multi-User Evaluation (Local vs Global Impostors) ===")
    print("Subject | ROC AUC | Precision | Recall | F1 | Threshold")
    for r in results:
        print(f"{r['Subject']:>15} | {r['ROC AUC']:>7} | {r['Precision']:>9} | {r['Recall']:>6} | {r['F1']:>4} | {r['Threshold']:>9}")

    df = pd.DataFrame(results)
    summary = df.mean(numeric_only=True)
    print("\n=== Summary Across All Accounts ===")
    print(f"Mean ROC AUC: {summary['ROC AUC']:.3f}")
    print(f"Mean Precision: {summary['Precision']:.3f}")
    print(f"Mean Recall: {summary['Recall']:.3f}")
    print(f"Mean F1: {summary['F1']:.3f}")
    print(f"Mean Threshold: {summary['Threshold']:.3f}")

if __name__ == "__main__":
    main()
