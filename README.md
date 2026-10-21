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
- V1, V3, V4, V14 y V17 son las componentes PCA con mayor separación entre clases.
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

**Justificación de retención de features:**
- `Time` + `hour`: se conservan ambas. `Time` captura la posición absoluta en la ventana de 2 días del dataset; `hour` captura el ciclo diario. Son complementarias.
- `Amount` + `log_amount`: se conservan ambas. `log_amount` reduce el sesgo de la distribución y beneficia modelos lineales; `Amount` conserva la escala original y beneficia modelos de árboles.
- Se conservan las 28 V originales: el EDA mostró que V14, V17, V12 y V10 aportan señal.

**Feature engineering compartido:** la lógica de `hour`, `log_amount` y `V_sum` está centralizada en `src/features/build_features.py`, que usan tanto el entrenamiento como la API. Expone `build_features(df)` y `FEATURE_ORDER` (33 columnas: Time, V1..V28, Amount, hour, log_amount, V_sum).

## Resumen ejecutivo del EDA

EDA sobre `data/processed/creditcard_clean.csv` (283,726 transacciones, 31 columnas, 0 nulos):

- **Desbalanceo severo:** Class=0 (legítimo) 283,253 → 99.83%; Class=1 (fraude) 473 → 0.17% (ratio ~599:1).
- **Montos:** las transacciones fraudulentas exhiben mediana ($9.82) y colas distintas a las legítimas ($22.00); Amount por sí solo no discrimina.
- **Tiempo:** la incidencia de fraude varía por ventana temporal y hora del día.
- **PCA:** V1, V3, V4, V14 y V17 son las componentes con mayor separación entre clases.
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

### Limitaciones del modelo

- **Umbral 0.5 sin optimizar:** un umbral más bajo (0.2-0.3) aumentaría el recall a costa de más falsos positivos; el óptimo depende del costo de FN vs FP.
- **Sin validación cruzada:** un único split 70/30 puede dar métricas optimistas o pesimistas; una CV estratificada daría intervalos de confianza.
- **Alta dependencia de V14:** concentra ~66.8% del peso del XGBoost; un cambio de distribución en producción podría degradarlo silenciosamente.
- **Features PCA no interpretables:** V1..V28 no aportan narrativa de negocio.
- **Sin tuning de hiperparámetros:** hay margen de mejora en PR-AUC.

### Contrato API ↔ modelo

- La API recibe **30 features crudas** (`Time`, `V1..V28`, `Amount`).
- Aplica `src.features.build_features.build_features()` para generar `hour`, `log_amount` y `V_sum`.
- Reordena al orden de entrenamiento usando `feature_names_in_` del modelo (fallback: `FEATURE_ORDER`, 33 features).
- Esto mantiene compatibilidad tanto con el modelo mock de 30 features como con el modelo formal de 33 features, sin reentrenar.

### Solución de problemas: 404 en `/predict` y `/predict/batch`

**Las rutas correctas no llevan prefijo `/api`:**

| Endpoint | Método | URL correcta | URL incorrecta (404) |
|---|---|---|---|
| Predicción individual | POST | `/predict` | `/api/predict` |
| Predicción en lote | POST | `/predict/batch` | `/api/predict/batch` |
| Salud | GET | `/health` | — |
| Swagger | GET | `/docs` | — |

**Checklist de verificación:**

1. Arrancar el servidor **desde la raíz del repo** y con el venv:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   uvicorn src.api.main:app --host 127.0.0.1 --port 8000
   ```
2. Confirmar que el puerto es el mismo que usas en la URL (8000). Si el puerto está ocupado, uvicorn falla o usa otro.
3. Confirmar que el proceso quedó corriendo: `GET http://127.0.0.1:8000/health` debe responder 200.
4. Confirmar las rutas publicadas: `GET http://127.0.0.1:8000/openapi.json` debe listar `/predict` y `/predict/batch`.
5. Usar **POST** y `Content-Type: application/json`. `GET /predict` devuelve **405** (no 404), y un `POST` a una ruta inexistente devuelve 404.
6. Si cambiaste código, reinicia uvicorn (sin `--reload` no toma cambios automáticamente).

**Prueba rápida (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

**Prueba de `/predict` (curl):**
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"Time":0.0,"V1":-1.359807,"V2":-0.072781,"V3":2.536347,"V4":1.378155,"V5":-0.338321,"V6":0.462388,"V7":0.239599,"V8":0.098698,"V9":0.363787,"V10":0.090794,"V11":-0.5516,"V12":-0.617801,"V13":-0.99139,"V14":-0.311169,"V15":1.468177,"V16":-0.470401,"V17":0.207971,"V18":0.025791,"V19":0.403993,"V20":0.251412,"V21":-0.018307,"V22":0.277838,"V23":-0.110474,"V24":0.066928,"V25":0.128539,"V26":-0.189115,"V27":0.133558,"V28":-0.021053,"Amount":149.62}'
```

**Prueba de `/predict/batch` (curl):**
```bash
curl -X POST "http://127.0.0.1:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"transactions":[{"Time":0.0,"V1":-1.359807,"V2":-0.072781,"V3":2.536347,"V4":1.378155,"V5":-0.338321,"V6":0.462388,"V7":0.239599,"V8":0.098698,"V9":0.363787,"V10":0.090794,"V11":-0.5516,"V12":-0.617801,"V13":-0.99139,"V14":-0.311169,"V15":1.468177,"V16":-0.470401,"V17":0.207971,"V18":0.025791,"V19":0.403993,"V20":0.251412,"V21":-0.018307,"V22":0.277838,"V23":-0.110474,"V24":0.066928,"V25":0.128539,"V26":-0.189115,"V27":0.133558,"V28":-0.021053,"Amount":149.62}]}'
```

> Diagnóstico verificado el 2026-10-20: `/predict` y `/predict/batch` responden 200 con el modelo formal; `/api/predict` responde 404 porque la API no usa prefijo.
