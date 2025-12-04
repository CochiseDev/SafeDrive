# algoritmos.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

def entrenar_modelo(path_csv, algoritmo="Árbol de decisión"):
    """
    path_csv: ruta al CSV de datos
    algoritmo: nombre del modelo a entrenar ("Árbol de decisión", "Random Forest", "Deep Learning")
    
    Retorna:
        resultados: dict con métricas y modelo entrenado
        df: DataFrame original
    """
    df = pd.read_csv(path_csv, sep=";")
    target = "intensidad"
    X = df.drop(columns=[target, "fecha"], errors="ignore")  # Ignorar si no existe columna fecha
    y = df[target]

    # Columnas categóricas y numéricas
    categoricas = X.select_dtypes(include=["object"]).columns.tolist()
    numericas = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Preprocesamiento
    preprocesamiento = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numericas),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categoricas)
        ]
    )

    # Pipelines de modelos
    modelos = {
        "Árbol de decisión": Pipeline([
            ("pre", preprocesamiento),
            ("model", DecisionTreeRegressor(random_state=42, max_depth=5, min_samples_leaf=5))
        ]),
        "Random Forest": Pipeline([
            ("pre", preprocesamiento),
            ("model", RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                max_features="sqrt",
                n_jobs=-1,
                random_state=42
            ))
        ]),
        "Deep Learning": Pipeline([
            ("pre", preprocesamiento),
            ("model", MLPRegressor(
                hidden_layer_sizes=(64,32),
                activation="relu",
                max_iter=500,
                solver="adam",
                early_stopping=True,
                random_state=42
            ))
        ])
    }

    if algoritmo not in modelos:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar
    modelo = modelos[algoritmo]
    modelo.fit(X_train, y_train)

    # Predicción y métricas
    pred = modelo.predict(X_test)
    resultados = {
        "rmse": np.sqrt(mean_squared_error(y_test, pred)),
        "r2": r2_score(y_test, pred),
        "mae": mean_absolute_error(y_test, pred),
        "modelo": modelo
    }

    return resultados, df