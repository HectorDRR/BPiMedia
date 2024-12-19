# !/home/hector/bin/mipython/bin/env python3
# -*- coding: utf-8 -*-
# Macro para generar comprobar los NIF/NIE de los socios y mandarles un correo en caso de error
#
# 20241211, Ver 0.3: Permitimos NIF/NIE de menos cifras e incluimos cabecera en la salida para poder enviar los correos con el Mail Merge en el Thunderbird
# 20241207, Ver 0.1: Primera implementación
#
import csv, sys

def validoDNI(dni):
    tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
    dig_ext = "XYZ"
    reemp_dig_ext = {'X':'0', 'Y':'1', 'Z':'2'}
    numeros = "1234567890"
    dni = dni.upper()
    dig_control = dni[-1]
    dni = dni[:-1]
    if dni[0] in dig_ext:
        dni = dni.replace(dni[0], reemp_dig_ext[dni[0]])
    return len(dni) == len([n for n in dni if n in numeros]) \
        and tabla[int(dni)%23] == dig_control
    return False
    
fichero = sys.argv[1]
# Escribimos cabecera para poder usar el Mail Merge en el Thunderbird
lista = ['codigo,id.externo,Nombre,email\n']
with open(fichero, newline='',  encoding='utf-8-sig') as csvfile:
    pp=csv.reader(csvfile, delimiter=';')
    flag = 0
    for row in pp:
        # Nos saltamos la primera línea que tiene las cabeceras
        if flag == 0:
            flag = 1
            continue
        # Quitamos espacio al final del NIF/NIE si lo hay
        print(row)
        row[1] = row[1].strip()
        # Comprobamos que es NIF/NIE
        if not validoDNI(row[1].upper()) and row[1][-1:].isalpha() and row[0] < "7651":
            # Añadimos a la lista en mayúsculas
            lista.append(row[0] + ',' + row[1].upper() + ',' + row[2] + ',' + row[3])
            flag += 1
print(flag)
input()
with open(fichero[0:-4] + '_erroneos.csv', 'w') as csvfile:
    for f in lista:
        csvfile.writelines(f + '\n')
exit