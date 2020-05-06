# Macro para acceder al Venus GX y obtener datos de la instalación fotovoltaica
# Nos subscribimos al tópica que nos interesa, en este caso la producción de la FotoVoltaica, SOC batería y consumo
function json {
        # Extrae de una cadena JSON tipo {"item": valor} el valor
        echo ${1:`expr index "$1" :`:-1}
}
[ "$Victron p" == " p" ] && Victron=$1
mosquitto_sub -h venus -t N/$Victron/pvinverter/32/Ac/Power -C 1 >/tmp/FV &
mosquitto_pub -h venus -t R/$Victron/pvinverter/32/Ac/Power -m ''
sleep .5
mosquitto_sub -h venus -t N/$Victron/battery/512/Soc -C 1 >/tmp/Bat &
mosquitto_pub -h venus -t R/$Victron/battery/512/Soc -m ''
sleep .5
mosquitto_sub -h venus -t N/$Victron/system/0/Ac/Consumption/L1/Power -C 1 >/tmp/Cons &
mosquitto_pub -h venus -t R/$Victron/system/0/Ac/Consumption/L1/Power -m ''
sleep .5
# Definimos la variable
linea=''
# Leemos los distintos ficheros para unirlos
for f in Cons FV Bat 
do
	vari=`cat /tmp/$f`
	vari=$(json "$vari")
	vari=$(LC_ALL=C printf "%.*f\n" 2 "$vari")
	linea=$linea\"$f\":$vari,
done
# Si hay fichero de log, extraemos la temperatura de allí, si no, la pedimos directamente a la placa.
if [ -f /var/log/placa.log ]; then
	ACS=`tail /var/log/placa.log |grep SENSOR|tail -1 |cut -c 132-135`
fi
[ `expr length "$ACS"` -eq 0 ] && ACS=`curl -s http://placa/cm?cmnd=Status%2010|cut -c 89-92`
# Obtenemos todos los valores de estadística de la web de Victron (24h, semana, mes y año)
fvTotal=`cat /tmp/fvhoy`
# Al unirlo, le quitamos la ',' final a línea y la '{' incial de fvhoy
echo \{${linea:0:-1},\"ACS\":$ACS,${fvTotal:1}>/mnt/f/Placas.txt
