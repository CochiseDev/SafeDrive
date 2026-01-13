"""
Ejemplo de uso del Modo Usuario Normal de forma programática.
Simula lo que haría un usuario en la GUI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from aemet_scraper import AemetScraper
from aemet_mapper import AemetMapper
from algorithms import preparar_datos_prediccion
import pandas as pd
import joblib
import os


def ejemplo_completo():
    """
    Ejemplo completo de predicción con Modo Usuario Normal.
    """
    
    print("\n" + "=" * 70)
    print("EJEMPLO: Predicción de Tráfico - Modo Usuario Normal")
    print("=" * 70)
    
    # --- PASO 1: Cargar modelo entrenado ---
    print("\n1️⃣  Cargando modelo entrenado...")
    
    # Buscar modelo .pkl o .mdl en el directorio actual
    model_files = [f for f in os.listdir('.') if f.endswith(('.pkl', '.mdl'))]
    
    if not model_files:
        print("❌ No se encontró ningún modelo (.pkl o .mdl) en el directorio actual")
        print("   Entrena primero con: python app.py → Entrenamiento")
        return
    
    model_path = model_files[0]
    print(f"   Usando: {model_path}")
    
    try:
        model_package = joblib.load(model_path)
        trained_results = {
            'modelo': model_package['modelo'],
            'features_numericas': model_package.get('features_numericas', []),
            'features_categoricas': model_package.get('features_categoricas', []),
            'zona_stats': model_package.get('zona_stats', {}),
            'hora_stats': model_package.get('hora_stats', {}),
            'median_values': model_package.get('median_values', {}),
        }
        print("   ✓ Modelo cargado correctamente")
    except Exception as e:
        print(f"   ❌ Error cargando modelo: {e}")
        return
    
    # --- PASO 2: Obtener datos de AEMET ---
    print("\n2️⃣  Obteniendo datos meteorológicos de AEMET...")
    
    scraper = AemetScraper()
    
    if not scraper.test_connection():
        print("   ❌ No se puede conectar a AEMET")
        print("   Verifica tu conexión a internet")
        return
    
    print("   ✓ Conexión a AEMET establecida")
    
    # Obtener datos horarios
    hourly_data = scraper.get_hourly_data()
    
    if not hourly_data:
        print("   ❌ No se pudieron obtener datos de AEMET")
        return
    
    print(f"   ✓ Se obtuvieron datos para {len(hourly_data)} horas")
    
    # Seleccionar hora de predicción (14:00)
    target_hour = "14"
    if target_hour not in hourly_data:
        print(f"   ⚠️  No hay datos para la hora {target_hour}")
        target_hour = list(hourly_data.keys())[0]
        print(f"   Usando hora {target_hour} en su lugar")
    
    aemet_raw = hourly_data[target_hour]
    
    print(f"\n   Datos para las {target_hour}:00:")
    for key, value in aemet_raw.items():
        print(f"     {key:25s}: {value}")
    
    # --- PASO 3: Mapear datos al formato del modelo ---
    print("\n3️⃣  Mapeando datos AEMET al formato del modelo...")
    
    mapper = AemetMapper()
    aemet_mapped = mapper.create_prediction_dict(aemet_raw)
    
    print("   ✓ Datos mapeados correctamente:")
    for key, value in aemet_mapped.items():
        if isinstance(value, float):
            print(f"     {key:25s}: {value:8.2f}")
        else:
            print(f"     {key:25s}: {value}")
    
    # --- PASO 4: Seleccionar zonas ---
    print("\n4️⃣  Seleccionando zonas para predicción...")
    
    # Cargar zonas
    try:
        traffic_zones = pd.read_csv("12-2024_TrafficZones.csv", sep=";", encoding="latin-1")
    except:
        print("   ❌ No se pudo cargar archivo de zonas")
        return
    
    # Seleccionar ejemplo de zonas (las primeras 5)
    selected_zones = [
        3871,  # Av. Cardenal Herrera Oria
        4370,  # Arlanza
        5902,  # Islas Cies
        3912,  # Ramón y Cajal
        4443,  # María Molina
    ]
    
    print(f"   Seleccionadas {len(selected_zones)} zonas:")
    for zone_id in selected_zones:
        zone_name = traffic_zones[traffic_zones['id'] == zone_id]['nombre'].values
        if len(zone_name) > 0:
            print(f"     [{zone_id}] {zone_name[0]}")
    
    # --- PASO 5: Crear DataFrame de predicción ---
    print("\n5️⃣  Preparando datos para predicción...")
    
    fecha_str = datetime.now().strftime("%d/%m/%Y") + f" {target_hour}:00"
    
    rows = []
    for zone_id in selected_zones:
        row = {
            'id': zone_id,
            'fecha': fecha_str,
        }
        row.update(aemet_mapped)
        rows.append(row)
    
    df_pred = pd.DataFrame(rows)
    print(f"   ✓ DataFrame creado con {len(df_pred)} filas")
    
    # --- PASO 6: Feature Engineering ---
    print("\n6️⃣  Aplicando feature engineering...")
    
    df_prepared = preparar_datos_prediccion(df_pred, trained_results)
    print(f"   ✓ Features preparadas: {df_prepared.shape}")
    
    # --- PASO 7: Predicción ---
    print("\n7️⃣  Ejecutando modelo de predicción...")
    
    modelo = trained_results['modelo']
    predicciones = modelo.predict(df_prepared)
    
    print(f"   ✓ Predicción completada")
    
    # --- PASO 8: Clasificar nivel de tráfico ---
    print("\n8️⃣  Clasificando nivel de tráfico...")
    
    zona_stats = trained_results.get('zona_stats', {})
    
    def classify_traffic(pred_val, zone_id):
        if zone_id in zona_stats:
            media = zona_stats[zone_id].get('mean', 0)
            std = zona_stats[zone_id].get('std', 1)
        else:
            media = 150
            std = 100
        
        z_score = (pred_val - media) / std if std > 0 else 0
        
        if z_score <= -0.5:
            return "Bajo"
        elif z_score >= 0.5:
            return "Alto"
        else:
            return "Medio"
    
    # --- RESULTADOS ---
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DE PREDICCIÓN")
    print("=" * 70)
    
    results = []
    for i, zone_id in enumerate(selected_zones):
        zone_name = traffic_zones[traffic_zones['id'] == zone_id]['nombre'].values[0]
        pred = predicciones[i]
        nivel = classify_traffic(pred, zone_id)
        
        results.append({
            'id': zone_id,
            'zona': zone_name,
            'prediccion': pred,
            'nivel': nivel
        })
    
    results_df = pd.DataFrame(results)
    
    # Mostrar tabla
    print("\n")
    print(f"{'ID':>6} | {'Predicción':>12} | {'Nivel':>8} | Zona")
    print("-" * 70)
    
    for _, row in results_df.iterrows():
        print(f"{row['id']:>6} | {row['prediccion']:>12.0f} | {row['nivel']:>8} | {row['zona']}")
    
    # Estadísticas
    print("\n" + "-" * 70)
    print("ESTADÍSTICAS:")
    print(f"  Predicción media: {predicciones.mean():.0f} veh/15min")
    print(f"  Predicción mín:   {predicciones.min():.0f} veh/15min")
    print(f"  Predicción máx:   {predicciones.max():.0f} veh/15min")
    
    bajos = sum(1 for r in results if r['nivel'] == 'Bajo')
    medios = sum(1 for r in results if r['nivel'] == 'Medio')
    altos = sum(1 for r in results if r['nivel'] == 'Alto')
    
    print(f"\n  Zonas Bajo:  {bajos}")
    print(f"  Zonas Medio: {medios}")
    print(f"  Zonas Alto:  {altos}")
    
    print("\n" + "=" * 70)
    print("✨ Predicción completada exitosamente ✨")
    print("=" * 70 + "\n")
    
    return results_df


if __name__ == "__main__":
    try:
        resultado = ejemplo_completo()
        if resultado is not None:
            print("\nPara usar en GUI:")
            print("1. python app.py")
            print("2. Ir a pestaña 'Usuario Normal'")
            print("3. Cargar modelo")
            print("4. Seleccionar fecha/hora/zonas")
            print("5. Click en 'Obtener datos de AEMET'")
            print("6. Click en '🔮 PREDECIR'")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
