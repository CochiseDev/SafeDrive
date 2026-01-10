# algoritmos.py

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def _agregar_features_temporales(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el mismo feature engineering temporal y de interacciones usado en entrenamiento."""
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True)
    df["hora"] = df["fecha"].dt.hour
    df["mes"] = df["fecha"].dt.month
    df["dia_semana"] = df["fecha"].dt.dayofweek
    df["es_fin_semana"] = (df["dia_semana"] >= 5).astype(int)
    df["trimestre"] = df["fecha"].dt.quarter

    # Cíclicas
    df["hora_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
    df["hora_cos"] = np.cos(2 * np.pi * df["hora"] / 24)
    df["mes_sin"] = np.sin(2 * np.pi * df["mes"] / 12)
    df["mes_cos"] = np.cos(2 * np.pi * df["mes"] / 12)
    df["dia_sin"] = np.sin(2 * np.pi * df["dia_semana"] / 7)
    df["dia_cos"] = np.cos(2 * np.pi * df["dia_semana"] / 7)

    # Interacciones
    df["es_noche"] = ((df["hora"] >= 22) | (df["hora"] < 6)).astype(int)
    df["es_manana"] = ((df["hora"] >= 6) & (df["hora"] < 12)).astype(int)
    df["es_tarde"] = ((df["hora"] >= 12) & (df["hora"] < 18)).astype(int)
    df["es_trafico_punta"] = ((df["hora"] >= 7) & (df["hora"] <= 9)) | ((df["hora"] >= 17) & (df["hora"] <= 20))
    df["es_trafico_punta"] = df["es_trafico_punta"].astype(int)

    df["conditionsDay"] = df["conditionsDay"].fillna("unknown")
    return df

def entrenar_modelo(path_csv, algoritmo="Random Forest Mejorado"):
    """
    Entrena un modelo para predecir intensidad de tráfico usando solo features disponibles a priori.

    Se guardan las estadísticas calculadas en entrenamiento (medianas, agregados
    por zona y hora) para poder reutilizarlas al predecir y así permitir que el
    CSV de predicción solo contenga las columnas base (sin las derivadas).
    """
    df_raw = pd.read_csv(path_csv, sep=";")
    target = "intensidad"

    # ==================== FEATURE ENGINEERING BASE ====================
    df = _agregar_features_temporales(df_raw)

    # Agregados por zona y hora (se calculan con la intensidad conocida)
    zona_stats = df.groupby("id")[target].agg(['mean', 'std', 'min', 'max']).reset_index()
    zona_stats.columns = ['id', 'zona_intensidad_media', 'zona_intensidad_std', 'zona_intensidad_min', 'zona_intensidad_max']
    zona_stats['zona_intensidad_std'] = zona_stats['zona_intensidad_std'].fillna(0)

    hora_stats = df.groupby("hora")[target].agg(['mean', 'std']).reset_index()
    hora_stats.columns = ['hora', 'hora_intensidad_media', 'hora_intensidad_std']
    hora_stats['hora_intensidad_std'] = hora_stats['hora_intensidad_std'].fillna(0)

    # Valores por defecto para ids/horas no vistas
    zona_defaults = {
        'zona_intensidad_media': zona_stats['zona_intensidad_media'].median(),
        'zona_intensidad_std': zona_stats['zona_intensidad_std'].median(),
        'zona_intensidad_min': zona_stats['zona_intensidad_min'].median(),
        'zona_intensidad_max': zona_stats['zona_intensidad_max'].median(),
    }
    hora_defaults = {
        'hora_intensidad_media': hora_stats['hora_intensidad_media'].median(),
        'hora_intensidad_std': hora_stats['hora_intensidad_std'].median(),
    }

    # Merge de estadísticas al conjunto de entrenamiento
    df = df.merge(zona_stats, on='id', how='left')
    df = df.merge(hora_stats, on='hora', how='left')

    # ==================== SELECCIONAR FEATURES ====================
    features_numericas = [
        "hora_sin", "hora_cos", "mes_sin", "mes_cos", "dia_sin", "dia_cos",
        "hora", "mes", "es_fin_semana", "es_noche", "es_manana", "es_tarde", "es_trafico_punta",
        "id", "zona_intensidad_media", "zona_intensidad_std", "zona_intensidad_min", "zona_intensidad_max",
        "hora_intensidad_media", "hora_intensidad_std",
        "temp", "feelslike", "dew", "humidity", "precip", "precipprob",
        "windgust", "windspeed", "winddir", "cloudcover", "visibility",
        "conductores_hombres", "conductores_mujeres",
        "De 18 a 24 años", "De 25 a 34 años", "De 35 a 44 años", 
        "De 45 a 54 años", "De 55 a 64 años", "De 65 a 74 años",
        "Turismo", "Motocicletas", "Furgonetas", "Bicicletas"
    ]

    features_categoricas = [
        "conditionsDay"
    ]

    features_numericas = [f for f in features_numericas if f in df.columns]
    features_categoricas = [f for f in features_categoricas if f in df.columns]

    X = df[features_numericas + features_categoricas].copy()
    y = df[target].copy()

    median_values = {col: X[col].median() for col in features_numericas}
    for col in features_numericas:
        X[col] = X[col].fillna(median_values[col])

    preprocesamiento = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), features_numericas),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop="if_binary"), features_categoricas)
        ],
        remainder='passthrough'
    )

    modelos = {
        "Random Forest Mejorado": Pipeline([
            ("pre", preprocesamiento),
            ("model", RandomForestRegressor(
                n_estimators=250,
                max_depth=20,
                min_samples_leaf=3,
                min_samples_split=5,
                max_features="sqrt",
                n_jobs=-1,
                random_state=42,
                warm_start=False
            ))
        ]),

        "Gradient Boosting": Pipeline([
            ("pre", preprocesamiento),
            ("model", GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                min_samples_leaf=3,
                min_samples_split=5,
                subsample=0.8,
                random_state=42
            ))
        ]),

        "Deep Learning Mejorado": Pipeline([
            ("pre", preprocesamiento),
            ("model", MLPRegressor(
                hidden_layer_sizes=(128, 64, 32),
                activation="relu",
                solver="adam",
                alpha=0.001,
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=50,
                random_state=42
            ))
        ]),

        "Árbol de decisión optimizado": GridSearchCV(
            Pipeline([
                ("pre", preprocesamiento),
                ("model", DecisionTreeRegressor(random_state=42))
            ]),
            param_grid={
                "model__max_depth": [10, 15, 20, 25],
                "model__min_samples_leaf": [2, 3, 5],
                "model__min_samples_split": [5, 10]
            },
            cv=5,
            scoring="neg_mean_squared_error",
            n_jobs=-1
        )
    }

    if algoritmo not in modelos:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}. Disponibles: {list(modelos.keys())}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = modelos[algoritmo]
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    y_test_nonzero = y_test[y_test > 0]
    y_pred_nonzero = y_pred[y_test > 0]

    mape = mean_absolute_percentage_error(y_test_nonzero, y_pred_nonzero) if len(y_test_nonzero) > 0 else np.nan

    resultados = {
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "mae": mean_absolute_error(y_test, y_pred),
        "r2": r2_score(y_test, y_pred),
        "mape": mape,
        "modelo": modelo,
        "features_numericas": features_numericas,
        "features_categoricas": features_categoricas,
        "median_values": median_values,
        "zona_stats": zona_stats,
        "hora_stats": hora_stats,
        "zona_defaults": zona_defaults,
        "hora_defaults": hora_defaults,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_pred": y_pred
    }

    return resultados, df


def preparar_datos_prediccion(df_pred: pd.DataFrame, resultados_entrenamiento: dict) -> pd.DataFrame:
    """Replica el feature engineering del entrenamiento usando las estadísticas guardadas."""
    features_numericas = resultados_entrenamiento.get("features_numericas", [])
    features_categoricas = resultados_entrenamiento.get("features_categoricas", [])
    median_values = resultados_entrenamiento.get("median_values", {})
    zona_stats = resultados_entrenamiento.get("zona_stats")
    hora_stats = resultados_entrenamiento.get("hora_stats")
    zona_defaults = resultados_entrenamiento.get("zona_defaults", {})
    hora_defaults = resultados_entrenamiento.get("hora_defaults", {})

    df_feat = _agregar_features_temporales(df_pred)

    # Adjuntar estadísticos aprendidos (no podemos recalcularlos sin la intensidad real)
    if zona_stats is not None:
        df_feat = df_feat.merge(zona_stats, on='id', how='left')
        for col, default_val in zona_defaults.items():
            if col in df_feat.columns:
                df_feat[col] = df_feat[col].fillna(default_val)

    if hora_stats is not None:
        df_feat = df_feat.merge(hora_stats, on='hora', how='left')
        for col, default_val in hora_defaults.items():
            if col in df_feat.columns:
                df_feat[col] = df_feat[col].fillna(default_val)

    # Asegurar columnas esperadas
    for col in features_numericas:
        if col not in df_feat.columns:
            df_feat[col] = median_values.get(col, 0)
    for col in features_categoricas:
        if col not in df_feat.columns:
            df_feat[col] = "unknown"

    X_pred = df_feat[features_numericas + features_categoricas].copy()

    for col in features_numericas:
        X_pred[col] = X_pred[col].fillna(median_values.get(col, 0))
    for col in features_categoricas:
        X_pred[col] = X_pred[col].fillna("unknown")

    return X_pred