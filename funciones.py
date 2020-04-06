#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funciones.py Conjunto de macros para gestionar las descargas del emule, torrent, y la creación y mantenimiento de mi página web

En primer lugar, mantendremos una lista de las funciones implementadas, su función y los parámetros que soporta, estando entre [] aquellos 
que son opcionales
"""

import time, shutil, os, re, sys, stat

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)
# Aunque la lectura de los ficheros es rápida, creamos una variable global que contenga todas las series para
# no estarlas cargando cada vez que queremos comprobar un capítulo desde Capitulo.Existe()
Series = []

class Capitulo:
	""" Tratamiento de capítulos de series, teniendo en cuenta si se manipulan a través de FTP o localmente
	Dividimos el nombre en:
		Titulo: Solo el título del capítulo
		Serie: El nombre de la Serie
		Capi: El número del capítulo
		Doble: Si es un capítulo doble
		Temp: El número de la temporada
		Tipo: La extensión
		Todo: El nombre completo del fichero
		ConSerie: El nombre completo con el nombre de la Serie como prefijo para ponerlo en una carpeta Serie[\\,/]Todo
	"""
	def __init__(self, Todo, FTP = False):
		""" Inicializamos las variables y dividimos el nombre del capítulo en sus componentes
		"""
		self.Todo = Todo
		self.FTP = FTP
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
			# Obtenemos la temporada buscando la x después del título
			self.Temp = Todo[len(result[0])+1:Todo.find('x', len(result[0]))]
			# Si no tiene título buscamos el '.'. En caso contrario, buscamos el primer espacio
			if len(self.Titulo) == 0:
				buscar = '.'
			else:
				buscar = ' '
			self.Capi = Todo[Todo.find('x',len(result[0])+1)+1:Todo.find(buscar,len(result[0])+1)]
			# Si es un capítulo doble
			if len(self.Capi) > 2:
				self.Doble = True
			else:
				self.Doble = False
			self.Tipo = Todo[-3:]
			# Limpiamos el nombre del capítulo
			self.Limpia()
			self.ConSerie = self.Serie + env.DIR + self.Todo
		else:
			self.Ok = False
		# Para confirmar que los datos se están extrayendo correctamente 
		#print(self.__dict__)
		return

	def Existe(self, Debug = False):
		""" Para comprobar si la serie ya existe y procurar ponerle el mismo nombre que ya tiene o si no existe,
		crear su carpeta
		"""
		# Cargamos las series que conocemos actualmente para no confundir las mayúsculas y minúsculas
		# Lo hacemos usando una variable global para optimizar
		global Series
		Existe = False
		# Asignamos el destino a PASADOS
		destino = '/mnt/e/pasados/'
		# En caso de que aún no las hayamos cargado, cargamos las series, tanto de las que ya tienen carátulas como de las que
		# están en pasados pero que aún no hemos copiado o creado carátula
		if len(Series) == 0:
			if self.FTP:
				# Guardamos la carpeta actual
				anterior = self.FTP.pwd()
				self.FTP.cwd('/mnt/f/scaratulas/')
				Series = self.FTP.nlst()
				self.FTP.cwd(destino)
				SinCaratula = self.FTP.nlst()
				# Volvemos a la carpeta inicial
				self.FTP.cwd(anterior)
			else:
				Series = next(os.walk(env.MM + 'scaratulas'))[2]
				SinCaratula = next(os.walk(env.PASADOS))[2]
			# Quitamos la extensión de la carátula
			Series = [f[0:-4] for f in Series]
			# Para las nuevas que aún no tengamos carátulas y no se nos empiecen a copiar con distintos nombres
			Series += SinCaratula
		# Comprobamos que no ha habido un error con las minúsculas y mayúsculas
		if self.Serie in Series:
			Existe = True
			# Comprobamos que existe la carpeta en Pasados, ya que es posible que la Serie exista pero la carpeta no
			if self.FTP:
				actual = self.FTP.pwd()
				try:
					self.FTP.cwd(destino + self.Serie)
				except:
					Log('Creamos la carpeta ' + self.Serie + ' en remoto', Debug)
					self.FTP.mkd(destino + self.Serie)
				# Volvemos a nuestra carpeta
				self.FTP.cwd(actual)
		else:
			for s in Series:
				# Si el nombre en mayúsculas es igual, pero no lo es el original
				if s.upper() == self.Serie.upper() and not s == self.Serie:	
					# Renombramos el fichero original con el nombre que ha de tener
					# print('Nombre actual: ' + self.Serie, 'Nombre correcto: ' + s, 'Nombre a cambiar: ' + self.Todo.replace(self.Serie,s))
					if self.FTP:
						self.FTP.rename(self.Todo, self.Todo.replace(self.Serie,s))
					else:
						os.rename(self.Todo, self.Todo.replace(self.Serie,s))
					# Cambiamos también las variables
					self.Todo = self.Todo.replace(self.Serie,s)
					self.ConSerie = self.ConSerie.replace(self.Serie,s)
					self.Serie = s
					# Consideramos que la serie existe
					Existe = True
					break
		# Si llegamos hasta aquí es que no existe la carpeta ni hay un error en mayúsculas/minúsculas
		if not Existe:
			# Creamos la carpeta
			if self.FTP:
				try:
					self.FTP.mkd(destino + self.Serie)
				except:
					Log('Ha habido un error creando por FTP la carpeta ' + destino + self.Serie, True)
			else:
				os.mkdir(env.PASADOS + self.Serie)
			# La añadimos a la lista para no intentar volver a crearla
			Series.append(self.Serie)
		# Siempre devolvemos True porque de no existir, la creamos justo antes de retornar. Habrá que ver si en el futuro habrá que cambiarlo
		return True
		
	def Limpia(self):
		""" Limpiamos el nombre del capítulo para quitar lo incluido entre corchetes
		"""
		donde = self.Titulo.find('[')
		if (donde >= 0):
			#Si hay un espacio antes del corchete también lo eliminamos
			if self.Titulo[donde-1] == ' ':
				donde -= 1
			sinf = self.Serie + ' ' + self.Temp + 'x' + self.Capi + ' ' + self.Titulo[0:donde] + '.' + self.Tipo
			if not self.FTP:
				try:
					os.rename(self.Todo, sinf)
				except OSError as e:
					print('Ha ocurrido un error renombrando el fichero ' + sinf + ': ' + e.strerror)
			else:
				self.FTP.rename(self.Todo, sinf)
			self.Titulo = self.Titulo[0:donde]
			self.Todo = sinf
		return

	def Vemos(self):
		""" Si el capítulo está en la lista de series que estamos viendo
		"""
		#Leemos las series que estamos viendo para no borrarlas
		with open (env.SERIESVER) as file:
			ver = file.readlines()
		ver = [x[:-1] for x in ver]
		if self.Serie in ver:
			return True
		return False
	
	def Pasa(self, Donde = env.PASADOS):
		""" Se encarga de pasar o mover el capítulo a su carpeta correspondiente. Solo tenemos que pasarle la ruta raiz, 
		por defecto, asumimos env.PASADOS.
		Asumimos que se usará solo cuando vaya a la carpeta correspondiente con el nombre de la serie.
		En caso de guardarlo en disco externo (Donde = env.SERIESG) solo lo copiamos, no lo movemos y le cambiamos los permisos
		"""
		if Donde == env.SERIESG:
			quehacemos = 'mv'
		else:
			quehacemos = 'cp'
		# Si no existe la carpeta de la serie, comprobamos mayúsculas y minúsculas y la creamos
		if not os.path.exists(Donde + self.Serie):
			self.Existe()
		if not Queda(capi.Todo, Donde):
			if input('No queda espacio en ' + Donde) == 'n':
				return
		try:
			os.system(quehacemos + ' ' + self.Todo + ' ' + Donde + self.Serie + '/')
		except OSError as e:
			Log('Ha ocurrido un error al hacer ' + quehacemos + 'a ' + Donde + self.Serie + '/ ' + e.strerror, True)
			return
		# Si lo hemos copiado a los discos externos, lo marcamos
		if quehacemos == 'cp':
			os.chmod(self.Todo, 0o766)
		Log('Pasado (' + quehacemos + ') ' + self.Todo + ' a ' + Donde + self.Serie)

class SonoffTH:
	""" Para manipular los SonOff con sensor de temperatura
	"""
	#import paho.mqtt.client as mqtt
	# Definimos como constante, importándola de env., la temperatura mínima del agua hasta que encontremos la manera de hacer un cálculo 
	# aproximado de manera automática. Hemos visto que en invierno necesitamos un mínimo de 40º mientras que en verano, con el agua de 
	# base más caliente, 35 grados es suficiente.
	# Partimos de que en Octubre tenemos que empezar a subir la temperatura del agua y lo hacemos de grado en grado partiendo de 35º
	mes = time.localtime().tm_mon
	# A partir de Octubre sencillamente le restamos los 9 meses anteriores y tenemos 1 grado por cada mes hasta Diciembre
	if mes > 9:
		mes = mes - 9
	# A partir de Enero y hasta Mayo, aumentamos los 3º anteriores + 1
	else:
		if mes < 5 :
			mes = 3 + mes
		else:
			mes = 0
	# Y por ahora, asumimos que Junio va a estar calentito y que vamos a mantener la consigna mínima de 35º de Junio a Septiembre
	TMin = env.TEMPERATURA + mes
	def __init__(self, Topico, Debug = False):
		""" Inicializamos el objeto con el tópico que hemos asignado al SonOff
		"""
		# Por si queremos imprimir los mensajes
		self.Debug = Debug
		self.Topico = Topico
		# Creo el cliente
		#self.client = self.mqtt.Client(Topico)
		# Conecto al broker
		#self.client.connect('192.168.1.8')
		# Asigno la función que va a procesar los mensajes recibidos
		#self.client.on_message = self.SonOff_leo
		# Lo despertamos de su letargo para que nos responda más rápido, ya que hemos observado que con el sleep activado tarda más tiempo
		#self.client.publish('cmnd/' + self.Topico + '/SLEEP', '0')
		# Al cambiar el sleep, se reinicia, por lo que hay que darle un par de segundos para que vuelva a estar activos
		#time.sleep(15)
		# Me subscribo a los tópicos necesarios, Estado y Temperatura
		#self.client.subscribe([('stat/' + self.Topico + '/RESULT', 0), ('stat/' + self.Topico + '/STATUS10', 0)])
		# Comenzamos el bucle
		#self.client.loop_start()
		# Pedimos Temperatura
		if not Topico == 'bomba':
			self.LeeTemperatura()
		# Pedimos Estado
		self.LeeEstado()
	
	def Controla(self, Modo, TMax = env.TEMPERATURA, Tiempo = 0):
		""" Función encargada de controlar el SonOff de la placa a través de MQTT.
		Si Controla: 0 Paramos la placa
					 1 Activamos manualmente con opción de tiempo para desonexión automática
					 2 Estamos controlando la placa de manera automática
					 4 Nueva función de control automático de manera más segura, usando backlog para asegurarse de que no se queda nada conectado
		Partimos de una consigna de 40º mínimo y 43º máximo que hemnos visto es suficiente para bañarnos los 3
		TMax: Temperatura máxima a alcanzar cuando el control es automático
		TMin: Temperatura mínima para proceder con el control automático
		Tiempo: En segundos que queremos mantener la placa funcionando
		
		**Por seguridad, por si hubiera algún problema con la mulita o pérdida de conexió Wifi, procedemos a usar el comando
		'backlog' que nos permite agrupar varios comandos en una sola orden, de manera que siempre que activemos el SonOff
		también le mandaremos la orden de apagado con un delay en medio. De esta manera, aunque el programa o la conexión 
		fallen nos aseguramos de que el sonfoff se desactivará tras el tiempo de 'delay' enviado, que es un máximo de 6 minutos.
		
		Tiempo: Por ahora, solo lo aplicamos al control manual de encendido. Si es >0 damos la orden de encender 
		durante ese tiempo y después apagar.
		
		Pendiente elevar la temperatura mínima dependiendo de la época del año. Hemos visto que en verano con 35º es suficiente 
		para ducharnos los 3, pero en invierno, como el agua que entra en el depósito está mucho más fría, la caída de temperatura 
		es mucho mayor en menos tiempo, por lo que pasamos a subirlo a 40º. Tendremos que encontrar una referencia externa para poder 
		variar esa consigna de manera automática.
		"""
		# En caso de pasarlo desde línea de comando como string, lo pasamos a int. Si ya viene como int no pasa nada
		Modo = int(Modo)
		TMax = int(TMax)
		#TMin = int(TMin)
		Teimpo = int(Tiempo)
		if (Modo == 0 and self.LeeEstado() == 'ON'):
			# Paramos el SonOff
			#self.client.publish('cmnd/' + self.Topico + '/POWER', 'OFF')
			self.MandaCurl('Power Off')
			if self.Debug:
				print(self.Topico + ': Power Off ' + self.LeeEstado())
			Log('Desactivamos la ' + self.Topico + ' manualmente', self.Debug)
			return
		if (Modo == 1 and self.Estado == 'OF'):
			if Tiempo == 0:
				# Activamos el SonOff
				#self.client.publish('cmnd/' + self.Topico + '/POWER', 'ON')
				self.MandaCurl('Power On')
				if self.Debug:
					print(self.Topico + 'Power ON', 'Estado: ' + self.LeeEstado())
				Log('Activamos la ' + self.Topico + ' manualmente', self.Debug)
			else:
				# Activamos el SonOff por un tiempo determinado. El tiempo nos viene en segundos pero el SonOff lo recibe en ms
				#self.client.publish('cmnd/' + self.Topico + '/BACKLOG', 'POWER ON;DELAY ' + str(Tiempo * 10) + ';POWER OFF')
				self.MandaCurl('Backlog Power on;Delay ' + str(Tiempo) + '0;Power Off')
				if self.Debug:
					print(self.Topico + 'Backlog Power on;Delay ' + str(Tiempo) + '0;Power Off\nEstado: ' + self.LeeEstado())
				Log('Activamos la ' + self.Topico + ' manualmente durante ' + str(Tiempo) + ' segundos', self.Debug)
			return
		if Modo == 2:
			# Si la temperatura está por debajo de la requerida
			if self.LeeTemperatura() < self.TMin:
				# Si está desactivada, la activamos
				if self.Estado == 'OF':
					#self.client.publish('cmnd/' + self.Topico + '/POWER', 'ON')
					self.MandaCurl('Power On')
					Log('Activamos la ' + self.Topico, self.Debug)
			# Subimos la consigna ,en el caso de la placa, debido a que el sensor está demasiado cerca de la resistencia y la temperatura 
			# sube muy rápido y no refleja la real del agua
			if self.Temperatura > TMax:
				# Si está activada, la paramos
				if self.Estado == 'ON':
					#self.client.publish('cmnd/' + self.Topico + '/POWER', 'OFF')
					self.MandaCurl('Power Off')
					Log('Desactivamos la ' + self.Topico + '', self.Debug)
			return
		if Modo == 4:
			# Para ir desarrollando el control totalmente automatizado embebido en el objeto
			# Si la temperatura está por debajo de la requerida
			while self.LeeTemperatura() < self.TMin:
				# En caso de problema leyendo la temperatura
				if self.Temperatura == 0:
					Log('Hemos tenido problemas leyendo la Temperatura de la ' + self.Topico)
					return False
				# Calculamos el tiempo necesario para llegar a la temperatura deseada. Primero obtenemos los grados de diferencia
				temperatura = self.TMin - self.Temperatura
				# En base al tipo de instalación, definimos el coeficiente de tiempo por cada grado. Suprimimos el de la bomba puesto que lo ponemos un tiempo fijo
				#if self.Topico == 'bomba':
					# En el caso de la bomba, 12 segundos por grado
				#	grado = 12
				if self.Topico == 'placa':
					# En el caso de la placa, partiendo de 2 kW de resistencia y 200 l de depótiso obtenemos unos 7 minutos. 1º = 4.180 Julios x kg = 4.180 * 200 kg = 836.000 J / 2.000 W = 418 seg.
					grado = 418
				Tiempo = temperatura * grado
				# Solo podemos poner un delay de máximo 6 minutos, y la placa necesita 7 minutos por grado
				# Si está desactivada, la activamos
				if self.Estado == 'OF':
					Log('Activamos la ' + self.Topico + ' durante ' + str(Tiempo // 60) + ':' + '{:0>2d} '.format(Tiempo % 60) + 'partiendo de una temperatura de ' + str(self.Temperatura) + 'º para alcanzar los ' + str(self.TMin) + 'º', self.Debug)
					if Tiempo > 360:
						# En caso de tenerla que mantener más de 6 minutos encendida los hacemos en tramos de 6 minutos
						for f in range(0, Tiempo // 360, 1):
							#self.client.publish('cmnd/' + self.Topico + '/BACKLOG', 'POWER ON;DELAY 3600;POWER OFF')
							self.MandaCurl('BACKLOG POWER ON;DELAY 3600;POWER OFF')
							time.sleep(365)
							# Para ir monitorizando, vamos pasando al log la temperatura
							Log('Temperatura de la ' + self.Topico + ': ' + str(self.LeeTemperatura()) + 'º', self.Debug)
							#if self.Temperatura >= TMax:
							#	break
						# Y por último, la mantenemos encendida el tiempo restante no múltiplo de 6 minutos
						# Al delay el tiempo se le pasa en décimas de segundo, así que en vez de * 10 sencillamente le añadimos un 0
						#self.client.publish('cmnd/' + self.Topico + '/BACKLOG', 'POWER ON;DELAY ' + str(Tiempo % 360) + '0;POWER OFF')
						self.MandaCurl('BACKLOG POWER ON;DELAY ' + str(Tiempo % 360) + '0;POWER OFF')
						time.sleep(Tiempo % 360 + 2)
					else:
						#self.client.publish('cmnd/' + self.Topico + '/BACKLOG', 'POWER ON;DELAY ' + str(Tiempo) + '0;POWER OFF')
						self.MandaCurl('BACKLOG POWER ON;DELAY ' + str(Tiempo) + '0;POWER OFF')
						time.sleep(Tiempo + 2)
				# Esperamos un minuto para dar tiempo a que la temperatura en el sensor se estabilize
				time.sleep(60)
			Log('Terminamos el control de la ' + self.Topico + ' con una temperatura de ' + str(self.Temperatura) + 'º', self.Debug)
			# Por si la hemos conectado manualmente
			if self.Estado == 'ON':
				self.MandaCurl('POWER OFF')
		return True

	def LeeEstado(self):
		""" Esta función obtiene el estado del SonOff para saber si está encendido o apagado
		"""
		# Debido a que algunas veces la bomba no responde a tiempo y produce un error, intentamos primero hacerle ping a ver si 'despierta'
		cuantos = 0
		while cuantos < 3:
			if os.system('ping -c 2 ' + self.Topico) == 0:
				cuantos = 3
			else:
				cuantos += 1
		self.Estado = eval(self.MandaCurl('Power'))['POWER'][0:2]
		return self.Estado
	
	def SonOff_leo(self, client, userdata, message):
		""" Esta función es llamada desde SonOff para hacer las lecturas y procesar los mensajes suscritos de SonOff
		"""
		import json

		# Lo importamos en formato json
		self.mensaje = json.loads(message.payload.decode("utf-8"))
		if self.Debug:
			Log('Debug, self.mensaje: ' + str(self.mensaje))
		if 'StatusSNS' in self.mensaje:
			# Extraemos la temperatura
			self.Temperatura = int(self.mensaje["StatusSNS"]["DS18B20"]["Temperature"])
		elif 'POWER' in self.mensaje:
			# Extraemos el estado
			self.Estado = self.mensaje["POWER"][0:2]
		return

	def LeeTemperatura(self):
		""" Esta función obtiene la temperatura actual del sensor del SonOff.		
		"""
		self.Temperatura = round(eval(self.MandaCurl('Status 10'))['StatusSNS']['DS18B20']['Temperature'])
		return self.Temperatura

	def MandaCurl(self, Comando):
		#import pycurl
		#from io import BytesIO
		#buffer = BytesIO()
		#c = pycurl.Curl()
		#c.setopt(c.URL, 'http://' + self.Topico + '/cm?cmnd=' + Comando.replace(' ','%20'))
		#c.setopt(c.WRITEDATA, buffer)
		#c.perform()
		#c.close()
		#return buffer.getvalue().decode()
		# Debido a los problemas para istalar el PyCurl en el Odroid lo hacemos a través de una llamada al sistema
		Comando = Comando.replace(';','%3B')
		respuesta = os.popen('curl -s "http://' + self.Topico + '/cm?cmnd=' + Comando.replace(' ','%20')+'"').read()
		#Log('MandaCurl: ' + Comando, True)
		return respuesta
		
def BajaSeries(Batch = False, Debug = False):
	""" Se conecta por FTP a la mula para comprobar si hay nuevos capítulos de las series que tenemos
	en el curro y bajarse los que falten.
	Tenemos pendiente implementar control de capítulos sobreescritos por problemas
	Tenemos que tener en cuenta aquellas series que están enteras en el curro pero no en el servidor
	Y también aquellas que ya no están en el servidor
	Añadimos conexión por SSH para poder modificar permisos de manera parcial al no poder hacerlo a través de FTP
	Queda pendiente usar sftp también de manera que podamos eliminar totalmente el uso de FTP
	"""
	from ftplib import FTP
	import paramiko
	import claves
	# Para convertir a boleano el valor del parámetro
	Batch = (Batch == 'True')
	Debug = (Debug == 'True')
	# Abrimos la conexión por ssh
	#client = paramiko.SSHClient()
	#client.load_system_host_keys()
	#client.set_missing_host_key_policy(paramiko.WarningPolicy)
    #client.connect('hrr.no-ip.info', port = 2222, username = claves.FTPMulitaUser, password = claves.FTPMulitaPasswd)
	client = paramiko.Transport(('hrr.no-ip.info', 2222))
	client.connect(username = claves.FTPMulitaUser, password = claves.FTPMulitaPasswd)
	# Ahora realizamos la conexión al servidor FTP
	ftp = FTP()
	ftp.connect('hrr.no-ip.info', 2211)
	# Cambiamos encoding a utf8 para que se respeten los acentos
	ftp.encoding='utf-8'
	ftp.login(claves.FTPMulitaUser, claves.FTPMulitaPasswd)
	# Vamos a las Series
	os.chdir(env.PASADOS)
	ftp.cwd('/mnt/e/Series/')
	# Generamos la lista de series que hay
	os.system('dir /b /ad >ver.txt')
	lista = ftp.nlst()
	print(lista)
	#session = client.open_channel(kind='session')
	for f in lista:
		capi = Capitulo(f, ftp)
		# Si no es una serie o no está en la lista, la movemos a otros y pasamos al siguiente
		if not capi.Ok:
			destino = '/mnt/e/otros/'
			Log('Pasamos ' + f + ' a Otros', Debug)
			ftp.rename(f, destino + f)
			continue
		# Comprobamos si el nombre es correcto y creamos la carpeta en caso necesario
		capi.Existe()
		# Asignamos el destino a PASADOS
		destino = '/mnt/e/pasados/'
		# A partir de aquí hemos de usar capi.Todo por si el nombre ha cambiado
		# Si no es de las que seguimos en el curro
		if not capi.Vemos():
			# Cambiamos atributos para marcarla como bajada.
			#ftp.sendcmd('SITE CHMOD 766 ' + capi.Todo)
			session = client.open_channel(kind='session')
			session.exec_command('chmod u+x "Series/' + capi.Todo + '"')
			# Lo movemos a su carpeta
			Log('Movemos ' + capi.Todo + ' a su carpeta', Debug)
			try:
				ftp.rename(capi.Todo, destino + capi.Serie + '/' + capi.Todo)
			except:
				Log('Ha habido algún problema moviendo ' + capi.Todo + ' a ' + destino + capi.Serie + '/' + capi.Todo, Debug)
			continue
		# Si es de alguna serie que nos interesa
		# Lo descargamos en su carpeta si hay espacio
		if not Queda(capi.Todo, env.PASADOS, ftp):
			if Batch:
				Log('No queda espacio para bajar ' + f)
				continue
			else:
				if input('No queda espacio suficiente en ' + env.PASADOS[0:2] + ', limpia') == 'n':
					continue
		os.chdir(capi.Serie)
		with open(capi.Todo, 'wb') as file:
			Log('Descargamos ' + capi.Todo, True)
			if ftp.retrbinary('RETR ' + capi.Todo, file.write, 10240) == '226 Transfer complete.':
				# Cambiamos atributos para marcarla como bajada. Pendiente leerlos primero para solo cambiar el primero
				#ftp.sendcmd('SITE CHMOD 766 ' + capi.Todo)
				#session = client.open_channel(kind='session')
				session.exec_command('chmod u+x "Series/' + capi.Todo + '"')
				# Lo movemos a su carpeta
				Log('Lo movemos a ' + destino + capi.Serie + '/', Debug)
				ftp.rename(capi.Todo, destino + capi.Serie + '/' + capi.Todo)
		# Volvemos a la carpeta de pasados
		os.chdir('..')
	# Mandamos al amule a refrescar la ubicación de los ficheros compartidos
	session = client.open_channel(kind='session')
	session.exec_command('/home/hector/bin/compartidos')
	# Cerramos conexiones para que no haya timeouts al descargar las pelis
	session.close()
	client.close()
	Log('Salida del "compartidos":' + session.recv(2048).decode('ascii'))
	# Nos vamos a las Pelis
	os.chdir(env.HD)
	ftp.cwd('/mnt/e/HD')
	# Obtenemos la lista de películas pendientes de procesar
	listaremota = []
	ftp.retrlines('list *.mkv', callback=listaremota.append)
	lista = []
	# Pendiente bajar también las infantiles que no se hayan bajado. Revisar que permisos tienen y como cambiarlos
	for f in listaremota:
		if f[0:4] == '-rw-':
			# Partimos de buscar el primer espacio a partir del campo hora
			lista.append(f[f.find(' ',53)+1:])
	lista.sort()
	for f in lista:
		print(lista.index(f) + 1, f)
	# Empezamos a bajarnos las películas
	for f in lista:
		if not Queda(f, env.HD, ftp):
			if Batch:
				Log('No queda espacio para bajar ' + f)
				continue
			else:
				if input('No queda espacio suficiente en ' + env.HD[0:2] + ', limpia') == 'n':
						continue
		with open(f, 'wb') as file:
			Log('Descargamos ' + f, Debug)
			if ftp.retrbinary('RETR ' + f, file.write, 10240) == '226 Transfer complete.':
				# Cambiamos atributos para marcarla como bajada. Pendiente leerlos primero para solo cambiar el primero
				# ftp.sendcmd('SITE CHMOD 766 ' + f)
				#stdin, stdout, stderr = client.exec_command('chmod u+x HD/' + f)
				# Abrimos conexión al terminar cada peli puesto que algunas tardan demasiado y estaban causando timeouts
				client = paramiko.Transport(('hrr.no-ip.info', 2222))
				client.connect(username = claves.FTPMulitaUser, password = claves.FTPMulitaPasswd)
				session = client.open_channel(kind='session')
				session.exec_command('chmod u+x "HD/' + f + '"')
				session.close()
				client.close()
	Log('Hemos temrinado con las pelis  y cerramos')
	# Cerramos la conexión
	ftp.close()
	return

def Bomba(Debug = False):
	""" Desde aquí controlamos el funcionamiento de la bomba con el Basic sin sensor
	"""
	
	if type(Debug)==str:
		Debug = eval(Debug)
	# Creamos las instancias
	bomba = SonoffTH('bomba', Debug)
	# Si está en funcionamiento salimos
	if bomba.Estado == 'ON':
		Log('La bomba está conectada, así que no la activamos', Debug)
		return
	# Activamos la bomba durante env.TBOMBA segundos
	bomba.Controla(1, Tiempo = env.TBOMBA)
	time.sleep(env.TBOMBA + 1)
	if Debug:
		Log('El estado de la bomba después de' + str(env.TBOMBA) + ' segundos es ' + bomba.LeeEstado())
	placa = SonoffTH('placa', Debug)
	# Si el agua no está caliente, y no es de las 23 a las 6 horas, activamos la placa durante 6 minutos
	if (placa.Temperatura < placa.TMin and int(time.strftime('%H')) < 23 and int(time.strftime('%H')) > 5):
		placa.Controla(1, Tiempo = 360)
	return

def BombaConSensor(Debug = False):
	""" Desde aquí controlamos el funcionamiento de la bomba cuando tenemos sensor de temperatura. Como ahora no tenemos, simplificamos el proceso.
	"""
	import subprocess
	
	if type(Debug)==str:
		Debug = eval(Debug)
	# Diferencial de temperatura a alcanzar
	delta = 2
	# Creamos las instancias
	bomba = SonoffTH('bomba', Debug)
	# Si la temperatura actual es mayor de 25º es que ya ha estado en funcionamiento, así que salimos
	if bomba.Temperatura > 25:
		Log('La temperatura de la bomba es de ' + str(bomba.Temperatura) + 'º, así que no la activamos', Debug)
		return
	placa = SonoffTH('placa', Debug)
	# Pasamos el valor a una variable para poder finalizar el objeto
	tplaca = placa.Temperatura
	# Si el agua no está caliente, activamos la placa
	if (tplaca < placa.TMin and int(time.strftime('%H')) < 23 and int(time.strftime('%H')) > 6):
		# Temporalmente, creamos un subproceso para el tema de calentar el agua de la placa sin esperar para poder lanzar la bomba, que es lo que nos interesa. Y lo lanzamos el subproceso redirigiendo la salida y los errores a la misma variable
		sub = subprocess.Popen(['python3','/home/hector/bin/funciones.py Placa 4'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# Objetivo a alcanzar. En principio, 2 grados más que la actual
	temperatura = bomba.Temperatura + delta
	# Aplicamos el nuevo control automático embebido en la clase
	#bomba.Controla (4, TMax = 35)
	# Lo dejamos inutilizado hasta confirmar que el control embebido está funcionando correctamente
	# Volvemos a activarlo para hacer pruebas de calibración.
	while (bomba.Estado == 'OF' and bomba.Temperatura < temperatura):
		# Vamos comprobando la temperatura cada 10 segundos para un total de x segundos y después esperamos
		for f in range(0, 6):
			# Activamos la bomba durante x segundos y esperamos 60 más para que llegue el calor al sensor
			bomba.Controla(1, temperatura, 0, 10)
			time.sleep(10)
			if bomba.LeeTemperatura() >= temperatura:
				break
		# Después de haber activado la bomba durante x segundos en tramos de 10, esperamos a ver si la temperatura sube
		for g in range(0, 6):
			time.sleep(10)
			if bomba.LeeTemperatura() >= temperatura:
				break			
	Log('Despues de ' + str(f*10 + g*10) + ' segundos la temperatura es de ' + str(bomba.Temperatura) + 'º y al comenzar era de ' + str(temperatura -delta) + 'º', True)
	time.sleep(150)
	Log('Después de 150 segundos más la temperatura es de ' + str(bomba.LeeTemperatura()) + 'º')
	return

def Borra(Liberar = 30, Dias = 20, Auto = 0):
	"""Se encarga de liberar espacio eliminando los ficheros más viejos que hay en las series sin
	contar los que están en las series que vemos (env.SERIESVER) Por defecto, liberará 20 GB.
	Añadimos un parámetro Auto para poder lanzarlo de manera automática desde Discolleno cuando 
	el emule detecta que no hay espacio, de manera que no pregunta nada.
	"""
	Log('Vamos a proceder a eliminar ficheros viejos de pasados')
	# Sacamos la lista de ficheros con mas de 30 días de antiguedad y que los permisos 
	# indican que ya ha sido copiado a disco externo
	os.chdir(env.PASADOS)
	salida = os.popen('find . -type f -mtime +' + str(Dias) + ' -perm -u+rw ! -iname "*.jpg"|sort').read()
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
	#Quitamos las series que estamos viendo. Añadimos el .upper() por si ha camabiado la mayúscula/minúscula en algún momento
	for l in lista:
		No = 0
		for v in ver:
			if v.upper() == l[0:l.find('/')].upper():
				No = 1
				break
		if not No:
			borrar.append(l)
	libre = Borra2(borrar, Liberar)
	# Si no hemos conseguido liberar el espacio solicitado pasamos a las series ya vistas
	if (Liberar > libre and Auto == 0):
		BorraVistos(Liberar)
	else:
		os.system("/home/hector/bin/compartidos")
	# Eliminamos las carpetas sin serie
	if Auto == 0:
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
				que = input('¿Borramos ' + f + '? (N)o / (T)odos: ').upper() 
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
	""" Se encarga de hacer una lista con los ficheros que se han visto de 'pasados' para luego poder proceder a borrarlos.
		La TV Samsung modifica un campo bookmark para poder recordar por donde íbamos, que marca los segundos transcurridos desde el inicio
		o en caso de que se haya visto hasta el final, pone un 0 en dicho Bookmark. Esto nos crea un pequeño conflicto, ya que en algunas ocasiones
		empezamos a ver el siguiente capítulo al actual 'sin querer', y eso puede ocasionar que el bookmark se quede a 0 y la función asuma
		que ya se ha visto. No veo fácil solución, a parte de que en caso de que ocurra darle un poco para adelante de manera que nos aseguremos 
		que no se queda a 0
	"""
	# Obtenemos el listado de ficheros con bookmarks y con su duración
	Liberar = float(Liberar)
	lista = os.popen('sqlite3 /mnt/e/.mini/files.db "select path,sec,duration from bookmarks inner join details on bookmarks.id=details.id where path like \'/mnt/e/pasados/%\' order by path;"').read()
	lista = list(filter(None, lista.split('\n')))
	borrar = []
	# Hacemos un backup de los bookmarks
	with open(env.LOG[:-9] + 'Bookmarks.bak', 'w') as file:
		for f in lista:
			file.write(f + '\n')
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
		que = input('Procedemos? (N)o / Nº: ').upper()
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

def Clasifica(Carpeta = './'):
	""" Función para pasar las películas de los discos a carpetas organizadas alfabéticamente por la primera letra 
	ya que con discos tan grandes es un suplicio buscarlas con el WDTV.
	"""
	# Nos pasamos a la carpeta de destino
	os.chdir(Carpeta)
	# Cargamos la lista de ficheros
	filenames = next(os.walk('.'))[2]
	# La ordenamos alfabéticamente
	filenames.sort()
	letra = ''
	# Respasamos la lista y cada vez que encontramos una primera letra nueva creamos la carpeta y pasamos los ficheros con
	# esa letra a la carpeta
	for f in filenames:
		if not f[0] == letra:
			letra = f[0]
			if not os.path.exists(letra):
				os.mkdir(letra)
		os.rename(f, letra + env.DIR + f)
	return			

def Copia():
	"""Se encarga de realizar una copia del contenido de varias carpetas modificado desde ayer al ftp de Movelcan
		También lanza una macro, rcopias.sh, para usar el rclone y copiar el contenido al Google Drive
	"""
	from ftplib import FTP
	import claves
	
	# Designamos las carpetas que copiar
	rutas = ['/home/hector/bin', '/mnt/e/util', '/mnt/f', '/mnt/f/scripts', '/mnt/e/.mini']
	# Creamos la copia de los bookmarks del minidlna
	os.system('sqlite3 /mnt/e/.mini/files.db "select path,sec,duration from bookmarks inner join details on bookmarks.id=details.id where path like \'/mnt/e/pasados/%\' order by path;" >/mnt/e/.mini/Bookmarks.txt')
	# Abrimos la conexión FTP
	ftp = FTP()
	ftp.connect('files.000webhost.com', 21)
	# Cambiamos encoding a utf8 para que se respeten los acentos
	ftp.encoding='utf-8'
	ftp.login(claves.FTPMovelcanUser, claves.FTPMovelcanPasswd)
	ftp.cwd('Copias')
	for f in rutas:
		os.chdir(f)
		# Obtenemos le nombre de la carpeta que será el del zip
		carpeta = f[f.rfind('/') + 1:] + '.zip'
		# Generamos el zip en /tmp con los ficheros modificados en el último día
		os.system('find . -maxdepth 1 -type f -mtime -1 -exec zip /tmp/' + carpeta + ' {} \;')
		# Si hay algo que copiar lo subimos por FTP a la carpeta del día en curso
		if os.path.exists('/tmp/' + carpeta):
			ftp.cwd(time.strftime('%a'))
			with open('/tmp/' + carpeta, 'rb') as fichero:
				Log('Copia de ' + f + ': ' + ftp.storbinary('STOR ' + carpeta, fichero).replace('\n', '. '), True)
			ftp.cwd('..')
			# Una vez transferido, lo eliminamos. Falta hacer un chequeo para comprobar que se ha subido correctamente
			os.remove('/tmp/' + carpeta)
	ftp.close()
	# Lanzamos el rcopias.sh
	devuelve = os.system('/home/hector/bin/rcopias.sh >>/tmp/salcopias.txt')
	return devuelve

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
	
def CreaWeb(p1 = 'Ultimas', Pocas = 0, Debug = False):
	""" Se encarga de generar las distintas páginas web necesarios para la gestión de las películas y las series.
	El fichero html estará en env.PLANTILLAS con el mismo nombre que la plantilla.
	Se habilita una opción especial para cuando estamos en el curro que también anunciamos series
	El p1 será la plantilla a usar, por defecto, el más usado, Ultimas
	El Pocas habilita la manera antigua de presentar las carátulas. Útil para el curro y las Últimas sin índices y con las
	carátulas visibles
	Modificamos para tratar a partir de los discos de 8 TB las películas en carpetas por la inicial para poder manejarlas mejor desde el WDTV
	"""
	import codecs
	
	if type(Debug) == str:
		Debug = True
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
		#if not os.path.exists(env.TMP + p1):
		# Creamos el fichero con las pelis o series a incluir en la página
		if p1 == 'Todas':
			os.system('cat ' + env.PLANTILLAS + 'HD* >' + env.TMP + 'Todas')
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
				Log('Error al procesar el comentario en el byte ' + str(e.start) + ' del fichero: ' + p1, True)
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
		titulo = peli
		# Si es una peli, quitamos la extensión. Si es una carpeta, por ejemplo de un documental, no hacemos nada.
		if not ser == 's':
			if peli[-4] == '.':
				titulo = peli[:-4]
		# Chequeamos si hay carátula. Asumimos que si no hay carátula tampoco hay Msheet
		if Debug:
			print(env.MM + ser + 'caratulas/' + titulo + '.jpg')
		if os.path.exists(env.MM + ser + 'caratulas/' + titulo + '.jpg'):
			if Pocas:
				caratula = '><img src="' + url + ser + 'caratulas/' + titulo + '.jpg" \\'
			else:
				caratula = 'class="hover-lib" id="' + url + ser + 'caratulas/' + titulo + '.jpg" title="' + disco + ':' + comen + '" '
			termina = '</a>'
		else:
			cfaltan.append(peli)
		if Debug:
			print(caratula)
		# Chequeamos si hay Msheet
		if os.path.exists(env.MM + ser + 'Msheets/' + peli + '_sheet.jpg'):
			linpeli = '<a href="' + url + ser + 'Msheets/' + peli + '_sheet.jpg" target="_Sheet" title="' + disco + ':' + comen + '" ' + caratula + '>'
		elif caratula != '' :
			linpeli = '<a href="#" title="' + disco + ':' + comen + '">' + caratula + '></a>'
			mfaltan.append(peli)
		# Modificamos para no buscar el trailer en las series, ya que la mayoría no tienen y solo generamos basura en el log
		if ser != 's':
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

def Discolleno():
	"""Es lanzada cuando el emule detecta que queda 1 GB o menos libre.
	Se encargará de hacer una primera limpieza, y en caso de que no sea suficiente, mandar un mensaje avisando del problema
	"""
	#Si ya hemos mandado el mensaje e intentado limpiar en esta hora, ignoramos el proceso, puesto que el emule lo lanza cada minuto
	hora = time.strftime('%Y%m%d%H')
	if os.path.exists('/tmp/' + hora):
		return
	else:
		#Si hemos creado un fichero la hora antes, lo eliminamos
		if os.path.exists('/tmp/' + str(int(hora) -1 )):
			os.remove('/tmp/' + str(int(hora) -1 ))
	#Primero lanzamos la función de borrar de manera automática que debería de dejar 20 GB libres
	Borra(Auto = 1)
	libre = Libre('/mnt/e/')
	if libre > 5:
		return
	#Si no hemos alcanzado los 5 GB y no lo hemos hecho ya, mandamos un correo
	os.system('df -h /mnt/e | mutt -s "Disco de la PiMulita sin espacio" -c Hector.D.Rguez@gmail.com &>>/tmp/' + hora)
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

def FAApi(Serie, Mini = 0):
	""" Para obtener directamente desde filmaffinity la página y la carátula de las series y Miniseries
	"""
	# En caso de que haya más de una palabra tenemos que meter un '+' entre ellas
	pp = Serie
	if len(Serie.split()) > 1:
		pp = ''
		for f in Serie.split():
			pp = pp + f + '+'
		pp = pp[0:-1]
	# Primero obtenemos las posibles coincidencias, ya que la búsqueda no permite 'ands'
	lista = eval(MandaCurl('https://api-filmaffinity.herokuapp.com/api/busqueda/' + pp))
	pagina = ''
	imagen = ''
	#Mini = eval(Mini)
	# En caso de que sea una Miniserie tenemos que cambiar la búsqueda
	if Mini == 1:
		coletilla = 'MINI'
	else:
		coletilla = ''
	for f in lista:
		print(f['titulo'].upper(),Serie.upper())
		if f['titulo'].upper().startswith(Serie.upper() + ' (' + coletilla + 'SERIE DE TV)'):
			pagina = f['id'] + '.html'
			os.popen('wget -qO ' + env.TMP + 'FAApi ' + pagina)
			# Parece que el wget es asíncrono y no espera a terminar de sacar el fichero cuando se invoca, por lo que ponemos una pausa
			time.sleep(1)
			with open(env.TMP + 'FAApi') as file:
				for f in file:
					if f.startswith('<meta property="og:image"'):
						imagen = f.split()[2][9:-1]
			break
	if pagina == '':
		Log('No se ha encontrado la serie en FilmAffinity: ', True)
		print(lista)
	return pagina, imagen

def GeneraLista(Listado, Pelis, Serie = False, Debug = False):
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
				if env.SISTEMA == 'Windows':
					# Tenemos que cambiar el parámetro Listado[-2:] puesto que en windows no funciona
					pass
				capis = ':' + ListaCapitulos(f, Listado[-2:] + env.DIR + 'Series' + env.DIR, Debug)
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

def GuardaHD(Disco = 'HD-TB-8-1'):
	""" Se encarga de pasar las películas a los discos externos USB para su almacenamiento
		Empezaremos solo por las pelis por ser más sencillo su tratamiento. Tenemos que tener 
		montado el disco en la ruta anterior a la que señala la variable HDG (/mnt/HD)
		Como los discos ya tienen una gran capacidad (8 TB) las clasificamos en carpetas por la 
		primera letra para facilitar su búsqueda desde el WDTV y otros.
		El parámetro Etiq es el que se va a pasar a la función ListaPelis para almcenar la lista 
		actualizada de películas.
		Pasamos como parámetro la etiqueta del disco a montar
	"""
	if not (os.path.exists(env.HDG + 'Pelis') or os.path.exists(env.HDG + 'Infantiles')) and not Disco == '':
		# Si devuelve 0 (False) es que todo ha ido bien. Si es mayor que 0 (True)
		if os.system('sudo mount /dev/disk/by-label/' + Disco + ' /mnt/HD'):
			print('No podemos montar el disco ' + Disco + ' en /mnt/HD o no tiene una carpeta "Pelis"')
			return
	Log('Comenzamos la copia de pelis HD', True)
	# Nos vamos a la carpeta de las pelis
	os.chdir(env.HD)
	if os.path.exists(env.HDG + 'Pelis/'):
		GuardaPelis('Pelis', '6')
	# Empezamos con las Infantiles
	if os.path.exists(env.HDG + 'Infantiles/'):
		GuardaPelis('Infantiles', '4')
		CreaWeb('Infantiles')
	# Generamos la lista de películas del disco y la página web
	ListaPelis()
	CreaWeb('Todas')
	CreaWeb('Pelis')
	CreaWeb('Vistas')
	# Limpiamos las carátulas que hayan quedado en la carpeta env.HD
	LimpiaHD()
	Etiq = GuardaLibre(env.HDG)
	# Paramos el disco duro por si lo hemos dejado copiando. El parámetro -Sx establece en x*5 segundos el tiempo de inactividad antes de pararse
	os.system('sync &&cd &&sudo umount /mnt/HD &&sudo hdparm -y /dev/disk/by-label/HD-TB-8-1')
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
	# Obtenemos el espacio total
	total = Total(Ruta)
	# Obtenemos la etiqueta 
	Etiq = Etiqueta(Ruta[:-1])
	# Formamos la línea a escribir
	linea = '{:10} = '.format(Etiq) + '{:8,.2f} GB, '.format(libre) + '{:.2f} TB'.format(total)
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
		Como los discos ya tienen una gran capacidad (8 TB) las clasificamos en carpetas por la 
		primera letra para facilitar su búsqueda desde el WDTV y otros.
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
			if not os.path.exists(env.HDG + Cuales + env.DIR + peli[0]):
				os.mkdir(env.HDG + Cuales + env.DIR + peli[0])
			shutil.copy(peli, env.HDG + Cuales + env.DIR + peli[0])
			shutil.copy(peli[:-3] + 'jpg', env.HDG + Cuales + env.DIR + peli[0])
		except IOError as e:
			Log('Ha ocurrido un error copiando la película ' + peli + e.strerror, True)
			continue
		# Copiamos también la sheet
		try:
			shutil.copy('/mnt/f/Msheets/' + peli + '_sheet.jpg', env.HDG + Cuales + env.DIR + peli[0])
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
	if deb:
		deb = True
	lista = []
	cuantos = 0
	Log('Comenzamos la copia de las Series ' + Ruta, True)
	# Confirmamos que está montado el disco de destino, y si no, lo montamos usando el by-label por los problemas con el Stretch y el fstab
	while not os.path.exists(env.SERIESG + Ruta + '/Series/') and cuantos < 5:
			os.system('sudo mount /dev/disk/by-label/Series_' + Ruta[0] +'-' + Ruta[1] + ' ' + env.SERIESG + Ruta)
			time.sleep(1)
			cuantos += 1
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
			print('Y también a las copiadas: ' + env.SERIESG + Ruta + '/Series/' + serie)
		else:
			os.chmod(serie, 0o644)
			# También los cambiamos en el disco de destino para en el caso de recuperarlos para verlos no aparezcan como pendientes de copiar de nuevo
			os.chmod(env.SERIESG + Ruta + '/Series/' + serie, 0o644)
		# Log('Se ha copiado la serie ' + serie, True)
	Log('Hemos terminado de copiar las series', True)
	# Si no estamos depurando seguimos con el resto de procesos
	if not deb:
		GuardaLibre(env.SERIESG + Ruta + '/')
		ListaSeries(Ruta)
		CreaWeb('Series')
		# Desmontamos la unidad
		os.system('sync &&sudo umount /dev/disk/by-label/Series_' + Ruta[0] +'-' + Ruta[1])
		# Dormimos la unidad
		os.system('sudo hdparm -y /dev/disk/by-label/Series_' + Ruta[0] +'-' + Ruta[1])
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
		trailer = 'No hay trailer'
	if trailer == '':
		trailer = 'No hay trailer'
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
	""" Obtenemos el espacio libre en disco, por defecto, en GB
	"""
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
				libre = round(int(f.FreeSpace) / Tam, 3)
				break
	else:
		disco = os.statvfs(p1)
		libre = round((disco.f_frsize * disco.f_bavail) / Tam, 3)
	return libre

def Limpia(f):
	""" Se encarga de limpiar el nombre de los ficheros descargados para eliminar todo lo posterior al primer '['
	"""
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
			# Hacemos una lista con los ficheros a borrar por si hay además algún .tmp o .srt
			borra = glob.glob(f[:-3] + '*')
			for g in borra:
				print('Borramos ' + g)
				os.remove(g)
	# También eliminamos los posibles .tmp que se hayan quedado residuales del ThumbGen
	lista = glob.glob('*.tmp')
	if len(lista) > 0:
		for f in lista:
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

def LimpiaPuntos(Mascara, Parent = '('):
	""" Se encarga de limpiar el nombre de los ficheros descargados para eliminar '.' entre palabra y palabra y a partir del primer '(' o
	cadena pasada como segundo parámetro, para los casos donde no haya un paréntesis sinque la coletilla empiece de otra manera
	"""
	import glob
	# Cargamos la lista de ficheros que coinciden con la máscara
	sinparent = ''
	lista = glob.glob(Mascara)
	for f in lista:
		donde = f.find(Parent)
		if (donde >= 0 and (f[-3:] == 'avi' or f[-3:] == 'mkv' or f[-3:] == 'srt')):
			#Si hay un punto o espacio antes del paréntesis o principio de la coletilla también lo eliminamos
			if f[donde-1] == '.' or f[donde-1] == ' ':
				donde -= 1
			# Nos quedamos con lo que hay hasta justo antes del paréntesis o principio de la coletilla 
			sinparent = f[0:donde]
		else:
			# Si no, nos quedamos con todo menos la extensión, asumiendo que ésta es de solo 3 caracteres
			sinparent = f[:-4]
		# Cambiamos los '.' por ' ' y añadimos la extensión
		sinparent = sinparent.replace('.', ' ') + f[-4:]
		# Renombramos
		try:
			os.rename(f,sinparent)
		except OSError as e:
			print('Ha ocurrido un error renombrando el fichero ' + f + ': ' + e.strerror)
			return f
		print('Limpiamos el nombre del fichero %s a %s' % (f, sinparent))
	f = sinparent
	return f

def ListaCapitulos(Serie, Ruta, Debug = False):
	""" Se encarga de revisar los capítulos de una serie dada para sacar un resumen de los mismos y 
	detectar si faltan capítulos en alguna temporada o están repetidos.
	
	Para que esta función funcione correctamente será necesario asegurarse de que la nomenclatura de
	los capítulos es homogénea, y no tenemos mezcla de mayúsculas o minúsculas así como otras alteraciones
	
	Esta es una segunda versión usando el Objeto Capitulo que aún está pendiente de desarrollar correctamente.
	Nos quedamos con problemas para tratar los capítulos dobles, por ejemplo en Babylon Berlin que además se trata del primero
	"""
	import glob
	if env.SISTEMA == 'Windows':
		env.SERIESG = ''
	if Debug:
		Log('Empezamos con la lista de ' + Serie + ' en  ' + Ruta, Debug)
	os.chdir(env.SERIESG + Ruta + Serie)
	# Leemos todos los capítulos
	lista = glob.glob('*.avi')
	lista.extend(glob.glob('*.mkv'))
	lista.extend(glob.glob('*.mp4'))
	lista.sort()
	# Convertimos en objeto y lo metemos en una lista
	serie = []
	for f in lista:
		serie.append(Capitulo(f))
	# Ahora toca recorrer la lista separando temporadas, quedándonos con el primer y último capítulo
	# y también informar si nos saltamos alguno
	# cogemos la información de la primera temporada y el primer capítulo almacenado
	tem = serie[0].Temp
	# Metemos en una lista los números de las temporadas y los capítulos para mostrarlos en pantalla y poder depurar
	lista = serie[0].Serie + ': '
	for f in serie:
		lista = lista + f.Temp + 'x' + f.Capi + ', '
	print(lista[:-2])
	# Guardamos el primer capítulo teniendo en cuenta si es doble
	if serie[0].Doble:
		capi = serie[0].Capi[0:2]
	else:
		capi = serie[0].Capi
	resumen = tem + 'x' + capi + '-'
	# Lo convertimos a entero para usarlo en el bucle. Le restamos 1 por si la serie empieza en 0 (Piloto) para que en el bucle funcione correctamente
	capi = int(capi) - 1
	saltados = ''
	repetidos = ''
	for f in serie:
		# Si hemos cambiado de temporada
		if not tem == f.Temp:
			if f.Doble:
				tcapi = f.Capi[0:2]
			else:
				tcapi = f.Capi
			# Ponemos en el resumen el capítulo final de la temporada anterior y el primero de la actual
			resumen = resumen + '{0:02d}'.format(capi) + ', ' + f.Temp + 'x' + tcapi + '-'
			tem = f.Temp
			capi = int(tcapi)
			# Saltamos al siguiente
			continue
		# Chequeamos si es un capítulo doble y nos quedamos con el último y cambiamos doble a 2 para la suma siguiente en el chequeo de si nos falta un capítulo
		if f.Doble:
			if Debug:
				print(f.Todo)
			tcapi = int(f.Capi[-2:])
			doble = int(f.Capi[-2:]) - int(f.Capi[0:2]) + 1
		else:
			tcapi = int(f.Capi)
			doble = 1
		# Si nos hemos saltado un capítulo
		if not tcapi == capi + doble:
			# Si está repetido
			if tcapi == capi:
				#Log('Capítulo ' + tem + 'x{:02}'.format(capi) + ' de la serie %s repetido' % Serie, True)
				repetidos = repetidos + tem + 'x{:02}, '.format(capi)
				continue
			# Entonces, falta, así que lo añadimos a la lista, pero hay que comprobar si hay más seguidos que faltan
			# y hay que ponernos un límite de 24 para no seguir hasta el infinito
			for x in range(capi + 1, 24):
				if not tcapi == x:
					saltados = saltados + tem + 'x{0:02d}, '.format(x)
				else:
					break
		capi = tcapi
	resumen = resumen + '{0:02d}'.format(capi)
	if len(saltados) > 1:
		resumen = resumen + '. Faltan = ' + saltados[:-2]
		Log('Capítulos que faltan en ' + Serie + ': ' + saltados, True)
	if len(repetidos) > 1:
		resumen = resumen + '. Repetidos = ' + repetidos[:-2]
		Log('Capítulos repetidos en ' + Serie + ': ' + repetidos, True)
	return resumen

def ListaCapitulos2(Serie, Ruta):
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
	lista.extend(glob.glob('*.mp4'))
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

def ListaSeries(Ruta='', Debug = False):
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
	if type(Debug) == str:
		Debug = eval(Debug)
	if os.path.exists(env.SERIESG + Ruta + env.DIR + 'Series'):
		# Guardamos la carpeta donde estamos
		pop = os.getcwd()
		# Nos vamos a la carpeta raíz de las series
		os.chdir(env.SERIESG + Ruta + env.DIR + 'Series')
		# Obtenemos la lista de las series
		series = sorted(next(os.walk('.'))[1])
		GeneraLista(etiq, series, True, Debug)
		# Volvemos a la carpeta inicial
		os.chdir(pop)
	# Mostramos al final los capítulos que faltan
	os.system('grep Faltan ' + env.PLANTILLAS + etiq)
	return
	
def Log(p1, imp = False, fallo = ''):
	"""Función para escribir en el log del sistema de mulita
	p1 es el mensaje a escribir
	imp si es verdadero lo imprimimos en panatala además de ponerlo en el log
	fallo mostraría la rutina que dio origen al mensaje. Faltaría automatizarlo.
	"""
	escri = time.strftime('%d/%m/%Y %H:%M:%S') + ' ' + fallo + p1 + '\n'
	with open(env.LOG, 'a', encoding='utf-8') as fichero:
		fichero.write(escri)
	if imp:
		print(escri)
	return

def MandaCurl(URL):
	#import pycurl
	#from io import BytesIO
	#buffer = BytesIO()
	#c = pycurl.Curl()
	#c.setopt(c.URL, URL)
	#c.setopt(c.WRITEDATA, buffer)
	#c.perform()
	#c.close()
	#return buffer.getvalue().decode()
	respuesta = os.popen('curl -s ' + URL).read()
	return respuesta
	
def ObtenLista(Ulti = 0, Debug = 0):
	""" Mini función para obtener las películas de una carpeta determinada.
		Ahora tenemos que tener en cuenta que a partir de los discos de 8 TB las pelis las guardamos en carpetas por iniciales
	"""
	import glob
	# Si estamos en el curro
	if env.SISTEMA == 'Windows':
		# Si últimas, solo las nuevas ordenadas por fecha, en caso contrario, ordenadas por nombre y sin el thumbs.db '/a-h'
		if int(Ulti) > 0:
			cuales = '/aa-h /o-d'
			pelis = list(filter(None,os.popen('dir /b *.mkv *.mp4 *.wmv *.avi' + cuales).read().split('\n')))
			return pelis
	# Buscamos en el interior de cada carpeta
	pelis = []
	folders = next(os.walk('.'))[1]
	# En el curro hay que tener en cuenta que si hay al menos una carpeta no hará la lista del resto de pelis
	if len(folders) > 0:
		for f in folders:
			# Nos pasamos a la carpeta si hay subcarpetas. De lo contrario procesamos lo que hay en la actual
			os.chdir(f)
			# Generamos la lista teniendo en cuenta las distintas extensiones
			pelis += glob.glob('*.mkv') + glob.glob('*.wmv') + glob.glob('*.mp4') + glob.glob('*.avi')
			# La lista de las carpetas. Tenemos un problema cuando la carpeta está vacía, aunque desconozco el porqué.
			carpetas = next(os.walk('.'))[1]
			if len(carpetas) > 0:
				pelis.extend(carpetas)
			# Volvemos a la carpeta padre
			os.chdir('..')
	else:
		pelis += glob.glob('*.mkv') + glob.glob('*.wmv') + glob.glob('*.mp4') + glob.glob('*.avi')
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

def PasaaBD(Fichero = '/var/log/placa.log', Debug = False):
	""" Esta función pasa a una Base de Datos en sqlite3 la información de la placa solar y la bomba obtenida a través del MQTT
	y volcada en /var/log/placa.log. Una vez renombramos el fichero, pasamos los datos, y los archivamos en un zip.
	"""
	import sqlite3, datetime
	
	if type(Debug) == str:
		Debug = eval(Debug)
	# Confirmamos que existe el fichero placa.log
	if not os.path.exists(Fichero):
		Log('No hay nada que importar de la placa')
		return
	# Nos vamos a la carpeta donde almacenaremos los logs
	os.chdir('/mnt/e/.mini/')
	esotro = False
	con = sqlite3.connect('placa.db')
	cursor = con.cursor()
	# Creamos las tablas sólo la primera vez
	# cursor.execute('''Create TABLE Placa (Fecha	Char(19)	Primary Key Not Null, Temperatura	Real	Not Null, Encendido	Int	Not Null)''')
	# cursor.execute('''Create TABLE Bomba (Fecha	Char(19)	Primary Key Not Null, Temperatura	Real	Not Null, Encendido	Int	Not Null)''')
	# Tomamos la hora del momento por si hay un cambio de minuto en medio de la operación, que ya nos pasó.
	hora = time.strftime('%H%M')
	if Fichero == '/var/log/placa.log':
		# Renombramos el log para no recibir más datos durante el proceso y cambiamos los permisos. Reiniciamos el rsyslog que si no se queda abobado y no recibe más logs
		os.system('sudo mv ' + Fichero + ' placa_' + hora + '.log && sudo chmod 777 placa_' + hora + '.log &&sudo service rsyslog restart')
		# Cambiamos la variable para que apunte al fichero renombrado
		Fichero = 'placa_' + hora + '.log'
	else:
		esotro = True
	# Cargamos los datos de la placa. Idealmente, deberíamos hacer la criba nosotros y no a través del grep. Modificamos el grep debido al que al quitarle el soporte de MQTT al Tasmota cambia la línea de log
	Datos = list(filter(None,os.popen("grep -E 'placa.*SENSOR|placa.*STATE' " + Fichero + ' --color=none').read().split('\n')))
	if Debug:
		print(Datos)
	Encendido = -1
	Temperatura = 0.0
	contador = 0
	#Log('Comenzamos la importación de datos de la Placa a la BD en sqlite3 con el primer dato: ' + Datos[0][0:15])
	for f in Datos:
		try:
			mensaje = eval(f[f.index('{'):])
		except:
			continue
		if 'DS18B20' in mensaje:
			Temperatura = float(mensaje['DS18B20']['Temperature'])
		if 'POWER' in mensaje:
			Fecha = mensaje['Time'].replace('T',' ')
			if mensaje['POWER'] == 'ON':
				Encendido = 1
			else:
				Encendido = 0
		# Si ya tenemos ambos datos, pasamos al siguiente
		if not Temperatura == 0 and not Encendido == -1:
			print(Fecha, Temperatura, Encendido)
			cursor.execute("INSERT INTO Placa (Fecha, Temperatura, Encendido) VALUES ('" + Fecha + "', " + str(Temperatura) + ", " + str(Encendido) + ")")
			Temperatura = 0
			Encendido = -1
			contador += 1
	con.commit()
	# Ahora procesamos los encendidos de la Bomba
	Datos = list(filter(None,os.popen("grep -E 'bomba.*POWER = ON' " + Fichero + ' --color=none').read().split('\n')))
	if Debug:
		print(Datos)
	Encendido = 1
	# Como actualmente no tenemos sensor en la Bomba dejamos el valor a 0
	Temperatura = 0
	#Log('Comenzamos la importación de datos de la bomba a la BD en sqlite3 con el primer dato: ' + Datos[0][0:15])
	for g in Datos:
		# Convertimos la fecha y hora. Tenemos que tener en cuenta el salto de año puesto que importamos a las 11. ***Pendiente***
		# Primero le añadimos el año
		Fecha = g[0:6] + ' ' + str(datetime.datetime.now().year) + ' ' + g[7:15]
		# Lo importamos a una fecha para sacarlo luego en el formato ISO 8601 de manera automática
		Fecha = datetime.datetime.strptime(Fecha, '%b %d %Y %H:%M:%S')
		print(Fecha, Temperatura, Encendido)
		cursor.execute("INSERT INTO Bomba (Fecha, Temperatura, Encendido) VALUES ('" + str(Fecha) + "', " + str(Temperatura) + ", " + str(Encendido) + ")")
		contador += 1
	con.close()
	# Añadimos el log horario al del día
	if not esotro:
		os.system('cat ' + Fichero + ' >> placa_' + time.strftime('%Y%m%d') + '.log && rm ' + Fichero)
	# Si es el último de la noche, lo movemos al zip de los logs 
	if time.strftime('%H%M') == '2330':
		os.system('zip -m logs.zip placa_' + time.strftime('%Y%m%d') + '.log')
		Log('Terminamos por hoy la importación de datos del log de la Placa a la BD con el ' + f[0:15] + '  y hemos importado ' + str(contador) + ' valores y comprimido el log')

def Placa(Quehacemos = 4, Tiempo = 0):
	""" Función encargada de controlar el SonOff de la placa a través de MQTT.
	Si Quehacemos: 0 Paramos la placa
				   1 Activamos la placa
				   4 Estamos controlando la placa de manera automática (Las consignas de temperatura están establecidas por defecto en la clase)
				   Otro solo consultamos temperatura
	En caso de solo querer apagarla vamos a prescindir del MQTT e ir directamente usando el curl
	"""
	# Cambiamos el tipo del parámetro por si lo hemos llamado desde línea de comando y nos llega como string
	Quehacemos = int(Quehacemos)
	# Si solo queremos apagar, mandamos el comando por curl y evitamos la inicialización de la clase
	if Quehacemos == 0:
		return MandaCurl('http://placa/cm?cmnd=Power%20Off')
	if Quehacemos == 4:
		# En caso de habernos bañado todos podemos crear un fichero en /tmp para que no se lance más. Comprobamos la existencia de dicho fichero
		# y en caso de que exista salimos, pero antes comprobamos si es la última activación en la noche (21:45) en ese caso, antes de salir, lo borramos
		if os.path.exists('/tmp/TodosBañados'):
			if (int(time.strftime('%H%M')) > 2144 or (int(time.strftime('%H%M')) > 755 and int(time.strftime('%H%M')) < 801)):
				os.remove('/tmp/TodosBañados')
				Log('Borramos TodosBañados')
			else:
				Log('Ya se han bañado todos así que no activamos placa')
			return
		# Comprobamos si está corriendo ya el control de la placa. En caso de que no lo esté solo devolverá 3 procesos: el bash que lanza el cron, el de Botones y el pgrep
		# Si lo está devuelve 4 en caso de que se haya lanzado por el cron, lo más habitual
		proceso = list(os.popen('pgrep -af Placa'))
		print(proceso)
		if len(proceso) > 3:
			Log('Ya está corriendo el proceso de control de la Placa, por lo que salimos')
			return
	# Creamos la instancia de la placa
	placa = SonoffTH('placa', True)
	if (placa.LeeTemperatura() >= placa.TMin and Quehacemos == 4):
		Log('La temperatura del agua está a ' + str(placa.Temperatura) + 'º y la consigna es de ' + str(placa.TMin) + 'º, por lo que no activamos la placa', True)
	else:
		# En caso de control sencillo, como ya está programado en la clase lo pasamos directamente
		placa.Controla(Quehacemos, Tiempo = Tiempo)
	return placa.Temperatura

def Prueba(Param, Debug = False):
	""" Para probar funciones que estamos desarrollando
		Procesado de los mensajes de la bomba
	"""
	print(type(Param)==str, int(Param))
	#print(pp.Temp, pp.Estado)
	return

def Queda(Fichero, Destino, FTP = False):
	""" Función para comprobar, antes de copiar, si queda espacio suficiente en la carpeta de destino
	"""
	libre =  Libre(Destino, 'M')
	if FTP:
		tamaño = FTP.size(Fichero)
	else:
		tamaño = os.path.getsize(Fichero)
	if (tamaño / (1024 * 1024.0)) > libre:
		Log('No queda espacio en ' + Destino +' para ' + Fichero + ', ' + str(tamaño), True)
		return False
	return True

def ReiniciaDLNA():
	""" *En OBRAS* Función para reiniciar el MiniDLNA en caso de ficheros corruptos pero manteniendo los bookmarks de los ficheros exitentes
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
	mini_cursor.execute("select path,sec,duration from bookmarks inner join details on bookmarks.id=details.id where path like '/mnt/e/pasados/%' order by path;")
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

def SacaSubs(P1, Pista = '3'):
	""" Función encargada de extraer los subtítulos forzados de un fichero mkv para poder verlos en la TV del Salón
	La creamos a raiz de series como Star Trek Discovery.
	Empezaremos por adaptarla solo a ésta, que los subtítulos siempre están en la pista 3 (0: vídeo, 1 y 2 audios)
	pero la idea es hacerla más genérica y que pueda detectar el flag de forzado de manera automática.
	"""
	
	error = os.system('mkvextract tracks "' + P1 + '" ' + Pista + ':"' + P1[:-3] + 'srt"')
	return error

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

def Temperatura(Cada = 1, Cual = 'Temperatura'):
	""" Se encarga de crear una gráfica con la temperatura del agua en la placa solar de la última semana y un fichero de texto
		con el tiempo que ha estado la placa activa en el mes en curso.
	"""
	import sqlite3, datetime
	# Importamos los últimos datos a la BD
	PasaaBD()
	# Cargamos los datos excluyendo los de la Bomba, por ahora
	bd = sqlite3.connect('/mnt/e/.mini/placa.db')
	cursor = bd.cursor()
	# Obtenemos la fecha de ayer para sacar los de las últimas 24 horas
	fecha = datetime.datetime.now()
	# Obtenemos cuantos minutos ha estado encedida la placa este mes
	activo = list(cursor.execute("select count(Encendido)*5 from placa where encendido=1 and fecha like '" + fecha.strftime('%Y-%m-%%') + "'"))[0][0]
	# Lo pasamos a horas y minutos
	activo = f'{activo // 60:02}:{activo % 60:02}'
	with open(env.WEB + 'Activo.txt', 'w') as file:
		file.writelines(activo)
	# Retrocedemos una semana
	fecha = fecha - datetime.timedelta(days = 7)
	# Añadimos el .fetchall() para pasar los datos como una lista y no seguir usando el cursor
	datos = cursor.execute("Select * From placa Where Fecha > '" + fecha.strftime('%Y-%m-%d %H:%M') + "'").fetchall()
	# Cerramos la base de datos
	bd.close()
	with open(env.WEB + Cual + '.csv', 'w') as file:
		# Escribo cabeceras
		file.writelines('Hora,Temperatura,Activo\n')
		for f in datos:
			# Para que funcione la gráfica correctamente, ponemos a '' cuando está apagada e igualamos a la temperatura 
			# cuando está encendida. De esta manera se superpone en la gráfica sobre la temperatura en rojo cuando está activa
			if f[2] == 1:
				acti = f[1]
			else:
				acti = ''
			file.writelines(f[0] + ',' + str(f[1]) + ',' + str(acti) + '\n')
	return

def Temperatura_Anual(Cual = 'TemperaturaA'):
	""" Se encarga de crear una gráfica con la temperatura mínima, media y máxima del agua a las 18:000 en la placa solar de
		cada mes del último año y también el timepo que ha estado encendida.
	"""
	import sqlite3, datetime, dateutil.relativedelta
	# Cargamos los datos excluyendo los de la Bomba, por ahora
	bd = sqlite3.connect('/mnt/e/.mini/placa.db')
	cursor = bd.cursor()
	# Obtenemos la fecha
	fecha = datetime.datetime.now()
	# Creamos la tabla que va a almacenar todos los valores, Min, Media, Max y Activo
	Valores = [[]]
	# Limpiamos para que no se nos quede el primer elemento vacío y podamos meterla en el bucle
	Valores.clear()
	# Hacemos bucle yendo desde hace 2 años hacia adelante, de manera que podremos comparar el mes pasado con el de hace un año
	for f in range(25,0,-1):
		# Retrocedemos en el tiempo
		EsteMes = fecha - dateutil.relativedelta.relativedelta(months = f)
		# Obtenemos la Tª mínima, media y máxima a las 18:0%
		Valores.append(list(cursor.execute("select  Min(Temperatura), Round(Avg(Temperatura),1), Max(Temperatura) from placa where fecha like '" + EsteMes.strftime('%Y-%m-__ 18:0%%') + "'"))[0])
		# Obtenemos cuantos minutos ha estado encedida la placa cada mes
		Valores[25-f] = Valores[25-f], list(cursor.execute("select count(Encendido)*5 from placa where encendido=1 and fecha like '" + EsteMes.strftime('%Y-%m-%%') + "'"))[0][0], EsteMes.strftime('%Y%m15')
	# Cerramos la base de datos
	bd.close()
	# Creamos el fichero de datos
	with open(env.WEB + Cual + '.csv', 'w') as file:
		# Escribo cabeceras
		file.writelines('Mes,Mínima,Media,Máxima,Horas_Activa\n')
		for f in Valores:
			file.writelines(str(f[2]) + ',' + str(f[0][0]) + ',' + str(f[0][1]) + ',' + str(f[0][2]) + ',' + str(round(f[1]/60,1)) + '\n')
	return

def Temperatura_CreaWeb(Datos, Cada = 2, Cual = 'Temperatura', Activo = 0):
	""" Separamos la parte encargada de generar la página web para poder llamarla varias veces de cara a crear las páginas 
	que necesitemos. Por ahora, solo hacemos la de las últimas 24h y la última hora, pero más adelante esperamos poder generarlas
	a petición desde la web.
	"""
	# Cargamos la plantilla
	with open(env.PLANTILLAS + 'Canvas.1') as file:
		planti = file.read().split('\n')
	planti[18] = ' ' * 28 + "xLabel: 'Cada " + str(int(Cada) * 5) + " minutos',"
	# Abrimos la pagina web
	with open(env.WEB + Cual + '.html', 'w') as file:
		# Copiamos las primeras líneas antes de los datos
		for f in range(0,25,1):
			file.writelines(planti[f] + '\n')
		# Pasamos el valor de los minutos que ha estado activa la placa este mes
		file.writelines(' ' * 28 + 'conectada: ' + str(Activo) + ',\n')
		# Escribimos el comienzo de los datos
		file.writelines(' ' * 28 + 'dataPoints: [')
		cont = 0
		escribir = []
		espacios = 40
		for f in Datos:
			# Para dejar el html bien identado
			if len(escribir) == 0:
				espacios = 0
			else:
				espacios = 40
			# Cogemos solo una de 'Cada' lecturas
			if cont == int(Cada):
				cont = 0
				escribir.append(' ' * espacios + "{ x: '" + f[0][11:16] + "', y: " + str(f[1]) +", z: " + str(f[2]) + " },\n")
			cont += 1
		escribir[len(escribir) - 1] = escribir[len(escribir) - 1][0:-2] + "]\n"
		# Pasamos los datos al html
		for f in escribir:
			file.writelines(f)
		for f in range(25,len(planti),1):
			file.writelines(planti[f] + '\n')

def Total(p1, Tam = 'T'):
	""" Devuelve el espacio total que hay en un disco determinado en TB
	"""
	if Tam == 'M':
		Tam = 1024 * 1024
	elif Tam == 'G':
		Tam = 1024 * 1024 * 1024
	elif Tam == 'T':
		Tam = 1024 * 1024 * 1024 * 1024

	if env.SISTEMA == 'Windows':
		import wmi
		sys = wmi.WMI()
		for f in sys.Win32_LogicalDisk():
			if f.Caption == p1[0:2].upper():
				total = round(int(f.Size) / Tam, 3)
				break
	else:
		disco = os.statvfs(p1)
		total = round((disco.f_blocks * disco.f_bsize) / Tam, 3)
	return total
	
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
			except zipfile.BadZipFile as e:
				Log('Ha habido un problema descomprimiendo el supuesto zip: ' + p1, True)
				return ''
		else:
			Log('No encontramos el fichero NFO para ' + p1)
			return ''
	with open(env.TMP + 'NFO', encoding="utf-8") as file:
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
	Añadimos la rutina para extraer subtítulos en caso de que sea una serie que viene en .mkv para poder verla en la TV
	"""
	Copio = int(Copio)
	Monta = int(Monta)
	copiado = 0
	# Por si nos hemos despistado, montamos el pen-drive. Lo hacemos por etiqueta para así poder usar cualquiera
	if Copio and not os.path.exists(env.PENTEMP + 'Series'):
		os.system('sudo mount /dev/disk/by-label/Hector-HD64 /media')
		#Si no está montado el pendrive, salimos
		if not os.path.exists(env.PENTEMP + 'Series'):
			Log('No esta montado el pendrive', True)
			return
	# Activamos el led verde para informar de que hemos empezado la copia
	os.system('/home/hector/bin/ledonoff heartbeat')
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
			# Chequeamos si es un mkv y pertenece a una serie que estamos viendo para extraer los subtítulos
			if capi.Tipo == 'mkv' and capi.Vemos():
				Log('Extraemos los subtítulos de ' + capi.Todo, True, 'Traspasa: ')
				SacaSubs(env.PASADOS + capi.ConSerie)
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
	#En caso de que solo procesemos lo que tenemos acumulado, prescindimos de procesar las pelis
	if Copio:
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
