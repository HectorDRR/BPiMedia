# -*- coding: utf-8 -*-
""" Programa para hacer un salvapantallas en una sola pantalla en Windows para que a Dácil se le apague la pantalla del Youtube
	Tenemos en cuenta tanto el ratón como la ventana que está activa.
"""
import win32gui, time, sys, os
# Vamos a poner un tiempo por defecto de minuto y medio
if len(sys.argv) == 2:
	Timeout = int(sys.argv[1])
else:
	Timeout = 90
# Si hay un segundo parámetro asumimos que estamos en modo debug
if len(sys.argv) > 2:
	Debug = True
else:
	Debug = False
# Cogemos el segundo actual
ultimo = int(time.time())
# Asumimos que el monitor está activado en este momento
encendido = True
atenuado = False
error = False
while True:
	# Cuando el ordenador se bloquea, no hay ventana activa, así que nos saltamos la comprobación
	try:
			# Obtenemos la esquina izquierda de la ventana activa
			left = win32gui.GetWindowRect(win32gui.GetForegroundWindow())[0]
	except:
		time.sleep(3)
		continue
	error = False
	# Obtenemos la posición del ratón
	raton = win32gui.GetCursorPos()[0]
	# Si la pantalla está apagada y el ratón está en ella, la encendemos
	if (not encendido or atenuado) and raton < 0:
		os.system('e:\\Winutil\\MultiscreenBlank2.exe /reveal id \\\\.\\DISPLAY2')
		encendido = True
		atenuado = False
	# Si estamos en la pantalla o la ventana activa lo está, renovamos último
	if raton < 0 or left < 0:
		ultimo = int(time.time())
		# Si está apagado, con doble click se activa, hasta que encontremos como apagarlo de verdad
		# Hay que tener en cuenta que el MultiScreenblank2 genera una ventana negra encima de lo que haya y la activa
		# por lo que la variable left pasa a ser -1280
		#if not monitor:
		#	os.system('e:\\winutil\enciende.exe')
	# Si no, comprobamos si ha pasado el timeout desde ultimo y está encendido
	elif int(time.time()) - ultimo > int(Timeout/2) and not atenuado:
		# Bajamos brillo
		os.system('e:\\Winutil\\MultiscreenBlank2.exe /minimized /dim50 id \\\\.\\DISPLAY2')
		atenuado = True
	elif int(time.time()) - ultimo > Timeout and atenuado and encendido:
		# Bajamos brillo
		os.system('e:\\Winutil\\MultiscreenBlank2.exe /minimized /blank id \\\\.\\DISPLAY2')
		encendido = False
	# Esperamos 1 segundo
	time.sleep(1)
	if Debug:
		print('ratón y ventana', raton, left)
		print(encendido, atenuado)
