# fraud-detection

Proyecto de detección de fraude en transacciones bancarias (dataset de Kaggle: creditcard).

## Estructura del proyecto

```
fraud-detection/
├── data/raw/             # Datos crudos (no versionados)
├── data/processed/       # Datos procesados (no versionados)
├── notebooks/            # Notebooks de EDA y modelado
├── src/                  # Código fuente
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── api/
│   └── dashboard/
├── models/               # Modelos entrenados (no versionados)
├── tests/                # Tests
├── requirements.txt
└── README.md
```

## Configuración

1. Crear el entorno virtual: `python -m venv .venv`
2. Activarlo: `.\.venv\Scripts\Activate.ps1`
3. Instalar dependencias: `pip install -r requirements.txt`

## Uso

```bash
python src/data/load_data.py
```

## Resumen ejecutivo del EDA

EDA sobre `data/processed/creditcard_clean.csv` (283,726 transacciones, 31 columnas, 0 nulos):

- **Desbalanceo severo:** Class=0 (legítimo) 283,253 → 99.83%; Class=1 (fraude) 473 → 0.17% (ratio ~599:1).
- **Montos:** las transacciones fraudulentas exhiben mediana ($9.82) y colas distintas a las legítimas ($22.00); Amount por sí solo no discrimina.
- **Tiempo:** la incidencia de fraude varía por ventana temporal y hora del día.
- **PCA:** V17, V14, V12 y V10 muestran mayor separación entre clases.
- **Outliers:** presentes en Amount y varias V; informativos, no eliminar sin análisis.
- **Implicación de modelado:** evaluar con precision/recall/PR-AUC, considerar class weights y balanceo solo en train (evitar leakage).

Ver `notebooks/01_eda.ipynb` para el análisis completo.

## Modelado (`notebooks/03_modeling.ipynb`)

- Split estratificado 70/30 (seed 42) sobre `creditcard_features.csv`.
- Comparación de 3 modelos (LogisticRegression, RandomForest, XGBoost) × 2 estrategias (class_weight='balanced' y SMOTE solo en train).
- **Ganador: XGBoost con SMOTE** — Precision 0.875, Recall 0.789, F1 0.830, ROC-AUC 0.963, PR-AUC 0.823.
- Matriz de confusión del ganador: [[84960, 16], [30, 112]].
- Features más importantes: V14, V4, V12, V17, V10.
- Modelo persistido en `models/best_model.pkl` (no versionado, ignorado por .gitignore).
