#!/usr/bin/env python3
"""
Test rápido de los modelos para validar funcionamiento correcto.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from algorithms import entrenar_modelo

def test_rapido():
    """Prueba rápida de un modelo."""
    print("PRUEBA RAPIDA DEL MODELO\n")
    print("Entrenando Random Forest Mejorado...")
    
    try:
        resultados, df = entrenar_modelo(
            "2024_DatasetSample.csv",
            algoritmo="Random Forest Mejorado"
        )
        
        print("\n[OK] Modelo entrenado exitosamente!")
        print("\nResultados:")
        print(f"  RMSE: {resultados['rmse']:.2f}")
        print(f"  MAE:  {resultados['mae']:.2f}")
        print(f"  R2:   {resultados['r2']:.4f}")
        
        # Información sobre features
        print(f"\nFeatures utilizados:")
        print(f"  Numéricas: {len(resultados['features_numericas'])}")
        print(f"  Categóricas: {len(resultados['features_categoricas'])}")
        print(f"  Total: {len(resultados['features_numericas']) + len(resultados['features_categoricas'])}")
        
        # Información sobre datos
        print(f"\nDatos de entrenamiento y prueba:")
        print(f"  Train size: {len(resultados['X_train'])} muestras")
        print(f"  Test size:  {len(resultados['X_test'])} muestras")
        
        # Predicciones de ejemplo
        print(f"\nEjemplo de predicciones (primeras 3):")
        y_pred_sample = resultados['y_pred'][:3]
        y_test_sample = resultados['y_test'].iloc[:3].values
        
        for i in range(3):
            print(f"  Real: {y_test_sample[i]:6.0f} | Predicción: {y_pred_sample[i]:6.0f}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rapido()
    sys.exit(0 if success else 1)
