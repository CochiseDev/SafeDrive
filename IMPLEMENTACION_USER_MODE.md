# Modo Usuario Normal - Guía de Implementación

## 📦 Archivos Nuevos Agregados

### 1. **aemet_scraper.py** (287 líneas)
**Propósito**: Web scraping de datos meteorológicos de AEMET

**Características principales**:
- Clase `AemetScraper` para extraer predicciones horarias
- Método `get_hourly_data()`: Obtiene datos para 24-48 horas
- Método `test_connection()`: Verifica conectividad
- Manejo robusto de errores y timeouts
- Extrae: hora, condición, temperatura, viento, precipitación, humedad

**Ejemplo**:
```python
scraper = AemetScraper()
if scraper.test_connection():
    hourly_data = scraper.get_hourly_data()  # {hora: {datos}}
    datos_14h = hourly_data['14']  # Datos de las 14:00
```

---

### 2. **aemet_mapper.py** (359 líneas)
**Propósito**: Convertir datos AEMET al formato esperado por el modelo

**Características principales**:
- Clase `AemetMapper` con métodos de mapeo
- `map_condition()`: Traduce condiciones climáticas
  - "Parcialmente nublado" → "partly-cloudy"
  - "Lluvia" → "rain"
  - "Nieve" → "snow"
  - etc.

- `map_wind_direction()`: Convierte direcciones a grados (0-360°)
  - "SO" → 225°
  - "NE" → 45°
  - etc.

- `create_prediction_dict()`: Convierte datos raw AEMET a formato modelo
  - Entrada: datos brutos de AEMET
  - Salida: {temp, feelslike, humidity, windspeed, ...}

- Funciones de estimación (point of dew, cloudcover, visibility)

**Ejemplo**:
```python
mapper = AemetMapper()
mapped = mapper.create_prediction_dict({
    'estadoCielo': 'Parcialmente nublado',
    'temperatura': '22',
    'direccionViento': 'SO',
    ...
})
# Retorna: {temp: 22.0, conditionsDay: 'partly-cloudy', ...}
```

---

### 3. **user_mode.py** (568 líneas)
**Propósito**: Interfaz GUI para usuarios finales

**Componentes**:

#### Clase `ZoneSelector`
Widget para seleccionar zonas de tráfico:
- Búsqueda en tiempo real
- Listbox con 11,385 zonas
- Botones: "Seleccionar todos", "Deseleccionar todos"
- Muestra: [ID] Nombre de Zona

#### Clase `UserModeTab`
Pestaña principal "Usuario Normal" con 4 secciones:

1. **Cargar Modelo**: 
   - Botón para cargar archivo .pkl
   - Indicador de estado

2. **Fecha y Hora**:
   - DatePicker para DD/MM/YYYY
   - Spinbox para 0-23 horas

3. **Seleccionar Zonas**:
   - ZoneSelector integrado
   - 11,385 zonas disponibles

4. **Datos Meteorológicos**:
   - Botón "Obtener datos de AEMET"
   - Muestra datos extraídos en tabla

5. **Predicción**:
   - Botón "🔮 PREDECIR"
   - Ventana de resultados con tabla

**Métodos principales**:
- `_load_model()`: Carga modelo entrenado
- `_fetch_aemet_data()`: Obtiene datos de AEMET
- `_make_prediction()`: Ejecuta predicción
- `_show_results_window()`: Muestra resultados
- `_export_results()`: Exporta a CSV

---

### 4. **test_user_mode.py** (211 líneas)
**Propósito**: Suite de pruebas para validar la funcionalidad

**Pruebas incluidas**:
1. AEMET Scraper - Conectividad y extracción
2. AEMET Mapper - Mapeo de datos
3. Mapeo de Condiciones - AEMET → modelo
4. Mapeo de Viento - Direcciones → grados

**Uso**:
```bash
python test_user_mode.py
```

---

### 5. **ejemplo_user_mode.py** (269 líneas)
**Propósito**: Ejemplo completo de uso programático

**Flujo demostrativo**:
1. Carga modelo entrenado
2. Obtiene datos de AEMET
3. Mapea datos
4. Selecciona 5 zonas ejemplo
5. Aplica feature engineering
6. Ejecuta predicción
7. Clasifica nivel de tráfico
8. Muestra resultados

**Uso**:
```bash
python ejemplo_user_mode.py
```

---

### 6. **USER_MODE_GUIDE.md** (440 líneas)
**Propósito**: Documentación completa para usuarios

**Secciones**:
- Descripción general
- Instrucciones paso a paso
- Componentes técnicos
- Flujo de datos
- Mapeos de condiciones
- Estimaciones automáticas
- Troubleshooting
- Ejemplos de uso

---

## 📝 Cambios en Archivos Existentes

### `app.py`
**Modificaciones**:
1. Agregado import de `user_mode.py`
   ```python
   from user_mode import UserModeTab
   ```

2. Renombrada pestaña técnica
   ```python
   # Antes: "Predicción"
   # Ahora: "Predicción (Técnico)"
   ```

3. Instancia de UserModeTab en __init__
   ```python
   if self.traffic_zones is not None:
       self.user_mode_tab = UserModeTab(self.notebook, self.traffic_zones)
   ```

**Resultado**: 3 pestañas en vez de 2:
- Entrenamiento
- Predicción (Técnico)
- **Usuario Normal** ← NUEVA

---

## 🔄 Flujo de Datos Completo

```
┌─────────────────────────────────────────────────────┐
│   Usuario Abre app.py y va a "Usuario Normal"      │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│   1. Carga modelo .pkl                              │
│      user_mode.py → _load_model()                  │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│   2. Selecciona Fecha + Hora                        │
│      ZoneSelector → busca, selecciona zonas        │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│   3. Click "Obtener datos de AEMET"                 │
│      aemet_scraper.py → get_hourly_data()         │
│      ↓                                              │
│      aemet_mapper.py → create_prediction_dict()   │
│      ↓                                              │
│      Muestra datos en tabla                        │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│   4. Click "🔮 PREDECIR"                            │
│      Crea DataFrame (id, fecha, features...)       │
│      ↓                                              │
│      algorithms.preparar_datos_prediccion()        │
│      ↓                                              │
│      Modelo.predict(features)                      │
│      ↓                                              │
│      Clasificar: Bajo/Medio/Alto                   │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│   5. Muestra ventana de resultados                  │
│      Tabla: ID | Zona | Predicción | Nivel        │
│      Opción: Exportar a CSV                        │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Características Principales

### Para Usuarios Finales
✅ **Interfaz intuitiva**: Sin necesidad de código  
✅ **Búsqueda de zonas**: Filtra 11,385 zonas por nombre  
✅ **Datos meteorológicos automáticos**: Web scraping de AEMET  
✅ **Predicción en un click**: Resultado en segundos  
✅ **Exportar resultados**: Tabla a CSV  
✅ **Clasificación automática**: Bajo/Medio/Alto tráfico  

### Para Desarrolladores
✅ **Modular**: 3 módulos independientes (scraper, mapper, UI)  
✅ **Testeable**: Suite de pruebas incluida  
✅ **Documentado**: Docstrings y guías completas  
✅ **Robusto**: Manejo de errores y validaciones  
✅ **Extensible**: Fácil agregar nuevas funciones  

---

## 🧪 Validación de Funcionalidad

### Test 1: Conexión AEMET
```python
python test_user_mode.py
# ✓ Conexión a AEMET
# ✓ Se extraen 24+ horas
```

### Test 2: Mapeo de Datos
```python
# Prueba que "Parcialmente nublado" → "partly-cloudy"
# Prueba que "SO" → 225°
# Prueba estimaciones (punto rocío, visibilidad)
```

### Test 3: Predicción Completa
```python
python ejemplo_user_mode.py
# Simula flujo completo: modelo → AEMET → predicción
# Muestra 5 zonas con resultados
```

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Líneas de código nuevas | ~1,700 |
| Archivos nuevos | 6 |
| Clases nuevas | 2 |
| Métodos nuevos | ~40 |
| Condiciones mapeadas | 50+ |
| Zonas soportadas | 11,385 |
| Features en modelo | 25-30 |

---

## 🚀 Cómo Usar

### Modo GUI (Recomendado)
```bash
python app.py
# → Pestaña "Usuario Normal"
```

### Modo Programático
```bash
python ejemplo_user_mode.py
# Ejecuta ejemplo completo
```

### Pruebas
```bash
python test_user_mode.py
# Suite de 4 pruebas
```

---

## ⚠️ Requisitos Previos

1. **Modelo entrenado** (.pkl)
   - Entrena primero en pestaña "Entrenamiento"
   - O carga modelo existente

2. **Conexión a Internet**
   - Necesaria para obtener datos de AEMET

3. **Zona CSV**
   - `12-2024_TrafficZones.csv` debe existir
   - Contiene 11,385 zonas de Madrid

---

## 🔮 Próximas Mejoras

- [ ] Predicción multi-día
- [ ] Exportar a Excel con formato
- [ ] Mostrar predicciones en mapa
- [ ] Histórico de predicciones
- [ ] Comparar con datos reales
- [ ] API REST para integración

---

## 📞 Soporte

Para reportar issues o sugerencias:
1. Verificar logs en consola
2. Revisar USER_MODE_GUIDE.md (Troubleshooting)
3. Ejecutar test_user_mode.py para validar setup

---

**Versión**: 2.0 + Modo Usuario Normal  
**Fecha**: Enero 2026  
**Estado**: Producción - Listo para usar
