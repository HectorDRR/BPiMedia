#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Función para detectar los Dash Buttons de Amazon y controlar la bomba de recirculación de agua caliente
Hay que lanzarla con privilegios para poder poner la red en modo promiscuo y detectar la MAC de los botones
Se requiere de una segunda función, Boton_detecta, que es la que se dispara cuando se detecta una llamada ARP
"""

# Importamos la librería kamene que es la version de scapy con compatibilidad con Python3
from kamene.all import *
from funciones import SonoffTH, Bomba, Log
import datetime, sys

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)
Debug = False
# Para no repetir botón en un corto periodo de tiempo o log de conexión de equipo de Dácil
ultimo = ['',datetime.datetime.now()]

def Boton_detecta(pkt):
	""" Función para poder realizar la llamada al control de la bomba una vez detectada la presencia de alguno de los botones.
	Ampliada posteriormente para detectar cuando Dácil conecta alguno de sus aparatos
	"""
	# Primero definimos las MAC de los botones que usamos. Primero Rexel, segundo Fairy
	MACs = {'50:f5:da:59:e4:f6':'Fuera','6c:56:97:ef:79:3b':'Mío'}
	# Para controlar a Dácil las MACs de sus equipos. Me falta la Switch y la ota tablet
	dacil = {'00:24:8d:d2:43:30':'Play','d8:3c:69:e8:71:40':'Wiko','9c:e6:35:b8:b5:c7':'3DS','7c:c7:09:1f:55:05':'Tablet'}
	if pkt[ARP].op == 1: #network request
		if pkt[ARP].hwsrc in MACs: # Si aparece un botón llamamos a la función que se encarga del control del funcionamiento de la bomba
			Log('Detectado botón: ' + MACs.get(pkt[ARP].hwsrc), Debug)
			Bomba()
		# Algunos dispositivos parecen lanzar varios mensajes, por lo que descartamos mensajes repetidos guardando MAC y hora y 
		# viendo si es repetido en los últimos 3 segundos
		elif (pkt[ARP].hwsrc in dacil and not pkt[ARP].hwsrc == ultimo[0] and ultimo[1] > datetime.datetime.now() - datetime.timedelta(seconds = 3)):
			Log('Dácil ha conectado ' + dacil.get(pkt[ARP].hwsrc) + ' a la wifi', Debug)
	return

if __name__ == "__main__":
	""" En caso de que se ejecute desde la línea de comando, llamamos a la función dada como parámetro 1
	"""
	if len(sys.argv) == 2:
		Bomba('Manual')
		exit(0)
	else:
		# Lanzamos el bucle que se queda detectando las llamadas ARP. Este funcionará de manera ininterrumpida
		# Hay que lanzarlo con el arranque del equipo. 
		# Plantear su instalación en el router en vez de la mulita
		sniff(prn=Boton_detecta, filter="arp", store=0)
