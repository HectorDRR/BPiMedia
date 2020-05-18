#!/bin/bash
# Macro para acceder al Venus GX y obtener datos de la instalación fotovoltaica y de la placa de ACS
source /home/hector/bin/funciones.sh
[ "$Victron p" == " p" ] && Victron=$1
# Generamos la lista de elementos a usar con un array 'asociativo' en bash
declare -A lista
# Leemos lo vertido a red total
mosquitto_sub -h venus -t N/$Victron/grid/30/Ac/Energy/Reverse -C 1 >/tmp/Vertido &
mosquitto_pub -h venus -t R/$Victron/grid/30/Ac/energy/Reverse -m ''
# Incluimos los tópicos que nos interesas, en este caso la producción de la FotoVoltaica, consumo, Red y SOC batería
lista=([FV]=Ac/PvOnGrid/L1/Power [Consumo]=Ac/Consumption/L1/Power [Red]=Ac/Grid/L1/Power [Bateria]=Dc/Battery/Soc)
# Hacemos un bucle para suscribirnos al elemento y hacer la petición
for f in "${!lista[@]}"
do
	#echo /tmp/$f ${lista[$f]}
	mosquitto_sub -h venus -t N/$Victron/system/0/${lista[$f]} -C 1 >/tmp/$f &
	mosquitto_pub -h venus -t R/$Victron/system/0/${lista[$f]} -m ''
done
sleep 3
# Definimos la variable
linea=''
# Leemos los distintos ficheros para unirlos
for f in "${!lista[@]}"
do
	linea=$linea$(SacaValor $f)
done
linea=$linea$(SacaValor Vertido)
# Obtenemos todos los valores de estadística de la web de Victron (24h, semana, mes y año) desde Python
fvTotal=$(cat /tmp/fvhoy)
# Al unirlo, le quitamos la ',' final a línea y la '{' incial de fvhoy y añadimos en medio la fecha y hora de actualización
echo \{${linea:0:-1},\"Actualizado\":\"$(date +%c)\",${fvTotal:1}>/mnt/f/Placas.txt
# En paralelo, obtenemos la temperatura de la placa de ACS que ahora la hemos separado a otra página
Estado_Placa
