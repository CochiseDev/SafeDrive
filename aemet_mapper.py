"""
Mapeo de datos AEMET a formato de entrenamiento del modelo SafeDrive.

Convierte los datos scrapeados de AEMET a los formatos esperados por el modelo.
"""

import re
from typing import Dict, Any

# Mapeo de condiciones climáticas AEMET a condiciones del modelo
AEMET_CONDITIONS_MAPPING = {
    # Cielos despejados / claros
    'Despejado': 'clear',
    'Despejada': 'clear',
    'Cielo despejado': 'clear',
    'Poco nuboso': 'partly-cloudy',
    'Pocas nubes': 'partly-cloudy',
    'Intervalos nubosos': 'partly-cloudy',
    
    # Nublado
    'Nuboso': 'cloudy',
    'Nublado': 'cloudy',
    'Muy nuboso': 'cloudy',
    'Cielo cubierto': 'cloudy',
    'Cubierto': 'cloudy',
    'Nubes altas': 'cloudy',
    
    # Lluvia
    'Lluvia': 'rain',
    'Lluvias': 'rain',
    'Lluvia débil': 'rain',
    'Lluvia moderada': 'rain',
    'Lluvia fuerte': 'rain',
    'Chubascos': 'rain',
    'Chubasco': 'rain',
    'Chubascos débiles': 'rain',
    'Chubascos moderados': 'rain',
    'Chubascos fuertes': 'rain',
    'Llovizna': 'rain',
    'Garúa': 'rain',
    'Lluvia y nieve': 'rain',
    
    # Nieve
    'Nieve': 'snow',
    'Nevadas': 'snow',
    'Nieve débil': 'snow',
    'Nieve moderada': 'snow',
    'Nieve fuerte': 'snow',
    'Chubascos de nieve': 'snow',
    
    # Niebla
    'Niebla': 'foggy',
    'Niebla moderada': 'foggy',
    'Niebla densa': 'foggy',
    'Neblina': 'foggy',
    'Bancos de niebla': 'foggy',
    
    # Tormenta (mapear a lluvia por defecto)
    'Tormenta': 'rain',
    'Tormentas': 'rain',
    'Tormenta débil': 'rain',
    'Tormenta moderada': 'rain',
    'Tormenta fuerte': 'rain',
    'Tormenta con granizo': 'rain',
    'Granizo': 'rain',
}

# Mapeo de direcciones de viento AEMET
WIND_DIRECTION_MAPPING = {
    'N': 0,
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSO': 202.5,
    'SO': 225,
    'OSO': 247.5,
    'O': 270,
    'ONO': 292.5,
    'NO': 315,
    'NNO': 337.5,
    # Variaciones sin acento
    'SSE': 157.5,
    'OSO': 247.5,
}


class AemetMapper:
    """Mapea datos de AEMET a formato del modelo."""
    
    @staticmethod
    def map_condition(aemet_condition: str) -> str:
        """
        Mapea una condición climática de AEMET a formato del modelo.
        
        Args:
            aemet_condition: Condición climática tal como viene de AEMET
            
        Returns:
            Condición normalizada (clear, partly-cloudy, cloudy, rain, snow, foggy)
        """
        if not aemet_condition:
            return 'clear'
        
        # Buscar en el mapeo
        condition_lower = aemet_condition.lower().strip()
        
        # Búsqueda exacta primero
        for aemet_key, model_value in AEMET_CONDITIONS_MAPPING.items():
            if condition_lower == aemet_key.lower():
                return model_value
        
        # Búsqueda por substring (si contiene palabras clave)
        for aemet_key, model_value in AEMET_CONDITIONS_MAPPING.items():
            if aemet_key.lower() in condition_lower or condition_lower in aemet_key.lower():
                return model_value
        
        # Si no encuentra, por defecto clear
        print(f"⚠️ Condición AEMET no mapeada: '{aemet_condition}' → asignando 'clear'")
        return 'clear'
    
    @staticmethod
    def map_wind_direction(direction: str) -> float:
        """
        Mapea dirección de viento a grados (0-360).
        
        Args:
            direction: Dirección cardinal (N, NE, E, etc.)
            
        Returns:
            Grados (0-360)
        """
        if not direction:
            return 0.0
        
        direction_upper = direction.upper().strip()
        
        # Búsqueda en mapeo
        if direction_upper in WIND_DIRECTION_MAPPING:
            return WIND_DIRECTION_MAPPING[direction_upper]
        
        # Por defecto N
        print(f"⚠️ Dirección viento no mapeada: '{direction}' → asignando 0 (N)")
        return 0.0
    
    @staticmethod
    def clean_numeric(value: str) -> float:
        """
        Limpia y convierte valores numéricos de texto.
        
        Args:
            value: Valor como string (ej: "25", "12,5", "-5")
            
        Returns:
            Valor como float
        """
        if not value or value.lower() == 'null':
            return 0.0
        
        try:
            # Reemplazar coma por punto (formato español)
            clean_value = str(value).strip().replace(',', '.')
            return float(clean_value)
        except (ValueError, AttributeError):
            print(f"⚠️ No se pudo convertir valor numérico: '{value}' → asignando 0")
            return 0.0
    
    @staticmethod
    def create_prediction_dict(aemet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte datos raw de AEMET a formato esperado por el modelo.
        
        Args:
            aemet_data: Diccionario con datos scrapeados de AEMET
                Esperado: {
                    'hora': '14',
                    'estadoCielo': 'Parcialmente nublado',
                    'temperatura': '22',
                    'sensacionTermica': '20',
                    'direccionViento': 'SO',
                    'velocidadViento': '12',
                    'rachaMaxima': '25',
                    'precipitacion': '0',
                    'humedad': '65'
                }
            
        Returns:
            Diccionario con formato del modelo:
            {
                'temp': float,
                'feelslike': float,
                'winddir': float,
                'windspeed': float,
                'windgust': float,
                'precip': float,
                'humidity': float,
                'conditionsDay': str,
                'dew': float (estimado),
                'cloudcover': float (estimado),
                'visibility': float (estimado),
                'precipprob': float (estimado)
            }
        """
        temp = AemetMapper.clean_numeric(aemet_data.get('temperatura', '0'))
        feelslike = AemetMapper.clean_numeric(aemet_data.get('sensacionTermica', temp))
        winddir = AemetMapper.map_wind_direction(aemet_data.get('direccionViento', 'N'))
        windspeed = AemetMapper.clean_numeric(aemet_data.get('velocidadViento', '0'))
        windgust = AemetMapper.clean_numeric(aemet_data.get('rachaMaxima', windspeed))
        precip = AemetMapper.clean_numeric(aemet_data.get('precipitacion', '0'))
        humidity = AemetMapper.clean_numeric(aemet_data.get('humedadRelativa', '50'))
        conditions = AemetMapper.map_condition(aemet_data.get('estadoCielo', 'clear'))
        
        # Estimaciones basadas en datos disponibles
        dew = estimate_dew_point(temp, humidity)
        cloudcover = estimate_cloudcover(conditions)
        visibility = estimate_visibility(conditions, precip)
        precipprob = estimate_precip_probability(conditions, precip)
        
        return {
            'temp': temp,
            'feelslike': feelslike,
            'dew': dew,
            'humidity': humidity,
            'precip': precip,
            'precipprob': precipprob,
            'windgust': windgust,
            'windspeed': windspeed,
            'winddir': winddir,
            'cloudcover': cloudcover,
            'visibility': visibility,
            'conditionsDay': conditions,
        }


def estimate_dew_point(temp: float, humidity: float) -> float:
    """
    Estima el punto de rocío usando la aproximación de Magnus.
    
    Fórmula simplificada: Td ≈ T - ((100 - RH) / 5)
    """
    if humidity < 0 or humidity > 100:
        humidity = 50
    dew = temp - ((100 - humidity) / 5)
    return max(-40, min(temp, dew))  # Limitar valores razonables


def estimate_cloudcover(condition: str) -> float:
    """
    Estima cobertura de nubes basada en condición climática.
    """
    cloud_map = {
        'clear': 5,           # 0-20%
        'partly-cloudy': 35,  # 25-50%
        'cloudy': 75,         # 75-100%
        'rain': 85,           # Lluvia = muy nublado
        'snow': 90,           # Nieve = muy nublado
        'foggy': 95,          # Niebla = completamente cubierto
    }
    return cloud_map.get(condition, 50)


def estimate_visibility(condition: str, precip: float) -> float:
    """
    Estima visibilidad basada en condición y precipitación.
    Rango típico: 0-20 km
    """
    if condition == 'foggy':
        return 0.5  # Muy baja
    elif condition == 'rain' and precip > 5:
        return 2.0  # Baja
    elif condition == 'rain':
        return 5.0  # Moderada
    elif condition == 'snow' and precip > 5:
        return 1.0  # Muy baja
    elif condition == 'snow':
        return 3.0  # Baja
    elif condition == 'cloudy':
        return 10.0  # Moderada
    elif condition == 'partly-cloudy':
        return 15.0  # Buena
    else:  # clear
        return 20.0  # Excelente


def estimate_precip_probability(condition: str, precip: float) -> float:
    """
    Estima probabilidad de precipitación (0-100%).
    """
    if precip > 0:
        return 100.0  # Si hay precipitación, prob = 100%
    
    precip_map = {
        'clear': 0,
        'partly-cloudy': 10,
        'cloudy': 25,
        'rain': 80,
        'snow': 80,
        'foggy': 20,
    }
    return precip_map.get(condition, 20)


if __name__ == "__main__":
    # Prueba del mapeo
    test_data = {
        'hora': '14',
        'estadoCielo': 'Parcialmente nublado',
        'temperatura': '22',
        'sensacionTermica': '20',
        'direccionViento': 'SO',
        'velocidadViento': '12',
        'rachaMaxima': '25',
        'precipitacion': '0',
        'humedadRelativa': '65'
    }
    
    mapper = AemetMapper()
    result = mapper.create_prediction_dict(test_data)
    
    print("Datos AEMET:")
    for k, v in test_data.items():
        print(f"  {k}: {v}")
    
    print("\nDatos mapeados (formato modelo):")
    for k, v in result.items():
        print(f"  {k}: {v}")
