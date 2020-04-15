#!/bin/bash
#Macro para hacer copias de bin y /mnt/f a Google Drive usando rclone
# Ver 1.0: Excluimos la carpeta .git y __pycache__ de bin
# Ver 1.1: Añadimos /mnt/e/util y /mnt/e/.mini y también generamos un fichero con el crontab en bin antes de la copia
# Ver 1.2: Creamos el crontab .txt en /tmp y comparamos con el diff para ver si ha cambiado y copiarlo a bin
#
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Empezamos la copia al Google drive>>/mnt/e/.mini/milog.txt
# Generamos el crontab en /tmp para compararlo con el guardado. Si ha cambiado machacamos el que hay en bin para que se copie
crontab -l >/tmp/crontab.txt
diff /home/hector/bin/crontab.txt /tmp/crontab.txt >/dev/null
if [ $? -eq 1 ]
	then
		cp /tmp/crontab.txt /home/hector/bin/crontab.txt
fi
for f in /home/hector/bin /mnt/f /mnt/e/util /mnt/e/.mini; do 
	rclone sync $f Drive:Odroid/${f##*/} --exclude "art_cache/**" --exclude "__pycache__/*" --exclude ".git/**" -v --log-file /tmp/salcopias.txt
done
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Terminada la copia al Google drive>>/mnt/e/.mini/milog.txt
#for f in /home/hector/bin /mnt/f /mnt/e/util /mnt/e/.mini; do 
#	rclone size Drive:Odroid/${f##*/}>>/mnt/e/.mini/milog.txt
#done
