"""Carga del dataset de tarjetas de crédito y reconocimiento exploratorio básico."""

from pathlib import Path

import pandas as pd


def load_creditcard_data(path: str = "data/raw/creditcard.csv") -> pd.DataFrame:
    """Carga el dataset de fraude en tarjetas de crédito desde un CSV.

    Args:
        path: Ruta relativa al CSV dentro del proyecto.

    Returns:
        DataFrame con los datos cargados.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
    """
    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo en la ruta: {ruta}. "
            "Verifica que creditcard.csv esté en data/raw/."
        )
    df = pd.read_csv(ruta)
    return df


def basic_eda(df: pd.DataFrame) -> None:
    """Imprime un reconocimiento exploratorio básico del DataFrame.

    Args:
        df: DataFrame con los datos del dataset.
    """
    print("Shape (filas, columnas):", df.shape)
    print("\nTipos de datos por columna:")
    print(df.dtypes)
    print("\nConteo de nulos por columna:")
    print(df.isnull().sum())
    print("\nDistribución de Class (value_counts):")
    conteo = df["Class"].value_counts()
    print(conteo)
    print("\nDistribución de Class (porcentaje):")
    print(df["Class"].value_counts(normalize=True) * 100)


if __name__ == "__main__":
    try:
        data = load_creditcard_data("data/raw/creditcard.csv")
        basic_eda(data)
    except FileNotFoundError as e:
        print(f"Error: {e}")
