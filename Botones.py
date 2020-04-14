#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Inicialmente creada para detectar los Dash Buttons de Amazon y controlar la bomba de recirculación de agua caliente.
Al amazon elimnar estos boes y forzar su bloqueo de manera remota, solo se usa para detectar la conexión de los equipos de Dácil
y de cualquier otra MAC que queramos detectar y reflejar en el log.
Ampliamos su uso para incluir un cliente de MQTT para poder hacer que la placa no se active más cuando ya nos hayamos duchado los tres
o para volver a activarla

Hay que lanzarla con privilegios para poder poner la red en modo promiscuo y detectar la MAC de los equipos
Se requiere de una segunda función, Boton_detecta, que es la que se dispara cuando se detecta una llamada ARP
"""

# Importamos la librería kamene que es la version de scapy con compatibilidad con Python3
from kamene.all import *
from funciones import Log
import datetime, sys, os
import paho.mqtt.client as mqtt

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)

def Boton_detecta(pkt):
	""" Función para detectar cuando Dácil conecta alguno de sus aparatos
	"""
	# Para controlar a Dácil las MACs de sus equipos. Importante, las letras en minúsculas
	dacil = {'60:1d:91:fb:53:21':'Moto','ec:c4:0d:b6:77:21':'Switch','00:24:8d:d2:43:30':'Play','00:03:ab:d9:07:1b':'Wolder','d8:3c:69:e8:71:40':'Wiko','9c:e6:35:b8:b5:c7':'3DS','7c:c7:09:1f:55:05':'Tablet'}
	if pkt[ARP].op == 1: #network request
		# Algunos dispositivos parecen lanzar varios mensajes, por lo que descartamos mensajes repetidos 
		# viendo si es repetido en la última línea del log
		if pkt[ARP].hwsrc in dacil:
			if os.system('tail -1 ' + env.LOG + '|grep ' + dacil.get(pkt[ARP].hwsrc)) > 0:
				Log('Dácil ha conectado ' + dacil.get(pkt[ARP].hwsrc) + ' a la wifi', Debug)
		# Para comprobar hacemos que genere un log de cada máquina que pida IP
		if Debug:
			Log('Se ha conectado la MAC ' + pkt[ARP].hwsrc, Debug)
	return

def Leo_Boton(client, userdata, message):
	""" Esta función es llamada cada vez que llega un mensaje por MQTT del tópico al que nos hemos subscrito.
		Como solo esperamos un mensaje, solo procedemos a realizar la acción sin ningún control adicional
	"""
	#import json
	# Lo importamos en formato json
	#mensaje = json.loads(message.payload.decode("utf-8"))
	#if Debug:
		#Log('Debug, mensaje: ' + str(mensaje))
	# Llamamos a bin/bañados.sh que termina con el proceso de la placa, si está corriendo, crea el fichero '/tmp/TodosBañados' y para la placa
	if not os.path.exists('/tmp/TodosBañados'):
		Log('No se va a bañar nadie más, ' + str(os.system('/home/hector/bin/bañados.sh')))
		client.publish('stat/boton2/NOMAS','1')
	else:
		Log('Volvemos a activar la programación de la placa, ', os.remove('/tmp/TodosBañados'))
		client.publish('stat/boton2/NOMAS','0')
	return


if len(sys.argv) == 2:
	Debug = True
else:
	Debug = False
# Creo el cliente
client = mqtt.Client('Mulita')
# Conecto al broker
client.connect('192.168.1.8')
# Asigno la función que va a procesar los mensajes recibidos
client.on_message = Leo_Boton
# Lo despertamos de su letargo para que nos responda más rápido, ya que hemos observado que con el sleep activado tarda más tiempo
#client.publish('cmnd/' + Topico + '/SLEEP', '0')
# Me subscribo a los tópicos necesarios, Estado y Temperatura
client.subscribe('cmnd/boton2/NOMAS', 0)
# Comenzamos el bucle
client.loop_start()

# Lanzamos el bucle que se queda detectando las llamadas ARP. Este funcionará de manera ininterrumpida
# Hay que lanzarlo con el arranque del equipo. 
# Plantear su instalación en el router en vez de la mulita
sniff(prn=Boton_detecta, filter="arp", store=0)
