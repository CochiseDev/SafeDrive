"""
Script de prueba para la integración de AEMET y modo Usuario Normal.
"""

from datetime import datetime
from aemet_scraper import AemetScraper
from aemet_mapper import AemetMapper


def test_aemet_scraper():
    """Prueba la conexión y extracción de datos de AEMET."""
    print("=" * 60)
    print("TEST 1: Web Scraping AEMET")
    print("=" * 60)
    
    scraper = AemetScraper()
    
    print("\n🔍 Probando conexión a AEMET...")
    if scraper.test_connection():
        print("✓ Conexión exitosa")
    else:
        print("❌ Error de conexión")
        return False
    
    print("\n📊 Extrayendo datos horarios...")
    hourly_data = scraper.get_hourly_data()
    
    if hourly_data:
        print(f"✓ Se extrajeron {len(hourly_data)} horas")
        
        # Mostrar primera hora
        first_hour = list(hourly_data.keys())[0]
        print(f"\nDatos de la hora {first_hour}h:")
        for key, value in hourly_data[first_hour].items():
            print(f"  {key:25s}: {value}")
        
        return True
    else:
        print("❌ No se pudieron extraer datos")
        return False


def test_aemet_mapper():
    """Prueba el mapeo de datos AEMET al formato del modelo."""
    print("\n" + "=" * 60)
    print("TEST 2: Mapeo AEMET → Formato Modelo")
    print("=" * 60)
    
    # Datos de ejemplo (como vendría de AEMET)
    aemet_raw = {
        'hora': '14',
        'estadoCielo': 'Parcialmente nublado',
        'temperatura': '22',
        'sensacionTermica': '20',
        'direccionViento': 'SO',
        'velocidadViento': '12',
        'rachaMaxima': '25',
        'precipitacion': '2',
        'humedadRelativa': '65'
    }
    
    print("\n📝 Datos AEMET (raw):")
    for key, value in aemet_raw.items():
        print(f"  {key:25s}: {value}")
    
    mapper = AemetMapper()
    mapped = mapper.create_prediction_dict(aemet_raw)
    
    print("\n✓ Datos mapeados (formato modelo):")
    for key, value in mapped.items():
        if isinstance(value, float):
            print(f"  {key:25s}: {value:8.2f}")
        else:
            print(f"  {key:25s}: {value}")
    
    return True


def test_condition_mapping():
    """Prueba el mapeo de condiciones climáticas."""
    print("\n" + "=" * 60)
    print("TEST 3: Mapeo de Condiciones Climáticas")
    print("=" * 60)
    
    mapper = AemetMapper()
    
    test_cases = [
        'Despejado',
        'Parcialmente nublado',
        'Nublado',
        'Lluvia',
        'Nieve',
        'Niebla',
        'Tormenta fuerte',
        'Chubasco moderado',
    ]
    
    print("\nMapeando condiciones AEMET a formato modelo:")
    for condition in test_cases:
        mapped = mapper.map_condition(condition)
        print(f"  {condition:30s} → {mapped}")
    
    return True


def test_wind_direction():
    """Prueba el mapeo de direcciones de viento."""
    print("\n" + "=" * 60)
    print("TEST 4: Mapeo de Direcciones de Viento")
    print("=" * 60)
    
    mapper = AemetMapper()
    
    test_cases = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
    
    print("\nMapeando direcciones a grados:")
    for direction in test_cases:
        degrees = mapper.map_wind_direction(direction)
        print(f"  {direction:10s} → {degrees:6.1f}°")
    
    return True


if __name__ == "__main__":
    print("\n" + "🧪 SUITE DE PRUEBAS - MODO USUARIO NORMAL 🧪".center(60))
    print()
    
    results = []
    
    # Test 1: AEMET Scraper
    try:
        results.append(("AEMET Scraper", test_aemet_scraper()))
    except Exception as e:
        print(f"❌ Error en test AEMET Scraper: {e}")
        results.append(("AEMET Scraper", False))
    
    # Test 2: AEMET Mapper
    try:
        results.append(("AEMET Mapper", test_aemet_mapper()))
    except Exception as e:
        print(f"❌ Error en test AEMET Mapper: {e}")
        results.append(("AEMET Mapper", False))
    
    # Test 3: Condition Mapping
    try:
        results.append(("Mapeo de Condiciones", test_condition_mapping()))
    except Exception as e:
        print(f"❌ Error en test Mapeo de Condiciones: {e}")
        results.append(("Mapeo de Condiciones", False))
    
    # Test 4: Wind Direction
    try:
        results.append(("Mapeo de Viento", test_wind_direction()))
    except Exception as e:
        print(f"❌ Error en test Mapeo de Viento: {e}")
        results.append(("Mapeo de Viento", False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {test_name:30s} ... {status}")
    
    total_pass = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {total_pass}/{total} pruebas pasadas")
    
    if total_pass == total:
        print("\n✨ ¡Todas las pruebas pasaron! ✨")
    else:
        print(f"\n⚠️ {total - total_pass} prueba(s) fallaron")
