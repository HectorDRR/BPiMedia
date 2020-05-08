#!/bin/bash
# Macro para acceder al Venus GX y obtener datos de la instalación fotovoltaica
# Nos subscribimos al tópica que nos interesa, en este caso la producción de la FotoVoltaica, consumo, Red y SOC batería
function json {
        # Extrae de una cadena JSON tipo {"item": valor} el valor
        echo ${1:`expr index "$1" :`:-1}
}
[ "$Victron p" == " p" ] && Victron=$1
# Generamos la lista de elementos a usar con un array 'asociativo' en bash
declare -A lista
lista=([FV]=Ac/PvOnGrid/L1/Power [Consumo]=Ac/Consumption/L1/Power [Red]=Ac/Grid/L1/Power [Bateria]=Dc/Battery/Soc)
# Hacemos un bucle para suscribirnos al elemento y hacer la petición
for f in "${!lista[@]}"
do
	#echo /tmp/$f ${lista[$f]}
	mosquitto_sub -h venus -t N/$Victron/system/0/${lista[$f]} -C 1 >/tmp/$f &
	mosquitto_pub -h venus -t R/$Victron/system/0/${lista[$f]} -m ''
done
sleep 1.5
# Definimos la variable
linea=''
# Leemos los distintos ficheros para unirlos
for f in "${!lista[@]}"
do
	vari=$(cat /tmp/$f)
	vari=$(json "$vari")
	vari=$(LC_ALL=C printf "%.*f\n" 2 "$vari")
	linea=$linea\"$f\":$vari,
done
# Obtenemos todos los valores de estadística de la web de Victron (24h, semana, mes y año)
fvTotal=$(cat /tmp/fvhoy)
# Al unirlo, le quitamos la ',' final a línea y la '{' incial de fvhoy
echo \{${linea:0:-1},${fvTotal:1}>/mnt/f/Placas.txt
# En paralelo, obtenemos la temperatura de la placa de ACS que ahora la hemos separado a otra página
# Si hay fichero de log, extraemos la temperatura de allí, si no, la pedimos directamente a la placa.
if [ -f /var/log/placa.log ]; then
	ACS=`tail /var/log/placa.log |grep SENSOR|tail -1 |cut -c 132-135`
fi
[ `expr length "$ACS"` -eq 0 ] && ACS=`curl -s http://placa/cm?cmnd=Status%2010|cut -c 89-92`
echo \{\"ACS\":$ACS\}>/mnt/f/ACS.txt