#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
predict_texto_spacy_tfidf_v2.py

Evalua una consulta individual usando el modelo guardado.
"""

import argparse
import pickle
import re
import numpy as np

try:
    import spacy
except Exception:
    spacy = None


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z4áéíóúñü\s]", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_spacy_one(text, spacy_model="es_core_news_sm"):
    cleaned = clean_text(text)

    if spacy is None:
        return cleaned

    try:
        nlp = spacy.load(spacy_model)
    except Exception:
        return cleaned

    doc = nlp(cleaned)
    return " ".join(token.lemma_.lower() for token in doc)


def main():
    parser = argparse.ArgumentParser(description="Predice riesgo para un texto individual.")
    parser.add_argument("--text", required=True, help="Texto a evaluar.")
    parser.add_argument("--model", default="models/spacy_tfidf_sign_model.pkl")
    parser.add_argument("--spacy-model", default="es_core_news_sm")
    parser.add_argument("--threshold", type=float, default=0.5)

    args = parser.parse_args()

    with open(args.model, "rb") as f:
        artifact = pickle.load(f)

    model = artifact["model"]
    vectorizer = artifact["vectorizer"]

    normalized = normalize_spacy_one(args.text, spacy_model=args.spacy_model)
    X = vectorizer.transform([normalized])

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", [0, 1]))
    idx = classes.index(1) if 1 in classes else len(classes) - 1

    prob = float(proba[0, idx])
    riesgo_binario = int(prob >= args.threshold)
    riesgo_0_5 = int(np.clip(round(prob * 5), 0, 5))

    print("Texto:", args.text)
    print("Normalizado:", normalized)
    print("ProbabilidadRiesgo:", round(prob, 6))
    print("RiesgoBinario:", riesgo_binario)
    print("Riesgo:", riesgo_0_5)


if __name__ == "__main__":
    main()
