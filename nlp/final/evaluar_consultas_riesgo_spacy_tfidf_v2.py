#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
evaluar_consultas_riesgo_spacy_tfidf_v2.py

Objetivo:
- Leer un archivo de consultas en el formato del proyecto.
- Mantener la lectura tipo datos.py:
    * columna user_comments
    * separadores: |,  -->  <--
    * tomar el texto despues de ":"
- Normalizar los mensajes con spaCy, igual que normal.py.
- Transformar con el TfidfVectorizer ENTRENADO.
- Cargar el modelo entrenado y predecir riesgo.
- Guardar salida separada por tabs.

Uso basico:
    python evaluar_consultas_riesgo_spacy_tfidf_v2.py \
        --input msgs.csv \
        --model models/spacy_tfidf_sign_model.pkl \
        --output results/predicciones_riesgo.tsv

Salida completa:
    source_row, Mensaje, MensajeNormalizado, ProbabilidadRiesgo, RiesgoBinario, Riesgo

Salida en formato del proyecto:
    python evaluar_consultas_riesgo_spacy_tfidf_v2.py \
        --input msgs.csv \
        --output results/predicciones_formato_proyecto.tsv \
        --project-format

Salida project-format:
    Mensaje    Riesgo
"""

import argparse
import os
import pickle
import re
from typing import Iterable, List, Optional, Tuple, Any, Dict

import numpy as np
import pandas as pd

try:
    import spacy
except Exception:
    spacy = None


SPLIT_PATTERN = r"\|,|-->|<--"


def parse_separator(sep: str) -> str:
    """
    Permite pasar --sep "\\t" desde consola y convertirlo a tab real.
    """
    if sep == r"\t":
        return "\t"
    return sep


def divide_text(text: Any) -> List[str]:
    """
    Replica la idea de datos.py:
    - dividir por |, o --> o <--
    - tomar el contenido despues de ":"

    Diferencia intencional:
    - si una parte no tiene ":", no truena; conserva el texto.
    Esto hace que el script sea mas robusto para consultas nuevas.
    """
    if pd.isna(text):
        return []

    messages = []
    raw = str(text)

    for part in re.split(SPLIT_PATTERN, raw):
        part = part.strip()

        if not part:
            continue

        if ":" in part:
            part = part.split(":", 1)[1].strip()

        if part:
            messages.append(part)

    return messages


def clean_text(text: Any) -> str:
    """
    Misma limpieza base de normal.py.
    Nota:
    Se conserva el patron original [^a-z4áéíóúñü\\s] para mantener compatibilidad
    con el entrenamiento previo.
    """
    text = str(text).lower()
    text = re.sub(r"[^a-z4áéíóúñü\s]", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_spacy_model(model_name: str):
    if spacy is None:
        print("ADVERTENCIA: spaCy no esta instalado. Se usara solo clean_text().")
        return None

    try:
        nlp = spacy.load(model_name)
        print(f"spaCy cargado correctamente: {model_name}")
        return nlp
    except Exception as exc:
        print(f"ADVERTENCIA: no pude cargar spaCy '{model_name}': {exc}")
        print("Se usara solo clean_text().")
        return None


def normalize_spacy(corpus: Iterable[str], spacy_model: str = "es_core_news_sm") -> List[str]:
    """
    Normalizacion compatible con normal.py:
    - clean_text
    - lematizacion spaCy
    """
    cleaned = [clean_text(text) for text in corpus]
    nlp = load_spacy_model(spacy_model)

    if nlp is None:
        return cleaned

    normalized = []
    for doc in nlp.pipe(cleaned, batch_size=128):
        lemmas = [token.lemma_.lower() for token in doc]
        normalized.append(" ".join(lemmas))

    return normalized


def load_consultas(path: str, sep: str = "\t", text_col: Optional[str] = None) -> pd.DataFrame:
    """
    Lee el archivo de consultas.

    Soporta:
    1. columna user_comments con formato especial del proyecto
    2. columna Mensaje
    3. columna indicada por --text-col
    4. archivo de una sola columna
    """
    sep = parse_separator(sep)
    df = pd.read_csv(path, sep=sep)

    if df.empty:
        raise ValueError(f"El archivo esta vacio: {path}")

    if text_col:
        if text_col not in df.columns:
            raise KeyError(
                f"No existe la columna '{text_col}'. "
                f"Columnas disponibles: {list(df.columns)}"
            )
        selected_col = text_col
    elif "user_comments" in df.columns:
        selected_col = "user_comments"
    elif "Mensaje" in df.columns:
        selected_col = "Mensaje"
    elif len(df.columns) == 1:
        selected_col = df.columns[0]
    else:
        raise KeyError(
            "No pude detectar automaticamente la columna de texto. "
            "Usa --text-col. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    rows = []

    if selected_col == "user_comments":
        for source_row, raw_text in enumerate(df[selected_col].fillna("").tolist()):
            for msg in divide_text(raw_text):
                rows.append({"source_row": source_row, "Mensaje": msg})
    else:
        for source_row, raw_text in enumerate(df[selected_col].fillna("").tolist()):
            raw_text = str(raw_text).strip()
            if raw_text:
                rows.append({"source_row": source_row, "Mensaje": raw_text})

    if not rows:
        raise ValueError("No se extrajo ningun mensaje para evaluar.")

    return pd.DataFrame(rows, columns=["source_row", "Mensaje"])


def load_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def load_model_and_vectorizer(
    model_path: str,
    vectorizer_pkl: Optional[str] = "pkl/spacy_tfidf.pkl"
) -> Tuple[Any, Any, Dict[str, Any]]:
    """
    Carga modelo y vectorizador.

    Soporta 3 formas:
    A) artifact dict con:
        {"model": model, "vectorizer": vectorizer, ...}
    B) artifact dict con solo:
        {"model": model, ...}
       y el vectorizer se obtiene desde --vectorizer-pkl
    C) pickle que es directamente el modelo
       y el vectorizer se obtiene desde --vectorizer-pkl
    """
    artifact = load_pickle(model_path)

    metadata: Dict[str, Any] = {}

    if isinstance(artifact, dict) and "model" in artifact:
        model = artifact["model"]
        vectorizer = artifact.get("vectorizer")
        metadata.update(artifact)
    else:
        model = artifact
        vectorizer = None

    if vectorizer is None:
        if not vectorizer_pkl:
            raise KeyError(
                "El modelo no contiene vectorizer y no se proporciono --vectorizer-pkl."
            )

        vec_artifact = load_pickle(vectorizer_pkl)

        if isinstance(vec_artifact, dict) and "vectorizer" in vec_artifact:
            vectorizer = vec_artifact["vectorizer"]
            metadata.setdefault("normalization", vec_artifact.get("normalization", "spacy"))
            metadata.setdefault("vectorization", vec_artifact.get("vectorization", "tfidf"))
        else:
            raise KeyError(
                f"No encontre 'vectorizer' dentro de {vectorizer_pkl}. "
                "Asegurate de usar el pkl generado por normal.py, por ejemplo pkl/spacy_tfidf.pkl."
            )

    return model, vectorizer, metadata


def probability_positive_class(model: Any, X) -> np.ndarray:
    """
    Devuelve probabilidad de clase positiva/riesgosa.
    En el entrenamiento por signo:
        0 = seguro/no positivo
        1 = riesgoso/positivo
    """
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        classes = list(getattr(model, "classes_", [0, 1]))

        if 1 in classes:
            positive_index = classes.index(1)
        else:
            positive_index = len(classes) - 1

        return proba[:, positive_index]

    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        return 1.0 / (1.0 + np.exp(-scores))

    pred = model.predict(X)
    return np.asarray(pred, dtype=float)


def evaluate_messages(
    df_messages: pd.DataFrame,
    model: Any,
    vectorizer: Any,
    threshold: float = 0.5,
    spacy_model: str = "es_core_news_sm"
) -> pd.DataFrame:
    messages = df_messages["Mensaje"].astype(str).tolist()

    normalized = normalize_spacy(messages, spacy_model=spacy_model)

    # MUY IMPORTANTE:
    # aqui se usa transform(), no fit_transform().
    # El vocabulario debe ser exactamente el mismo del entrenamiento.
    X = vectorizer.transform(normalized)

    prob = probability_positive_class(model, X)
    prob = np.asarray(prob, dtype=float)

    riesgo_binario = (prob >= threshold).astype(int)

    # Modelo binario -> aproximacion a escala 0-5 usando probabilidad.
    riesgo_0_5 = np.rint(prob * 5).astype(int)
    riesgo_0_5 = np.clip(riesgo_0_5, 0, 5)

    result = df_messages.copy()
    result["MensajeNormalizado"] = normalized
    result["ProbabilidadRiesgo"] = np.round(prob, 6)
    result["RiesgoBinario"] = riesgo_binario
    result["Riesgo"] = riesgo_0_5

    return result


def save_results(df: pd.DataFrame, output_path: str, project_format: bool = False):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if project_format:
        cols = ["Mensaje", "Riesgo"]
    else:
        cols = [
            "source_row",
            "Mensaje",
            "MensajeNormalizado",
            "ProbabilidadRiesgo",
            "RiesgoBinario",
            "Riesgo",
        ]

    df[cols].to_csv(
        output_path,
        sep="\t",
        index=False,
        encoding="utf-8-sig"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Evalua consultas de riesgo con modelo spaCy + TF-IDF."
    )

    parser.add_argument("--input", required=True, help="Archivo de consultas: .csv/.tsv")
    parser.add_argument(
        "--model",
        default="models/spacy_tfidf_sign_model.pkl",
        help="Pickle del modelo entrenado."
    )
    parser.add_argument(
        "--vectorizer-pkl",
        default="pkl/spacy_tfidf.pkl",
        help=(
            "Pickle generado por normal.py que contiene el TfidfVectorizer. "
            "Solo se usa si --model no trae vectorizer."
        )
    )
    parser.add_argument(
        "--output",
        default="results/predicciones_riesgo.tsv",
        help="Ruta de salida TSV."
    )
    parser.add_argument(
        "--sep",
        default=r"\t",
        help="Separador de entrada. Usa '\\t' para tab o ',' para CSV normal."
    )
    parser.add_argument(
        "--text-col",
        default=None,
        help="Nombre de columna de texto si no es user_comments ni Mensaje."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Umbral para convertir probabilidad a RiesgoBinario."
    )
    parser.add_argument(
        "--spacy-model",
        default="es_core_news_sm",
        help="Modelo spaCy en espanol."
    )
    parser.add_argument(
        "--project-format",
        action="store_true",
        help="Guardar solo Mensaje y Riesgo, separado por tabs."
    )

    args = parser.parse_args()

    consultas = load_consultas(
        path=args.input,
        sep=args.sep,
        text_col=args.text_col
    )

    model, vectorizer, metadata = load_model_and_vectorizer(
        model_path=args.model,
        vectorizer_pkl=args.vectorizer_pkl
    )

    predicciones = evaluate_messages(
        df_messages=consultas,
        model=model,
        vectorizer=vectorizer,
        threshold=args.threshold,
        spacy_model=args.spacy_model
    )

    save_results(
        df=predicciones,
        output_path=args.output,
        project_format=args.project_format
    )

    print("=" * 70)
    print("EVALUACION FINALIZADA")
    print("=" * 70)
    print(f"Entrada:          {args.input}")
    print(f"Modelo:           {args.model}")
    print(f"Vectorizer pkl:   {args.vectorizer_pkl}")
    print(f"Salida:           {args.output}")
    print(f"Mensajes:         {len(predicciones)}")
    print(f"Project format:   {args.project_format}")
    print("\nDistribucion Riesgo 0-5:")
    print(predicciones["Riesgo"].value_counts().sort_index().to_string())

    print("\nPrimeros ejemplos:")
    preview_cols = ["Mensaje", "ProbabilidadRiesgo", "RiesgoBinario", "Riesgo"]
    print(predicciones[preview_cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
