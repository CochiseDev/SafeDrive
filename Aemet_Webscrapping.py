import requests
import re
from bs4 import BeautifulSoup
horasUrl = "https://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/madrid-id28079"

pageHoras = requests.get(horasUrl)

soupHoras = BeautifulSoup(pageHoras.content, 'html.parser')

filasHoras = list(soupHoras.find_all('tr', class_='fila_hora cabecera_niv2'))

for item in filasHoras:
  print(item)
  

datosHoras = {}
for item in filasHoras:
  hora = re.search(r'>(\d\d)<\/td>', str(item)).group(1)
  estadoCielo = re.search(r'src="\/imagenes\/png\/estado_cielo\/\S+.png" title="([a-zA-z ]+)"\/><\/td>', str(item)).group(1)
  temperatura = re.search(r'<td class="borde_rb">\s+(\d+)<\/td>\n<td class="borde_rb">\s+(\d+)<\/td>', str(item)).group(1)
  sensacionTermica = re.search(r'<td class="borde_rb">\s+(\d+)<\/td>\n<td class="borde_rb">\s+(\d+)<\/td>', str(item)).group(2)
  direccionViento = re.search(r'<div class="texto_viento">(\w+)<\/div>', str(item)).group(1)
  velocidadViento = re.search(r'<div class="texto_km_viento"><div>(\d+)<\/div><\/div>', str(item)).group(1)
  rachaMaxima = re.search(r'<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>', str(item)).group(1)
  precipitacion = re.search(r'<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>', str(item)).group(2)
  nieve = re.search(r'<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>', str(item)).group(3)
  humedadRelativa = re.search(r'<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>\n<td class="borde_rb">\s+(\S+)<\/td>', str(item)).group(4)
  datos = {
      'estadoCielo': estadoCielo,
      'temperatura': temperatura,
      'sensacionTermica': sensacionTermica,
      'direccionViento': direccionViento,
      'velocidadViento': velocidadViento,
      'rachaMaxima': rachaMaxima,
      'precipitacion': precipitacion,
      'nieve':nieve,
      'humedadRelativa': humedadRelativa
  }
  datosHoras[hora]=datos
  
diasUrl = 'https://www.aemet.es/es/eltiempo/prediccion/municipios/madrid-id28079#detallada'
diasPage = requests.get(diasUrl)
diasSoup = BeautifulSoup(diasPage.content, 'html.parser')

cabeceraDias = list(diasSoup.find_all('th', class_='borde_izq_dcha_fecha'))
colspanDias = {}
for th in cabeceraDias:
  colspanDias[th['title']] = th['colspan']
  


cabeceraTiempo = list(diasSoup.find_all('th', class_='borde_izq_dcha_estado_cielo'))
listaHoras = []
listaEstadosCielo = []
listaTemperaturas = []
for item in cabeceraTiempo:
  search =  re.search(r'<div class="fuente09em">(.*?)<\/div>', str(item))
  hora='null'
  if search:
    hora =search.group(1)
  listaHoras.append(hora)
  estadoCielo2 = re.search(r'.png" title="(.*)"\/><\/div>', str(item)).group(1)
  listaEstadosCielo.append(estadoCielo2)
  search = re.search(r'>(\d+)°C<\/div>', str(item))
  temperatura2 = 'null'
  if search:
    temperatura2 = search.group(1)
  listaTemperaturas.append(temperatura2)
  
precipitacionesDias = re.findall(r'<td class="nocomunes">(\d+)%', str(diasSoup))


cabeceraViento = list(diasSoup.find_all('td', class_='alinear_texto_centro nocomunes'))
listaDireccionViento = []
listaVelocidadViento = []
for elemento in cabeceraViento:
  direccionViento2 = re.search(r'<div class="texto_viento">(\w+)<\/div>', str(elemento)).group(1)
  velocidadViento2 = re.search(r'<div class="texto_km_viento"><div>(\d+)<\/div><\/div>', str(elemento)).group(1)
  listaDireccionViento.append(direccionViento2)
  listaVelocidadViento.append(velocidadViento2)
  

cabeceraSensacionTermica = list(diasSoup.find_all('td', class_='no_wrap nocomunes'))
listaSensacionTermica = []
for elemento in cabeceraSensacionTermica:
  listaSensacionTermica.append(elemento.text)