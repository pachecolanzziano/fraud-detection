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

## EDA (`notebooks/01_eda.ipynb`)

ANALIS EXPLORATORIO del dataset limpio `creditcard_clean.csv` (283,726 transacciones × 31 columnas, 0 nulos), en 26 celdas, con visualizaciones y hallazgos escritos en markdown.

**Análisis realizados:**
- Panorama general del dataset: shape, `head()`, `info()`, `describe()` y tipos.
- Desbalanceo de clases: conteo y proporción, barplot en escala normal y logarítmica.
- Distribución de `Amount`: histogramas globales y por clase, boxplot por `Class`.
- Distribución de `Time`: histogramas por clase y conversión a hora del día.
- Variables PCA (V1–V28): grid de histogramas superpuestos por clase.
- Matriz de correlación con `Class` y top 10 correlaciones absolutas.
- Valores atípicos: boxplots e IQR por `Amount` y V seleccionadas.

**Hallazgos clave:**
- Desbalanceo extremo: ~99.83% no fraude vs ~0.17% fraude (ratio ~599:1).
- `Amount` difiere entre clase fraude (mediana $9.82) y legítima (mediana $22.00); Amount por sí solo no discrimina.
- Mayor incidencia de fraude en ciertas ventanas temporales y horas del día.
- V17, V14, V12, V10 y V16 son las componentes PCA con mayor separación entre clases.
- Outliers relevantes (Amount: 31,685 por IQR) que, en fraude, pueden ser señal informativa, no ruido a eliminar.
- Correlaciones más altas con `Class`: V17 (−0.31), V14 (−0.29), V12 (−0.25), V10 (−0.21).

**Implicaciones:** métricas apropiadas (precision/recall/PR-AUC), considerar class weights o balanceo solo en train, evitar leakage. No se transformó ni se entrenó ningún modelo. Ver el notebook para el detalle completo.

## Feature Engineering (`notebooks/02_feature_engineering.ipynb`)

Parte del dataset limpio para crear features nuevas que mejoren la capacidad predictiva, con justificación y visualización para cada una. Genera `data/processed/creditcard_features.csv`.

**Features creadas:**
| Feature | Justificación |
|---|---|
| `hour` | Fraude se concentra en determinadas horas del día; captura el ciclo diario (Time → hora mod 24). |
| `log_amount` | `log1p(Amount)` comprime la cola larga y reduce el impacto de outliers manteniendo la diferenciación fraude/no fraude. |
| `V_sum` | Suma de V1..V28; captura el "nivel global" de anomalía en el espacio de componentes PCA. |

**Feature eliminada:**
| Feature | Motivo |
|---|---|
| `V_mean` | Linealmente redundante con `V_sum` (V_mean = V_sum / 28); idéntica correlación con `Class`, por lo que se elimina. |

**Restricciones respetadas:** no se balancearon clases, no se escaló, no se entrenaron modelos, la columna `Class` permanece intacta, no hubo data leakage. El CSV resultante conserva las mismas filas (283,726) y pasa de 31 a 34 columnas.

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
