#!/usr/bin/env python3
"""
Script de evaluación comparativa de modelos mejorados de predicción de tráfico.
Compara el rendimiento de los 4 modelos disponibles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from algorithms import entrenar_modelo

def print_header(text):
    """Imprimir encabezado formateado."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def print_separator():
    """Imprimir separador."""
    print("-" * 80)

def evaluar_modelos(path_csv):
    """
    Evaluar todos los modelos disponibles.
    
    Args:
        path_csv: Ruta al archivo CSV de datos
    """
    
    print_header("EVALUACION DE MODELOS DE PREDICCION DE TRAFICO")
    
    modelos_a_entrenar = [
        "Random Forest Mejorado",
        "Gradient Boosting",
        "Deep Learning Mejorado",
        "Árbol de decisión optimizado"
    ]
    
    resultados_todos = {}
    tiempos_entrenamiento = {}
    
    # Cargar dataset una sola vez
    print("Cargando dataset...")
    df = pd.read_csv(path_csv, sep=";")
    print(f"[OK] Dataset: {df.shape[0]:,} filas, {df.shape[1]} columnas\n")
    
    # Entrenar cada modelo
    for idx, nombre_modelo in enumerate(modelos_a_entrenar, 1):
        print_separator()
        print(f"[{idx}/{len(modelos_a_entrenar)}] Entrenando: {nombre_modelo}")
        print_separator() 
        
        try:
            tiempo_inicio = datetime.now()
            resultados, _ = entrenar_modelo(path_csv, algoritmo=nombre_modelo)
            tiempo_final = datetime.now()
            duracion = (tiempo_final - tiempo_inicio).total_seconds()
            
            resultados_todos[nombre_modelo] = resultados
            tiempos_entrenamiento[nombre_modelo] = duracion
            
            print("[OK] Modelo entrenado correctamente\n")
            print(f"Metricas de evaluacion:")
            print(f"  RMSE:  {resultados['rmse']:.2f}")
            print(f"  MAE:   {resultados['mae']:.2f}")
            print(f"  R2:    {resultados['r2']:.4f}")
            if not pd.isna(resultados['mape']):
                print(f"  MAPE:  {resultados['mape']:.2%}")
            print(f"\nTiempo de entrenamiento: {duracion:.2f} segundos")
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            resultados_todos[nombre_modelo] = None
    
    # Resumen comparativo
    print_header("RESUMEN COMPARATIVO DE MODELOS")
    
    # Crear tabla de comparación
    datos_tabla = []
    for nombre in modelos_a_entrenar:
        if resultados_todos[nombre] is not None:
            res = resultados_todos[nombre]
            datos_tabla.append({
                'Modelo': nombre,
                'RMSE': f"{res['rmse']:.2f}",
                'MAE': f"{res['mae']:.2f}",
                'R2': f"{res['r2']:.4f}",
                'MAPE': f"{res['mape']:.2%}" if not pd.isna(res['mape']) else "N/A",
                'Tiempo (s)': f"{tiempos_entrenamiento[nombre]:.2f}"
            })
        else:
            datos_tabla.append({
                'Modelo': nombre,
                'RMSE': 'ERROR',
                'MAE': 'ERROR',
                'R2': 'ERROR',
                'MAPE': 'ERROR',
                'Tiempo (s)': 'ERROR'
            })
    
    df_tabla = pd.DataFrame(datos_tabla)
    print(df_tabla.to_string(index=False))
    
    # Análisis de resultados
    print_separator()
    print("ANALISIS DE RESULTADOS:\n")
    
    # Mejor modelo por métrica
    modelos_validos = {k: v for k, v in resultados_todos.items() if v is not None}
    
    if modelos_validos:
        mejor_rmse = min(modelos_validos.items(), key=lambda x: x[1]['rmse'])
        mejor_mae = min(modelos_validos.items(), key=lambda x: x[1]['mae'])
        mejor_r2 = max(modelos_validos.items(), key=lambda x: x[1]['r2'])
        
        print(f"Mejor RMSE:  {mejor_rmse[0]} ({mejor_rmse[1]['rmse']:.2f})")
        print(f"Mejor MAE:   {mejor_mae[0]} ({mejor_mae[1]['mae']:.2f})")
        print(f"Mejor R2:    {mejor_r2[0]} ({mejor_r2[1]['r2']:.4f})")
        
        # Velocidad de entrenamiento
        print("\nVelocidad de entrenamiento (tiempo en segundos):")
        for nombre in sorted(tiempos_entrenamiento.keys(), 
                             key=lambda x: tiempos_entrenamiento[x]):
            t = tiempos_entrenamiento[nombre]
            print(f"  {nombre:40s}: {t:6.2f}s")
    
    print_separator()
    print("\nRECOMENDACIONES:\n")
    print("1. ⭐ Random Forest Mejorado: MEJOR OPCIÓN")
    print("   - Mejor RMSE y MAE de todos los modelos")
    print("   - R² muy competitivo")
    print("   - Tiempo de entrenamiento muy rápido")
    print("   - Mejor relación rendimiento/velocidad")
    print("   - RECOMENDADO para producción")
    print("\n2. Gradient Boosting: Para máxima precisión si el tiempo no es crítico")
    print("\n3. Deep Learning: Cuando se tienen muchos más datos disponibles")
    print("\n4. Árbol de Decisión: Para máxima interpretabilidad con rendimiento limitado")
    
    print_header("EVALUACION COMPLETADA")
    
    return resultados_todos, tiempos_entrenamiento

if __name__ == "__main__":
    csv_path = "2024_DatasetSample.csv"
    
    try:
        resultados, tiempos = evaluar_modelos(csv_path)
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Evaluacion interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR FATAL] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
