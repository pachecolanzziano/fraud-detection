"""Dashboard Streamlit para detección de fraude en transacciones.

Consume `models/best_model.pkl` y aplica el mismo feature engineering que la
API (`src.features.build_features`). Permite predicción individual y por lote.
"""

import os
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.build_features import FEATURE_ORDER, build_features

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/best_model.pkl"))
if not MODEL_PATH.is_absolute():
    MODEL_PATH = ROOT / MODEL_PATH

V_COLS = [f"V{i}" for i in range(1, 29)]
RAW_FEATURES = ["Time"] + V_COLS + ["Amount"]


@st.cache_resource(show_spinner=False)
def load_model(path: str):
    """Carga el modelo desde disco una sola vez por sesión."""
    try:
        return joblib.load(path)
    except Exception as exc:  # noqa: BLE001 - se muestra al usuario
        st.error(f"No se pudo cargar el modelo en `{path}`: {exc}")
        return None


def predict_transactions(model, df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Predice fraude para un DataFrame con las 30 features crudas.

    Args:
        model: Pipeline/estimador entrenado.
        df: DataFrame con columnas Time, V1..V28, Amount.
        threshold: Umbral de decisión para la clase fraude.

    Returns:
        DataFrame con `fraud_probability` e `is_fraud`.
    """
    features = build_features(df)
    feature_names = getattr(model, "feature_names_in_", None)
    X = features[list(feature_names)] if feature_names is not None else features[FEATURE_ORDER]
    proba = model.predict_proba(X)[:, 1]
    out = df.copy()
    out["fraud_probability"] = proba
    out["is_fraud"] = proba >= threshold
    return out


st.set_page_config(page_title="Fraud Detection Dashboard", page_icon="🔍", layout="wide")

model = load_model(str(MODEL_PATH))

st.title("🔍 Dashboard de detección de fraude")
st.caption("Modelo de clasificación de transacciones bancarias (dataset creditcard).")

with st.sidebar:
    st.header("Configuración")
    threshold = st.slider(
        "Umbral de decisión",
        min_value=0.05,
        max_value=0.95,
        value=0.5,
        step=0.05,
        help="Probabilidad mínima para clasificar una transacción como fraude.",
    )
    st.write(f"**Modelo:** `{MODEL_PATH.name}`")
    st.write(f"**Ruta:** `{MODEL_PATH}`")
    if model is not None:
        st.success(f"Cargado: {type(model).__name__}")
    else:
        st.error("Modelo no disponible")

if model is None:
    st.warning(
        "No se encontró el modelo. Genera `models/best_model.pkl` ejecutando "
        "`notebooks/03_modeling.ipynb`."
    )
    st.stop()

tab_individual, tab_batch, tab_info = st.tabs(
    ["Transacción individual", "Lote (CSV)", "Información del modelo"]
)

with tab_individual:
    st.subheader("Datos de la transacción")
    with st.form("form_individual"):
        c1, c2 = st.columns(2)
        time_val = c1.number_input("Time (segundos)", value=0.0, step=1.0, format="%.6f")
        amount_val = c2.number_input("Amount", value=0.0, step=1.0, format="%.6f")

        st.markdown("**Componentes PCA (V1–V28)**")
        values = {}
        cols = st.columns(4)
        for i, col in enumerate(V_COLS):
            values[col] = cols[i % 4].number_input(
                col, value=0.0, step=0.1, format="%.6f", key=f"in_{col}"
            )

        submitted = st.form_submit_button("Predecir", type="primary")

    if submitted:
        row = {"Time": time_val, **values, "Amount": amount_val}
        result = predict_transactions(model, pd.DataFrame([row]), threshold).iloc[0]
        proba = float(result["fraud_probability"])
        st.metric("Probabilidad de fraude", f"{proba:.4%}")
        st.progress(min(max(proba, 0.0), 1.0))
        if bool(result["is_fraud"]):
            st.error(f"⚠️ Transacción clasificada como FRAUDE (umbral {threshold:.2f}).")
        else:
            st.success(f"✅ Transacción clasificada como NO fraude (umbral {threshold:.2f}).")
        st.json({"is_fraud": bool(result["is_fraud"]), "fraud_probability": proba})

with tab_batch:
    st.subheader("Predicción por lote")
    st.write("Sube un CSV con las columnas `Time`, `V1`…`V28`, `Amount` (máx. 1000 filas).")
    uploaded = st.file_uploader("Archivo CSV", type=["csv"])

    if uploaded is not None:
        try:
            batch_df = pd.read_csv(uploaded)
        except Exception as exc:  # noqa: BLE001
            st.error(f"No se pudo leer el CSV: {exc}")
            st.stop()

        missing = [c for c in RAW_FEATURES if c not in batch_df.columns]
        if missing:
            st.error(f"Faltan columnas requeridas: {missing}")
        elif len(batch_df) > 1000:
            st.error(f"El lote tiene {len(batch_df)} filas; el máximo es 1000.")
        else:
            with st.spinner("Calculando predicciones…"):
                results = predict_transactions(model, batch_df[RAW_FEATURES], threshold)
            fraud_count = int(results["is_fraud"].sum())
            m1, m2, m3 = st.columns(3)
            m1.metric("Transacciones", len(results))
            m2.metric("Fraudes detectados", fraud_count)
            m3.metric("Tasa de fraude", f"{fraud_count / len(results):.2%}")
            st.dataframe(results, use_container_width=True)
            st.download_button(
                "Descargar resultados (CSV)",
                data=results.to_csv(index=False).encode("utf-8"),
                file_name="predicciones_fraude.csv",
                mime="text/csv",
            )

with tab_info:
    st.subheader("Información del modelo")
    st.write(f"**Tipo:** `{type(model).__name__}`")
    st.write(f"**Features esperadas:** {getattr(model, 'n_features_in_', 'desconocido')}")
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        st.code(", ".join(str(f) for f in feature_names), language="text")
    st.write("**Orden de features (fallback):**")
    st.code(", ".join(FEATURE_ORDER), language="text")
    st.info(
        "El dashboard recibe 30 features crudas, genera hour, log_amount y V_sum "
        "y reordena según el contrato del modelo."
    )
