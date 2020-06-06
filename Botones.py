#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Inicialmente creada para detectar los Dash Buttons de Amazon y controlar la bomba de recirculación de agua caliente.
Al amazon elimnar estos boes y forzar su bloqueo de manera remota, solo se usa para detectar la conexión de los equipos de Dácil
y de cualquier otra MAC que queramos detectar y reflejar en el log.
Hay que lanzarla con privilegios para poder poner la red en modo promiscuo y detectar la MAC de los equipos
Se requiere de una segunda función, Boton_detecta, que es la que se dispara cuando se detecta una llamada ARP
"""

# Importamos la librería kamene que es la version de scapy con compatibilidad con Python3
from kamene.all import *
from funciones import Log
import sys, os
# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)

def Boton_detecta(pkt):
	""" Función para detectar cuando Dácil conecta alguno de sus aparatos
	"""
	# Para controlar a Dácil las MACs de sus equipos. Importante, las letras en minúsculas
	dacil = {'60:1d:91:fb:53:21':'Moto','ec:c4:0d:b6:77:21':'Switch','00:24:8d:d2:43:30':'Wolder','d8:3c:69:e8:71:40':'Wiko','9c:e6:35:b8:b5:c7':'3DS','7c:c7:09:1f:55:05':'Tablet'}
	if pkt[ARP].op == 1: #network request
		# Algunos dispositivos parecen lanzar varios mensajes, por lo que descartamos mensajes repetidos 
		# viendo si es repetido en la última línea del log
		if pkt[ARP].hwsrc in dacil:
			if os.system('tail -1 ' + env.LOG + '|grep ' + dacil.get(pkt[ARP].hwsrc)) > 0:
				Log(f'Dácil ha conectado {dacil.get(pkt[ARP].hwsrc)} a la wifi', Debug)
		# Para comprobar hacemos que genere un log de cada máquina que pida IP
		if Debug:
			Log(f'Se ha conectado la MAC {pkt[ARP].hwsrc}', Debug)
	return

if __name__ == "__main__":
	if len(sys.argv) == 2:
		Debug = True
	else:
		Debug = False
	# Lanzamos el bucle que se queda detectando las llamadas ARP. Este funcionará de manera ininterrumpida
	# Hay que lanzarlo con el arranque del equipo. 
	# Plantear su instalación en el router en vez de la mulita
	sniff(prn=Boton_detecta, filter="arp", store=0)
