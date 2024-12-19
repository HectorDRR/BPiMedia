# !/home/hector/bin/mipython/bin/env python3
# -*- coding: utf-8 -*-
# Macro para generar los códigos para la promo de Zunder a partir del nº de socio de la AUVE y los últimos 4 caracteres del DNI
#
# 20241130, Ver 0.1: Primera implementación
#
import csv, re, sys

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
lista = ['Codigo']
with open(fichero, newline='',  encoding='utf-8-sig') as csvfile:
    pp=csv.reader(csvfile, delimiter=';')
    flag = 0
    for row in pp:
        # Nos saltamos la primera línea que tiene las cabeceras
        if flag == 0:
            flag = 1
            continue
        # Quitamos espacio al final del NIF/NIE si lo hay
        row[1] = row[1].strip()
        # Comprobamos que es NIF/NIE
        #if re.match(r"\d+[a-zA-Z]$",row[1]) != None or re.match(r"[x-zX-Z]\d+[a-zA-Z]$",row[1]) != None:
        if validoDNI(row[1].upper()):
            # Añadimos a la lista en mayúsculas
            lista.append('{:0>4}'.format(int(row[0]))+row[1].upper()[-4:])
        else: print(f'El asociado {row[0]} tiene un NIF/NIE inválido: {row[1]}')
print(lista)
input()
with open(fichero[0:-4] + '_zunder.csv', 'w') as csvfile:
    for f in lista:
        csvfile.writelines(f + '\n')
exit