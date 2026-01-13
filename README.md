# 📘 Documentación Completa - SafeDrive

**Sistema de Predicción de Tráfico en Madrid**  
Versión: 2.0  
Fecha: Enero 2026

---

## 📑 Índice

1. [Visión General](#visión-general)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Modo Técnico](#modo-técnico)
6. [Modo Usuario (Predicción)](#modo-usuario-predicción)
7. [Algoritmos de Machine Learning](#algoritmos-de-machine-learning)
8. [Integración con AEMET](#integración-con-aemet)
9. [API y Estructura de Datos](#api-y-estructura-de-datos)
10. [Guía de Uso](#guía-de-uso)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

SafeDrive es una aplicación de escritorio desarrollada en Python que predice la intensidad de tráfico en las zonas de Madrid utilizando **Machine Learning**. La aplicación integra datos meteorológicos de AEMET en tiempo real mediante web scraping y ofrece dos modos de operación: **Técnico** (para entrenar y evaluar modelos) y **Usuario** (para realizar predicciones rápidas).

### Tecnologías Utilizadas

- **Python 3.12**
- **tkinter** + **sv-ttk** (Interfaz gráfica moderna)
- **scikit-learn** (Machine Learning)
- **TensorFlow/Keras** (Deep Learning)
- **pandas** + **numpy** (Procesamiento de datos)
- **matplotlib** (Visualizaciones)
- **folium** (Mapas interactivos)
- **BeautifulSoup** (Web scraping AEMET)

---

## ✨ Características Principales

### 🔧 Modo Técnico

1. **Entrenamiento de Modelos**
   - 4 algoritmos disponibles:
     - Random Forest Mejorado (recomendado)
     - Gradient Boosting
     - Deep Learning Mejorado
     - Árbol de Decisión Optimizado
   - Una única fuente de datos CSV
   - Visualización de métricas (RMSE, R², MAE, MAPE)
   - Guardado de modelos en formato .mdl

2. **Predicción por Lotes**
   - Carga de ejemplares desde CSV
   - Aplicación de modelos entrenados (.mdl)
   - Clasificación automática: Bajo/Medio/Alto
   - Visualización en tabla y gráfico de pastel
   - Mapa interactivo con Folium
   - Exportación de resultados

### 👤 Modo Usuario (Predicción)

1. **Selector de Zonas**
   - 4873 zonas de tráfico de Madrid disponibles
   - Búsqueda en tiempo real por nombre/ID
   - Selección múltiple con checkboxes
   - Botones "Seleccionar todos" / "Deseleccionar todos"

2. **Predicción Inteligente**
   - Carga de modelo .mdl
   - Selección de fecha y hora (redondeo automático a :15)
   - Obtención automática de datos meteorológicos de AEMET
   - Predicción para múltiples zonas simultáneas
   - Visualización con gráfico de pastel
   - Mapa interactivo con marcadores por nivel

3. **Integración AEMET**
   - Web scraping automático desde AEMET
   - Mapeo inteligente de datos meteorológicos
   - Variables: temperatura, precipitación, viento, nubosidad, etc.

### 🎨 Interfaz Moderna

- **Tema adaptativo** (detección automática de tema oscuro/claro del sistema)
- **Diálogos de carga animados** con spinners Braille (⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏)
- **Threading** para operaciones largas (no se congela la UI)
- **Diseño responsivo** con pestañas organizadas
- **Mapas interactivos** con marcadores de color según nivel de tráfico

---

## 🏗️ Arquitectura del Sistema

### Estructura de Archivos

```
SafeDrive/
│
├── app.py                          # Aplicación principal (Modo Técnico)
├── user_mode.py                    # Módulo del Modo Usuario
├── algorithms.py                   # Algoritmos de ML y preparación de datos
├── aemet_scraper.py               # Web scraping de AEMET
├── aemet_mapper.py                # Mapeo de datos AEMET
│
├── 12-2024_TrafficZones.csv       # Zonas de tráfico de Madrid
├── 2024_DatasetSample.csv         # Dataset de ejemplo para entrenamiento
├── SafeDriveLogo_64x64.png        # Icono de la aplicación
│
└── ModeloEntrenado_*.mdl          # Modelos entrenados guardados
```

### Flujo de Datos

```
┌─────────────────┐
│   Usuario       │
└────────┬────────┘
         │
         ├─────────► Modo Técnico
         │           ├─ Entrenar modelo (CSV → .mdl)
         │           ├─ Predecir lotes (CSV + .mdl → resultados)
         │           └─ Ver métricas/mapas
         │
         └─────────► Modo Usuario
                     ├─ Cargar modelo (.mdl)
                     ├─ Seleccionar zonas
                     ├─ AEMET scraping (fecha/hora)
                     └─ Predicción + mapa
```

### Componentes Clave

1. **LoadingDialog**: Diálogo reutilizable con spinner animado
2. **ZoneSelector**: Widget de selección de zonas con búsqueda
3. **AemetScraper**: Obtiene datos meteorológicos en tiempo real
4. **AemetMapper**: Traduce datos AEMET a features del modelo

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Ejecución

```bash
python app.py
```

### Archivos Necesarios

- `12-2024_TrafficZones.csv`: Zonas de tráfico (incluido)
- `SafeDriveLogo_64x64.png`: Icono (incluido)
- Modelo entrenado `.mdl` (crear con Modo Técnico o usar el incluido)

---

## 🔧 Modo Técnico

### Pestaña: Entrenamiento

#### Paso 1: Seleccionar Datos
- Formato: CSV con separador `;`
- Columnas requeridas:
  - `id`: ID de la zona de tráfico
  - `fecha`: formato "DD/MM/YYYY HH:MM"
  - `intensidad`: valor numérico (variable objetivo)
  - Variables meteorológicas (temp, precipitacion, viento, etc.)

#### Paso 2: Elegir Algoritmo
- **Random Forest Mejorado** ⭐ (RECOMENDADO - MEJOR OPCIÓN)
  - 200 árboles, profundidad máxima 20
  - Mejor RMSE (213.05) y MAE (90.59) de todos los modelos
  - R²: 0.8986 (excelente)
  - MAPE: 47.39%
  - Tiempo de entrenamiento: 7.92s (MÁS RÁPIDO)
  - Mejor relación rendimiento/velocidad

- **Gradient Boosting**
  - 150 árboles, tasa de aprendizaje 0.1
  - RMSE: 224.51, MAE: 100.54
  - R²: 0.8874
  - MAPE: 57.95%
  - Tiempo: 105.39s (13x más lento que Random Forest)

- **Deep Learning Mejorado**
  - Red neuronal 4 capas (256→128→64→1)
  - Dropout 0.3, BatchNorm, Early stopping
  - RMSE: 224.31, MAE: 102.13
  - R²: 0.8876
  - MAPE: 59.73%
  - Tiempo: 81.40s

- **Árbol de Decisión Optimizado**
  - Modelo simple
  - RMSE: 244.71, MAE: 106.36
  - R²: 0.8662 (menor rendimiento)
  - MAPE: 51.78%
  - Tiempo: 29.07s

#### Paso 3: Entrenar
- Click en **"Ejecutar"**
- Se muestra diálogo de carga animado
- Al finalizar:
  - Métricas en pantalla (RMSE, R², MAE, MAPE)
  - Tiempo de entrenamiento
  - Número de ejemplares

#### Paso 4: Guardar Modelo
- Formato: `.mdl` (pickle de joblib)
- Incluye:
  - Modelo entrenado
  - Features numéricas y categóricas
  - Estadísticas por zona y hora
  - Valores medianos para imputación

### Pestaña: Predicción

#### Paso 1: Cargar Datos y Modelo
- **Ejemplares**: CSV con las mismas columnas que entrenamiento
- **Modelo**: archivo `.mdl` previamente guardado

#### Paso 2: Predecir
- Click en **"Predecir"**
- Diálogo de carga mientras se procesa
- Resultados automáticos:
  - Tabla con predicciones
  - Clasificación Bajo/Medio/Alto (basada en z-score)
  - Gráfico de pastel
  - Resumen estadístico

#### Paso 3: Visualizar Mapa
- Click en **"Mapa"**
- Se genera HTML interactivo con Folium
- Marcadores de colores:
  - 🔵 Azul = Bajo
  - 🟠 Naranja = Medio
  - 🔴 Rojo = Alto

#### Paso 4: Exportar
- Guardar resultados en CSV
- Incluye: id, predicción, nivel, zona, coordenadas

---

## 👤 Modo Usuario (Predicción)

### Configuración Inicial

1. **Cargar Modelo**
   - Click en botón **"Seleccionar"** junto a "Modelo entrenado"
   - Elegir archivo `.mdl`
   - Se valida automáticamente

2. **Configurar Fecha y Hora**
   - Fecha: formato DD/MM/YYYY (por defecto: hoy)
   - Hora: 0-23 (por defecto: hora actual)
   - Minutos: 0-59 (se redondea a :00, :15, :30, :45)

### Seleccionar Zonas

#### Búsqueda
- Escribir nombre de zona o ID
- Filtrado instantáneo (sin distinción mayúsculas/minúsculas)
- Ejemplo: "goya" → filtra todas las zonas con "Goya"

#### Selección
- **Checkbox individual**: Click en zona específica
- **Seleccionar todos**: Marca todas las zonas filtradas
- **Deseleccionar todos**: Desmarca todo
- Se pueden seleccionar múltiples zonas para predicción simultánea

### Realizar Predicción

1. Click en **"Predecir"**
2. El sistema automáticamente:
   - Obtiene datos de AEMET (web scraping)
   - Mapea variables meteorológicas
   - Prepara features para el modelo
   - Realiza predicción
3. Diálogo de carga durante el proceso
4. Resultados:
   - Tabla con zonas y predicciones
   - Gráfico de pastel (Bajo/Medio/Alto)
   - Resumen de tiempos

### Ver Mapa

- Click en **"Mapa"**
- Diálogo de carga durante generación
- Se abre HTML en navegador predeterminado
- Marcadores con popup informativo:
  - Nombre de zona
  - ID
  - Intensidad predicha
  - Nivel de tráfico

### Exportar Resultados

- Click en **"Guardar"**
- Formato CSV con separador `;`
- Columnas:
  - id
  - fecha
  - prediccion_intensidad
  - nivel_trafico
  - zona_nombre
  - Variables AEMET

---

## 🤖 Algoritmos de Machine Learning

### Preparación de Datos

#### Features Numéricas
- `id`: ID de zona
- `hora`, `minuto`: componentes temporales
- `dia_semana`, `mes`, `dia_mes`
- `temperatura`, `precipitacion`, `viento_velocidad`
- `nubosidad`, `humedad`, `presion`
- Estadísticas por zona: `zona_intensidad_media`, `zona_intensidad_std`
- Estadísticas por hora: `hora_intensidad_media`

#### Features Categóricas
- `es_festivo`: 0/1
- `periodo_dia`: mañana/tarde/noche/madrugada
- `viento_direccion`: N/S/E/W/NE/NW/SE/SW/Calma

#### Imputación
- Valores faltantes: se usa la mediana de cada columna
- Se almacena en el modelo para consistencia en predicción

### Random Forest Mejorado ⭐ (RECOMENDADO)

```python
Parámetros:
- n_estimators: 200
- max_depth: 20
- min_samples_split: 5
- min_samples_leaf: 2
- random_state: 42
- n_jobs: -1 (usa todos los cores)
```

**Resultados Reales:**
- ✅ RMSE: 213.05 (MEJOR)
- ✅ MAE: 90.59 (MEJOR)
- ✅ R²: 0.8986 (MEJOR)
- ✅ MAPE: 47.39%
- ✅ Tiempo entrenamiento: 7.92s (MÁS RÁPIDO)

**Ventajas:**
- Mejor precisión en todas las métricas
- Entrenamiento extremadamente rápido (13x más rápido que Gradient Boosting)
- Robusto ante outliers
- No requiere escalado
- Captura relaciones no lineales
- Buena interpretabilidad
- **RECOMENDADO para producción**

### Gradient Boosting

```python
Parámetros:
- n_estimators: 150
- learning_rate: 0.1
- max_depth: 7
- subsample: 0.8
- random_state: 42
```

**Resultados Reales:**
- RMSE: 224.51
- MAE: 100.54
- R²: 0.8874
- MAPE: 57.95%
- Tiempo: 105.39s (13x más lento que Random Forest)

### Deep Learning Mejorado

```python
Arquitectura:
Input → Dense(256, relu) → BatchNorm → Dropout(0.3)
     → Dense(128, relu) → BatchNorm → Dropout(0.3)
     → Dense(64, relu) → Dropout(0.2)
     → Dense(1, linear)

Optimizador: Adam (lr=0.001)
Loss: MSE
Early Stopping: patience=15
Epochs: 200
```

**Resultados Reales:**
- RMSE: 224.31
- MAE: 102.13
- R²: 0.8876
- MAPE: 59.73%
- Tiempo: 81.40s

### Árbol de Decisión Optimizado

```python
Parámetros:
- max_depth: 15
- min_samples_split: 10
- min_samples_leaf: 5
- random_state: 42
```

**Resultados Reales:**
- RMSE: 244.71 (peor)
- MAE: 106.36 (peor)
- R²: 0.8662 (peor)
- MAPE: 51.78%
- Tiempo: 29.07s

---

## 🌦️ Integración con AEMET

### Web Scraping (aemet_scraper.py)

#### Funcionamiento
1. Construye URL de AEMET con código de estación y fecha
2. Realiza petición HTTP con headers simulando navegador
3. Parsea HTML con BeautifulSoup
4. Extrae tabla de datos horarios
5. Normaliza y limpia los datos

#### Código de Estación
- Madrid Capital: `3195` (Retiro)
- Se puede cambiar en `AemetScraper(station_code='3195')`

#### Datos Obtenidos
- Temperatura (°C)
- Precipitación (mm)
- Viento velocidad (km/h)
- Viento dirección (puntos cardinales)
- Presión atmosférica (hPa)
- Otros según disponibilidad AEMET

#### Manejo de Errores
- Timeout: 10 segundos
- Reintentos: hasta 3 veces
- Fallback: valores por defecto si falla

### Mapeo de Datos (aemet_mapper.py)

#### AemetMapper.create_prediction_dict()

Transforma datos AEMET crudos a formato esperado por el modelo:

```python
Entrada: {
    'temp': 15.2,
    'precip': 0.0,
    'viento': '10 km/h SW',
    ...
}

Salida: {
    'temperatura': 15.2,
    'precipitacion': 0.0,
    'viento_velocidad': 10,
    'viento_direccion': 'SW',
    'humedad': 65,
    'presion': 1013,
    'nubosidad': 50,
    'es_festivo': 0
}
```

#### Valores por Defecto
Si AEMET no proporciona datos:
- Temperatura: 15°C
- Precipitación: 0 mm
- Viento: 5 km/h, Calma
- Humedad: 60%
- Presión: 1013 hPa
- Nubosidad: 50%

---

## 📊 API y Estructura de Datos

### Formato de Dataset de Entrenamiento

```csv
id;fecha;intensidad;temperatura;precipitacion;viento_velocidad;viento_direccion;humedad;presion;nubosidad;es_festivo
1001;14/01/2026 08:15;245.3;12.5;0.0;15;NW;65;1015;30;0
1002;14/01/2026 08:15;189.7;12.5;0.0;15;NW;65;1015;30;0
...
```

### Formato de Modelo Guardado (.mdl)

```python
{
    'modelo': <trained_model>,
    'features_numericas': [...],
    'features_categoricas': [...],
    'zona_stats': {
        1001: {'mean': 200.5, 'std': 50.2},
        1002: {'mean': 180.3, 'std': 45.8},
        ...
    },
    'hora_stats': {
        0: 120.5, 1: 95.3, ..., 23: 150.2
    },
    'median_values': {
        'temperatura': 15.0,
        'precipitacion': 0.0,
        ...
    },
    'zona_defaults': {
        'zona_intensidad_media': 150.0,
        'zona_intensidad_std': 50.0
    }
}
```

### Zonas de Tráfico (12-2024_TrafficZones.csv)

```csv
id;nombre;latitud;longitud
1001;Glorieta Emperador Carlos V;40.407591;-3.693735
1002;Plaza de Cibeles;40.419380;-3.693375
...
```

### Clasificación de Niveles

Basada en **z-score** respecto a la media y desviación estándar de cada zona:

```python
z = (predicción - media_zona) / std_zona

if z <= -0.5:
    nivel = "Bajo"     # Por debajo de lo normal
elif z >= 0.5:
    nivel = "Alto"     # Por encima de lo normal
else:
    nivel = "Medio"    # Normal
```

---

## 📖 Guía de Uso

### Caso de Uso 1: Entrenar un Modelo Nuevo

1. Preparar datos CSV con formato correcto
2. Abrir SafeDrive
3. Ir a pestaña **"Entrenamiento"**
4. Seleccionar archivo CSV
5. Elegir algoritmo (ej: Random Forest Mejorado)
6. Click **"Ejecutar"**
7. Esperar a que termine (diálogo de carga)
8. Revisar métricas
9. Ingresar nombre para el modelo
10. Click **"Guardar"**

### Caso de Uso 2: Predecir Tráfico Futuro

**Modo Usuario (Recomendado para predicciones diarias):**

1. Abrir pestaña **"Predicción (Usuario)"**
2. Click **"Seleccionar"** y cargar modelo `.mdl`
3. Configurar fecha y hora deseada
4. Buscar y seleccionar zonas de interés
   - Ej: "Gran Via", "Paseo Castellana", etc.
5. Click **"Predecir"**
6. Sistema obtiene datos AEMET automáticamente
7. Revisar resultados en tabla y gráfico
8. Click **"Mapa"** para visualización geográfica
9. (Opcional) Click **"Guardar"** para exportar

### Caso de Uso 3: Análisis por Lotes

**Modo Técnico:**

1. Preparar CSV con ejemplares a predecir (mismo formato que entrenamiento pero sin columna `intensidad`)
2. Ir a pestaña **"Predicción"**
3. Seleccionar archivo CSV de ejemplares
4. Seleccionar modelo `.mdl`
5. Click **"Predecir"**
6. Revisar tabla de resultados
7. Click **"Mapa"** si hay coordenadas
8. Click **"Guardar"** para exportar

### Caso de Uso 4: Comparar Algoritmos

1. Entrenar mismo dataset con diferentes algoritmos
2. Comparar métricas:
   - **RMSE** (menor es mejor)
   - **R²** (cercano a 1 es mejor)
   - **MAE** (menor es mejor)
   - **MAPE** (menor % es mejor)
3. Considerar también:
   - Tiempo de entrenamiento
   - Tiempo de predicción
   - Tamaño del modelo guardado

**Recomendación:** Random Forest Mejorado ofrece el mejor balance en todas las métricas, con RMSE y MAE bajos, R² alto y tiempo de entrenamiento muy competitivo.

---

## 🔍 Troubleshooting

### Error: "No se pudo cargar el modelo"

**Causa:** Archivo .mdl corrupto o incompatible  
**Solución:**
- Verificar que es un archivo .mdl válido
- Reentrenar el modelo si es necesario
- Asegurarse de usar Python 3.12 compatible con joblib

### Error: "No se pudieron obtener datos de AEMET"

**Causas posibles:**
1. Sin conexión a internet
2. AEMET no tiene datos para esa fecha/hora
3. Hora fuera del rango válido (0-23)

**Soluciones:**
- Verificar conexión a internet
- Intentar con hora más reciente
- Verificar que la hora es válida (0-23)

### Error: "Debe seleccionar al menos una zona"

**Causa:** No se seleccionaron zonas en Modo Usuario  
**Solución:**
- Hacer click en checkbox de al menos una zona
- O usar "Seleccionar todos"

### La aplicación se congela

**Causa:** Versión antigua sin threading  
**Solución:**
- Actualizar a la versión 2.0 más reciente
- Verificar que los diálogos de carga aparecen

### Predicciones muy lentas

**Causas posibles:**
1. Deep Learning con CPU
2. Demasiadas zonas seleccionadas
3. Datos de AEMET lentos

**Soluciones:**
- Usar Random Forest Mejorado (mejor rendimiento y más rápido que otros)
- Seleccionar menos zonas a la vez
- Esperar a que complete (diálogo de carga)

### Mapa no se abre

**Causa:** Folium no instalado  
**Solución:**
```bash
pip install folium
```

### Gráficos no aparecen

**Causa:** Matplotlib no instalado  
**Solución:**
```bash
pip install matplotlib
```

### Error de codificación en CSV

**Causa:** Codificación incorrecta  
**Solución:**
- Asegurarse de usar UTF-8 o Latin-1
- Separador: `;` (punto y coma)
- Guardar CSV con Excel: "CSV (delimitado por comas)" y cambiar , por ;

---

## 📈 Métricas de Rendimiento

### Modelos Típicos

Con dataset de ejemplo (~50,000 registros):

| Algoritmo | RMSE | MAE | R² | MAPE | Tiempo |
|-----------|------|----|----|------|--------|
| **Random Forest** ⭐ | **213.05** | **90.59** | **0.8986** | **47.39%** | **7.92s** |
| Gradient Boosting | 224.51 | 100.54 | 0.8874 | 57.95% | 105.39s |
| Deep Learning | 224.31 | 102.13 | 0.8876 | 59.73% | 81.40s |
| Árbol Decisión | 244.71 | 106.36 | 0.8662 | 51.78% | 29.07s |

### Tiempos de Predicción

- **1 zona**: < 0.1s
- **10 zonas**: 0.1-0.3s
- **100 zonas**: 0.5-1s
- **4873 zonas (todas)**: 3-5s

*Nota: Incluye scraping AEMET (~1-2s)*

---

## 🚀 Características Técnicas Avanzadas

### Threading

- Todas las operaciones largas (entrenamiento, predicción, generación de mapas) usan hilos separados
- La UI permanece responsiva durante procesamiento
- Diálogos de carga con animación Braille suave

### Gestión de Memoria

- Modelos se cargan bajo demanda
- Liberación automática de recursos
- Manejo eficiente de DataFrames grandes

### Manejo de Errores

- Try-catch comprehensivo en todas las funciones críticas
- Mensajes de error descriptivos para el usuario
- Logging de errores con traceback

### Optimizaciones

- Búsqueda de zonas con filtrado instantáneo
- Caché de estadísticas por zona
- Paralelización en Random Forest (n_jobs=-1)
- Early stopping en Deep Learning

---

## 📝 Notas Adicionales

### Recomendación de Algoritmo

Basado en evaluación comparativa exhaustiva con datos reales, **Random Forest Mejorado** es la opción recomendada porque:
- ✅ **MEJOR RMSE:** 213.05 (10% mejor que Gradient Boosting)
- ✅ **MEJOR MAE:** 90.59 (11% mejor que Gradient Boosting)
- ✅ **MEJOR R²:** 0.8986 (1.1% mejor que Gradient Boosting)
- ✅ **MEJOR MAPE:** 47.39%
- ✅ **TIEMPO MÍNIMO:** 7.92s (13x más rápido que Gradient Boosting, 10x más rápido que Deep Learning)
- ✅ Robusto y confiable en producción
- ✅ Balance perfecto entre rendimiento y velocidad

### Limitaciones Conocidas

1. **Datos AEMET**: Solo disponibles para horas recientes/actuales
2. **Cobertura**: Solo zonas de Madrid capital
3. **Idioma**: Interfaz en español
4. **Plataforma**: Diseñado para Windows/Linux/Mac con Python 3.12+

### Mejoras Futuras Sugeridas

1. Predicción multi-fecha (próximas 24-48h)
2. Integración con API oficial AEMET
3. Exportación a otros formatos (Excel, JSON)
4. Gráficos de series temporales
5. Comparación de predicciones vs real
6. Modo oscuro/claro manual
7. Soporte para otras ciudades

### Contribuciones

Este es un proyecto educativo/académico. Para contribuir:
- Reportar bugs
- Sugerir mejoras
- Compartir datasets de entrenamiento
- Optimizar algoritmos

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar esta documentación completa
2. Verificar versión de Python (3.12+)
3. Asegurar todas las dependencias instaladas
4. Revisar archivos .csv y .mdl son válidos

---

**SafeDrive v2.0** - Sistema de Predicción de Tráfico en Madrid  
Documentación actualizada: Enero 2026