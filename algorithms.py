# algoritmos.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
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

    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True)
    df["hora"] = df["fecha"].dt.hour
    df["hora_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
    df["hora_cos"] = np.cos(2 * np.pi * df["hora"] / 24)

    df["dia_semana"] = df["fecha"].dt.dayofweek
    #df["es_finde"] = (df["dia_semana"] >= 5).astype(int)
    df["dia_semana"] = df["dia_semana"].astype(str)

    #df["mes"] = df["fecha"].dt.month.astype(str)
    #df["hora_x_finde"] = df["hora"] * df["es_finde"]

    X = df.drop(columns=[target, "fecha", "hora", "conductores_hombres", "conductores_mujeres", "conductores_desconocidos", "Edad_desconocida", "De 10 a 17 años", "De 18 a 24 años", "De 25 a 34 años", "De 35 a 44 años", "De 45 a 54 años", "De 55 a 64 años", "De 65 a 74 años", "Más de 74 años", "Lesividad_leve", "Lesividad_grave", "Lesividad_fallecido", "Lesividad_desconocido", "Turismo", "Motocicletas", "Furgonetas", "Bicicletas", "Vehiculos_especiales", "longitud", "latitud", "sealevelpressure", "solarradiation", "solarenergy", "uvindex", "carga", "ocupacion", "vmed", "periodo_integracion"], errors="ignore")  # Ignorar en caso no existan las columnas
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
        "Árbol de decisión": GridSearchCV(
            Pipeline([
                ("pre", preprocesamiento),
                ("model", DecisionTreeRegressor(random_state=42))
            ]),
            param_grid={
                "model__max_depth": [None, 5, 10, 20],
                "model__min_samples_leaf": [1, 2, 5, 10],
                "model__min_samples_split": [2, 5, 10]
            },
            cv=5,
            scoring="neg_mean_squared_error",
            n_jobs=-1
        ),
        "Random Forest": Pipeline([
            ("pre", preprocesamiento),
            ("model", RandomForestRegressor(
                n_estimators=200,
                max_depth=None,
                min_samples_leaf=2,
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