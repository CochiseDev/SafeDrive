# Guía Técnica: Features de Predicción de Tráfico

## Índice
1. [Descripción General](#descripción-general)
2. [Features Temporales](#features-temporales)
3. [Features Meteorológicas](#features-meteorológicas)
4. [Features de Zona](#features-de-zona)
5. [Preprocesamiento](#preprocesamiento)

---

## Descripción General

El modelo utiliza **~40-50 features** divididas en 5 categorías principales:

```
Features de Predicción
├── Temporales (8)
├── Meteorológicas (11)
├── Zona (5)
└── Hora Agregada (2)
```

**Principio Fundamental:** Solo se utilizan features disponibles **antes de hacer la predicción** (a priori).

> **Nota Importante:** Se han eliminado los datos demográficos (género, edad, tipo de vehículo) que añadían ruido sin contribuir significativamente a la precisión del modelo.

---

## Features Temporales

### Variables Principales

| Feature | Tipo | Rango | Descripción |
|---------|------|-------|-------------|
| `hora` | Entero | 0-23 | Hora del día |
| `mes` | Entero | 1-12 | Mes del año |
| `dia_semana` | Entero | 0-6 | Día de la semana (0=Lunes) |
| `es_fin_semana` | Binario | 0/1 | 1 si sábado/domingo |
| `trimestre` | Entero | 1-4 | Trimestre del año |

### Variables Cíclicas

Las variables temporales se transforman en variables cíclicas para capturar la naturaleza repetitiva del tiempo:

```python
# Ciclo diario (24 horas)
hora_sin = sin(2π × hora / 24)
hora_cos = cos(2π × hora / 24)

# Ciclo anual (12 meses)
mes_sin = sin(2π × mes / 12)
mes_cos = cos(2π × mes / 12)

# Ciclo semanal (7 días)
dia_sin = sin(2π × dia_semana / 7)
dia_cos = cos(2π × dia_semana / 7)
```

**Ventaja:** 
- La distancia euclidiana entre (sin, cos) es proporcional a la distancia temporal
- 23:00 está cerca de 01:00 en el ciclo diario
- Evita la discontinuidad de variables categóricas

### Bandas Horarias

Se crean variables binarias para capturar patrones de tráfico por período del día:

```
es_noche = 1 si 22:00-06:00 (tráfico bajo, patrones predecibles)
es_manana = 1 si 06:00-12:00 (incremento matutino, hora punta)
es_tarde = 1 si 12:00-18:00 (tráfico equilibrado)
es_trafico_punta = 1 si 07:00-09:00 o 17:00-20:00 (máxima congestión)
```

**Interpretación:**
- Noche: Bajo volumen, tráfico fluido
- Mañana: Incremento gradual hacia la punta
- Tarde: Nivel medio, variabilidad moderada
- Punta: Máxima congestión, patrones más predecibles

---

## Features Meteorológicas

### Temperatura

| Feature | Unidad | Rango típico | Descripción |
|---------|--------|------|-------------|
| `temp` | °C | -5 a 40 | Temperatura real |
| `feelslike` | °C | -10 a 45 | Temperatura aparente (incluye viento) |
| `dew` | °C | -20 a 25 | Punto de rocío |

**Impacto en tráfico:**
- Temperaturas muy bajas (< 0°C): Reducen velocidad, aumentan accidentes
- Temperaturas altas (> 35°C): Congestión por maniobras lentas
- Punto de rocío alto: Indica humedad (menor visibilidad)

### Humedad y Precipitación

| Feature | Unidad | Rango | Descripción |
|---------|--------|-------|-------------|
| `humidity` | % | 0-100 | Humedad relativa |
| `precip` | mm | 0+ | Cantidad de precipitación |
| `precipprob` | % | 0-100 | Probabilidad de lluvia |

**Impacto:**
- Precipitación > 0mm: Reduce visibilidad y velocidad
- Humedad alta: Puede estar asociada a lluvia
- Precipprob > 70%: Indica clima inestable, mayor riesgo

### Viento

| Feature | Unidad | Rango | Descripción |
|---------|--------|-------|-------------|
| `windspeed` | km/h | 0-50+ | Velocidad del viento |
| `windgust` | km/h | 0-100+ | Velocidad de ráfagas máximas |
| `winddir` | grados | 0-360 | Dirección del viento |

**Impacto:**
- Ráfagas > 40 km/h: Afecta vehículos altos (camiones), pueden retrasos
- Dirección: No está normalizando, por eso se usa en forma continua

### Nubes y Visibilidad

| Feature | Unidad | Rango | Descripción |
|---------|--------|-------|-------------|
| `cloudcover` | % | 0-100 | Cobertura de nubes |
| `visibility` | km | 0-20+ | Visibilidad horizontal |

**Impacto:**
- cloudcover < 20%: Visibilidad excelente, menos accidentes
- visibility < 5km: Lluvia/niebla, tráfico más lento
- visibility > 15km: Condiciones óptimas, tráfico más fluido

### Condición Meteorológica (Categorical)

| Valor | Descripción | Impacto en Tráfico |
|-------|-------------|-------------------|
| `clear` | Despejado | Óptimo, tráfico fluido |
| `partly-cloudy` | Parcialmente nublado | Moderado, sin efectos |
| `cloudy` | Nublado | Leve reducción de visibilidad |
| `rain` | Lluvia | Moderado a alto (reduce velocidad) |
| `snow` | Nieve | Muy alto (máxima congestión) |
| `foggy` | Niebla | Muy alto (baja visibilidad) |

---

## Features de Zona

### ID de Zona

| Feature | Tipo | Rango | Descripción |
|---------|------|-------|-------------|
| `id` | Entero | 1001-11385 | Identificador único de zona de tráfico |

**Interpretación:**
- Cada ID representa una zona/segmento de carretera específico
- Captura características invariantes de la zona (ubicación, tipo de vía, etc.)

### Estadísticas Agregadas por Zona

Se calculan estadísticas históricas de intensidad para cada zona:

```python
zona_intensidad_media = promedio(intensidad) para cada id
zona_intensidad_std = desviacion_estandar(intensidad) para cada id
zona_intensidad_min = valor_minimo(intensidad) para cada id
zona_intensidad_max = valor_maximo(intensidad) para cada id
```

**Utilidad:**
- `media`: Nivel "base" de tráfico en esa zona
- `std`: Variabilidad (zonas estables vs. impredecibles)
- `min/max`: Rango de variación esperada

**Ejemplo:**
```
Zona A: media=200, std=50   (tráfico moderado, predecible)
Zona B: media=400, std=150  (tráfico alto, variable)
Zona C: media=100, std=20   (tráfico bajo, muy predecible)
```

---

## Features Hora Agregada

### Estadísticas por Hora Global

Se calculan promedios para cada hora del día (agregando todas las zonas):

```python
hora_intensidad_media = promedio(intensidad) para cada hora
hora_intensidad_std = desviacion_estandar(intensidad) para cada hora
```

**Utilidad:**
- Captura patrones globales de tráfico por hora
- Complementa las bandas horarias con valores cuantitativos

**Ejemplo:**
```
Hora 08:00: media=500, std=100  (punta matutina)
Hora 14:00: media=250, std=80   (postmeridiano)
Hora 22:00: media=80,  std=30   (noche)
```

---

## Variables Transformadas

### Estandarización (StandardScaler)

```python
X_scaled = (X - media) / desviacion_estandar
```

**Aplicado a:** Todas las features numéricas

**Razón:** 
- Los modelos (especialmente redes neuronales) aprenden mejor con variables normalizadas
- Evita que variables con mayor escala dominen el aprendizaje

**Ejemplo:**
```
Temperatura: rango 0-40°C → rango -2 a +2 (escala estándar)
Humedad: rango 0-100% → rango -1 a +3 (escala estándar)
```

### One-Hot Encoding (Variables Categóricas)

```python
conditionsDay:
- clear → [1, 0, 0, 0, 0, 0]
- cloudy → [0, 1, 0, 0, 0, 0]
- rain → [0, 0, 1, 0, 0, 0]
...
```

**Aplicado a:** 
- `conditionsDay` (6 categorías)

**Resultado:** 
- Se crea una columna binaria para cada categoría
- El modelo puede aprender efectos diferentes para cada condición

---

## Preprocesamiento

### Pipeline Completo

```python
ColumnTransformer:
├── Numéricas (40 features)
│   └── StandardScaler → normalización [-1 a +3]
└── Categóricas (1 feature)
    └── OneHotEncoder → 6 columnas binarias
    
Total features después de transformación: ~46
```

### Manejo de Valores Faltantes

```python
# En features numéricas
valor_faltante → mediana_feature
```

**Razón de usar mediana:**
- Robusta a outliers (mejor que media)
- Mantiene distribución del feature
- Alternativa: usar promedio por zona/hora

### Manejo de Valores Desconocidos en Categorías

```python
# En conditionsDay, si aparece valor nuevo
valor_desconocido → OneHotEncoder(handle_unknown='ignore')
# Resultado: todos los one-hot valores = 0
```

---

## Ejemplo de Datos Transformados

### Datos Originales
```
id=3490, fecha='01/01/2024 08:00', temp=12.5, humidity=85.0,
conductores_hombres=2, De25a34=1, Turismo=3, conditionsDay='cloudy'
```

### Después de Feature Engineering
```
id=3490
hora=8, mes=1, dia_semana=0, es_fin_semana=0, trimestre=1
hora_sin=0.707, hora_cos=0.707  (ciclo diario)
mes_sin=-0.087, mes_cos=0.996   (ciclo anual)
dia_sin=0.0, dia_cos=1.0         (ciclo semanal)
es_noche=0, es_manana=1, es_tarde=0, es_trafico_punta=1
zona_intensidad_media=500, zona_intensidad_std=100
hora_intensidad_media=450, hora_intensidad_std=80
temp=12.5, feelslike=10.0, humidity=85.0, windspeed=8.0
cloudcover=100, visibility=12.0
conductores_hombres=2, conductores_mujeres=1
De25a34=1, De45a54=0, Turismo=3, Motocicletas=0
conditionsDay_clear=0, conditionsDay_cloudy=1, conditionsDay_rain=0
```

### Después de Estandarización y Codificación
```
Todos los valores numéricos normalizados: [-1 a +3]
Variables categóricas transformadas a binarias: [0, 1]
```

---

## Resumen de Información Disponible

### Antes de Hacer la Predicción (A Priori)
✓ Fecha y hora (conocemos el momento exacto)
✓ Zona de tráfico (sabemos dónde predecir)
✓ Condiciones meteorológicas (pronóstico en tiempo real)
✓ Datos históricos (estadísticas de esa zona/hora)
✓ Información demográfica (censo de conductores)

### NO Disponible (Exluído del Modelo)
✗ Intensidad de tráfico actual (`ocupacion`, `carga`, `vmed`)
✗ Lesiones/accidentes (consecuencias, no causas)
✗ Coordenadas exactas (redundante con ID de zona)
✗ Metadatos de medición (`periodo_integracion`)

---

## Métricas de Evaluación

### RMSE (Root Mean Squared Error)
```
RMSE = √(Σ(predicción - real)² / n)
```
- Penaliza más los errores grandes
- Escala: mismas unidades que el target (vehículos/hora)
- **Mejor:** RMSE bajo

### MAE (Mean Absolute Error)
```
MAE = Σ|predicción - real| / n
```
- Interpretable directamente: error promedio en vehículos
- Robusto a outliers
- **Mejor:** MAE bajo

### R² (Coeficiente de Determinación)
```
R² = 1 - (SS_res / SS_tot)
```
- Proporción de varianza explicada (0-1)
- R²=1: Predicción perfecta
- R²=0: El modelo no aprende
- **Mejor:** R² cercano a 1

### MAPE (Mean Absolute Percentage Error)
```
MAPE = 100 × Σ(|predicción - real| / real) / n
```
- Error en porcentaje
- Útil cuando el target varía mucho en escala
- **Mejor:** MAPE bajo (< 20% es bueno)

---

**Documento Técnico - SafeDrive Traffic Prediction v2.0**
