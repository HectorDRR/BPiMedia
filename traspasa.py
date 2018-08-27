#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Primero importamos las librerías necesarias
import os
import shutil
import re
import time

import Entorno as env

def Limpia(f):
	donde = f.find('[')
	if (donde >= 0 and (f[-3:] == 'avi' or f[-3:] == 'mkv')):
		#Si hay un espacio antes del corchete también lo eliminamos
		if f[donde-1] == ' ':
			donde -= 1
		sinf = f[0:donde] + f[-4:]
		try:
			os.rename(f,sinf)
		except:
			print('Ha ocurrido un error renombrando el fichero: ' + str(os.error))
			return f
		#print(time.strftime("%d/%m/%y %H:%M:%S") + ' Limpiamos el nombre del fichero a ' + f)
		f = sinf
	return f

#Si no está montado el pendrive, salimos
if not os.path.exists(env.PENTEMP):
	print(time.strftime("%d/%m/%y %H:%M:%S") + ' No esta montado el pendrive')
	exit(1)
#Nos pasamos a la carpeta de las series
os.chdir(env.SERIES)
#Leemos los ficheros de la carpeta
filenames = next(os.walk('.'))[2]
#Cogemos cada fichero de la lista, lo copiamos al Pen y luego lo movemos a su respectiva carpeta en pasados
#Nos falta tener un control de errores en el caso de que el pen esté lleno
for f in filenames:
	print(time.strftime("%d/%m/%y %H:%M:%S") + ' Procesamos y copiamos el fichero ' + f)
	f = Limpia(f)
	try:
		shutil.copy(f,env.PENTEMP)
	except:
		print('Ha ocurrido un error en la copia' + str(os.error))
		continue
	#Generamos la expresión regular donde separar el nombre de la serie ' nnxnn '
	pp=re.compile(' \d+x\d\d')
	#Si obtenemos 2 pedazos al dividir la cadena siginifica que es una serie
	if len(pp.split(f))>1:
		serie=pp.split(f)[0]
		#print('Serie = ' + serie)
		#Si no existe la carpeta de la serie la creamos. Tenemos pendiente el no diferenciar mayúsculas y minúsculas
		if not os.path.exists(env.PASADOS + serie):
			print(time.strftime("%d/%m/%y %H:%M:%S") + ' No existe la carpeta de la serie ' + serie + ', así que la creamos')
			os.mkdir(env.PASADOS + serie)
		print(time.strftime("%d/%m/%y %H:%M:%S") + ' Movemos el fichero a su carpeta')
		try:
			shutil.move(f, env.PASADOS + serie)
		except:
			print('Ha ocurrido un error al mover el fichero ' + str(os.error))
			continue
		#Activamos el atributo u+x que equivale al de archivo de Windows. Así podemos controlar cuales son nuevos
		#para su posterior paso a los discos USB, tanto desde Windows como desde la misma Banana
		os.chmod(env.PASADOS + serie + '/' + f,0o766)
	else:
		#Si no es una serie lo pasamos a la carpeta otros
		print(time.strftime("%d/%m/%y %H:%M:%S") + ' Como parece que no es una serie, lo movemos a otros')
		try:
			shutil.move(f, env.TEMP)
		except:
			print('Ha ocurrido un error al mover el fichero ' + str(os.error))
			continue
		os.chmod(env.TEMP + f,0o766)
#Por último, le decimos al amule que vuelva a cargar los compartidos para que se de cuenta 
#que lo que antes estaba en Series ahora está en pasados y si se han creados nuevas carpetas
os.system("/home/hector/bin/compartidos")
#Lo demás sobra si lo hacemos desde el PC
#Nos pasamos a la carpeta de las pelis
os.chdir(env.HD)
filenames = next(os.walk('.'))[2]
for f in filenames:
	if (not os.access(f,os.X_OK) and not f[-4:]=='part'):
		f = Limpia(f)
		print(time.strftime("%d/%m/%y %H:%M:%S") + ' Copiamos la peli ' + f + ' al pen')
		try:
			shutil.copy(f,env.PENTEMP)
		except:
			print('Ha ocurrido un error al copiar el fichero al pen ' + str(os.error))
			continue
		#copiamos el fichero y le cambiamos el atributo
		os.chmod(f,0o766)
print(time.strftime("%d/%m/%y %H:%M:%S") + ' Terminamos')
exit(0)
