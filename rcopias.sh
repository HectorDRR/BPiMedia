#!/bin/bash
#Macro para hacer copias de bin y /mnt/f a Google Drive usando rclone
# Ver 1.0: Excluimos la carpeta .git y __pycache__ de bin
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Empezamos la copia al Google drive>>/mnt/e/.mini/milog.txt
rclone sync /home/hector/bin Drive:Odroid/bin --exclude "__pycache__/*" --exclude ".git/**" 
rclone sync /mnt/f Drive:Odroid/f
echo `date +%d/%m/%Y\ %H:%M:%S` [copias.sh] Terminada la copia al Google drive. Tamaño ocupado de bin y f:>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/bin>>/mnt/e/.mini/milog.txt
rclone size Drive:Odroid/f>>/mnt/e/.mini/milog.txt
