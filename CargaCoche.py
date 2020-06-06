#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Para controlar la carga del coche en función de la batería que existe en 
	el sistema FV y también dependiendo del botón que haya sido apretado en 
	el SonOff Dual del garaje.
	Primer botón: Carga solamente de la FV dependiendo de un SOC mínimo
	Segundo botón: Carga de la FV y si no ha acabado, conmuta a la red 
				después de las 23 horas (pendiente de implementar)
"""

from funciones import Log
import claves
import datetime, sys, os, json, time
import paho.mqtt.client as mqtt

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)

class AccesoMQTT:
	""" Para acceder al Venus GX a través de MQTT de cara a gestionar la recarga del coche del sistema FV
	"""
	def __init__(self, debug = False):
		self.debug = debug
		# Creo el cliente
		self.client = mqtt.Client('Coche')
		# Conecto al broker
		self.client.connect('venus')
		# Asigno la función que va a procesar los mensajes recibidos
		self.client.on_message = self.leo
		# Me subscribo a los tópicos necesarios, el SOC de la batería y el estado del relé
		self.client.subscribe([('N/' + claves.VictronInterna + '/system/0/Dc/Battery/Soc', 0), ('stat/CargaCoche/STATUS', 0)])
		# Comenzamos el bucle
		self.client.loop_start()
		# Inicializamos la variable que servirá para que no me mande más de un mensaje a la hora
		self.hora = 0
		self.rele1 = False
		self.bateria = 0
		# Pedimos el primer valor
		self.pregunta()

	def leo(self, client, userdata, message):
		""" Esta función es llamada para hacer las lecturas y procesar los mensajes suscritos
		"""
		# Lo importamos en formato json
		self.mensaje = json.loads(message.payload.decode('utf-8'))
		if "Status" in self.mensaje:
			if self.mensaje["Status"]["Power"] == 1 or self.mensaje["Status"]["Power"] == 3:
				self.rele1 = True
			else:
				self.rele1 = False
		elif "value" in self.mensaje:
			self.bateria = self.mensaje['value']
		# Aquí deberíamos de comprobar si la batería está por debajo de un valor y estamos cargando el coche
		# Por ahora solo lo hacemos en horario diurno para probar su funcionamiento
		if self.debug:
			Log(self.mensaje, True, '/tmp/Bateria.log')
			print(f'Bateria al {self.bateria}%, Relé1 = {self.rele1}')

	def pregunta(self):
		""" Manda la petición por MQTT
		"""
		# Pedimos el SOC y el status del SonOff Dual
		self.client.publish('R/' + claves.VictronInterna + '/system/0/Dc/Battery/Soc', '')
		self.client.publish('cmnd/CargaCoche/STATUS', '')
		
	def controla(self):
		""" Controla el estado de la batería y del relé y activa o desactiva 
			en función de la hora y el % de SOC
		"""
		# Obtenemos los datos de estado
		self.pregunta()
		# Nos quedamos con la hora para no saturar de mensjaes en la misma hora
		hora = datetime.datetime.now().hour
		# Si está activo el relé, la batería está por debajo del 50% y son entre las 8 y las 23
		if self.rele1 and self.bateria <= 50 and hora > 8 and hora < 23:
			# Deberíamos de cortar la carga o pasar a la red, dependiendo de 
			# 	lo que hayamos pedido
			# Esto lo controlaremos más adelante usando los dos botones que 
			# 	nos ofrece el SonOff Dual para ponerlos externos, seguramente 
			#	en la carcasa del cuadro. Por ahora, solo cargamos de la FV
			self.client.publish('cmnd/CargaCoche/POWER1', 'OFF')
			Log(f'Desconectamos el coche al {self.bateria}%', self.debug, '/tmp/Bateria.log')
			# Enviamos un mail comunicando el apagado si no lo hemos enviado antes
			if not hora == self.hora:
				Log(f'Batería al {self.bateria}%, desconectamos y mandamos correo', self.debug, '/tmp/Bateria.log')
				os.system(f'echo Desconecta el coche |mutt -s "La batería 
							está al {self.bateria}%" Hector.D.Rguez@gmail.com')
				self.hora = hora
		# Si no está activo el relé y tenemos más de un 55% de batería, 
		if not self.rele1 and self.bateria > 55 and hora > 8 and hora < 23:
			# Volvemos a conectarlo
			self.client.publish('cmnd/CargaCoche/POWER1', 'ON')
			Log(f'Batería al {self.bateria}%, conectamos y mandamos correo', self.debug, '/tmp/Bateria.log')

if __name__ == "__main__":
	if len(sys.argv) == 2:
		debug = True
	else:
		debug = False
	# Inicializamos el objeto para acceder al MQTT
	victron = AccesoMQTT(debug)
	# Nos quedamos en bucle eterno controlando cada minuto
	while True:
		victron.controla()
		time.sleep(60)
