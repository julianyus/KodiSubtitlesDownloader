import urllib2
import re
from bs4 import BeautifulSoup
import PTN
import xbmc
import unicodedata

class Idioma:
	def __init__(self, nombre, enlace):
		self.nombre = nombre
		self.enlace = enlace
	def __unicode__(self):
		return u"{ 'nombre': '"+self.nombre+"', 'enlace':'"+self.enlace+"'}"
class Version:
	def __init__(self, nombre):
		self.nombre = nombre
		self.idiomas = []
	def __str__(self):
		return "{ nombre: '" + self.nombre+ "'}"
	def __unicode__(self):
		return u"{ 'nombre': '" + self.nombre+ "', 'idiomas': ["+",".join(unicode(x) for x in self.idiomas)+"]}"
class Capitulo:
	def __init__(self, temporada, numero, texto):
		self.temporada = temporada
		self.numero = numero
		self.texto = texto
		self.versiones = []
	def __str__(self):
		return "{ temporada: " + self.temporada + ", numero: " + self.numero + ", texto: '" + self.texto + "', versiones: [" +",".join(str(x) for x in self.versiones) + "]  }"
	def __unicode__(self):
		return u"{ 'temporada': " + self.temporada + ", 'numero': " + self.numero + ", 'texto': '" + self.texto + "', 'versiones': [" +",".join(unicode(x) for x in self.versiones) + "]  }"

class Buscador:
	def __init__(self):
		self.urlRoot = "https://www.tusubtitulo.com/"
	def ParsearFichero(self, fichero):
		info = PTN.parse(fichero)
		print info
		return info
	def ObtenerSeriesCoincidentes(self, nombreSerie):
		response = urllib2.urlopen(self.urlRoot + "series.php")
		soup = BeautifulSoup(response, 'html.parser')
		seriesCoincidentes = soup.find_all('a', text=nombreSerie)
		return seriesCoincidentes
	def esFilaVersion(self, fila):
		imagenVersion = fila.find('img')
		if not imagenVersion is None:
			if imagenVersion != -1:
				if imagenVersion["src"]=="//www.tusubtitulo.com/images/folder_page.png":
					return True
		return False
	def ObtenerCapitulo(self, serieID, temporada, numeroCapitulo):
		response2 = urllib2.urlopen("https://www.tusubtitulo.com/ajax_loadShow.php?show="+serieID+"&season=" + temporada)
		soup2 = BeautifulSoup(response2, 'html.parser')  
		enlaceCapitulo = soup2.find('a', text=re.compile('\w*'+temporada+'x'+numeroCapitulo+'\w*'))
		if not enlaceCapitulo is None:
			capitulo=Capitulo(temporada, numeroCapitulo, enlaceCapitulo.getText())
			filas = list(enlaceCapitulo.parent.parent.parent.children)
			for fila in filas:
				if self.esFilaVersion(fila):
					imagenVersion = fila.find('img')
					version = Version(imagenVersion.parent.getText().strip())
					capitulo.versiones.append(version)		
					siguienteFila = fila.find_next_sibling("tr")
					while not siguienteFila is None and not self.esFilaVersion(siguienteFila):
						celdasIdioma = siguienteFila.find_all("td", {'class': 'language'})
						if len(celdasIdioma) > 0:
							enlacesDescarga = siguienteFila.find_all("a", text="Descargar")
							enlace = "https:"+enlacesDescarga[0]["href"]
							idioma = Idioma(celdasIdioma[0].getText().strip(), enlace)
							version.idiomas.append(idioma)
							#print(celdasIdioma[0])
						siguienteFila = siguienteFila.find_next_sibling("tr")
		return capitulo

def log(module, msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'),level=xbmc.LOGERROR ) 

def normalizeString(str):
    return unicodedata.normalize('NFKD', unicode(unicode(str, 'utf-8'))).encode('ascii','ignore')