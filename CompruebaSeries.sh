#! /bin/bash
# Macro para pasar a disco las series cuando hemos perdido los atributos en pasados y no sabemos cuales faltan
pushd /mnt/e/pasados
for f in *
do
	if [ -d "/mnt/$1/Series/$f" ];
	then
		rsync -vr --ignore-existing "$f/" "/mnt/$1/Series/$f/"
	else
		echo No existe $f
	fi
done
popd
