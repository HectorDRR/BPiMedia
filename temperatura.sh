#!/bin/bash
# Macro para cada hora activar la bomba y esperar unos segundos para procesar las temperaturas de la placa y actualizarla 
# en la página web
curl "http://bomba/cm?cmnd=backlog%20Power%20on;delay%20100;power%20off"
sleep 30
sed -E s/\<b\>..../\<b\>`curl -s 'http://placa/cm?cmnd=Status%2010'|cut -c 69-72`/ /mnt/f/index.html >/mnt/f/index.temp
mv /mnt/f/index.temp /mnt/f/index.html
python3 /home/hector/bin/funciones.py Temperatura
