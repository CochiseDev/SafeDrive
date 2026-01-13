# Modo Usuario Normal - SafeDrive

## 📋 Descripción General

El **Modo Usuario Normal** es una interfaz simplificada de SafeDrive diseñada para usuarios finales que quieren hacer predicciones de intensidad de tráfico sin necesidad de conocimientos técnicos.

### ¿Qué es diferente del modo técnico?

| Aspecto | Modo Técnico | Usuario Normal |
|--------|------------|-----------------|
| **Entrada de datos** | Sube CSV con métricas meteorológicas | Selecciona fecha/hora, AEMET obtiene datos |
| **Selección de zonas** | CSV con una columna 'id' | GUI con búsqueda y filtros |
| **Preparación de datos** | Manual | Automática (web scraping + mapeo) |
| **Complejidad** | Alta (Data Scientists) | Baja (Usuarios finales) |

---

## 🚀 Cómo Usar

### 1. Iniciar la Aplicación

```bash
python app.py
```

Verás 3 pestañas:
- **Entrenamiento**: Para entrenar nuevos modelos (técnico)
- **Predicción (Técnico)**: Para predicciones avanzadas
- **Usuario Normal**: ← AQUÍ PARA USUARIOS FINALES

### 2. Cargar un Modelo Entrenado

1. Click en **"Cargar modelo..."**
2. Selecciona un archivo `.pkl` de modelo entrenado
3. Verás confirmación: "✓ Modelo cargado: nombre_archivo.pkl"

### 3. Seleccionar Fecha y Hora

1. **Fecha**: Escribe en formato `DD/MM/YYYY` (ej: `15/01/2026`)
2. **Hora**: Usa el selector de 0-23 (ej: `14` = 14:00)

> Nota: Actualmente solo funciona para predicciones de hoy/mañana (AEMET proporciona datos horarios para 2-3 días)

### 4. Seleccionar Zonas

La lista muestra todas las **11,385 zonas de tráfico de Madrid**.

**Opciones:**
- **Búsqueda**: Escribe nombre de zona, avenida, etc.
  - Ejemplo: "Alcalá" muestra todas las zonas de Alcalá
  - Ejemplo: "M-30" muestra zonas de la M-30
  
- **Seleccionar todos**: Click botón "Seleccionar todos"
- **Deseleccionar todos**: Click botón "Deseleccionar todos"
- **Selección individual**: Click en zona + Ctrl/Cmd para múltiples

### 5. Obtener Datos Meteorológicos

1. Click en **"Obtener datos de AEMET"**
2. El sistema:
   - Se conecta a AEMET
   - Extrae predicción para la fecha/hora
   - Mapea datos al formato del modelo
   - Muestra los datos extraídos

**Ejemplo de datos extraídos:**
```
temp                 :     22.50
feelslike            :     20.50
humidity             :     65.00
windspeed            :     12.00
windgust             :     25.00
precip               :      2.00
cloudcover           :     35.00
visibility           :     10.00
conditionsDay        : partly-cloudy
```

### 6. Realizar Predicción

1. Click en **"🔮 PREDECIR"**
2. El sistema:
   - Crea filas de datos (una por zona)
   - Aplica feature engineering automático
   - Ejecuta el modelo
   - Clasifica tráfico como Bajo/Medio/Alto
   - Muestra tabla de resultados

### 7. Ver Resultados

Aparece ventana con tabla:

| ID | Zona | Predicción (veh/15min) | Nivel Tráfico |
|----|------|------------------------|---------------|
| 3871 | Av. Cardenal Herrera Oria | 125 | Bajo |
| 4370 | Arlanza | 280 | Alto |
| ... | ... | ... | ... |

**Opciones:**
- Exportar a CSV: Click "Exportar a CSV"
- Ver en pantalla: Tabla completa scrolleable

---

## 🔧 Componentes Técnicos

### `aemet_scraper.py`
Realiza web scraping de AEMET.

```python
from aemet_scraper import AemetScraper

scraper = AemetScraper()
hourly_data = scraper.get_hourly_data()
# Retorna: {hora: {estadoCielo, temperatura, ...}}
```

**Métodos:**
- `get_hourly_data()`: Extrae predicción por horas
- `test_connection()`: Verifica conectividad
- `get_forecast_for_datetime()`: Obtiene dato para fecha/hora específica

### `aemet_mapper.py`
Mapea datos AEMET al formato del modelo.

```python
from aemet_mapper import AemetMapper

mapper = AemetMapper()
mapped = mapper.create_prediction_dict({
    'estadoCielo': 'Parcialmente nublado',
    'temperatura': '22',
    ...
})
# Retorna: {temp, feelslike, humidity, ...}
```

**Características:**
- **Mapeo de condiciones**: "Parcialmente nublado" → "partly-cloudy"
- **Mapeo de viento**: "SO" → 225.0°
- **Estimaciones**: Punto de rocío, visibilidad, etc.
- **Validación**: Rango de valores razonables

### `user_mode.py`
Interfaz GUI para modo usuario.

**Clases:**
- `ZoneSelector`: Widget para seleccionar zonas
- `UserModeTab`: Pestaña principal

---

## 📊 Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│                   Usuario Selecciona                    │
│              Fecha (DD/MM/YYYY) + Hora (00-23)         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│          AemetScraper.get_hourly_data()                │
│                                                         │
│  GET https://www.aemet.es/.../madrid-id28079          │
│  ↓                                                      │
│  BeautifulSoup parse HTML                              │
│  ↓                                                      │
│  Extrae: estadoCielo, temperatura, viento, etc.       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│        AemetMapper.create_prediction_dict()            │
│                                                         │
│  "Parcialmente nublado" → "partly-cloudy"             │
│  "SO" → 225.0°                                        │
│  Estima: punto de rocío, visibilidad, etc.           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│          Usuario Selecciona Zonas                       │
│              (11,385 disponibles)                       │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│          Crea DataFrame de Predicción                   │
│                                                         │
│  Filas: Una por zona seleccionada                      │
│  Columnas: id, fecha, temp, humidity, ...             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│    preparar_datos_prediccion() - Feature Engineering    │
│                                                         │
│  ├─ Variables cíclicas: sin/cos(hora), sin/cos(mes)   │
│  ├─ Bandas horarias: noche, mañana, punta             │
│  ├─ Estadísticas por zona                             │
│  └─ Estadísticas por hora                             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│           Modelo.predict(features)                      │
│                                                         │
│  Entrada: ~25-30 features numéricos                    │
│  Salida: Intensidad predicha (veh/15min)              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│       Clasificar Nivel (Bajo/Medio/Alto)               │
│                                                         │
│  Usa z-score basado en estadísticas de zona           │
│  Z ≤ -0.5: Bajo                                        │
│  Z ≥ +0.5: Alto                                        │
│  -0.5 < Z < 0.5: Medio                                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Mostrar Resultados                         │
│                                                         │
│  Tabla: ID | Zona | Predicción | Nivel                │
│  Opción: Exportar a CSV                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Probar la Funcionalidad

```bash
python test_user_mode.py
```

Esto ejecuta 4 pruebas:
1. **AEMET Scraper**: Conectividad y extracción
2. **AEMET Mapper**: Mapeo de datos
3. **Mapeo de Condiciones**: Clima AEMET → modelo
4. **Mapeo de Viento**: Direcciones cardinales → grados

---

## 📝 Mapeos de Condiciones Climáticas

### AEMET → Modelo

| AEMET | Modelo |
|-------|--------|
| Despejado | clear |
| Poco nuboso, Parcialmente nublado | partly-cloudy |
| Nuboso, Nublado, Cubierto | cloudy |
| Lluvia, Chubascos, Tormenta | rain |
| Nieve | snow |
| Niebla, Neblina | foggy |

### Direcciones de Viento

| Dirección | Grados |
|-----------|--------|
| N | 0° |
| NE | 45° |
| E | 90° |
| SE | 135° |
| S | 180° |
| SO | 225° |
| O | 270° |
| NO | 315° |

---

## ⚙️ Estimaciones Automáticas

Cuando AEMET no proporciona ciertos datos, se estiman basados en la condición climática:

| Variable | Fórmula/Estimación |
|----------|------------------|
| Punto de rocío | Td = T - ((100 - RH) / 5) |
| Cobertura de nubes | Según condición (0-100%) |
| Visibilidad | Según condición y precip (0-20 km) |
| Prob. lluvia | 100% si hay precip, sino según condición |

---

## 🐛 Troubleshooting

### "No se puede conectar a AEMET"
- Verifica conexión a internet
- AEMET puede estar no disponible temporalmente
- Intenta en unos minutos

### "No hay datos para la hora X"
- AEMET solo proporciona datos para 2-3 días adelante
- Intenta con una hora diferente
- O intenta con otra fecha

### "Condición AEMET no mapeada"
- La aplicación asigna "clear" por defecto
- Aviso en consola: ⚠️ Condición no mapeada
- El modelo sigue funcionando normalmente

### Modelo no carga
- Verifica que el archivo `.pkl` es válido
- Fue entrenado con esta versión de SafeDrive
- Permisos de lectura en el archivo

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Predicción Simple
```
1. Fecha: 15/01/2026
2. Hora: 14
3. Zona: [3871] (Av. Cardenal Herrera Oria)
4. Obtener AEMET
5. Predecir
→ Resultado: 125 veh/15min, Bajo
```

### Ejemplo 2: Múltiples Zonas
```
1. Búsqueda: "Alcalá"
2. Seleccionar todos (todas las de Alcalá)
3. Fecha: 15/01/2026, Hora: 08
4. Obtener AEMET
5. Predecir
→ Resultados para todas las zonas de Alcalá
```

### Ejemplo 3: Hora Punta
```
1. Fecha: 15/01/2026
2. Hora: 08 (mañana punta)
3. Zona: [6698] (M-30)
4. Obtener AEMET
5. Predecir
→ Predicción para hora punta
```

---

## 📦 Dependencias

```
requests         - Web scraping
beautifulsoup4   - Parsing HTML
pandas           - DataFrames
scikit-learn     - Modelos ML
joblib           - Serialización
folium          - Mapas (opcional)
matplotlib      - Gráficos (opcional)
```

---

## 🔄 Flujo de Desarrollo Futuro

### Próximas mejoras:
- [ ] Predicción para múltiples días
- [ ] Exportar a Excel con formato
- [ ] Mostrar en mapa interactivo
- [ ] Histórico de predicciones
- [ ] Comparar con datos reales

---

**Versión**: 2.0  
**Fecha**: Enero 2026  
**Estado**: Producción
