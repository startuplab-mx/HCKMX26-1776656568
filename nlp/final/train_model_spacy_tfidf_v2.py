#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
train_model_spacy_tfidf_v2.py

Entrena LogisticRegression usando pkl/spacy_tfidf.pkl generado por normal.py.
Guarda modelo + vectorizador en un solo artifact:
    models/spacy_tfidf_sign_model.pkl
"""

import os
import pickle
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score


PKL_DATASET = "./pkl/spacy_tfidf.pkl"
MODEL_OUT = "models/spacy_tfidf_sign_model.pkl"


def main():
    print("=" * 70)
    print("ENTRENAMIENTO: spaCy + TF-IDF + LogisticRegression por signo")
    print("=" * 70)

    with open(PKL_DATASET, "rb") as f:
        data = pickle.load(f)

    required = ["X_train", "X_test", "y_train", "y_test", "vectorizer"]
    missing = [key for key in required if key not in data]
    if missing:
        raise KeyError(f"Faltan llaves en {PKL_DATASET}: {missing}")

    X_train = data["X_train"]
    X_test = data["X_test"]

    y_train = np.array(data["y_train"]).astype(float)
    y_test = np.array(data["y_test"]).astype(float)

    # Clasificacion por signo:
    # 1 = riesgo positivo
    # 0 = seguro / no positivo
    y_train_bin = (y_train > 0).astype(int)
    y_test_bin = (y_test > 0).astype(int)

    print("Distribucion train:", np.bincount(y_train_bin))

    if len(np.unique(y_train_bin)) < 2:
        raise ValueError("Se necesitan al menos dos clases: riesgo positivo y no positivo.")

    model = LogisticRegression(max_iter=1000, n_jobs=-1)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

    cv_results = cross_validate(
        model,
        X_train,
        y_train_bin,
        cv=cv,
        scoring=("accuracy", "roc_auc"),
        n_jobs=-1
    )

    print("\nAccuracy CV:", cv_results["test_accuracy"].mean())
    print("ROC-AUC CV:", cv_results["test_roc_auc"].mean())

    model.fit(X_train, y_train_bin)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test_bin, y_pred)
    roc_auc = roc_auc_score(y_test_bin, y_prob)

    print("\nRESULTADOS TEST:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")

    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)

    artifact = {
        "model": model,
        "vectorizer": data["vectorizer"],
        "normalization": data.get("normalization", "spacy"),
        "vectorization": data.get("vectorization", "tfidf"),
        "threshold": 0.5,
        "classes": model.classes_,
        "accuracy": float(accuracy),
        "roc_auc": float(roc_auc),
        "cv_accuracy": float(cv_results["test_accuracy"].mean()),
        "cv_roc_auc": float(cv_results["test_roc_auc"].mean()),
        "source_dataset": PKL_DATASET
    }

    with open(MODEL_OUT, "wb") as f:
        pickle.dump(artifact, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("\nModelo y vectorizador guardados en:")
    print(MODEL_OUT)

    print("\nEjemplos:")
    for i in range(min(5, X_test.shape[0])):
        print(f"Real: {y_test[i]:6.2f} | Prob riesgo+: {y_prob[i]:.3f} | Pred: {y_pred[i]}")


if __name__ == "__main__":
    main()
