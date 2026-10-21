"""Pipeline de limpieza del dataset de fraude en tarjetas de crédito."""

from pathlib import Path

import pandas as pd


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas duplicadas exactas del DataFrame.

    Args:
        df: DataFrame crudo.

    Returns:
        DataFrame sin duplicados.
    """
    df = df.copy()
    n_antes = len(df)
    df = df.drop_duplicates()
    print(f"Duplicados eliminados: {n_antes - len(df)}")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Imputa nulos en columnas numéricas con la mediana y elimina nulos en Class.

    Args:
        df: DataFrame de entrada.

    Returns:
        DataFrame sin valores nulos.
    """
    df = df.copy()
    total_nulos = int(df.isnull().sum().sum())
    print(f"Nulos encontrados: {total_nulos}")

    n_class = int(df["Class"].isnull().sum())
    if n_class > 0:
        df = df.dropna(subset=["Class"])
        print(f"Filas eliminadas con Class nulo: {n_class}")

    for col in df.select_dtypes(include="number").columns:
        n_col = int(df[col].isnull().sum())
        if n_col > 0:
            df[col] = df[col].fillna(df[col].median())
            print(f"Columna '{col}': {n_col} nulos imputados con la mediana")
    return df


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Ajusta los tipos de datos de las columnas.

    Args:
        df: DataFrame de entrada.

    Returns:
        DataFrame con tipos corregidos.
    """
    df = df.copy()
    if "Class" in df.columns:
        df["Class"] = df["Class"].astype(int)
    for col in ["Amount", "Time"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    for i in range(1, 29):
        col = f"V{i}"
        if col in df.columns:
            df[col] = df[col].astype(float)
    print("Tipos finales:")
    print(df.dtypes)
    return df


def validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Verifica que Amount y Time sean >= 0 y que Class sea 0 o 1.

    Args:
        df: DataFrame de entrada.

    Returns:
        El mismo DataFrame (sin modificaciones), tras reportar anomalías.
    """
    df = df.copy()
    if "Amount" in df.columns:
        print(f"Amount < 0: {int((df['Amount'] < 0).sum())}")
    if "Time" in df.columns:
        print(f"Time < 0: {int((df['Time'] < 0).sum())}")
    if "Class" in df.columns:
        print(f"Class no en {{0,1}}: {int((~df['Class'].isin([0, 1])).sum())}")
    return df


def preprocess(df: pd.DataFrame, output_path: str = "data/processed/creditcard_clean.csv") -> pd.DataFrame:
    """Ejecuta el pipeline de limpieza y guarda el CSV resultante.

    Args:
        df: DataFrame crudo.
        output_path: Ruta de salida del CSV limpio.

    Returns:
        DataFrame limpio.
    """
    filas_antes = len(df)
    df = drop_duplicates(df)
    df = handle_missing(df)
    df = fix_dtypes(df)
    df = validate_ranges(df)
    filas_despues = len(df)
    print(f"Filas antes: {filas_antes} | Filas después: {filas_despues}")

    ruta = Path(output_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"CSV guardado en: {ruta}")
    return df


def main() -> None:
    """Carga los datos crudos y ejecuta el pipeline de preprocesamiento."""
    from load_data import load_creditcard_data

    df = load_creditcard_data("data/raw/creditcard.csv")
    preprocess(df, "data/processed/creditcard_clean.csv")


if __name__ == "__main__":
    main()
