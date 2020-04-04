#!/bin/bash
#Macro para hacer copias de bin y /mnt/f a Google Drive usando rclone
# Ver 1.0: Excluimos la carpeta .git y __pycache__ de bin
# Ver 1.1: Añadimos /mnt/e/util y /mnt/e/.mini y también generamos un fichero con el crontab en bin antes de la copia
# Ver 1.2: Creamos el crontab .txt en /tmp y comparamos con el diff para ver si ha cambiado y copiarlo a bin
#
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Empezamos la copia al Google drive>>/mnt/e/.mini/milog.txt
# Generamos el crontab en /tmp para compararlo con el guardado. Si ha cambiado machacamos el que hay en bin para que se copie
crontab -l >/tmp/crontab.txt
diff /home/hector/bin/crontab.txt /tmp/crontab.txt
if [ $? -eq 1 ]
	then
		cp -y /tmp/crontab.txt /home/hector/bin/
fi
rclone sync /home/hector/bin Drive:Odroid/bin --exclude "__pycache__/*" --exclude ".git/**" -v
rclone sync /mnt/f Drive:Odroid/f -v
rclone sync /mnt/e/util Drive:Odroid/util -v
rclone sync /mnt/e/.mini Drive:Odroid/.mini --exclude "art_cache/**" -v
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Terminada la copia al Google drive. Tamaño ocupado de bin, f, util y .mini:>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/bin>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/f>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/util>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/.mini>>/mnt/e/.mini/milog.txt
