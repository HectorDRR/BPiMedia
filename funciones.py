#! /usr/bin/env python3 
# -*- coding: utf-8 -*-
"""
Funciones.py Conjunto de macros para gestionar las descargas del emule, torrent, y la creación y mantenimiento de mi página web

En primer lugar, mantendremos una lista de las funciones implementadas, su función y los parámetros que soporta, estando entre [] aquellos 
que son opcionales
"""

import time
import shutil
import os
import re
import sys
import stat

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)

class Capitulo:
	'Tratamiento de capítulos de series'
	def __init__(self, Todo):
		""" Inicializamos las variables y dividimos el nombre del capítulo en sus componentes
		"""
		self.Todo = Todo
		# Filtro para buscar donde está la numeración de la serie. Teniendo en cuenta que algunos capítutlos no tienen título
		# y viene un '.' directamente después del número del capítulo
		pp = re.compile(' \d+x\d\d(?:-\d\d)?')
		result = pp.split(Todo)
		# Si obtenemos 2 pedazos al dividir la cadena siginifica que es una serie
		if len(result) > 1:
			self.Ok = True
			self.Serie = result[0]
			# En caso de que haya título, habrá un espacio antes de su comienzo, así que lo suprimimos
			if result[1][0] == ' ':
				espacio = 1
			else:
				espacio = 0
			self.Titulo = result[1][espacio:-4]
			self.Temp = Todo[len(result[0])+1:Todo.find('x')]
			# Si no tiene título buscamos el '.'. En caso contrario, buscamos el primer espacio
			if len(self.Titulo) == 0:
				buscar = '.'
			else:
				buscar = ' '
			self.Capi = Todo[Todo.find('x',len(result[0])+1)+1:Todo.find(buscar,len(result[0])+1)]
			self.Tipo = Todo[-3:]
			# Limpiamos el nombre del capítulo
			self.Limpia()
			self.ConSerie = self.Serie + env.DIR + self.Todo
		else:
			self.Ok = False
		# Para confirmar que los datos se están extrayendo correctamente 
		#print(self.__dict__)
		return

	def Existe(self):
		""" Para comprobar si la serie ya existe y procurar ponerle el mismo nombre que ya tiene
		"""
		# Cargamos las series que conocemos actualmente para no confundir las mayúsculas y minúsculas
		Series = next(os.walk(env.MM + 'scaratulas'))[2]
		# Quitamos la extensión de la carátula
		Series = [f[0:-4] for f in Series]
		# Comprobamos que no ha habido un error con las minúsculas y mayúsculas
		for s in Series:
			# Si el nombre en mayúsculas es igual, pero no lo es el original
			if s.upper() == self.Serie.upper() and not s == self.Serie:	
				# Renombramos el fichero original con el nombre que ha de tener
				os.rename(self.Todo, self.Todo.replace(self.Serie,s))
				# Cambiamos también las variables
				self.Todo = self.Todo.replace(self.Serie,s)
				self.ConSerie = self.ConSerie.replace(self.Serie,s)
				self.Serie = s
				# Consideramos que la serie existe
				return True
		# Si llegamos hasta aquí es que no existe la carpeta ni hay un error en mayúsculas/minúsculas
		return False
		
	def Limpia(self):
		""" Limpiamos el nombre del capítulo para quitar lo incluido entre corchetes
		"""
		donde = self.Titulo.find('[')
		if (donde >= 0):
			#Si hay un espacio antes del corchete también lo eliminamos
			if self.Titulo[donde-1] == ' ':
				donde -= 1
			sinf = self.Serie + ' ' + self.Temp + 'x' + self.Capi + ' ' + self.Titulo[0:donde] + '.' + self.Tipo
			try:
				os.rename(self.Todo, sinf)
			except OSError as e:
				print('Ha ocurrido un error renombrando el fichero ' + sinf + ': ' + e.strerror)
			# Log('Limpiamos el nombre del fichero %s a %s' % (f, sinf))
			self.Titulo = self.Titulo[0:donde]
			self.Todo = sinf
		return

def BajaSeries():
	""" Se conecta por FTP a la mula para comprobar si hay nuevos capítulos de las series que tenemos
	en el curro y bajarse los que falten.
	Tenemos pendiente implementar control de capítulos sobreescritos por problemas
	Tenemos que tener en cuenta aquellas series que están enteras en el curro pero no en el servidor
	Y también aquellas que ya no están en el servidor
	"""
	from ftplib import FTP
	# Nos vamos a PASADOS
	os.chdir(env.PASADOS)
	# Obtenemos las series que estamos trayendo
	listalocal = os.listdir()
	# Ahora realizamos la conexión al servidor FTP
	ftp = FTP()
	ftp.connect('hrr.no-ip.info', 2211)
	ftp.login('hector', '44celeborN')
	ftp.cwd('pasados/')
	listaremota = ftp.nlst()
	
	return
def Borra(Liberar = 30, Dias = 30):
	"""Se encarga de liberar espacio eliminando los ficheros más viejos que hay en las series sin
	contar los que están en las series que vemos (env.SERIESVER) Por defecto, liberará 20 GB.
	"""
	Log('Vamos a proceder a eliminar ficheros viejos de pasados')
	# Sacamos la lista de ficheros con mas de 30 días de antiguedad y que los permisos 
	# indican que ya ha sido copiado a disco externo
	os.chdir(env.PASADOS)
	salida = os.popen('find . -type f -mtime +' + str(Dias) + ' -perm 644 ! -iname "*.jpg"|sort').read()
	# Leemos la lista de ficheros con más de 30 días. Filtramos los campos nulos que suelen quedar al final
	# de la salida y lo convertimos a lista puesto que filter saca un 'iterable'
	lista = sorted(filter(None, salida.split('\n')))
	# Quitamos el './' inicial
	lista = [x[2:] for x in lista]
	#Leemos las series que estamos viendo para no borrarlas
	with open (env.SERIESVER) as file:
		ver = file.readlines()
	ver = [x[:-1] for x in ver]
	borrar = []
	#Convertimos a entero el parámetro pasado en caso de que viniera como string
	if type(Liberar) is str:
	    Liberar = int(Liberar)
	#Quitamos las series que estamos viendo
	for l in lista:
		No = 0
		for v in ver:
			if v == l[0:l.find('/')]:
				No = 1
				break
		if not No:
			borrar.append(l)
	libre = Borra2(borrar, Liberar)
	# Si no hemos conseguido liberar el espacio solicitado pasamos a las series ya vistas
	if Liberar > libre:
		BorraVistos(Liberar)
	else:
		os.system("/home/hector/bin/compartidos")
	# Eliminamos las carpetas sin serie
	LimpiaPasados()
	return

def Borra2(borrar, Liberar, Preg=False):
	""" Se encarga de borrar la lista de ficheros que le pasamos hasta dejar libre el espacio
	definido en Liberar. Si ponemos en True el Preg, preguntaremos antes de borrar cada archivo.
	Esto último lo implementamos sobre todo para evitar, en el borrado de series vistas, borrar aquellas recién descargadas
	"""
	libre = 0
	for f in borrar:
		#Si hemos alcanzado la cantidad a liberar, terminamos
		libre = Libre(env.PASADOS, 'G')
		Log('Quedan ' + str(libre) + ' GB libres, a liberar ' + str(Liberar) + ' GB', True)
		if libre > Liberar:
			break
		# Obtenemos los permisos del fichero
		per = os.stat(f)
		# Si ya ha sido copiado (no tiene el permiso x de usuario) procedemos al borrado incluyendo subtítulos si los hubiere
		if not per.st_mode & stat.S_IXUSR:
			# Preguntamos si se quieren borrar 
			if Preg:
				que = input('¿Borramos ' + f + '? (No / Todos)').upper() 
				if que == 'N':
					continue
				if que == 'T':
					Preg = False
			try:
				os.remove(f)
			except OSError as e:
				Log('Hubo algún problema borrando ' + f + e.strerror, True)
				continue
			Log('Se borró correctamente ' + f, True)
	return libre

def BorraVistos(Liberar = 30):
	# Obtenemos el listado de ficheros con bookmarks y con su duración
	if type(Liberar) is str:
		Liberar = float(Liberar)
	lista = os.popen('sqlite3 /mnt/e/.mini/files.db "select path,sec,duration from bookmarks inner join details on bookmarks.id=details.id where path like \'/mnt/e/pasados/%\' order by path;"').read()
	lista = list(filter(None, lista.split('\n')))
	borrar = []
	# Seleccionamos los que han sido vistos más de un 95% o tiene un 0 que indica que se han visto completamente o que apenas se han empezado a ver
	for f in lista:
		ruta, bookmark, duracion = f.split('|')
		duracion = Duracion(duracion)
		if (int(bookmark) > 0.95 * duracion) or int(bookmark) == 0:
			borrar.append(ruta)
	if len(borrar) > 0:
		# Mostramos los ficheros a procesar
		print('\nVamos a proceder a borrar:\n')
		for f in range(len(borrar)):
			print('{0:2d} '.format(f) + borrar[f])
		# Preguntamos si realmente los queremos borrar
		que = input('Procedemos?').upper()
		if que == 'N':
			return
		if que.isnumeric():
			del borrar[0:int(que)]
		Borra2(borrar, Liberar, True)
		# Actualizamos en el aMule la lista de ficheros compartidos
		os.system("/home/hector/bin/compartidos")
	return

def BP(Peli, Comentario):
	""" Se encarga de eliminar una peli y dejar un comentario en Borradas_HD para no volver a caer en el error de bajarla
	"""
	import glob
	# Obtenemos la lista de ficheros a borrar
	print(Peli + '\n' + Comentario)
	lista = glob.glob(Peli[:-3] + '*')
	print(lista)
	if input('¿Estás seguro de borrar estos ficheros? (S)') == 'S':
		for f in lista:
			os.remove(f)
		# Dejamos el comentario en el fichero de Borradas
		with open(env.PLANTILLAS + 'Borradas_HD', 'a') as file:
			file.write(Peli + ':Borradas:' + Comentario + '\n')
		Log('Borramos ' + Peli + ' con el comentario: ' + Comentario, True)
	return

def Copia():
	"""Se encarga de realizar una copia del contenido de ~/bin y /mnt/e/util modificado desde ayer al ftp del cine
	"""
	#Nos vamos a la carpeta bin
	os.chdir('/home/hector/bin')
	os.system('find . -maxdepth 1 -type f -mtime -1 -exec curl --ftp-pasv -T {} ftp://hrr:21ceLeborn@ftp.ono.com/bin/ \;')
	#Nos vamos a la carpeta util
	os.chdir('/mnt/e/util')
	os.system('find . -maxdepth 1 -type f -mtime -1 -exec curl --ftp-pasv -T {} ftp://hrr:21ceLeborn@ftp.ono.com/util/ \;')
	#Método alternativo desde dentro de Python
	#Nos conectamos
	#ftp = FTP('cine.no-ip.info', user='u820276474', password='22celEborn')
	#Nos cambiamos a la carpeta de destino
	#ftp.cwd('bin')
	return

def CopiaNuevas(Pen):
	""" Se encarga de copiar las pelis o series nuevas desde el pen a las carpetas que tengo en metal para distribuir 
	a los aficionados del IAC
	"""
	import glob
	# Añadimos la carpeta Tarsi a la ruta
	Pen = Pen + '\\Series'
	# Confirmamos que existe la ruta de entrada
	if not os.path.exists(Pen):
		print('No se encunetra la carpeta ' + Pen)
		return
	# Nos pasamos al directorio origen
	os.chdir(Pen)
	# Cargamos la lista de ficheros del pen, independientemente de su extensión para también copiar los .srt u otros
	# que puedan surgir
	series = glob.glob('*')
	# La ordenamos
	series.sort()
	for f in series:
		# Metemos el capítulo en un objeto
		capi = Capitulo(f)
		# Si no es un capítulo pasamos al siguiente
		if not capi.Ok:
			continue
		# comprobamos si es una de las que estamos copiando y la copiamos
		if os.path.exists(env.SERIES + capi.Serie):
			# Si existe ya el fichero, lo omitimos. Más adelante comprobaremos fechas por si es uno arreglado
			if not os.path.exists(env.SERIES + capi.Serie + '\\' + capi.Todo):
				if not Queda(f, env.SERIES):
					input('No queda espacio suficiente en la carpeta de Series, limpia')
				# Lo copiamos
				print('Copiando "' + f + '" a ' + capi.Serie)
				shutil.copy(f, env.SERIES + capi.Serie + '\\')
	# Nos pasamos a la carpeta de Pelis
	os.chdir('..\\Pelis')
	pelis = glob.glob('*.mkv')
	pelis.sort()
	for f in pelis:
		# Si existe ya el fichero, lo omitimos. Más adelante comprobaremos fechas por si es uno arreglado
		if not os.path.exists(env.HD + f):
			# Comprobamos si queda espacio
			if not Queda(f, env.HD[0:2]):
				if input('No queda espacio suficiente en ' + env.HD[0:2] + ', limpia') == 'n':
					continue
			# Lo copiamos y le ponemos el atributo de archivo para que lo manipule julito2
			print('Copiando "' + f + '" a ' + env.HD)
			shutil.copy(f, env.HD)
			os.system('attrib +a "' + env.HD + f + '"')
	return
	
def CreaWeb(p1 = 'Ultimas', Pocas = 0):
	""" Se encarga de generar las distintas páginas web necesarios para la gestión de las películas y las series.
	El fichero html estará en env.PLANTILLAS con el mismo nombre que la plantilla.
	Se habilita una opción especial para cuando estamos en el curro que también anunciamos series
	El p1 será la plantilla a usar, por defecto, el más usado, Ultimas
	El Pocas habilita la manera antigua de presentar las carátulas. Útil para el curro y las Últimas sin índices y con las
	carátulas visibles
	"""
	import codecs
	
	if type(Pocas) == str:
		Pocas = True
	# En caso de crear la página de Series
	if p1 == 'Series':
		ser = 's'
		que = p1
	else:
		que = 'películas'
		ser = ''
	# Abrimos la plantilla
	try:
		with open(env.PLANTILLAS + p1 + '.1') as file:
			plantilla = file.readlines()
	except OSError as e:
		Log('Ha habido un error: ' + e.strerror + '\n abriendo la plantilla ' + p1, True)
		return
	plantilla = [x[:-1] for x in plantilla]
	# Ponemos la fecha
	plantilla[-1] = plantilla[-1] + ' ' + (time.strftime('%a, %d %b %Y %H:%M') + '</p>')
	plantilla.append('<p align="center"><a href="index.html">Atrás</a></p>')
	# Inicializamos variables
	fila = 0
	url = ''
	# Para crear listas con cartátulas, Msheets y Trailers que faltan
	cfaltan = []
	mfaltan = []
	tfaltan = []
	# Si estamos en el curro, y estamos generando el correo, tenemos que añadir toda la URL
	if env.SISTEMA == 'Windows':
		url = 'http://cine.no-ip.info/'
	# Guardaremos el índice en una lista para añadirlo a posteriori
	indice = '<p align="center">'
	cuerpo = ['<table width="95%" align="center" style="border-spacing:2px 10px"><tr>']
	# Si es la página de últimas, obtenemos la lista directamente y la ordenamos por fecha
	if p1 == 'Ultimas':
		Pocas = True
		titulo = 'Últimas Películas Añadidas'
		os.chdir(env.HD)
		pelis = ObtenLista(1)
		# Tenemos que añadirle a la lista los otros dos campos
		pelis = [x + ':Ultimas:' for x in pelis]
		# Procedemos a quitar el atributo u+x a las carátulas para diferenciar cuando 
		# hay pelis nuevas y lanzar la creación de la página de últimas
		os.system('chmod u-x *.jpg')
	else:
		if not os.path.exists(env.TMP + p1):
			# Creamos el fichero con las pelis o series a incluir en la página
			if p1 == 'Todas':
				os.system('cat ' + env.PLANTILLAS + 'HD*>' + env.TMP + 'Todas')
			else:
				if p1 == 'Series':
					deque = 'Series_*'
				else:
					deque = 'HD*' + p1
				os.system('cat ' + env.PLANTILLAS + deque + '>' + env.TMP + p1)
		with open(env.TMP + p1) as file:
			try:
				pelis = file.readlines()
			except UnicodeDecodeError as e:
				Log('Error al procesar el comentario en el byte ' + str(e.start), True)
				return 'Error con el juego de caracteres'
		# Quitamos el retorno de carro del final '\n' y suprimimos posibles líneas vacías producto de unir varios ficheros
		if not Pocas:
			pelis = sorted(set(filter(None,[x[:-1] for x in pelis])))
		titulo = p1
	# Ponemos el título de la página
	plantilla.insert(3, '\t<title>' + titulo + '</title>')
	plantilla.insert(15, '<h1>' + titulo + '</h1>')
	# Para no repetir el índice al principio de la página pero si dejar un enlace
	lind = pelis[0][0]
	indice = indice + '<a href="#' + lind + '">' + lind + '</a> '
	plantilla.append('<p align="center">Número de ' + que + ': ' + str(len(pelis)) + '</p>')
	# Empezamos el bucle de generación
	for p in pelis:
		# Separamos los campos
		peli, disco, comen = p.split(':',2)
		if Pocas:
			print(peli)
		# Inicializamos algunas variables dentro del bucle
		linpeli = ''
		termina = ''
		caratula = ''
		trai = ''
		indi = ''
		# Chequeamos si tenemos que añadir una letra nueva al índice
		if not lind == peli[0]:
			lind = peli[0]
			indice = indice + '<a href="#' + lind + '">' + lind + '</a> '
			indi = '<a name="' + lind + '"></a>'
			# Ponemos una marca para luego rellenarla con el índice alfabético menos en la de Últimas
			if not Pocas:
				cuerpo.append('indice')
				# Y cambiamos de fila
				fila = 4
		# Chequeamos si tenemos que cerrar la fila actual y crear una nueva fila
		if fila == 4:
			fila = 0
			cuerpo.append('</tr>\n<tr>')
		# Para poder anunciar las pelis junto con las series en el curro
		if Pocas:
			curro = Divide(peli)
			if type(curro) is list:
				disco = peli[len(curro[0])+1:]
				peli = curro[0]
				ser = 's'
		# Si trabajamos con series dejamos el título tal cual, en caso de pelis, quitamos la extensión para buscar la carátula
		# Nos falta ver como tratar las pelis en carpetas (Blu-Ray)
		if ser:
			titulo = peli + '.'
		else:
			titulo = peli[:-3]
		# Chequeamos si hay carátula. Asumimos que si no hay carátula tampoco hay Msheet
		if os.path.exists(env.MM + ser + 'caratulas/' + titulo + 'jpg'):
			if Pocas:
				caratula = ' title="' + disco + ':' + comen + '"><img src="' + url + ser + 'caratulas/' + titulo + 'jpg" \\'
			else:
				caratula = ' class="hover-lib" id="' + url + ser + 'caratulas/' + titulo + 'jpg" title="' + disco + ':' + comen + '" '
		else:
			cfaltan.append(peli)				
		# Chequeamos si hay Msheet
		if os.path.exists(env.MM + ser + 'Msheets/' + peli + '_sheet.jpg'):
			linpeli = '<a href="' + url + ser + 'Msheets/' + peli + '_sheet.jpg" target="_Sheet"' + caratula + '>'
			termina = '</a>'
		else:
			mfaltan.append(peli)
		trai = Trailer(peli)
		# Añadimos un \n para que sea más fácil localizarlo desde el curro para anunciar las pelis
		if len(trai) > 0:
			trai = '\n <a href="' + trai + '" target="_trailer">[T]</a>\n'
		else:
			trai = ''
			tfaltan.append(peli)
		# Ya que tenemos todos los componentes, formamos la línea
		if ser and Pocas:
			peli = peli + peli[len(curro[0]):len(curro[0])+6]
		cuerpo.append('<td valign="top" width="25%"><p align="center">' + indi + linpeli + '<br /><font size="-1">' + peli + '</font>' + termina + trai + '</td>')
		fila += 1
	# Terminamos la tabla
	cuerpo.append('</tr>\n</table>\n<p align="center"><a href="index.html">Atrás</a></p>')
	# Completamos el índice
	if not Pocas:
		plantilla.append(indice + '</p>')
	# Rellenamos todos los índices en cada cambio de letra para facilitar la movilidad por la página
	while True:
		try:
			cuerpo[cuerpo.index('indice')] = '</tr>\n<tr><td colspan="4" style="border:1px solid black">' + indice + '</p></td>'
		except ValueError:
			break
	# Juntamos
	plantilla.extend(cuerpo)
	# Terminamos la página
	plantilla.append('</body>')
	plantilla.append('<script type="text/javascript" src="' + url + 'jquery.js"></script>')
	plantilla.append('<script type="text/javascript" src="' + url + 'hover-lib.js"></script>')
	plantilla.append('</html>')
	# Escribimos la página en env.WEB ya que hemos pasado del hosting externo y usamos también la BPI como servidor web
	with codecs.open(env.WEB + p1 + '.html', 'w', encoding='utf-8-sig') as file:
		for linea in plantilla:
			file.write(linea + '\n')
	# Escribimos las listas de lo que falta
	if len(cfaltan) > 0:
		with open(env.PLANTILLAS + ser + 'caratulas.faltan', 'w') as file:
			for f in cfaltan:
				file.write(f + '\n')
	if len(mfaltan) > 0:
		with open(env.PLANTILLAS + ser + 'msheets.faltan', 'w') as file:
			for f in mfaltan:
				file.write(f + '\n')
	if len(tfaltan) > 0:
		with open(env.PLANTILLAS + ser + 'trailer.faltan', 'w') as file:
			for f in tfaltan:
				file.write(f + '\n')
	# Eliminamos el fichero usado para crear la página excepto cuando son las últimas, que no se genera fichero
	if not p1 == 'Ultimas':
		os.system(env.DEL + env.TMP + p1)
	return

def Divide(Serie):
	"""Dividimos un nombre de serie dividido en Serie y capítulo. Si obtenemos 2 pedazos al 
	dividir la cadena devolvemos la Serie y el título del capítulo en una lista. Si no, devolvemos la
	cadena que nos mandaron
	"""
	pp = re.compile(' \d+x\d\d(?:-\d\d)?')
	Result = pp.split(Serie)
	#Si obtenemos 2 pedazos al dividir la cadena siginifica que es una serie
	if len(Result)>1:
		return(Result)
	else:
		return(Serie)

def Duracion(Tiempo):
	""" Convertimos el tiempo del formato HH:MM:SS a segundos
	"""
	hora, minuto, seg = Tiempo.split(':')
	return (int(hora) * 3600) + (int(minuto) * 60) + int(seg[0:2])

def Etiqueta(Ruta):
	""" Obtenemos la etiqueta del disco montado en Ruta sin la '/' final
	"""
	if env.SISTEMA == 'Windows':
		pp = os.popen('vol ' + Ruta[0:2]).read().split('\n')
		Etiq = pp[0][pp[0].find('es')+3:]
	else:
		Etiq = os.popen('mount -l|grep ' + Ruta[:-1]).read()
		Etiq = Etiq[Etiq.find('[')+1:-2]
	return Etiq

def GeneraLista(Listado, Pelis, Serie = False):
	""" Pequeña función para generar la lista de películas o series con sus comentarios si los hubiera.
	La separamos de la función principal para poder llamarla cuando realizamos la lista de últimas
	
	Listado contiene el nombre del fichero donde se va a almacenar la lista
	Pelis es una lista con los elementos a tratar
	Serie es un booleano que nos indica si se trata de una serie (True) o no (False)
	"""
	# Procesamos la lista añadiendo los comentarios si los hubiera
	with open(env.PLANTILLAS + Listado.replace(':',''), 'w') as file:
		for f in Pelis:
			comen = ''
			# Si se trata de series, cambiamos algunas cosas
			if Serie:
				que = f + env.DIR + f + '.'
				capis = ':' + ListaCapitulos(f, Listado[-2:] + env.DIR + 'Series' + env.DIR)
			else:
				que = f[:-3]
				capis = ''
			if os.path.exists(que + 'txt'):
				with open(que + 'txt') as fiche:
					try:
						comen = fiche.readline()
					except UnicodeDecodeError as e:
						Log('Error al procesar el comentario de ' + f, True)
						continue
				comen = comen[:-1]
			file.write(f + ':' + Listado + ':' + comen + capis + '\n')
	return

def GuardaHD():
	""" Se encarga de pasar las películas a los discos externos USB para su almacenamiento
		Empezaremos solo por las pelis por ser más sencillo su tratamiento. Tenemos que tener 
		montado el disco en la ruta anterior a la que señala la variable HDG (/mnt/HD)
		El parámetro Etiq es el que se va a pasar a la función ListaPelis para almcenar la lista 
		actualizada de películas.
	"""
	Log('Comenzamos la copia de pelis HD', True)
	# Nos vamos a la carpeta de las pelis
	os.chdir(env.HD)
	if os.path.exists(env.HDG + 'Pelis/'):
		GuardaPelis('Pelis', '6')
	# Empezamos con las Infantiles
	if os.path.exists(env.HDG + 'Infantiles/'):
		GuardaPelis('Infantiles', '4')
	# Generamos la lista de películas del disco y la página web
	ListaPelis()
	CreaWeb('Todas')
	CreaWeb('Pelis')
	# Limpiamos las carátulas que hayan quedado en la carpeta env.HD
	LimpiaHD()
	Etiq = GuardaLibre(env.HDG)
	# Paramos el disco duro por si lo hemos dejado copiando. El parámetro -Sx establece en x*5 segundos el tiempo de inactividad antes de pararse
	os.system('cd &&sleep 3&&sudo hdparm -S3 /dev/disk/by-label/' + Etiq + ' &&sudo umount /mnt/HD')
	return

def GuardaLibre(Ruta):
	""" Guarda el espacio total y libre en el disco que estamos tratando y lo almacena en env.PLANTILLAS + 'quedan.txt'
	"""
	# Leemos el fichero que contiene todos los discos
	with open(env.PLANTILLAS + 'quedan.txt') as file:
		lista = file.readlines()
	# Quitamos los finales de línea
	lista = [x[:-1] for x in lista]
	# Obtenemos el espacio libre
	libre = Libre(Ruta)
	# Obtenemos la etiqueta 
	Etiq = Etiqueta(Ruta[:-1])
	# Formamos la línea a escribir
	linea = Etiq + ' = ' + '{:,g}'.format(libre) + ' GB'
	# Buscamos la etiqueta de nuestro disco y ponemos el nuevo espacio libre. Devuelve una lista de un elemento
	vieja = [x for x in lista if x.startswith(Etiq)]
	# Por si no estaba, buscamos la línea y si no está, la añadimos
	try:
		donde = lista.index(vieja[0])
		lista[donde] = linea
	except IndexError as e:
		lista.append(linea)
	# Escribimos de nuevo el fichero
	lista.sort()
	with open(env.PLANTILLAS + 'quedan.txt', 'w') as file:
		for f in lista:
			file.write(f + '\n')
	print('Libre en ' + linea)
	return Etiq

def GuardaPelis(Cuales, Que):
	""" Macro para guardar las pelis adultas o infantiles en los discos duros correspondientes
		Cuales se correponde con el tipo de Pelis, por ahora solo las normales y las infantiles
		Que se corresponde con los permisos que las distinguen, ?66 en el caso de las pelis y 
		?46 en el caso de las infantiles por lo que solo mandamos el permiso de grupo, 6 o 4.
	"""
	# Encendemos el led
	os.system('/home/hector/bin/ledonoff heartbeat')
	# Generamos la lista de las pelis que no se han pasado copiado rw?r?-rw-
	# Más adelante, aprenderemos como hacer esto desde el mismo Python sin tener que recurrir al find
	salida = os.popen("find . -type f -name '*.mkv' -perm 7" + Que + "6 -o -perm 6" + Que + "6").read()
	# Convertimos en lista y quitamos elementos nulos
	lista = sorted(filter(None, salida.split('\n')))
	# Quitamos el './' inicial
	lista = [x[2:] for x in lista]
	print(lista, env.HDG + Cuales)
	# Cogeremos cada peli y la copiaremos al disco que definiremos como GHD hasta que se llene y pasemos a otros
	for peli in lista:
		Log('Copiamos la peli: ' + peli, True)
		if not Queda(peli, env.HDG + Cuales):
			continue
		try:
			shutil.copy(peli, env.HDG + Cuales)
			shutil.copy(peli[:-3] + 'jpg', env.HDG + Cuales)
		except IOError as e:
			Log('Ha ocurrido un error copiando la película ' + peli + e.strerror, True)
			continue
		# Copiamos también la sheet
		try:
			shutil.copy('/mnt/f/Msheets/' + peli + '_sheet.jpg', env.HDG + Cuales)
		except IOError as e:
			Log('Ha ocurrido un error copiando la Msheet ' + peli + e.strerror, True)
			continue
		# Cambiamos los permisos para marcarla como ya copiada rwxrwxrwx
		per =  os.stat(peli)
		os.chmod(peli, per.st_mode | stat.S_IRWXG | stat.S_IRWXO)
		Log('Se ha copiado la película ' + peli)
	Log('Hemos terminado de copiar las pelis HD', True)
	os.system('/home/hector/bin/ledonoff none')
	return

def GuardaSeries(Ruta, deb = False):
	""" Se encarga de pasar las series a los discos externos USB para su almacenamiento
		Si la llamamos con deb = True la ponemos en modo depuración para que 
		no haga efecto sino muestre lo que va a hacer
	"""
	lista = []
	Log('Comenzamos la copia de las Series ' + Ruta, True)
	# Confirmamos que está montado el disco de destino, y si no, lo montamos
	while not os.path.exists(env.SERIESG + Ruta + '/Series/'):
			os.system('sudo mount ' + env.SERIESG + Ruta)
			time.sleep(3)
	# Encendemos el led verde para mostrar que estamos copiando
	os.system('/home/hector/bin/ledonoff heartbeat')
	# Nos vamos a la carpeta de las Series
	os.chdir(env.PASADOS)
	# Generamos la lista de las series que ya han pasado por el pen y aún no han sido copiadas u+rwx
	# Más adelante, aprenderemos como hacer esto desde el mismo Python sin tener que recurrir al find
	# Teníamos quitados los jpg con ' ! -iname "*.jpg"' pero entonces no se actualiza el folfer ni el folder_sheet
	salida = os.popen('find . -type f -perm -u+rwx').read()
	# Convertimos la salida en lista y quitamos el \n final
	leido = sorted(filter(None, salida.split('\n')))
	# Quitamos el './' inicial
	leido = [x[2:] for x in leido]
	# Nos quedamos con las series que están alfabéticamente en el rango que contiene el disco (Ruta)
	# La pasamos a mayúsculas por series como 'iZombie' que se quedaban fuera de la selección
	for f in leido:
		if (f[0].upper() >= Ruta[0] and f[0].upper() <= Ruta[1]):
			lista.append(f)
	# Mostramos los ficheros a procesar
	for f in range(len(lista)):
		print('{0:2d} '.format(f) + lista[f])
	# Cogeremos cada capítulo y lo copiaremos al disco
	for serie in lista:
		Log('Copiamos la Serie ' + str(lista.index(serie)+1) + ' de ' + str(len(lista)) + ' a la ruta ' + env.SERIESG + Ruta + '/Series/' + serie, True)
		if deb:
			print(serie, env.SERIESG + Ruta + '/Series/' + serie)
		else:
			# En caso de estar copiando la carátula y la Sheet de la serie, dividimos nosotros el nombre. En caso contrario genera una carpeta 'f'
			# Tratamos por igual las sheet (folder*.jpg) y los subtítulos (*.rar)
			ser = []
			ser.append(serie[:serie.find('/')])
			ser.append(serie[serie.find('/')+1:])
			if not os.path.exists(env.SERIESG + Ruta + '/Series/' + ser[0]):
				Log('No existe la carpeta de la serie ' + serie + ', así que la creamos', True)
				try:
					os.mkdir(env.SERIESG + Ruta + '/Series/' + ser[0])
				except OSError as e:
					Log('Ha ocurrido un error creando la carpeta %s. Error: %s' % (ser[0], e.strerror), True)
					continue
				# Si está la carátula, la copiamos junto con la Msheet
				if os.path.exists(env.MM + 'scaratulas/' + ser[0] + '.jpg'):
					shutil.copy(env.MM + 'scaratulas/' + ser[0] + '.jpg', env.SERIESG + Ruta + '/Series/' + ser[0] + '/folder.jpg')
					shutil.copy(env.MM + 'sMsheets/' + ser[0] + '_sheet.jpg', env.SERIESG + Ruta + '/Series/' + ser[0] + '/folder_sheet.jpg')
			if not Queda(serie, env.SERIESG + Ruta + '/Series/'):
				continue
			try:
				shutil.copy(serie, env.SERIESG + Ruta + '/Series/' + ser[0] + '/')
			except IOError as e:
				Log('Ha ocurrido un error copiando la serie %s. Error: %s' % (serie, e.strerror), True)
				continue
		# Cambiamos los permisos para marcarla como ya copiada rw-r--r--
		if deb:
			print('cambiamos permisos a ' + serie)
		else:
			os.chmod(serie,0o644)
		# Log('Se ha copiado la serie ' + serie, True)
	Log('Hemos terminado de copiar las series', True)
	GuardaLibre(env.SERIESG + Ruta + '/')
	ListaSeries(Ruta)
	CreaWeb('Series')
	# Desmontamos la unidad
	os.system('sudo umount ' + env.SERIESG + Ruta)
	# Apagamos el led
	os.system('/home/hector/bin/ledonoff none')
	return

def JTrailer(Peli, Debug = 0):
	""" Se encarga de extraer la URL de los trailers de las páginas de últimas y Todas desde
	el trabajo para generar allí las listas.
	"""
	import codecs
	# Leemos el fichero con todas las películas
	with codecs.open(env.TMP + 'Todas.html', 'r', encoding='utf-8-sig') as f:
		lista = f.readlines()
	# En pp almacenamos los trailers
	pp = []
	# En qq nos quedamos con los títulos de las pelis
	qq = []
	una = 0
	# Leemos línea por línea, cuando encontramos una peli, cogemos el trailer de la siguiente línea
	# en caso de que lo haya, si no, lo ponemos a nulo y pasamos a la siguiente
	for f in range(20,len(lista) - 5):
		if lista[f].startswith('<td v'):
			donde = lista[f].find('-1"')+4
			qq.append(lista[f][donde:lista[f].find('.mkv<',donde) + 4])
			if lista[f + 1][-8:-5] == '[T]':
				pp.append(lista[f + 1][9:-27])
			else:
				pp.append('')
	# Imprimimos la lista para depurar
	if Debug:
		for f in range(len(pp) - 1):
			print(str(f) + ': ', qq[f], pp[f])
	# Por si hay un problema con los acentos o ñ tenemos que comprobar que se encuentra la película
	try:
		trailer = pp[qq.index(Peli)]
	except ValueError as e:
		print('No se encuentra la peli: ' + Peli + '.\nQuizás problemas con acentos o ñ')
		trailer = ''
	return trailer

def Led():
	""" Se encarga de encender un Led en la salida 17 durante un segundo y apagarlo después
	"""
	import RPi.GPIO as GPIO
	#Especificamo el modo de direccionar los GPIOs en la RPi
	GPIO.setmode(GPIO.BCM)
	#Definimos el puerto como de salida
	GPIO.setup(17, GPIO.OUT)
	#Lo activamos
	GPIO.output(17, 1)
	#Esperamos un segundo
	time.sleep(1)
	#Desactivamos
	GPIO.output(17, 0)
	#Limpiamos los puertos para quitarles la configuración
	GPIO.cleanup(17)
	return exit

def Libre(p1, Tam = 'G'):
	#Obtenemos el espacio libre en disco, por defecto, en GB
	if Tam == 'M':
		Tam = 1024 * 1024
	else:
		if Tam == 'G':
			Tam = 1024 * 1024 * 1024
	if env.SISTEMA == 'Windows':
		import wmi
		sys = wmi.WMI()
		for f in sys.Win32_LogicalDisk():
			if f.Caption == p1[0:2].upper():
				libre = int(f.FreeSpace) / Tam
				break
	else:
		disco = os.statvfs(p1)
		libre = (disco.f_frsize * disco.f_bavail) / Tam
	return libre

def Limpia(f):
	donde = f.find('[')
	if (donde >= 0 and (f[-3:] == 'avi' or f[-3:] == 'mkv' or f[-3:] == 'srt')):
		#Si hay un espacio antes del corchete también lo eliminamos
		if f[donde-1] == ' ':
			donde -= 1
		sinf = f[0:donde] + f[-4:]
		try:
			os.rename(f,sinf)
		except OSError as e:
			print('Ha ocurrido un error renombrando el fichero ' + sinf + ': ' + e.strerror)
			return f
		# Log('Limpiamos el nombre del fichero %s a %s' % (f, sinf))
		f = sinf
	return f

def LimpiaHD():
	""" Se encarga de eliminar las carátulas de aquellas películas que hemos eliminado desde el GUI del Transmission
	"""
	import glob
	os.chdir(env.HD)
	lista = glob.glob('*.jpg')
	for f in lista:
		if not os.path.exists(f[:-3] + 'mkv'):
			print('Borramos ' + f)
			os.remove(f)
	lista = glob.glob('*.tmp')
	for f in lista:
		print('Borramos ' + f)
		os.remove(f)
	return

def LimpiaPasados():
	""" Se encarga de eliminar aquellas carpetas de pasados que ya no contienen series sino solamente la carátula o sheet
	"""
	import glob
	os.chdir(env.PASADOS)
	for f in next(os.walk('.'))[1]:
		# Nos pasamos a la carpeta
		os.chdir(f)
		# Contamos el número de capítulos que hay
		capi = len(glob.glob('*.avi')) + len(glob.glob('*.mkv')) + len(glob.glob('*.mp4'))
		# salimos de la carpeta
		os.chdir('..')
		# Si no hay capítulos
		if capi == 0:
			# Mostramos el contenido de la carpeta
			print(next(os.walk('.'))[2])
			if input('¿Borramos la carpeta "' + f + '"? (s/N)') == 's':
				# Borramos la carpeta
				print('Carpeta "' + f + '" borrada')
				shutil.rmtree(f)
	return

def ListaCapitulos(Serie, Ruta):
	""" Se encarga de revisar los capítulos de una serie dada para sacar un resumen de los mismos y 
	detectar si faltan capítulos en alguna temporada o están repetidos.
	
	Para que esta función funcione correctamente será necesario asegurarse de que la nomenclatura de
	los capítulos es homogénea, y no tenemos mezcla de mayúsculas o minúsculas así como otras alteraciones
	"""
	import glob
	if env.SISTEMA == 'Windows':
		env.SERIESG = ''
		
	os.chdir(env.SERIESG + Ruta + Serie)
	# Leemos todos los capítulos
	lista = glob.glob('*.avi')
	lista.extend(glob.glob('*.mkv'))
	lista.sort
	donde = len(Serie) + 1
	# Primero separamos la serie del capítulo para poder quedarnos solo con la temporada y el capítulo
	caps = [f[donde:f.find(' ', donde)] for f in lista]
	for f in caps:
		if f.find('.') > 0:
			caps[caps.index(f)] = f[0:f.find('.')]
	# Por si acaso las series no se llaman igual, ordenamos la lista
	caps.sort()
	# Ahora toca recorrer la lista separando temporadas, quedándonos con el primer y último capítulo
	# y también informar si nos saltamos alguno
	# cogemos la información de la primera temporada y el primer capítulo almacenado
	tem = caps[0][0:caps[0].find('x')]
	print(caps, Serie)
	# Le restamos 1 al capítulo para que haya una secuencia válida. No empezamos por 0 puesto que hay series
	# que parte están grabadas en CD, no en disco duro
	capi = int(caps[0][-2:]) - 1
	resumen = caps[0] + ' - '
	saltados = ''
	for f in caps:
		# Si hemos cambiado de temporada
		if not tem == f[0:f.find('x')]:
			# Ponemos en el resumen el capítulo final de la temporada anterior y el primero de la actual
			resumen = resumen + '{0:02d} '.format(capi) + ', ' + f + ' - '
			tem = f[0:f.find('x')]
			capi = 0
			if int(f[-2:]) == 0:
				capi = -1
		# Chequeamos si es un capítulo doble y añadimos 1 a la suma para que no nos de como que falta 
		# el primero de los dos, puesto que solo chequea los dos últimos carcteres de la cadena
		if f.find('-') > 0:
			capi = capi + 1
		# Si nos hemos saltado un capítulo
		if not int(f[-2:]) == capi + 1:
			# Si está repetido
			if int(f[-2:]) == capi:
				Log('Capítulo ' + tem + 'x' + str(capi) + ' de la serie %s repetido' % Serie, True)
				continue
			# Entonces, falta, así que lo añadimos a la lista, pero hay que comprobar si hay más seguidos que faltan
			# y hay que ponernos un límite de 24 para no seguir hasta el infinito
			for x in range(capi + 1, 24):
				if not int(f[-2:]) == x:
					saltados = saltados + tem + 'x{0:02d}, '.format(x)
				else:
					break
		capi = int(f[-2:])
	resumen = resumen + '{0:02d} '.format(capi)
	if len(saltados) > 0:
		resumen = resumen + '. Faltan= ' + saltados
		Log('Capítulos que faltan en ' + Serie + ': ' + saltados, True)
	return resumen
	
def ListaPelis(Ulti = 0, Ruta = env.HDG):
	""" Se encarga de generar la lista de películas de un disco en concreto para después poder procesarla
	y generar la página web correspondiente.
	El formato de la lista es peli:etiqueta_carpeta:comentario
	El formato del nombre es Etiqueta_carpeta
	Normalmente es llamado desde GuardaHD(Etiq) aunque se le puede llamar de manera independiente
	El fichero con la lista se almacena en env.PLANTILLAS
	Por defecto asume que el path a usar es la ruta donde se guardan las pelis env.HDG pero puede ser cambiado
	si lo invocamos con el parámetro Ruta='[...]/'
	"""
	# En caso de generar la lista de las últimas películas que hay en el servidor
	if int(Ulti):
		os.chdir(env.HD)
		pelis = ObtenLista(1)
		GeneraLista('HD_Ultimas', pelis)
	else:
		# Si no, partimos de que se trata de uno de los disco de almacenamiento
		# Obtenemos la etiqueta del disco montado en Ruta, por defecto env.HDG (le quitamos la '/' final)
		Etiq = Etiqueta(Ruta[:-1])
		carpetas = ['Pelis', 'Documentales', 'Vistas', 'Infantiles', 'Musica', 'Cortos', 'SD']
		for car in carpetas:
			# Si existe la carpeta, la revisamos
			print(car)
			if os.path.exists(Ruta + car + '/'):
				os.chdir(Ruta + car + '/')
				pelis = ObtenLista()
				GeneraLista(Etiq + '_' + car, pelis)
		# Guardamos el espacio libre en la unidad
		GuardaLibre(Ruta)
	return

def ListaSeries(Ruta=''):
	""" Se encarga de generar la lista de series de un disco en concreto para después poder procesarla
	y generar la página web correspondiente.
	El formato de la lista es serie:comentario:Capítulos
	El formato del nombre es Series_Etiqueta
	Normalmente es llamado desde GuardaSeries(Etiq) aunque se le puede llamar de manera independiente
	Si lo llamamos desde DOS, tenemos que obtener la etiqueta y sustituir la ruta por ella en parte del código
	El fichero con la lista se almacena en env.PLANTILLAS
	"""
	
	if env.SISTEMA == 'Windows':
		etiq = Etiqueta(Ruta)
		env.SERIESG = ''
	else:
		etiq = 'Series_' + Ruta
		
	if os.path.exists(env.SERIESG + Ruta + env.DIR + 'Series'):
		# Guardamos la carpeta donde estamos
		pop = os.getcwd()
		# Nos vamos a la carpeta raíz de las series
		os.chdir(env.SERIESG + Ruta + env.DIR + 'Series')
		# Obtenemos lalista de las series
		series = sorted(next(os.walk('.'))[1])
		GeneraLista(etiq, series, True)
		# Volvemos a la carpeta inicial
		os.chdir(pop)
	# Mostramos al final los capítulos que faltan
	os.system('cat ' + env.PLANTILLAS + etiq + '|grep Faltan')
	return
	
def Log(p1, imp = False, fallo = ''):
	"""Función para escribir en el log del sistema de multia
	"""
	escri = time.strftime('%d/%m/%Y %H:%M:%S') + ' ' + fallo + p1 + '\n'
	with open(env.LOG, 'a') as fichero:
		fichero.write(escri)
	if imp:
		print(escri)
	return

def ObtenLista(Ulti = 0):
	""" Mini función para obtener las películas de una carpeta determinada.
	"""
	import glob
	# Si estamos en el curro
	if env.SISTEMA == 'Windows':
		# Si últimas, solo las nuevas ordenadas por fecha, en caso contrario, ordenadas por nombre y sin el thumbs.db '/a-h'
		if Ulti:
			cuales = '/aa-h /o-d'
			pelis = list(filter(None,os.popen('dir /b *.mkv *.mp4 *.wmv *.avi' + cuales).read().split('\n')))
			return pelis
	# Generamos la lista teniendo en cuenta las distintas extensiones
	pelis = glob.glob('*.mkv') + glob.glob('*.wmv') + glob.glob('*.mp4') + glob.glob('*.avi')
	# La lista de las carpetas. Tenemos un problema cuando la carpeta está vacía, aunque desconozco el porqué.
	carpetas = next(os.walk('.'))[1]
	if len(carpetas) > 0:
		pelis.extend(carpetas)
	# Las ordenamos alfabéticamente
	if Ulti:
		pelis.sort(key=os.path.getmtime, reverse=True)
	else:
		pelis.sort()
	return pelis

def Para():
	""" Se encarga de imprimir los parámetros pasados a funciones.py para depurar algún posible error
	"""
	for f in (range(1,len(sys.argv))):
		print(str(f) + ': ' + sys.argv[f])

def Prueba(Capi):
	""" Para probar funciones que estamos desarrollando
	"""
	pp = Capitulo(Capi)
	print(pp.Existe())
	return

def Queda(Fichero, Destino):
	""" Función para comprobar, antes de copiar, si queda espacio suficiente en la carpeta de destino
	"""
	libre =  Libre(Destino, 'M')
	if (os.path.getsize(Fichero)/(1024 * 1024.0)) > libre:
		Log('No queda espacio en ' + Destino +' para ' + Fichero, True)
		return False
	return True

def ReiniciaDLNA():
	""" Función para reiniciar el MiniDLNA en caso de ficheros corruptos pero manteniendo los bookmarks de los ficheros exitentes
	También aprovecharemos para reiniciar el art_cache
	"""
	import sqlite3
	
	# Paramos servicio
	os.system('sudo service minidlna stop')
	# Eliminamos el art_cache
	os.system('sudo rm -r /mnt/e/.mini/art_cache')
	# Abrimos BD
	mini_db = sqlite3.connect('/mnt/e/.mini/files.db')
	# Creamos cursor
	mini_cursor = mini_db.cursor()
	# Obtenemos la lista de bookmarks activos
	mini_cursor.execute("SELECT path,sec FROM bookmarks INNER JOIN details ON bookmarks.id=details.id")
	# Guardamos esta tabla
	Marcadores = mini_cursor.fetchall()
	# Cerramos el cursor y la BD
	mini_cursor.close()
	mini_db.close()
	# Lanzamos el minidlna en modo restauración de la BD
	os.system('sudo minidlnad -R')
	# Ahora tenemos que esperar hasta que en el log indique que ha terminado la indexación
	mini_log = ''
	while not 'Finished parsing playlists' in mini_log:
		time.sleep(15)
		mini_log = os.system('tail -1 /mnt/e/.mini/minidlna.log').read()
	# Terminamos el proceso minidlna de reindexado
	#os.system('kill minidlnad')
	
	return True

def Renombra(Viejo, Nuevo):
	""" Función para renombrar los capítulos de una serie de manera que mantengan una nomenclatura homogénea
	"""
	import glob
	lista = glob.glob('*' + Viejo + '*')
	lista.sort()
	for f in lista:
		if Viejo in f:
			print('Cambiando ' + f + ' por ' + f.replace(Viejo, Nuevo))
			os.rename(f, f.replace(Viejo, Nuevo))
	if env.SISTEMA == 'Windows':
		os.system('dir "*' + Nuevo + '*"')
	else:
		os.system('ls "*' + Nuevo + '*"')
	return

def RenPeli(P1, P2):
	"""Se encarga de renombrar todos los ficheros relacionados con una película para el caso de que haya habido algún 
	problema con su nomenclatura
	P1 = Nombre erróneo
	P2 = Nombre correcto
	"""
	# Primero renombramos la película en la carpeta local
	Renombra(P1, P2)
	# Luego la carátula
	os.chdir(env.MM + 'caratulas')
	Renombra(P1, P2)
	# Y por último la información y la sheet
	os.chdir(env.MM + 'Msheets')
	Renombra(P1, P2)
	return

def RenSerie(P1, P2, Ruta = env.PASADOS, Todo = 0):
	"""Se encarga de renombrar todos los ficheros de una serie para el caso de que haya habido algún 
	problema con su nombreclatura
	P1 = Nombre erróneo de la serie
	P2 = Nombre correcto
	Ruta = Si no se especifica, asumimos que estamos en env.PASADOS. Tiene que contener el '/' final
	Todo = Si a uno, también renombramos los metadatos, carátula y Msheets
	"""
	import glob
	print(P1, P2, Todo, Ruta)
	# Primero comprobamos si existe la carpeta a renombrar
	if not os.path.exists(Ruta + P1):
		print('No encuentro ' + P1)
		return
	# Comprobamos si existe el destino o si queremos crearlo
	if not os.path.exists(Ruta + P2):
		if not input('¿Estás seguro de crear una nueva carpeta ' + P2 + ' (S=1, N=0)?'):
			return
		os.mkdir(Ruta + P2)
	# Vamos a la carpeta de la serie
	os.chdir(Ruta + P1)
	# Movemos los capítulos y el resto del contenido
	lista = glob.glob('*')
	lista.sort()
	print(lista)
	for f in lista:
		if P1 in f:
			print('Movemos ' + f + ' a ' + P2 + '/' + f.replace(P1, P2))
			os.rename(f, '../' + P2 + '/' + f.replace(P1, P2))
		else:
			print('Movemos ' + f + ' a ../' + P2 + '/' + f)
			os.rename(f, '../' + P2 + '/' + f)
	os.chdir(Ruta)
	# Eliminamos la carpeta erronea
	Log('Elimnamos ' + Ruta + P1, True)
	os.rmdir(Ruta + P1)
	# Si no se ha especificado 'Todo' salimos, en caso contrario, modificamos también los metadatos
	if not int(Todo):
		return
	# Luego la carátula
	os.chdir(env.MM + 'scaratulas')
	Renombra(P1, P2)
	# Y por último la información y la sheet
	os.chdir(env.MM + 'sMsheets')
	Renombra(P1, P2)
	return

def SubCanciones(p1):
	""" Se encarga de suprimir de un fichero de subtítulos todas las líneas de texto excepto las que pertenecen a canciones (#...#)
	Nos falta tratar las líneas mixtas, que contienen texto normal y letros de canciones
	"""
	import pysrt
	lista = pysrt.open(p1, encoding='iso-8859-1')
	f = 0
	# Optamos por un while True debido que a medida que borramos líneas la lista se va haciendo más pequeña, por lo que no nos vale
	# un range(0,len(lista)) y además, al borrar nos saltamos la siguiente si estamos en un bucle.
	# Con un contador, conseguimos no saltar nada y solo incrementar el contador cuando no borramos
	while True:
		# Si no contiene canción lo borramos
		if lista[f].text.find('#') < 0:
			print(lista[f].text)
			del lista[f]
			# Comprobamos que no nos hemos pasado del tamaño de la lista para evitar un 'index out of range'
			if len(lista) == f:
				break
			continue
		# Nos quedamos solo con la parte de canción, localizando el inicio y final
		ini = lista[f].text.find('#')
		fin = lista[f].text.find('#', ini+1)
		lista[f].text = lista[f].text[ini:fin+1]
		# Si no nos pasamos, incrementamos y seguimos con la siguiente
		if len(lista) > f + 1:
			f += 1
		else:
			break
	# Guardamos añadiendo el sufijo .for
	lista.save(p1[:-3] + 'for.srt', encoding='iso-8859-1')
	return
	
def Trailer(p1):
	""" Se encarga de extraer del fichero NFO de una peli la información necesaria para obtener la URL del trailer de la película
	"""
	import xml.etree.ElementTree as ET
	from xml.dom.minidom import parseString
	import xml
	import zipfile
	
	if not os.path.exists(env.TMP + 'NFO'):
		if os.path.exists(env.MM + 'Msheets/' + p1 + '.tgmd'):
			try:
				with zipfile.ZipFile(env.MM + 'Msheets/' + p1 + '.tgmd') as zip:
					zip.extract('NFO', path=env.TMP)
				if os.path.getsize(env.TMP + 'NFO') < 40:
					Log('Ha habido un problema procesando el trailer: ' + p1)
					os.remove(env.TMP + 'NFO')
					return ''
			except BadZipFile as e:
				Log('Ha habido un problema descomprimiendo el supuesto zip: ' + p1 + e.strerror, True)
				return ''
		else:
			Log('No encontramos el fichero NFO para ' + p1)
			return ''
	with open(env.TMP + 'NFO') as file:
		info = file.read()
	dom = parseString(info)
	try:
		xmlTrailer = dom.getElementsByTagName('trailer')[0].toxml()
	except ValueError as e:
		Log('No se ha encontrado el trailer: ' + p1 + e)
		os.remove(env.TMP + 'NFO')
		return ''
	except IndexError as e:
		Log('Ha habido un problem con el trailer: ' + p1 + ', ' + str(e))
		os.remove(env.TMP + 'NFO')
		return ''
	xmlTrailer = xmlTrailer.replace('<trailer>', '').replace('</trailer>', '')
	if xmlTrailer.startswith('http')==False:
		Log('Ha habido algún problema con ' + p1 + xmlTrailer, True, '[Error] ')
		os.remove(env.TMP + 'NFO')
		return ''
	#with open(env.TMP + p1 + '.tr', 'w') as file:
	#	info = file.write(xmlTrailer)
	os.remove(env.TMP + 'NFO')
	return xmlTrailer

def Traspasa(Copio = 1, Monta = 1):
	""" Se encarga de pasar lo bajado a Series al pendrive de mi hermano y a su correspondiente carpeta en pasados
	Copio si valor 1, se encarga de decirle si copia los ficheros al pen, en caso de 0 solo los procesa para ponerlos en pasados
	Monta si valor 1, desmonta el pen al acabar, en caso de 0 lo deja montado
	"""
	Copio = int(Copio)
	Monta = int(Monta)
	copiado = 0
	# Por si nos hemos despistado, montamos el pen-drive. Lo hacemos por etiqueta para así poder usar cualquiera
	if not os.path.exists(env.PENTEMP + 'Series'):
		os.system('sudo mount /dev/disk/by-label/Hector-HD64 /media')
	#Si no está montado el pendrive, salimos
	if not os.path.exists(env.PENTEMP + 'Series'):
		Log('No esta montado el pendrive', True)
		if Copio:
			exit(1)
	# Activamos el led verde para informar de que hemos empezado la copia
	os.system('/home/hector/bin/ledonoff cpu0')
	# Cargamos las series que conocemos actualmente para no confundir las mayúsculas y minúsculas
	os.chdir(env.MM + 'scaratulas')
	Series = next(os.walk('.'))[2]
	# Quitamos la extensión de la carátula
	Series = [f[0:-4] for f in Series]
	# Nos pasamos a la carpeta de las series
	os.chdir(env.SERIES)
	# Leemos los ficheros de la carpeta
	filenames = next(os.walk('.'))[2]
	# Mostramos la lista de ficheros a procesar
	for x in filenames:
		print(filenames.index(x) + 1, x)
	# Cogemos cada fichero de la lista, lo copiamos al Pen y luego lo movemos a su respectiva carpeta en pasados
	for f in filenames:
		Log('Procesamos y copiamos el fichero ' + f, True)
		capi = Capitulo(f)
		# Si es una serie lo procesamos, en caso contrario, lo mandamos al temp
		if capi.Ok:
			# Si no existe la carpeta de la serie, comprobamos mayúsculas y minúsculas y la creamos
			if not os.path.exists(env.PASADOS + capi.Serie):
				capi.Existe()
		if Copio:
			# Si no queda espacio en destino pasamos al siguiente
			if not Queda(capi.Todo, env.PENTEMP + 'Series'):
				continue
			try:
				shutil.copy(capi.Todo, env.PENTEMP + 'Series')
			except OSError as e:
				Log('Ha ocurrido un error en la copia' + e.strerror, True)
				continue
		# Si es una serie lo procesamos, en caso contrario, lo mandamos al temp
		if capi.Ok:
			# Como puede haber habido un error de may/min volvemos a chequear si existe la carpeta. Si no existe, la creamos
			if not os.path.exists(env.PASADOS + capi.Serie):
				os.mkdir(env.PASADOS + capi.Serie)
				Log('No existe la carpeta de la serie ' + capi.Serie + ', así que la creamos', True)
			# Si ya está en pasados movemos la vieja al TEMP y ponemos la nueva en su lugar
			if os.path.exists(env.PASADOS + capi.ConSerie):
				try:
					shutil.move(env.PASADOS + capi.ConSerie, env.TEMP)
					Log('Movemos capítulo viejo %s al TEMP' % capi.Todo, True)
				except OSError as e:
					Log('Ha ocurrido un error al mover el fichero %s al TEMP' % e, True)
					continue
			# Movemos la serie a su carpeta
			try:
				shutil.move(capi.Todo, env.PASADOS + capi.ConSerie)
				Log('Movemos el fichero a su carpeta')
			except shutil.Error as e:
				Log('Ha ocurrido un error al mover el fichero %s' % e, True, '[Error]')
				continue
			# Activamos el atributo u+x que equivale al de archivo de Windows. Así podemos controlar cuales son nuevos
			# para su posterior paso a los discos USB, tanto desde Windows como desde la misma Banana
			# Cambiamos los permisos a rwxrw-rw-
			os.chmod(env.PASADOS + capi.ConSerie, 0o766)
			copiado = 1
		else:
			# Si no es una serie lo pasamos a la carpeta otros
			Log('Como parece que no es una serie, lo movemos a otros')
			try:
				shutil.move(capi.Todo, env.TEMP)
			except OSError as e:
				Log('Ha ocurrido un error al mover el fichero %s' % e, True)
				continue
			# Cambiamos los permisos a rwxrw-rw-
			os.chmod(env.TEMP + capi.Todo, 0o766)
			copiado = 1
	# Por último, le decimos al amule que vuelva a cargar los compartidos para que se de cuenta 
	# que lo que antes estaba en Series ahora está en pasados y si se han creados nuevas carpetas
	if copiado:
		os.system("/home/hector/bin/compartidos")
	# Nos pasamos a la carpeta de las pelis
	os.chdir(env.HD)
	filenames = next(os.walk('.'))[2]
	for f in filenames:
		if (not os.access(f,os.X_OK) and not f[-4:]=='part' and not f[-3:]=='jpg'):
			f = Limpia(f)
			Log('Copiamos la peli ' + f, True)
			# Comprobamos si hay espacio suficiente
			if not Queda(f, env.PENTEMP + 'Pelis'):
				continue
			# Copiamos el fichero
			try:
				shutil.copy(f,env.PENTEMP + 'Pelis')
			except OSError as e:
				Log('Ha ocurrido un error al copiar el fichero al pen ' + e.strerror, True)
				continue
			except IOError as e:
				Log('Ha ocurrido un error al copiar el fichero al pen ' + e.strerror, True)
				continue
			# Obtenemos los atributos actuales
			per = os.stat(f)
			# Y le añadimos 'x' al usuario para marcarla como pasada al Pen. 
			# Con el '|' hacemos un OR entre los permisos actuales y el que le queremos añadir
			os.chmod(f, per.st_mode | stat.S_IXUSR)
			copiado = 1
	# Si hay películas nuevas, generamos la página de Últimas. CreaWeb se encarga de cambiar los permisos de los jpg
	if len(os.popen("find . -perm 744 -name '*.jpg'").read()) > 0:
		CreaWeb('Ultimas')
		# Y limpiamos la carpeta de .jpg innecesarios
		LimpiaHD()
	salta = 0
	# Desmontamos el pen porque cuando lo cogemos por la mañana no sabemos si se ha copiado algo o no a no ser que especifiquemos lo contrario
	if Monta:
		while True:
			if os.system('sudo umount /media') == 0:
				break
			else:
				time.sleep(5)
				salta += 1
				# Lo intentamos 5 veces, si no lo conseguimos, sacamos el error y terminamos
				if salta == 5:
					Log('Hubo un problema desmontando el Pen')
					break
	Log('Terminamos', True)
	# Apagamos el led verde para informar de que hemos terminado la copia
	os.system('/home/hector/bin/ledonoff none')
	return

if __name__ == "__main__":
	""" En caso de que se ejecute desde la línea de comando, llamamos a la función dada como parámetro 1
	"""
	#for f in (range(1,len(sys.argv))):
	#	print(str(f) + ': ' + sys.argv[f])
	if len(sys.argv) == 1:
		for f in dir():
			print(f)
	if len(sys.argv) >= 6:
		print(locals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
	elif len(sys.argv) == 5:
		print(locals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4]))
	elif len(sys.argv) == 4:
		print(locals()[sys.argv[1]](sys.argv[2], sys.argv[3]))
	elif len(sys.argv) == 3:
		print(locals()[sys.argv[1]](sys.argv[2]))
	elif len(sys.argv) == 2:
		print(locals()[sys.argv[1]]())
	#print(len(sys.argv), sys.argv[1:])
	exit(0)
