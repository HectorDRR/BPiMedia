#!/bin/bash
# Macro para chequear si los procesos principales del sistema están funcionando y si no, arrancarlos.
# Generamos la lista de elementos a usar con un array 'asociativo' en bash
declare -A lista
lista=([transmission-da]='sudo service transmission-daemon start' [amuled]='sudo service amule-daemon restart' [Botones.py]='sudo screen -d -m -S Botones -h 20000 /home/hector/bin/boton.sh' [CargaCoche]='screen -d -m -S CargaCoche -h 20000 /home/hector/bin/CargaCoche.py' [vsftpd]='sudo service vsftpd start' [noip2]='sudo noip2' [minidlnad]='/usr/local/sbin/minidlnad')
# Ahora hacemos el bucle para comprobar los procesos
for f in "${!lista[@]}"
do
	pgrep -f $f
	if [ $? -eq 1 ]
	then
		echo $(date) $f cascado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		${lista[$f]}
	fi
done
# Hay un chequeo extra por el amule que algunas veces no desparece el proceso pero está inactivo
tail -1 /mnt/e/.aMule/logfile|grep -e 'Todos los archivos' -e 'All PartFiles' -e 'Asio Sockets'
if [ $? -eq 0 ]
	then
		echo $(date) aMule parado, lo arrancamos de nuevo>>/tmp/mulacaida.txt
		sudo service amule-daemon stop
		sudo service amule-daemon start
		#pkill -9 amule
		#amuled -c /mnt/e/.aMule/ -f
fi
