#!/usr/bin/env python3
"""
🚀 GUÍA RÁPIDA - Modo Usuario Normal de SafeDrive

Este archivo contiene instrucciones paso a paso para usar
el nuevo Modo Usuario Normal.
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🎉 BIENVENIDO A SAFEDRÏVE - MODO USUARIO NORMAL 🎉              ║
║                                                                            ║
║                  Predicción de Tráfico para Usuarios Finales               ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

═════════════════════════════════════════════════════════════════════════════
  OPCIÓN 1: PRUEBAS RÁPIDAS (Validar que todo funciona)
═════════════════════════════════════════════════════════════════════════════

  1. Pruebas unitarias (4 tests):
     $ python test_user_mode.py
     
     Valida:
     ✓ Conexión a AEMET
     ✓ Mapeo de condiciones climáticas
     ✓ Mapeo de direcciones de viento
     ✓ Integración completa


  2. Ejemplo completo (predicción real):
     $ python ejemplo_user_mode.py
     
     Simula:
     ✓ Cargar modelo entrenado
     ✓ Obtener datos de AEMET
     ✓ Seleccionar 5 zonas
     ✓ Realizar predicción
     ✓ Mostrar resultados


═════════════════════════════════════════════════════════════════════════════
  OPCIÓN 2: USAR LA APLICACIÓN GRÁFICA (Recomendado)
═════════════════════════════════════════════════════════════════════════════

  1. Inicia la aplicación:
     $ python app.py

  2. Verás 3 pestañas (arriba):
     • Entrenamiento
     • Predicción (Técnico)
     • Usuario Normal  ← AQUÍ PARA TI

  3. En "Usuario Normal", sigue estos pasos:

     PASO 1: Cargar modelo
     ─────────────────────
     • Click en "Cargar modelo..."
     • Selecciona un archivo .pkl
     • Verás: "✓ Modelo cargado: nombre.pkl"

     PASO 2: Seleccionar fecha y hora
     ────────────────────────────────
     • Fecha: Escribe DD/MM/YYYY (ej: 15/01/2026)
     • Hora: Selecciona 0-23 (ej: 14)

     PASO 3: Seleccionar zonas
     ─────────────────────────
     • OPCIÓN A: Búsqueda
       - Escribe nombre de zona (ej: "Alcalá", "M-30")
       - Se filtran automáticamente
     
     • OPCIÓN B: Seleccionar manualmente
       - Click en zona individual
       - Ctrl+Click para múltiples

     • OPCIONES DE BOTONES:
       - "Seleccionar todos" (todas las 11,385)
       - "Deseleccionar todos"

     PASO 4: Obtener datos meteorológicos
     ────────────────────────────────────
     • Click en "Obtener datos de AEMET"
     • Espera a que se conecte y descargue
     • Verás datos como:
       - temperatura: 22.50
       - humidity: 65.00
       - conditionsDay: partly-cloudy

     PASO 5: Realizar predicción
     ───────────────────────────
     • Click en "🔮 PREDECIR"
     • Espera a que calcule...
     • Aparecerá ventana con resultados

     PASO 6: Ver resultados
     ─────────────────────
     • Tabla con columnas:
       ID | Zona | Predicción | Nivel Tráfico
       
     • Niveles:
       - Bajo   (Tráfico fluido)
       - Medio  (Normal)
       - Alto   (Congestionado)

     PASO 7 (Opcional): Exportar
     ──────────────────────────
     • Click "Exportar a CSV"
     • Guarda resultados en archivo


═════════════════════════════════════════════════════════════════════════════
  BÚSQUEDA DE ZONAS - EJEMPLOS
═════════════════════════════════════════════════════════════════════════════

  Para encontrar zonas específicas, usa el campo de búsqueda:

  Búsqueda        → Zonas encontradas
  ─────────────────────────────────────────────────────────────
  "Alcalá"        → Todas las zonas de Alcalá
  "M-30"          → Todas las zonas de la M-30
  "Cardenal"      → Calles con "Cardenal" en el nombre
  "Arlanza"       → Avenida Arlanza
  "Retiro"        → Parque del Retiro y alrededores
  "Congreso"      → Zona de Congreso de los Diputados
  "Pío XII"       → Avenida Pío XII
  ""              → TODAS las 11,385 zonas


═════════════════════════════════════════════════════════════════════════════
  REQUISITOS
═════════════════════════════════════════════════════════════════════════════

  Hardware:
  • Cualquier PC/Mac/Linux (usado: Windows)
  • RAM: 4GB+ recomendado
  • Conexión a Internet: Necesaria para AEMET

  Software:
  • Python 3.8+
  • Librerías (instala si no las tienes):
    $ pip install pandas scikit-learn requests beautifulsoup4

  Archivos:
  • "12-2024_TrafficZones.csv" (11,385 zonas)
  • Modelo entrenado ".pkl" (entrena primero en "Entrenamiento")


═════════════════════════════════════════════════════════════════════════════
  PROBLEMAS Y SOLUCIONES
═════════════════════════════════════════════════════════════════════════════

  ❌ "No se puede conectar a AEMET"
  ✓ Solución: Verifica conexión a Internet. Intenta en unos minutos.

  ❌ "No hay datos para la hora X"
  ✓ Solución: AEMET solo predice 2-3 días adelante. Intenta otra hora.

  ❌ "Ningún modelo cargado"
  ✓ Solución: Ve a pestaña "Entrenamiento" y entrena primero.

  ❌ "Condición AEMET no mapeada: X"
  ✓ Solución: Aviso normal. Se asigna "clear" por defecto. Sigue funcionando.

  ❌ "Error cargando modelo"
  ✓ Solución: El archivo .pkl puede estar corrupto. Entrena de nuevo.


═════════════════════════════════════════════════════════════════════════════
  ARCHIVOS IMPORTANTES
═════════════════════════════════════════════════════════════════════════════

  Código:
  • app.py                    - Aplicación principal
  • aemet_scraper.py         - Obtiene datos de AEMET
  • aemet_mapper.py          - Mapea datos
  • user_mode.py             - Interface Usuario Normal
  
  Documentación:
  • USER_MODE_GUIDE.md       - Guía completa (lectura recomendada)
  • MODO_USUARIO_COMPLETADO.md - Resumen de cambios
  
  Pruebas:
  • test_user_mode.py        - Suite de pruebas
  • ejemplo_user_mode.py     - Ejemplo completo

  Datos:
  • 12-2024_TrafficZones.csv - 11,385 zonas de Madrid


═════════════════════════════════════════════════════════════════════════════
  FLUJO TÍPICO DE UN USUARIO
═════════════════════════════════════════════════════════════════════════════

  Escenario: "Quiero saber tráfico en la M-30 a las 8 de la mañana"

  $ python app.py
  → Pestaña "Usuario Normal"
  → Cargar modelo.pkl
  → Fecha: 15/01/2026 (hoy)
  → Hora: 08
  → Buscar: "M-30"
  → Seleccionar todas las de M-30
  → Click "Obtener datos de AEMET"
  → Click "🔮 PREDECIR"
  → Ver tabla con resultados
  → Exportar a CSV (si quieres guardar)

  ⏱️  Tiempo total: 1-2 minutos


═════════════════════════════════════════════════════════════════════════════
  INFORMACIÓN TÉCNICA
═════════════════════════════════════════════════════════════════════════════

  Features utilizados por el modelo:
  • Temperatura, humedad, viento, precipitación
  • Hora del día (variables cíclicas)
  • Zona de tráfico
  • NO incluye datos demográficos

  Clasificación de tráfico:
  • Bajo  (Z ≤ -0.5):  Tráfico fluido
  • Medio (-0.5 < Z < 0.5): Normal
  • Alto  (Z ≥ 0.5):  Congestionado

  Datos meteorológicos:
  • Fuente: AEMET (Agencia Estatal de Meteorología)
  • Actualización: Cada hora
  • Cobertura: Madrid y alrededores


═════════════════════════════════════════════════════════════════════════════
  CONTACTO Y SOPORTE
═════════════════════════════════════════════════════════════════════════════

  Para más información:
  1. Lee USER_MODE_GUIDE.md
  2. Ejecuta test_user_mode.py para validar
  3. Ve a pestaña "Entrenamiento" si necesitas entrenar modelo


═════════════════════════════════════════════════════════════════════════════

  ¡Listo para empezar! 

  Comando para iniciar:
  $ python app.py

  ¡Que disfrutes! 🎉

═════════════════════════════════════════════════════════════════════════════
""")

# Pequeña validación
print("\n🔍 Validando setup...")

import sys
import os

checks = []

# Check 1: Python version
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
checks.append((f"Python {py_version}", sys.version_info >= (3, 8)))

# Check 2: Pandas
try:
    import pandas
    checks.append(("pandas", True))
except:
    checks.append(("pandas", False))

# Check 3: scikit-learn
try:
    import sklearn
    checks.append(("scikit-learn", True))
except:
    checks.append(("scikit-learn", False))

# Check 4: Zones CSV
checks.append(("12-2024_TrafficZones.csv", os.path.exists("12-2024_TrafficZones.csv")))

# Check 5: Archivos nuevos
checks.append(("aemet_scraper.py", os.path.exists("aemet_scraper.py")))
checks.append(("aemet_mapper.py", os.path.exists("aemet_mapper.py")))
checks.append(("user_mode.py", os.path.exists("user_mode.py")))

print("\nEstado del setup:")
all_ok = True
for name, status in checks:
    symbol = "✓" if status else "❌"
    print(f"  {symbol} {name}")
    if not status:
        all_ok = False

if all_ok:
    print("\n✨ Todo listo para usar Modo Usuario Normal ✨")
    print("\nComando para iniciar:")
    print("  $ python app.py")
else:
    print("\n⚠️ Algunos componentes están faltando")
    print("   Instala: pip install pandas scikit-learn requests beautifulsoup4")
