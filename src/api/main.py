"""API FastAPI para servir el modelo de detección de fraude.

Expone endpoints de información, salud y predicción individual/en lote.
El modelo se carga desde `models/best_model.pkl` al iniciar la aplicación.
"""

import logging
import os
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List

from src.features.build_features import FEATURE_ORDER, build_features

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "models/best_model.pkl")
FRAUD_THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "0.5"))
API_VERSION = os.getenv("API_VERSION", "0.1.0")

FEATURES = FEATURE_ORDER


class TransactionInput(BaseModel):
    """Transacción individual de entrada."""

    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float


class PredictionOutput(BaseModel):
    """Resultado de una predicción individual."""

    is_fraud: bool
    fraud_probability: float
    threshold: float
    model_name: str


class BatchInput(BaseModel):
    """Lista de transacciones para predicción en lote."""

    transactions: List[TransactionInput] = Field(..., max_length=1000)


class BatchOutput(BaseModel):
    """Resultado de una predicción en lote."""

    predictions: List[PredictionOutput]
    total: int


class HealthOutput(BaseModel):
    """Estado del servicio y del modelo."""

    status: str
    model_loaded: bool
    model_path: str
    version: str


def _load_model():
    """Carga el modelo desde disco; devuelve None si no está disponible."""
    try:
        model = joblib.load(MODEL_PATH)
        logger.info("Modelo cargado desde %s", MODEL_PATH)
        return model
    except Exception as exc:  # noqa: BLE001 - degradación elegante intencional
        logger.warning("No se pudo cargar el modelo en %s: %s", MODEL_PATH, exc)
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo al iniciar y libera recursos al apagar."""
    app.state.model = _load_model()
    yield
    app.state.model = None


app = FastAPI(
    title="Fraud Detection API",
    description="API para predicción de fraude en transacciones bancarias.",
    version=API_VERSION,
    lifespan=lifespan,
)


def _predict_one(transaction: TransactionInput) -> PredictionOutput:
    """Genera la predicción de una transacción usando el modelo cargado.

    Recibe las 30 features crudas, aplica `build_features` para obtener
    hour, log_amount y V_sum, y reordena según el contrato del modelo
    (`feature_names_in_` si existe; si no, `FEATURE_ORDER`).
    """
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    payload = (
        transaction.model_dump()
        if hasattr(transaction, "model_dump")
        else transaction.dict()
    )
    raw = pd.DataFrame([payload], columns=["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"])
    features = build_features(raw)

    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        X = features[list(feature_names)]
    else:
        X = features[FEATURES]

    proba = float(model.predict_proba(X)[:, 1][0])
    return PredictionOutput(
        is_fraud=proba >= FRAUD_THRESHOLD,
        fraud_probability=proba,
        threshold=FRAUD_THRESHOLD,
        model_name=type(model).__name__,
    )


@app.get("/")
def root() -> dict:
    """Devuelve información básica del servicio."""
    return {
        "service": "fraud-detection-api",
        "version": API_VERSION,
        "docs": "/docs",
        "endpoints": ["/health", "/predict", "/predict/batch"],
    }


@app.get("/health", response_model=HealthOutput)
def health():
    """Indica si el modelo está cargado (200) o no (503)."""
    loaded = app.state.model is not None
    payload = HealthOutput(
        status="ok" if loaded else "degraded",
        model_loaded=loaded,
        model_path=MODEL_PATH,
        version=API_VERSION,
    )
    if not loaded:
        return JSONResponse(status_code=503, content=payload.model_dump())
    return payload


@app.post("/predict", response_model=PredictionOutput)
def predict(transaction: TransactionInput) -> PredictionOutput:
    """Predice si una transacción individual es fraudulenta."""
    return _predict_one(transaction)


@app.post("/predict/batch", response_model=BatchOutput)
def predict_batch(batch: BatchInput) -> BatchOutput:
    """Predice un lote de hasta 1000 transacciones."""
    if len(batch.transactions) > 1000:
        raise HTTPException(status_code=400, detail="Máximo 1000 transacciones por lote")
    predictions = [_predict_one(t) for t in batch.transactions]
    return BatchOutput(predictions=predictions, total=len(predictions))
