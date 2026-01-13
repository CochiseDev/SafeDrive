"""
Web scraping mejorado para AEMET.
Extrae datos meteorológicos de la página de predicción de AEMET.
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class AemetScraper:
    """Realiza web scraping de datos meteorológicos de AEMET."""
    
    BASE_URL = "https://www.aemet.es"
    MADRID_HOURLY_URL = "https://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/madrid-id28079"
    MADRID_DETAILED_URL = "https://www.aemet.es/es/eltiempo/prediccion/municipios/madrid-id28079#detallada"
    
    # Headers para evitar bloqueos
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def __init__(self, timeout: int = 10):
        """Inicializa el scraper."""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_hourly_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene datos de predicción por horas.
        
        Returns:
            Diccionario {hora: {datos meteorológicos}}
        """
        try:
            response = self.session.get(self.MADRID_HOURLY_URL, timeout=self.timeout)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar filas de datos horarios
            rows = soup.find_all('tr', class_='fila_hora cabecera_niv2')
            
            hourly_data = {}
            
            for row in rows:
                try:
                    row_str = str(row)
                    
                    # Extraer hora
                    hora_match = re.search(r'>(\d{1,2})<\/td>', row_str)
                    if not hora_match:
                        continue
                    hora = hora_match.group(1).zfill(2)
                    
                    # Extraer datos
                    data = {
                        'hora': hora,
                        'estadoCielo': self._extract_text(row_str, r'title="([^"]+)"\/><\/td>'),
                        'temperatura': self._extract_number(row_str, r'<td class="borde_rb">\s*(\d+)<\/td>', 0),
                        'sensacionTermica': self._extract_number(row_str, r'<td class="borde_rb">\s*(\d+)<\/td>', 1),
                        'direccionViento': self._extract_text(row_str, r'<div class="texto_viento">(\w+)<\/div>'),
                        'velocidadViento': self._extract_number(row_str, r'<div class="texto_km_viento"><div>(\d+)<\/div>', 0),
                        'rachaMaxima': self._extract_number(row_str, r'borde_rb">\s*(\d+)<\/td>\n<td class="borde_rb">\s*(\d+)', 0),
                        'precipitacion': self._extract_number(row_str, r'borde_rb">\s*(\d+)<\/td>\n<td class="borde_rb">\s*(\d+)', 1),
                        'humedadRelativa': self._extract_number(row_str, r'borde_rb">\s*(\d+)<\/td>\n<td class="borde_rb">\s*(\d+)<\/td>\n<td class="borde_rb">\s*(\d+)<\/td>\n<td class="borde_rb">\s*(\d+)', 3),
                    }
                    
                    hourly_data[hora] = data
                    
                except Exception as e:
                    print(f"⚠️ Error procesando fila horaria: {e}")
                    continue
            
            return hourly_data
            
        except requests.RequestException as e:
            print(f"❌ Error en request AEMET: {e}")
            return {}
    
    def get_daily_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene datos de predicción diaria.
        
        Returns:
            Diccionario {fecha: {datos meteorológicos}}
        """
        try:
            response = self.session.get(self.MADRID_DETAILED_URL, timeout=self.timeout)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            daily_data = {}
            
            # Extraer fechas y datos
            # Este es más complejo, retornar vacío por ahora
            
            return daily_data
            
        except requests.RequestException as e:
            print(f"❌ Error en request AEMET (daily): {e}")
            return {}
    
    @staticmethod
    def _extract_text(html_str: str, pattern: str, group: int = 1) -> str:
        """Extrae texto usando regex."""
        match = re.search(pattern, html_str)
        return match.group(group) if match else ''
    
    @staticmethod
    def _extract_number(html_str: str, pattern: str, group: int = 0) -> str:
        """Extrae número usando regex."""
        try:
            matches = re.findall(pattern, html_str)
            if not matches:
                return '0'
            if isinstance(matches[0], tuple):
                return matches[0][group] if group < len(matches[0]) else '0'
            elif group < len(matches):
                return matches[group]
            return '0'
        except (IndexError, TypeError, AttributeError):
            return '0'
    
    def get_forecast_for_datetime(self, target_date: datetime) -> Optional[Dict[str, Any]]:
        """
        Obtiene predicción para una fecha/hora específica.
        
        Args:
            target_date: datetime con fecha y hora
            
        Returns:
            Diccionario con datos meteorológicos o None
        """
        # Si es hoy o mañana, usar datos horarios
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        if target_date.date() == today.date() or target_date.date() == tomorrow.date():
            hourly_data = self.get_hourly_data()
            hora = str(target_date.hour).zfill(2)
            
            if hora in hourly_data:
                return hourly_data[hora]
        
        return None
    
    def test_connection(self) -> bool:
        """Prueba la conexión a AEMET."""
        try:
            response = self.session.get(self.MADRID_HOURLY_URL, timeout=5)
            return response.status_code == 200
        except:
            return False


if __name__ == "__main__":
    # Prueba del scraper
    print("🌐 Probando conexión a AEMET...")
    scraper = AemetScraper()
    
    if scraper.test_connection():
        print("✓ Conexión exitosa\n")
        
        print("📊 Extrayendo datos horarios...")
        hourly = scraper.get_hourly_data()
        
        if hourly:
            print(f"✓ Se extrajeron {len(hourly)} horas\n")
            
            # Mostrar primeras 3 horas
            for hora, datos in list(hourly.items())[:3]:
                print(f"Hora {hora}h:")
                for key, value in datos.items():
                    print(f"  {key}: {value}")
                print()
        else:
            print("❌ No se pudieron extraer datos")
    else:
        print("❌ Error de conexión a AEMET")
