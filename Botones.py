#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Función para controlar los Dash Buttons de Amazon para activar la bomba de recirculación de agua caliente
"""

# Importamos la librería kamene que es la version de scapy con compatibilidad con Python3
from kamene.all import *
from funciones import SonoffTH, Bomba, Log
import time
import sys

# Definición de variables para hacer la macro portable entre distintas configuraciones/plataformas
env = __import__('Entorno_' + sys.platform)
# Ponemos a True si queremos impresión de mensajes de depuración
Debug = False

def Boton_Apretado(MAC):
	""" Desde aquí controlamos el funcionamiento de la bomba.
	Lo hemos pasado a funciones y lo importamos al principio por lo que aquí ya no tiene utilidad
	Lo dejamos temporalmente hasta confirmar que fucnionacorrectamente de esta nueva manera
	"""
	# Creamos las instancias
	bomba = SonoffTH('bomba')
	if bomba == False:
		return(False)
	# Si la temperatura actual es mayor de 30º es que ya ha estado en funcionamiento, así que salimos
	if bomba.Temperatura > 30:
		Log('La temperatura de la bomba es de ' + str(bomba.Temperatura) + 'º, así que no la activamos', Debug)
		del(bomba)
		return
	placa = SonoffTH('placa')
	if placa == False:
		return(False)
	# Si el agua no está caliente, activamos la placa. Hay que pasar este valor a la clase
	TMin = 40
	while placa.Temperatura < TMin:
		placa.Controla(2)
		# asumimos 3 minutos (180 segundos) por cada grado a subir para alcanzar la consigna
		tiempo = (TMin - int(placa.Temperatura)) * 180
		time.sleep(tiempo)
		# Desconectamos la placa
		placa.Controla(0)
		# Esperamos 5 minutos para que baje la temperatura del sensor
		time.sleep(300)
		# Leemos de nuevo la temperatura de la placa
		placa.LeeTemperatura
	# Activamos la depuración dentro del objeto
	#bomba.Debug = True
	# Objetivo a alcanzar. En principio, 3 grados más que la actual
	temperatura = bomba.Temperatura + 3
	# Aplicamos el nuevo control automático embebido en la clase
	#bomba.Controla (4, TMax = 35, TMin = 30)
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
	Log('Despues de ' + str(f*10 + g*10) + ' segundos la temperatura es de ' + str(bomba.Temperatura) + 'º y al comenzar era de ' + str(temperatura -5) + 'º', True)
	time.sleep(150)
	Log('Después de 150 segundos más la temperatura es de ' + str(bomba.LeeTemperatura()) + 'º')
	if False:
		# Comprobamos si está desactivada la bomba y que la temperatura es menor del objetivo
		while (not bomba.Estado == 'ON' and bomba.LeeTemperatura() < temperatura):
			# Calculamos el tiempo de funcionamiento en base al diferencial de temperatura. Como lo establecemos en 5º vamos a poner 12 segundos por º
			tiempo = (temperatura - bomba.Temperatura) * 12
			# La activamos durante el tiempo necesario. No es necesaria la temperatura mínima, que es el segundo parámetro, puesto que lo controlamos manualmente
			Log('Activamos bomba con una temperatura de ' + str(bomba.Temperatura) + ' durante ' + str(tiempo) + ' segundos', Debug)
			bomba.Controla(1, temperatura, 0, tiempo)
			# Debido a la inercia térmica, esperamos un minuto adicional antes de volver a leer la temperatura para dar tiempo a que el calor llegue al sensor
			time.sleep(tiempo + 60)
			# La paramos. Ya no es necesario al implementar el parámetro de tiempo con el backlog en la llamada al SonOff
			# Log('Paramos la bomba ' + str(tiempo) + ' segundos después y esperamos 60 segundos para volver a medir la temperatura', Debug)
			# bomba.Controla(0)
		else:
			# Si está activa la paramos
			Log('Paramos la bomba. Temp. Inicial: ' + str(temperatura - 5) + 'º y la temperatura final es de ' + str(bomba.Temperatura) + 'º', Debug)
			if bomba.Estado == 'ON':
				bomba.Controla(0)
		time.sleep(300)
		Log('Temperatura de la bomba 5 minutos después: ' + str(bomba.LeeTemperatura()) + 'º', Debug)
	# Finalizamos los objetos
	bomba.Fin()
	placa.Fin()
	return

def Boton_detecta(pkt):
	""" Función anexa a Boton para poder realizar el control una vez detectada la presencia de alguno de los botones.
		La idea es que cuando se pulsa un botón se comprueba la temperatura en la entrada de la bomba. Si esta es inferior
		a 30º ponemos en funcionamiento la bomba durante un minuto y volvemos a comprobar la temperatura.
		En caso de haber llegado a la consigna, paramos la bomba.
		Tenemos que preveer la posible acción de ambos botones o de repetir botón antes de haber terminado la acción del 
		primero, por lo que lo primero será comprobar si la bomba ya está en funcionamiento.
	"""
	# Primero definimos las MAC de los botones que usamos. Como la función de ambos botones va a ser la misma,
	# no diferenciaremos entre un botón y otro y las meteremos en una lista. Primero Rexel, segundo Fairy
	MACs = ['50:f5:da:59:e4:f6','6c:56:97:ef:79:3b']
	if pkt[ARP].op == 1: #network request
		if pkt[ARP].hwsrc in MACs: # Si aparece un botón llamamos a la función que se encarga del control del funcionamiento de la bomba
			Log('Detectado botón: ' + pkt[ARP].hwsrc, Debug)
			Bomba()
	return

""" Función para detectar los Dash Buttons de Amazon y controlar la bomba de recirculación de agua caliente
Hay que lanzarla con privilegios para poder poner la red en modo promiscuo y detectar la MAC de los botones
Se requiere de una segunda función, Boton_detecta, que es la que se dispara cuando se detecta una llamada ARP
"""
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
