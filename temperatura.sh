#!/bin/bash
# Macro para cada hora procesar las temperaturas de la placa y actualizarla en la página web
temp=`curl -s http://placa/cm?cmnd=Status%2010|cut -c 89-92`
~/bin/venus.sh
if [ ${#temp} -gt 0 ]
	then
	sed -E s/de\ \<b\>..../de\ \<b\>$temp/ /mnt/f/index.orig >/mnt/f/index.temp
	sed -E s/\<i\>xxx/\<i\>`cat /tmp/FV|cut -c 11-15`/ /mnt/f/index.temp >/mnt/f/index.html
	python3 /home/hector/bin/funciones.py Temperatura
fi
#echo `date`: Hemos procesado la temperatura de la placa >> /mnt/e/.mini/milog.txt
