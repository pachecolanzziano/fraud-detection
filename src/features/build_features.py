"""Feature engineering compartido entre entrenamiento y API."""
import numpy as np
import pandas as pd


V_COLS = [f"V{i}" for i in range(1, 29)]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Construye hour, log_amount y V_sum a partir de features crudas.
    Replica exactamente la lógica de notebooks/02_feature_engineering.ipynb.
    """
    out = df.copy()
    out["hour"] = (out["Time"] / 3600) % 24
    out["log_amount"] = np.log1p(out["Amount"])
    out["V_sum"] = out[V_COLS].sum(axis=1)
    return out


FEATURE_ORDER = ["Time"] + V_COLS + ["Amount", "hour", "log_amount", "V_sum"]
