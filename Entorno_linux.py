# -*- coding: utf-8 -*-
"""Definiciones de rutas y variables para hacer el programa portable entre distintas plataformas/configuraciones
"""
#Pelis en HD
HD = '/mnt/e/HD/'
#Disco externo donde guardar las pelis HD
HDG = '/mnt/HD/'
#Series ya tratadas
PASADOS = '/mnt/e/pasados/'
#Pen Temporal
PENTEMP = '/media/'
#Series recien descargadas
SERIES = '/mnt/e/Series/'
#Punto inicial de montaje de los discos de las series
SERIESG = '/mnt/'
#Temporal donde van las series no tratadas u otros ficheros
TEMP  = '/mnt/e/otros/'
#Carpeta temporal
TMP = '/tmp/'
#Fichero con las series a ver
SERIESVER = '/mnt/e/ver.txt'
#Ubicación del fichero de log
LOG = '/mnt/e/.mini/milog.txt'
#Plantillas páginas web
PLANTILLAS = '/mnt/e/util/'
#Información Multimedia (carátulas, sheets, etc.)
MM = '/mnt/f/'
#Página web
WEB = '/mnt/f/'
#Sistema del equipo
#import platform
#SISTEMA = platform.system()
#del platform
SISTEMA = 'Linux'
#Comando para borrar
DEL = 'rm '
#Separa Directorios
DIR = '/'
#Para cambiar permisos/Atributos. Pendiente de implementar
ATTRIB = 'chmod '