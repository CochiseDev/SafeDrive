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

def entrenar_modelo(path_csv, algoritmo="Random Forest Mejorado"):
    """
    Entrena un modelo para predecir intensidad de tráfico usando solo features disponibles a priori.
    
    FEATURES UTILIZADAS (solo información disponible antes de predecir):
    - Fecha/Hora: hora (cyclical), día de la semana, mes
    - Zona: id (zona de tráfico)
    - Meteorología: temp, feelslike, dew, humidity, precip, precipprob, 
                    windgust, windspeed, winddir, cloudcover, visibility, conditionsDay
    - Demográfico: género conductores, edad conductores, tipo vehículos
    
    FEATURES EXCLUIDAS (son resultado del tráfico, no predictores):
    - carga, ocupacion, vmed (estado actual del tráfico)
    - Lesividad (consecuencia)
    - longitud, latitud (usar id es suficiente)
    - periodo_integracion (metadato)
    
    path_csv: ruta al CSV de datos
    algoritmo: nombre del modelo a entrenar
    
    Retorna:
        resultados: dict con métricas y modelo entrenado
        df: DataFrame con features procesadas
    """
    df = pd.read_csv(path_csv, sep=";")
    target = "intensidad"

    # ==================== FEATURE ENGINEERING ====================
    
    # Procesar fecha
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True)
    df["hora"] = df["fecha"].dt.hour
    df["mes"] = df["fecha"].dt.month
    df["dia_semana"] = df["fecha"].dt.dayofweek
    df["es_fin_semana"] = (df["dia_semana"] >= 5).astype(int)
    df["trimestre"] = df["fecha"].dt.quarter
    
    # Features cíclicas para hora (24h)
    df["hora_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
    df["hora_cos"] = np.cos(2 * np.pi * df["hora"] / 24)
    
    # Features cíclicas para mes (12 meses)
    df["mes_sin"] = np.sin(2 * np.pi * df["mes"] / 12)
    df["mes_cos"] = np.cos(2 * np.pi * df["mes"] / 12)
    
    # Features cíclicas para día de la semana
    df["dia_sin"] = np.sin(2 * np.pi * df["dia_semana"] / 7)
    df["dia_cos"] = np.cos(2 * np.pi * df["dia_semana"] / 7)
    
    # Interacciones importantes
    df["es_noche"] = ((df["hora"] >= 22) | (df["hora"] < 6)).astype(int)
    df["es_manana"] = ((df["hora"] >= 6) & (df["hora"] < 12)).astype(int)
    df["es_tarde"] = ((df["hora"] >= 12) & (df["hora"] < 18)).astype(int)
    df["es_trafico_punta"] = ((df["hora"] >= 7) & (df["hora"] <= 9)) | ((df["hora"] >= 17) & (df["hora"] <= 20))
    df["es_trafico_punta"] = df["es_trafico_punta"].astype(int)
    
    # Limpiar datos de condiciones meteorológicas
    df["conditionsDay"] = df["conditionsDay"].fillna("unknown")
    
    # Crear aggregaciones por zona
    zona_stats = df.groupby("id")["intensidad"].agg(['mean', 'std', 'min', 'max']).reset_index()
    zona_stats.columns = ['id', 'zona_intensidad_media', 'zona_intensidad_std', 'zona_intensidad_min', 'zona_intensidad_max']
    zona_stats['zona_intensidad_std'] = zona_stats['zona_intensidad_std'].fillna(0)
    df = df.merge(zona_stats, on='id', how='left')
    
    # Crear agregaciones por hora del día
    hora_stats = df.groupby("hora")["intensidad"].agg(['mean', 'std']).reset_index()
    hora_stats.columns = ['hora', 'hora_intensidad_media', 'hora_intensidad_std']
    hora_stats['hora_intensidad_std'] = hora_stats['hora_intensidad_std'].fillna(0)
    df = df.merge(hora_stats, on='hora', how='left')
    
    # ==================== SELECCIONAR FEATURES ====================
    
    # Features a usar: meteorología + demográfico + temporales + zona
    features_numericas = [
        # Temporales cíclicas
        "hora_sin", "hora_cos", "mes_sin", "mes_cos", "dia_sin", "dia_cos",
        # Temporales categóricas
        "hora", "mes", "es_fin_semana", "es_noche", "es_manana", "es_tarde", "es_trafico_punta",
        # Zona y estadísticas por zona
        "id", "zona_intensidad_media", "zona_intensidad_std", "zona_intensidad_min", "zona_intensidad_max",
        "hora_intensidad_media", "hora_intensidad_std",
        # Meteorología numéricas
        "temp", "feelslike", "dew", "humidity", "precip", "precipprob",
        "windgust", "windspeed", "winddir", "cloudcover", "visibility",
        # Demográfico (distribución de conductores y vehículos)
        "conductores_hombres", "conductores_mujeres",
        "De 18 a 24 años", "De 25 a 34 años", "De 35 a 44 años", 
        "De 45 a 54 años", "De 55 a 64 años", "De 65 a 74 años",
        "Turismo", "Motocicletas", "Furgonetas", "Bicicletas"
    ]
    
    features_categoricas = [
        "conditionsDay"  # Tipo de condición meteorológica
    ]
    
    # Verificar que existan todas las columnas
    features_numericas = [f for f in features_numericas if f in df.columns]
    features_categoricas = [f for f in features_categoricas if f in df.columns]
    
    X = df[features_numericas + features_categoricas].copy()
    y = df[target].copy()
    
    # Llenar NaN en features numéricas con mediana
    for col in features_numericas:
        X[col] = X[col].fillna(X[col].median())
    
    # ==================== PREPROCESAMIENTO ====================
    
    preprocesamiento = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), features_numericas),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop="if_binary"), features_categoricas)
        ],
        remainder='passthrough'
    )

    # ==================== DEFINIR MODELOS ====================
    
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

    # ==================== DIVIDIR Y ENTRENAR ====================
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = modelos[algoritmo]
    modelo.fit(X_train, y_train)

    # ==================== EVALUAR ====================
    
    y_pred = modelo.predict(X_test)
    
    # Evitar división por cero en MAPE
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
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_pred": y_pred
    }

    return resultados, df