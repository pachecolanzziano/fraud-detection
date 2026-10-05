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
