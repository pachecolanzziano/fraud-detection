"""MODELO MOCK - reemplazar en fase de modeling.

Script mínimo para entrenar un Pipeline de LogisticRegression sobre las features
crudas de data/processed/creditcard_clean.csv y guardar models/best_model.pkl.
Su único objetivo es desbloquear el desarrollo de la API.
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_PATH = "models/best_model.pkl"
INPUT_PATH = "data/processed/creditcard_clean.csv"


def load_data(path: str = INPUT_PATH) -> tuple[pd.DataFrame, pd.Series]:
    """Carga el CSV limpio y separa features (X) y objetivo (y).

    Args:
        path: Ruta relativa al CSV limpio.

    Returns:
        Tupla (X, y).
    """
    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero src/data/preprocess.py."
        )
    df = pd.read_csv(ruta)
    X = df.drop(columns=["Class"])
    y = df["Class"]
    return X, y


def build_pipeline() -> Pipeline:
    """Construye el pipeline StandardScaler + LogisticRegression balanceada."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def main() -> None:
    """Entrena el modelo mock, lo evalúa y lo guarda en models/best_model.pkl."""
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"X_train: {X_train.shape} | X_test: {X_test.shape}")

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    print("\nClassification report (test):")
    print(classification_report(y_test, y_pred, digits=4))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

    ruta = Path(MODEL_PATH)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, ruta)
    print(f"\nModelo guardado en: {ruta}")


if __name__ == "__main__":
    main()
