#!/bin/bash
source /home/hector/bin/funciones.sh
uptime
free -h
tem=$(cat /sys/class/thermal/thermal_zone0/temp)
echo Temperatura del Odroid: ${tem:0:2}º
if [ $1p == sp ];
	then Series;
	exit;
fi
# Obtenemos estado y temperatura de la placa
Estado_Placa
echo Temperatura del agua: $ACSº
echo Estado de la placa: $Placa
for f in Consumo FV Bateria 
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
echo HD pendiente pasar a Metal
find /mnt/e/HD/ -maxdepth 1 -name '*.mkv' \( -perm 666 -o -perm 646 -o -perm 677 \) -exec du -ch '{}' +
echo HD pendiente pasar a disco
find /mnt/e/HD/ -maxdepth 1 -name '*.mkv' \( -perm 666 -o -perm 766 ! -name '*.part' \) -exec du -ch '{}' +
echo HD Infantiles pendientes de pasar a disco
find /mnt/e/HD/ -maxdepth 1 -name '*.mkv'  \( -perm 746 -o -perm 646 ! -name '*.part' \) -exec du -ch '{}' +
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
dmesg -T|grep -v 'vidioc_try_fmt:379'|tail -30
echo el Syslog
read p
sudo tail -40 /var/log/syslog|grep -v CRON
[ -f /var/log/placa.log ] && tail /var/log/placa.log
[ -f /tmp/mulacaida.txt ] && cat /tmp/mulacaida.txt
[ -f /tmp/ftpcaido.txt ] && cat /tmp/ftpcaido.txt
echo la carga del coche
read p
ssh -l root venus tail -20 /home/root/lib/Carga.log
