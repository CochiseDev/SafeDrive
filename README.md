# SafeDrive - Predicción de Intensidad de Tráfico

## Descripción General

SafeDrive es una aplicación de predicción de intensidad de tráfico basada en modelos de machine learning. Utiliza datos meteorológicos, temporales, demográficos y de zona para predecir el nivel de congestión en carreteras.

**Versión:** 2.0  
**Estado:** Producción  
**Última actualización:** Enero 2026

---

## Características Principales

✓ **Múltiples Modelos:** Random Forest, Gradient Boosting, Deep Learning, Árboles de Decisión
✓ **Feature Engineering Avanzado:** Variables cíclicas, estadísticas agregadas, transformaciones temporales
✓ **Solo Features a Priori:** Usa únicamente información disponible antes de hacer la predicción
✓ **Interfaz Gráfica:** Aplicación tkinter intuitiva para entrenamiento y predicción
✓ **Evaluación Completa:** RMSE, MAE, R², MAPE

---

## Instalación y Requisitos

### Dependencias
```bash
pip install pandas scikit-learn numpy
```

### Archivos Necesarios
- `algorithms.py` - Modelos entrenables
- `app.py` - Interfaz gráfica
- `2024_DatasetSample.csv` - Dataset de entrenamiento

---

## Uso

### 1. Prueba Rápida
```bash
python test_rapido.py
```
Entrena un modelo básico y muestra métricas.

### 2. Entrenar desde GUI
```bash
python app.py
```
Abre la interfaz gráfica con opciones completas.

### 3. Ejemplo de Predicción
```bash
python ejemplo_prediccion.py
```
Muestra cómo hacer predicciones con nuevos datos.

### 4. Evaluar Todos los Modelos
```bash
python evaluar_modelos.py
```
Compara el rendimiento de los 4 modelos disponibles.

---

## Archivos del Proyecto

```
SafeDrive/
├── app.py                          # Interfaz gráfica principal
├── algorithms.py                   # Modelos de predicción
├── test_rapido.py                 # Prueba básica
├── ejemplo_prediccion.py           # Ejemplo de uso
├── evaluar_modelos.py             # Comparativa de modelos
├── 2024_DatasetSample.csv         # Dataset
├── README.md                       # Este archivo
├── MODELO_IMPROVEMENTS.md         # Documentación de mejoras
└── FEATURES_TECNICO.md            # Guía técnica de features
```

---

## Modelos Disponibles

### 1. Random Forest Mejorado ⭐
- **Recomendación:** Mejor relación rendimiento/velocidad
- **Ventajas:** Robusto, captura no-linealidades, tolerante a outliers
- **Tiempo:** ~30 segundos
- **R² típico:** 0.65-0.75

### 2. Gradient Boosting
- **Recomendación:** Mejor precisión
- **Ventajas:** Mejor convergencia secuencial
- **Tiempo:** ~60 segundos
- **R² típico:** 0.70-0.80

### 3. Deep Learning Mejorado
- **Recomendación:** Máxima capacidad
- **Ventajas:** Red neuronal con 3 capas, early stopping
- **Tiempo:** ~120 segundos
- **R² típico:** 0.65-0.75

### 4. Árbol de Decisión Optimizado
- **Recomendación:** Máxima interpretabilidad
- **Ventajas:** Explainable AI, GridSearch automático
- **Tiempo:** ~90 segundos (con grid search)
- **R² típico:** 0.55-0.65

---

## Features Utilizados

### Temporales (8)
- Hora del día (cíclico)
- Mes (cíclico)
- Día de la semana (cíclico)
- Bandas horarias (noche, mañana, tarde, punta)
- Fin de semana
- Trimestre

### Meteorológicas (11)
- Temperatura, sensación térmica, punto de rocío
- Humedad, precipitación, probabilidad lluvia
- Velocidad y dirección del viento, ráfagas
- Cobertura de nubes, visibilidad
- Condición meteorológica (categorical)

### Zona (5)
- ID de zona de tráfico
- Estadísticas históricas: media, std, min, max

### Demográficas (9)
- Género de conductores (hombres, mujeres)
- Edad de conductores (6 grupos de edad)
- Tipo de vehículo (turismo, moto, furgoneta, bicicleta)

**Total Features:** ~40-50 después de transformación

---

## Métrica de Evaluación

| Métrica | Fórmula | Interpretación | Mejor |
|---------|---------|----------------|-------|
| RMSE | √(Σ(pred-real)²/n) | Error cuadrático medio | Bajo |
| MAE | Σ\|pred-real\|/n | Error absoluto medio | Bajo |
| R² | 1-(SSres/SStot) | Varianza explicada | Cercano a 1 |
| MAPE | 100×Σ(\|pred-real\|/real)/n | Error porcentual | Bajo |

---

## Estructura de Datos del Dataset

```csv
id;fecha;intensidad;ocupacion;carga;vmed;...;conditionsDay;longitud;latitud
3871;01/01/2024 0:00;46;0;1;0;...;cloudy;-366,91;4,04
4370;01/01/2024 0:00;48;3;7;0;...;cloudy;-371,78;4,04
...
```

### Columnas Principales

| Columna | Tipo | Descripción | Usado |
|---------|------|-------------|-------|
| id | Int | Zona de tráfico | ✓ |
| fecha | DateTime | Fecha y hora | ✓ |
| intensidad | Int | **TARGET**: Vehículos/15min | - |
| conditionsDay | String | Condición meteorológica | ✓ |
| temp | Float | Temperatura (°C) | ✓ |
| humidity | Float | Humedad (%) | ✓ |
| conductores_hombres | Int | Cantidad | ✓ |
| De25a34años | Int | Conductores 25-34 años | ✓ |
| Turismo | Int | Vehículos tipo turismo | ✓ |
| ocupacion | Int | Ocupación (%) | ✗ |
| carga | Int | Valor agregado | ✗ |
| vmed | Int | Velocidad media | ✗ |

---

## Uso Programático

### Entrenar un Modelo
```python
from algorithms import entrenar_modelo

resultados, df = entrenar_modelo(
    path_csv="2024_DatasetSample.csv",
    algoritmo="Random Forest Mejorado"
)

print(f"R²: {resultados['r2']:.4f}")
print(f"RMSE: {resultados['rmse']:.2f}")
```

### Hacer Predicciones
```python
modelo = resultados['modelo']
X_nuevo = df_nuevos_datos  # Preparar datos igual que en entrenamiento

predicciones = modelo.predict(X_nuevo)
```

---

## Mejoras Implementadas v2.0

### Versión Anterior (v1.0)
❌ Usaba features de resultado (ocupacion, carga, vmed)
❌ Feature engineering limitado
❌ Modelos básicos
❌ No validación apropiada

### Versión Actual (v2.0)
✓ Solo features a priori
✓ Variables cíclicas temporales
✓ Estadísticas agregadas por zona y hora
✓ 4 modelos avanzados
✓ Métricas completas (RMSE, MAE, R², MAPE)
✓ Documentación técnica completa

Detalles completos en [MODELO_IMPROVEMENTS.md](MODELO_IMPROVEMENTS.md)

---

## Documentación Técnica

- **[MODELO_IMPROVEMENTS.md](MODELO_IMPROVEMENTS.md)** - Análisis detallado de mejoras
- **[FEATURES_TECNICO.md](FEATURES_TECNICO.md)** - Guía técnica de cada feature

---

## Próximas Mejoras

1. Lag features (intensidad de hora anterior)
2. Eventos especiales (festivos, obras)
3. Datos exógenos (accidentes, cierres)
4. Ensemble de modelos
5. Auto-ML para tuning automático
6. Validación temporal (time series CV)

---

## Licencia

Proyecto de investigación - SafeDrive 2026

---

## Contacto y Soporte

Para reportar bugs o sugerencias, abrir un issue en el repositorio.

---

**Última actualización:** Enero 10, 2026  
**Versión:** 2.0  
**Status:** Producción