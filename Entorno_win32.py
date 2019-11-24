"""Definiciones de rutas y variables para hacer el programa portable entre distintas plataformas/configuraciones
"""
#Pelis en HD
HD = 'p:\\pelis\\'
#Donde guardar las pelis
HDG = 'p:\\'
#Series ya tratadas
PASADOS = 'z:\\'
#Pen Temporal
PENTEMP = 'f:\\'
#Series recien descargadas
SERIES = 'z:\\'
#Donde Guardar las Series. Usado solo para listarlas y comprobar que no faltan capítulos
SERIESG = '\\\\metal\\Series\\'
#Temporal donde van las series no tratadas u otros ficheros
TEMP  = '\\\\metal\\Series\\otros\\'
#Carpeta temporal
TMP = 'j:\\temp\\'
#Fichero con las series a ver
SERIESVER = '\\\\metal\\Series\\ver.txt'
#Log del sistema
LOG = 'e:\\winutil\\syslog.txt'
#Sheets
MM = 'e:\\Trabajo\\'
#Plantillas
PLANTILLAS = 'e:\\winutil\\'
#Web
WEB = HD
#Sistema del equipo
#import platform
#SISTEMA = platform.system()
#del platform
SISTEMA = 'Windows'
#Comando para borrar
DEL = 'del '
#Separa Directorios
DIR = '\\'
# Constantes del sistema que pueden variar a lo largo del año
# Consigna de temperatura de la placa
TEMPERATURA = 38
# Tiempo de funcionamiento de la bomba
TBOMBA = 60