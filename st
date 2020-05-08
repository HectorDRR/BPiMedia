#!/bin/bash
function procesos {
	# Comprueba la existencia de los procesos normales del sistema
	for f in amuled transmiss minidlna smb vsftpd noip2 python3; do
        	pgrep -a $f
        	if [ $? -eq 1 ]
                	then
                	echo Existe un problema con el proceso $f
                	read p
        	fi
	done
}
function Series {
	# Lista las series pendientes de pasar a disco
	find /mnt/e/pasados/ -type f -perm -u+rwx -exec du -ch '{}' +|sort -k 2|more
}
function json {
	# Extrae de una cadena JSON tipo {"item": valor} el valor
	echo ${1:`expr index "$1" :`:-1}
}
uptime
free -h
tem=$(cat /sys/class/thermal/thermal_zone0/temp)
echo Temperatura del Odroid: ${tem:0:2}º
if [ $1p == sp ];
	then Series;
	exit;
fi
# ~/bin/venus.sh Como lo estamos ejecutando cada 15 minutos, no vale la pena hacerlo cada vez que ejecutemos el st
# Si hay fichero de log, extraemos la temperatura de allí, si no, la pedimos directamente a la placa.
if [ -f /var/log/placa.log ]; then
	ACS=$(tail /var/log/placa.log |grep SENSOR|tail -1 |cut -c 132-135)
	Placa=$(tail /var/log/placa.log|grep placa/STATE|tail -1|cut -c 205-207)
fi
if [ `expr length "$ACS"` -eq 0 ]; then	
	ACS=$(curl -s http://placa/cm?cmnd=Status%2010|cut -c 89-92)
	Placa=$(curl -s http://placa/cm?cmnd=Status|cut -c 90)
fi
echo Temperatura del agua: $ACSº
echo Estado de la placa: $Placa
for f in Cons FV Bat 
do
	vari=$(cat /tmp/$f)
	vari=$(json "$vari")
	vari=$(LC_ALL=C printf "%.*f\n" 2 "$vari")
	echo $f: $vari
done
procesos
# Vemos cuanto espacio queda libre para ponerlo en otro color en caso de que haya poco
# Usamos el printf para conventirlo a entero redondeando puesto que el bash no admite comparar floats
printf -v tam '%.0f' $(df -h /mnt/e|tail -1|cut -c 31-33)
echo .
if [ $tam -lt 10 ] 
	then echo -e "Solo quedan \e[31m$tam\e[0m GB libres en /mnt/e"
	else echo -e "Quedan \e[92m$tam \e[0m GB libres en /mnt/e"
fi
echo .
cat /mnt/e/util/quedan.txt
if [ -a /media/Series ]
    then
	echo Ahora lo que hay en el pen, luego lo que hay en la carpeta HD pendiente
	read p
	ls -lhst /media/Series /media/Pelis
fi
echo HD pendiente pasar a Pen
find /mnt/e/HD/ -maxdepth 1 \( -perm 666 -o -perm 646 -o -perm 677 \) -exec du -ch '{}' +
echo HD pendiente pasar a disco
find /mnt/e/HD/ -maxdepth 1 \( -perm 666 -o -perm 766 \) -exec du -ch '{}' +
echo HD Infantiles pendientes de pasar a disco
find /mnt/e/HD/ -maxdepth 1 \( -perm 746 -o -perm 646 \) -exec du -ch '{}' +
ls -lhst /mnt/e/HD|grep drwx
echo Ahora las Series
read p
ls -lhst /mnt/e/Series
echo Series pendientes de copiar
read p
Series
echo El log del aMule
read p
tail -20 /mnt/e/.aMule/logfile
echo El log del Transmission
read p
sudo grep transmission /var/log/syslog|tail -30
echo El log del minidlna y del traspasa
read p
tail -15 /mnt/e/.mini/minidlna.log
tail -20 /mnt/e/.mini/milog.txt
echo Lo que hay en otros
read p
ls -lhst /mnt/e/otros
echo El transmission
read p
transmission-remote localhost:8964 -l
echo El Amule
read p
amulecmd -c "show DL"
echo El Log del sistema
dmesg -T|grep -v 'shrunk window'|tail -30
echo el Syslog
read p
sudo tail -40 /var/log/syslog|grep -v CRON
tail /var/log/placa.log
[ -f /tmp/mulacaida.txt ] && cat /tmp/mulacaida.txt
[ -f /tmp/ftpcaido.txt ] && cat /tmp/ftpcaido.txt
