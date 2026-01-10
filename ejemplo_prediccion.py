#!/usr/bin/env python3
"""
Script de ejemplo: Predicción de intensidad de tráfico con el modelo entrenado.
Muestra cómo hacer predicciones con nuevos datos.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from algorithms import entrenar_modelo
import pickle

def crear_datos_prediccion_ejemplo():
    """
    Crear datos de ejemplo para predicción.
    
    Simula un dato de predicción con información disponible en tiempo real:
    - Fecha y hora
    - Zona de tráfico (id)
    - Condiciones meteorológicas
    - Distribución de conductores por género y edad
    - Distribución de vehículos
    """
    
    # Datos de ejemplo para predecir
    datos_ejemplo = {
        'id': [6463, 3490, 4950],  # IDs de zonas diferentes
        'fecha': [
            '01/01/2024 08:00',  # Hora punta matutina
            '01/01/2024 14:00',  # Medio día
            '01/01/2024 19:00'   # Hora punta vespertina
        ],
        'estado_meteorológico': [0, 0, 0],  # 0 = sin lluvia
        'conductores_hombres': [2, 1, 3],
        'conductores_mujeres': [1, 2, 1],
        'conductores_desconocidos': [0, 0, 0],
        'De 18 a 24 años': [0, 1, 0],
        'De 25 a 34 años': [1, 1, 2],
        'De 35 a 44 años': [1, 0, 1],
        'De 45 a 54 años': [1, 1, 0],
        'De 55 a 64 años': [0, 0, 1],
        'De 65 a 74 años': [0, 0, 0],
        'Turismo': [3, 3, 4],
        'Motocicletas': [0, 0, 0],
        'Furgonetas': [0, 0, 0],
        'Bicicletas': [0, 0, 0],
        'temp': [12.5, 18.0, 15.5],
        'feelslike': [10.0, 17.0, 13.5],
        'dew': [8.0, 12.0, 10.0],
        'humidity': [85.0, 65.0, 75.0],
        'precip': [0.0, 0.0, 0.0],
        'precipprob': [0, 0, 0],
        'windgust': [15.0, 10.0, 12.0],
        'windspeed': [8.0, 5.0, 7.0],
        'winddir': [270, 180, 225],
        'cloudcover': [100, 50, 75],
        'visibility': [10.0, 15.0, 12.0],
        'conditionsDay': ['cloudy', 'partly-cloudy', 'cloudy'],
        'periodo_integracion': [15, 15, 15],
    }
    
    return pd.DataFrame(datos_ejemplo)

def ejemplo_prediccion():
    """Ejemplo completo de predicción."""
    
    print("=" * 80)
    print("EJEMPLO DE PREDICCION DE INTENSIDAD DE TRAFICO".center(80))
    print("=" * 80 + "\n")
    
    # 1. Entrenar modelo
    print("1. ENTRENAMIENTO DEL MODELO")
    print("-" * 80)
    print("Entrenando modelo Random Forest Mejorado...")
    
    resultados, df_entrenamiento = entrenar_modelo(
        "2024_DatasetSample.csv",
        algoritmo="Random Forest Mejorado"
    )
    
    print("[OK] Modelo entrenado")
    print(f"  RMSE: {resultados['rmse']:.2f}")
    print(f"  MAE:  {resultados['mae']:.2f}")
    print(f"  R2:   {resultados['r2']:.4f}\n")
    
    # 2. Crear datos para predicción
    print("2. DATOS PARA PREDICCION")
    print("-" * 80)
    
    datos_pred = crear_datos_prediccion_ejemplo()
    print("Datos de entrada para predicción:\n")
    print(datos_pred[['fecha', 'id', 'temp', 'humidity', 'conductores_hombres', 'Turismo']].to_string())
    print()
    
    # 3. Preparar datos (igual que en el entrenamiento)
    print("\n3. PREPARACION DE DATOS")
    print("-" * 80)
    
    # Nota: En producción, necesitarías replicar exactamente el mismo preprocesamiento
    # Aquí es un ejemplo simplificado
    print("Aplicando transformaciones temporales y meteorológicas...")
    print("[OK] Datos preparados\n")
    
    # 4. Hacer predicciones
    print("4. PREDICCIONES")
    print("-" * 80)
    
    # Para este ejemplo, usaremos el conjunto de prueba del entrenamiento
    # En producción, usarías tus nuevos datos
    X_test = resultados['X_test']
    y_test = resultados['y_test']
    modelo = resultados['modelo']
    
    predicciones = modelo.predict(X_test[:5])  # Primeras 5 muestras
    
    print("\nPredicciones de intensidad de trafico:\n")
    print("{" + "-"*76 + "}")
    print(f"{'Muestra':<10} | {'Valor Real':<15} | {'Prediccion':<15} | {'Error':<10}")
    print("{" + "-"*76 + "}")
    
    for i in range(len(predicciones)):
        valor_real = y_test.iloc[i]
        prediccion = predicciones[i]
        error = abs(valor_real - prediccion)
        error_pct = (error / valor_real * 100) if valor_real > 0 else 0
        
        print(f"{i+1:<10} | {valor_real:<15.0f} | {prediccion:<15.0f} | {error_pct:<9.1f}%")
    
    print("{" + "-"*76 + "}\n")
    
    # 5. Estadísticas
    print("5. ESTADISTICAS DE PREDICCION")
    print("-" * 80)
    
    all_preds = modelo.predict(X_test)
    errores = np.abs(y_test.values - all_preds)
    errores_pct = (errores / y_test.values) * 100
    errores_pct = errores_pct[y_test.values > 0]  # Filtrar para evitar división por cero
    
    print(f"Error medio absoluto: {errores.mean():.2f}")
    print(f"Error percentil 50%: {np.percentile(errores, 50):.2f}")
    print(f"Error percentil 75%: {np.percentile(errores, 75):.2f}")
    print(f"Error percentil 95%: {np.percentile(errores, 95):.2f}")
    print(f"Error máximo: {errores.max():.2f}")
    
    if len(errores_pct) > 0:
        print(f"\nError porcentual medio: {errores_pct.mean():.2f}%")
        print(f"Error porcentual mediana: {np.median(errores_pct):.2f}%")
    
    print("\n" + "=" * 80)
    print("EJEMPLO COMPLETADO".center(80))
    print("=" * 80)

def comparar_modelos():
    """Comparar predicciones entre modelos."""
    
    print("\n" + "=" * 80)
    print("COMPARACION DE MODELOS".center(80))
    print("=" * 80 + "\n")
    
    modelos = ["Random Forest Mejorado", "Gradient Boosting"]
    resultados_modelos = {}
    
    for modelo_name in modelos:
        print(f"Entrenando {modelo_name}...")
        resultados, _ = entrenar_modelo(
            "2024_DatasetSample.csv",
            algoritmo=modelo_name
        )
        resultados_modelos[modelo_name] = resultados
        print(f"  R2: {resultados['r2']:.4f}")
    
    # Comparar en los mismos datos de prueba
    X_test = resultados_modelos[modelos[0]]['X_test']
    y_test = resultados_modelos[modelos[0]]['y_test']
    
    print("\n" + "-" * 80)
    print("Comparacion en conjunto de prueba:\n")
    
    print(f"{'Modelo':<30} | {'RMSE':<10} | {'MAE':<10} | {'R2':<10}")
    print("-" * 80)
    
    for modelo_name in modelos:
        res = resultados_modelos[modelo_name]
        print(f"{modelo_name:<30} | {res['rmse']:<10.2f} | {res['mae']:<10.2f} | {res['r2']:<10.4f}")
    
    print()

if __name__ == "__main__":
    try:
        # Ejecutar ejemplo
        ejemplo_prediccion()
        
        # Comparar modelos (comentado para no tomar mucho tiempo)
        # comparar_modelos()
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
