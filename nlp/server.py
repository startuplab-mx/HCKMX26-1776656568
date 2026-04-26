#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py  –  Servidor FastAPI para el pipeline de clasificación de textos.
Importa directamente la lógica de predict_texto_spacy_tfidf_v2.py
en lugar de llamarlo como subproceso, evitando el bug del return temprano.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import shutil
import os
import pickle
import re
import numpy as np

try:
    import spacy
except Exception:
    spacy = None

# ── Spacy opcional ────────────────────────────────────────────────────────────
try:
    import spacy as _spacy
except Exception:
    _spacy = None

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Pipeline de Clasificación de Textos",
    description=(
        "API para organizar datos, normalizar textos, entrenar modelos "
        "y evaluar consultas de riesgo con spaCy + TF-IDF."
    ),
    version="2.0.0",
)

# ─────────────────────────────────────────────────────────────────────────────
# Directorios
# ─────────────────────────────────────────────────────────────────────────────
DATASETS_DIR = "datasets"
RESULTS_DIR = "results"
MODELS_DIR = "models"

for _d in [DATASETS_DIR, RESULTS_DIR, MODELS_DIR, f"{DATASETS_DIR}/original_dataset"]:
    os.makedirs(_d, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Lógica de predicción (inline, sin subproceso)
# Reproduce exactamente la lógica de predict_texto_spacy_tfidf_v2.py
# ─────────────────────────────────────────────────────────────────────────────
_nlp_cache: dict = {}  # cache de modelos spaCy ya cargados


def clean_text(text: str) -> str:
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


def predict_one(
    text: str,
    model_path: str = "models/spacy_tfidf_sign_model.pkl",
    spacy_model: str = "es_core_news_sm",
    threshold: float = 0.5,
) -> dict:
    """
    Carga el artefacto entrenado y devuelve la predicción para un texto.
    Retorna: text, normalized, prob, riesgo_binario, riesgo_0_5.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Modelo no encontrado en '{model_path}'. "
            "Ejecuta primero POST /modelo/entrenar."
        )

    with open(model_path, "rb") as f:
        artifact = pickle.load(f)

    model = artifact["model"]
    vectorizer = artifact["vectorizer"]

    normalized = normalize_spacy_one(text, spacy_model=spacy_model)
    X = vectorizer.transform([normalized])
    proba = model.predict_proba(X)

    classes = list(getattr(model, "classes_", [0, 1]))
    idx = classes.index(1) if 1 in classes else len(classes) - 1
    prob = float(proba[0, idx])

    riesgo_binario = int(prob >= threshold)
    riesgo_0_5 = int(np.clip(round(prob * 5), 0, 5))

    return {
        "text": text,
        "normalized": normalized,
        "prob": round(prob, 6),
        "riesgo_binario": riesgo_binario,
        "riesgo_0_5": riesgo_0_5,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helper para subprocesos (scripts externos)
# ─────────────────────────────────────────────────────────────────────────────
def run_script(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def save_upload(upload: UploadFile, destination: str):
    with open(destination, "wb") as f:
        shutil.copyfileobj(upload.file, f)


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class ScriptResult(BaseModel):
    returncode: int
    stdout: str
    stderr: str
    message: str


class PredictRequest(BaseModel):
    text: str
    model_path: Optional[str] = "models/spacy_tfidf_sign_model.pkl"
    spacy_model: Optional[str] = "es_core_news_sm"
    threshold: Optional[float] = 0.5


class PredictResponse(BaseModel):
    text: str
    normalized: str
    prob: float
    riesgo_binario: int
    riesgo_0_5: int


# ─────────────────────────────────────────────────────────────────────────────
# 1 · Datos
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/datasets/upload",
    summary="Sube un CSV al directorio de datasets",
    tags=["1 - Datos"],
)
async def upload_csv(
    file: UploadFile = File(...),
    dataset_type: str = Query(
        ...,
        description="Tipo de dataset: 'malign' o 'good'",
        pattern="^(malign|good)$",
    ),
):
    """
    Guarda el archivo como **malign_dataset.csv** o **good_dataset.csv**
    dentro de `datasets/`.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Solo se aceptan archivos .csv")

    dest = os.path.join(DATASETS_DIR, f"{dataset_type}_dataset.csv")
    save_upload(file, dest)
    return {"message": f"Archivo guardado en '{dest}'", "path": dest}


@app.post(
    "/datasets/organizar",
    response_model=ScriptResult,
    summary="Ejecuta datos.py para concatenar y organizar datasets",
    tags=["1 - Datos"],
)
async def organizar_datos():
    """
    Corre `datos.py`.
    Genera el dataset original en `datasets/original_dataset/`.
    """
    r = run_script(["python", "datos.py"])
    return ScriptResult(
        **r,
        message="OK" if r["returncode"] == 0 else "Error al ejecutar datos.py",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2 · Normalización
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/normalizacion/ejecutar",
    response_model=ScriptResult,
    summary="Ejecuta normal.py para generar pickles normalizados",
    tags=["2 - Normalización"],
)
async def normalizar_textos():
    """
    Corre `normal.py`.
    Genera los `.pkl` con split 80/20 y 5-fold listo para entrenamiento.
    """
    r = run_script(["python", "normal.py"])
    return ScriptResult(
        **r,
        message="Normalización completada"
        if r["returncode"] == 0
        else "Error en normalización",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3 · Experimentos
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/experimentos/{nombre_experimento}",
    response_model=ScriptResult,
    summary="Ejecuta un experimento de la carpeta experiments/",
    tags=["3 - Experimentos"],
)
async def ejecutar_experimento(nombre_experimento: str):
    """
    Corre `experiments/<nombre_experimento>.py`.
    Ejemplo: `/experimentos/clasificacion_riesgo`
    """
    script = os.path.join("experiments", f"{nombre_experimento}.py")
    if not os.path.exists(script):
        raise HTTPException(404, f"Experimento '{script}' no encontrado.")
    r = run_script(["python", script])
    return ScriptResult(
        **r,
        message="Experimento completado"
        if r["returncode"] == 0
        else "Error en experimento",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4 · Entrenamiento
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/modelo/entrenar",
    response_model=ScriptResult,
    summary="Entrena el modelo final spaCy + TF-IDF v2",
    tags=["4 - Modelo Final"],
)
async def entrenar_modelo():
    """
    Corre `final/train_model_spacy_tfidf_v2.py`.
    El dump del modelo se guarda en `models/`.
    """
    r = run_script(["python", "final/train_model_spacy_tfidf_v2.py"])
    return ScriptResult(
        **r,
        message="Entrenamiento completado"
        if r["returncode"] == 0
        else "Error en entrenamiento",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5 · Evaluación en lote
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/evaluar/lote",
    summary="Evalúa un CSV de consultas y devuelve el TSV de predicciones",
    tags=["5 - Evaluación"],
)
async def evaluar_lote(
    file: UploadFile = File(...),
    project_format: bool = Query(
        False,
        description="Si True, genera salida en formato proyecto (mensaje + riesgo)",
    ),
):
    """
    Recibe un CSV con consultas, lo evalúa con el modelo entrenado
    y retorna el TSV de predicciones para descarga.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Solo se aceptan archivos .csv")

    input_path = os.path.join(DATASETS_DIR, "consulta_temp.csv")
    output_name = (
        "predicciones_formato_proyecto.tsv"
        if project_format
        else "predicciones_riesgo.tsv"
    )
    output_path = os.path.join(RESULTS_DIR, output_name)

    save_upload(file, input_path)

    cmd = [
        "python",
        "final/evaluar_consultas_riesgo_spacy_tfidf_v2.py",
        "--input",
        input_path,
        "--output",
        output_path,
    ]
    if project_format:
        cmd.append("--project-format")

    r = run_script(cmd)

    if r["returncode"] != 0:
        raise HTTPException(
            500,
            detail=f"Error al evaluar consultas:\n{r['stderr']}",
        )
    if not os.path.exists(output_path):
        raise HTTPException(500, "El script no generó el archivo de salida.")

    return FileResponse(
        path=output_path,
        media_type="text/tab-separated-values",
        filename=output_name,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6 · Predicción individual  (lógica inline — sin subproceso)
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/predecir",
    response_model=PredictResponse,
    summary="Predice el riesgo de un texto individual",
    tags=["6 - Predicción"],
)
async def predecir_texto(body: PredictRequest):
    """
    Evalúa un texto libre con el modelo entrenado.

    | Campo | Descripción |
    |---|---|
    | **prob** | Probabilidad de riesgo (0.0 – 1.0) |
    | **riesgo_binario** | 0 = seguro · 1 = riesgo |
    | **riesgo_0_5** | Escala de 0 a 5 |

    Los parámetros `model_path`, `spacy_model` y `threshold` son opcionales;
    usan los valores por defecto del modelo entrenado si no se envían.
    """
    try:
        result = predict_one(
            text=body.text,
            model_path=body.model_path,
            spacy_model=body.spacy_model,
            threshold=body.threshold,
        )
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error en predicción: {e}")

    return PredictResponse(**result)


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────────
@app.get(
    "/estado",
    summary="Verifica qué artefactos existen en disco",
    tags=["Utilidades"],
)
async def estado():
    """
    Devuelve un resumen de los archivos generados por el pipeline:
    datasets, pickles, modelos y resultados.
    """

    def ls(path: str) -> list[str]:
        return sorted(os.listdir(path)) if os.path.exists(path) else []

    return {
        "datasets": ls(DATASETS_DIR),
        "original_dataset": ls(f"{DATASETS_DIR}/original_dataset"),
        "pickles": [f for f in ls(".") if f.endswith(".pkl")],
        "models": ls(MODELS_DIR),
        "results": ls(RESULTS_DIR),
    }


@app.get(
    "/resultados/{filename}",
    summary="Descarga un archivo de resultados generado",
    tags=["Utilidades"],
)
async def descargar_resultado(filename: str):
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, f"'{filename}' no encontrado en results/")
    return FileResponse(path=path, filename=filename)


# ─────────────────────────────────────────────────────────────────────────────
# Entrada directa
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)