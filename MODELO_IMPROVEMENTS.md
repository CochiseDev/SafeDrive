# Mejoras en el Modelo de Predicción de Tráfico - SafeDrive

## Resumen de Cambios

Se ha realizado una optimización significativa del modelo de predicción de intensidad de tráfico, enfocándose en usar **solo las features disponibles a priori** (en el momento de hacer la predicción).

---

## Problemas Identificados en el Modelo Anterior

❌ **Uso de features no disponibles a priori:**
- `carga`: Estado actual del tráfico (resultado, no predictor)
- `ocupacion`: Estado actual del tráfico (resultado, no predictor)
- `vmed`: Velocidad media (resultado, no predictor)
- `periodo_integracion`: Metadato sin significado predictivo

❌ **Feature Engineering Limitado:**
- Pocas transformaciones temporales
- No se aprovechaban patrones cíclicos de hora/mes/día
- No se utilizaban estadísticas agregadas por zona y hora

❌ **Modelos Básicos:**
- Decision Tree, Random Forest simple, MLP básico
- Falta de modelos más avanzados como Gradient Boosting

---

## Mejoras Implementadas

### 1. **Selección de Features Estratégica** ✓

#### Features Incluidas (Disponibles a priori):

**Temporales:**
- Hora del día (cyclical: sin/cos)
- Mes (cyclical: sin/cos)
- Día de la semana (cyclical: sin/cos)
- Fin de semana (binario)
- Trimestre
- Bandas horarias: Noche (22:00-06:00), Mañana, Tarde
- Hora punta de tráfico (07:00-09:00, 17:00-20:00)

**Meteorológicas:**
- Temperatura actual, sensación térmica
- Punto de rocío, humedad
- Precipitación (cantidad), probabilidad de lluvia
- Viento: ráfagas, velocidad, dirección
- Cobertura de nubes, visibilidad
- Tipo de condición meteorológica (categorical)

**Zona de Tráfico:**
- ID de zona
- Estadísticas históricas por zona: media, std, min, max de intensidad
- Estadísticas históricas por hora: media, std de intensidad

**Demográfico (Distribución de conductores y vehículos):**
- Género: Hombres, Mujeres
- Edad: Conductores de 18-24, 25-34, 35-44, 45-54, 55-64, 65-74 años
- Tipo de vehículo: Turismo, Motocicletas, Furgonetas, Bicicletas

#### Features Excluidas (No disponibles a priori):

- ❌ `carga`: Valor agregado de ocupación × velocidad
- ❌ `ocupacion`: Porcentaje de ocupación (estado actual)
- ❌ `vmed`: Velocidad media (estado actual)
- ❌ `periodo_integracion`: Metadato de integración
- ❌ `Lesividad_*`: Consecuencias (efecto, no causa)
- ❌ `longitud, latitud`: Información redundante con ID de zona
- ❌ `sealevelpressure, solarradiation, solarenergy, uvindex`: Poco relevantes

### 2. **Feature Engineering Avanzado** ✓

```python
# Variables cíclicas para capturar patrones repetitivos
hora_sin = sin(2π × hora / 24)      # Patrón diario
hora_cos = cos(2π × hora / 24)

mes_sin = sin(2π × mes / 12)        # Patrón estacional
mes_cos = cos(2π × mes / 12)

dia_sin = sin(2π × día_semana / 7)  # Patrón semanal
dia_cos = cos(2π × día_semana / 7)
```

**Ventajas:**
- Captura la continuidad temporal (23:00 → 01:00 es cercano)
- Evita discontinuidades artificiales
- Reduce dimensionalidad vs One-Hot Encoding

**Estadísticas Agregadas:**
- Por zona: Media, std, min, max de intensidad (aprender patrones por ubicación)
- Por hora: Media, std de intensidad (patrones horarios globales)

### 3. **Modelos Mejorados** ✓

#### Modelo 1: Random Forest Mejorado
```
n_estimators=250
max_depth=20
min_samples_leaf=3
min_samples_split=5
max_features="sqrt"
```
**Ventajas:** Robusto, captura no-linealidades, tolerante a outliers

#### Modelo 2: Gradient Boosting (NUEVO)
```
n_estimators=200
learning_rate=0.05
max_depth=5
subsample=0.8
```
**Ventajas:** Mejor convergencia que Random Forest, secuencial (entiende secuencias)

#### Modelo 3: Deep Learning Mejorado
```
hidden_layers=(128, 64, 32)
activation=relu
solver=adam
early_stopping=True
```
**Ventajas:** Mayor capacidad de aprendizaje, mejor para relaciones complejas

#### Modelo 4: Árbol de Decisión Optimizado (NUEVO)
- Grid Search sobre hiperparámetros
- Interpretabilidad máxima

### 4. **Preprocesamiento Mejorado** ✓

```python
ColumnTransformer:
├── Numéricas: StandardScaler (normalización)
└── Categóricas: OneHotEncoder (variables dummy)
```

**Manejo de valores faltantes:**
- Rellenar con mediana (robusto a outliers)
- Variables categóricas: manejo de valores desconocidos

### 5. **Nuevas Métricas de Evaluación** ✓

- **RMSE**: Error cuadrático medio (penaliza errores grandes)
- **MAE**: Error absoluto medio (interpretable en unidades de tráfico)
- **R²**: Porcentaje de varianza explicada
- **MAPE**: Error porcentual absoluto medio (normalizador por escala)

---

## Impacto Esperado

### Mejor Predicción Porque:

1. **Features más relevantes:** Solo utilizamos información realmente disponible
2. **Feature engineering temporal:** Captura ciclos diarios, semanales y estacionales
3. **Estadísticas por zona:** Aprovecha variabilidad geográfica
4. **Modelos más potentes:** Gradient Boosting suele superar Random Forest
5. **Preprocesamiento robusto:** Normalización y manejo correcto de categorías

### Casos de Uso Mejorados:

✓ Predicción con datos meteorológicos en tiempo real
✓ Integración con calendarios (identificar picos de tráfico)
✓ Análisis por tipo de conductor y vehículo
✓ Predicción por zona específica
✓ Generalizabilidad a nuevas fechas/zonas

---

## Cómo Usar los Nuevos Modelos

```python
from algorithms import entrenar_modelo

# Entrenar cualquiera de los 4 modelos
resultados, df = entrenar_modelo(
    "2024_DatasetSample.csv",
    algoritmo="Random Forest Mejorado"  # o "Gradient Boosting", "Deep Learning Mejorado"
)

# Acceder a resultados
print(f"RMSE: {resultados['rmse']:.2f}")
print(f"MAE: {resultados['mae']:.2f}")
print(f"R²: {resultados['r2']:.4f}")
print(f"MAPE: {resultados['mape']:.2%}")

# Usar modelo para predicciones
modelo = resultados['modelo']
predicciones = modelo.predict(X_nuevo)
```

---

## Estructura de Features

```
Total Features: ~40-50 (después de expansión one-hot)

Categorías:
├── Temporales (8 features)
│   ├── Cíclicas: hora_sin, hora_cos, mes_sin, mes_cos, dia_sin, dia_cos
│   ├── Bandas: es_noche, es_manana, es_tarde, es_trafico_punta
│   └── Estructura: fin_semana, trimestre
│
├── Meteorológicas (11 features)
│   ├── Temperatura: temp, feelslike, dew
│   ├── Humedad: humidity
│   ├── Precipitación: precip, precipprob
│   ├── Viento: windgust, windspeed, winddir
│   ├── Visibilidad: cloudcover, visibility
│   └── Tipo: conditionsDay (categorical)
│
├── Zona (5 features)
│   ├── id
│   └── Estadísticas por zona: media, std, min, max intensidad
│
├── Hora Agregada (2 features)
│   └── Estadísticas por hora: media, std intensidad
│
└── Demográfico (9 features)
    ├── Género: conductores_hombres, conductores_mujeres
    ├── Edad: De 18-24, 25-34, 35-44, 45-54, 55-64, 65-74 años
    └── Vehículos: Turismo, Motocicletas, Furgonetas, Bicicletas
```

---

## Próximas Mejoras Posibles

1. **Lag Features:** Intensidad de la hora anterior (requiere histórico)
2. **Eventos Especiales:** Calendario de eventos, festivos, vacaciones
3. **Datos Exógenos:** Obras, accidentes, cierres de carreteras
4. **Ensemble:** Combinar predicciones de múltiples modelos
5. **Tuning Avanzado:** Bayesian Optimization, Auto-ML (AutoML)
6. **Validación Temporal:** Time series cross-validation (no random split)

---

**Versión:** 2.0  
**Fecha:** Enero 2026  
**Estado:** Implementado y Testado
