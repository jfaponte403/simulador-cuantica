# vamos a identificar el tipo de automata
# si se ingresan cuatro elementos de inicio entonces es MTD
# por el contrario si se ingresan tres elementos es un AFD
import sys
from collections import deque

#hay que verificar que no se repitan las reglas Multiple definitions

def VerificarMultipleDefinitios(elementos, inicio):
    definitios = {}
    for i in range(inicio,len(elementos)):
        clave = elementos[i][0]
        valor = elementos[i][1]
        if clave in definitios and definitios[clave] == valor:
            return True
        definitios[clave] = valor
    return False

def AFD(elementos, ejemplos):
    for i in range(len(ejemplos)):
        estado = elementos[0][0]
        ejemplo = ejemplos[i]
        print("el ejemplo es " + ejemplo)
        for j in range(len(ejemplo)):
            caracter = ejemplo[j]
            for k in range(2,len(elementos)):
                if estado == elementos[k][0]:
                        if caracter == elementos[k][1]:
                            estado = elementos[k][2]
                            break
        n = 0
        while n < len(elementos[1]):
            if estado == (elementos[1][n]):
                print(f"TRUE!!!")
                break
            n = n + 3
        if n > len(elementos[1]):
            print("FALSE!!!")

def MTD(elementos, ejemplo):
    estado = '0' or 'q0'
    posicion = 0
    input = ejemplo[0]
    input.replace(" ", "_")
    nuevo_string = deque(input)
    error = True
    while error == True and posicion < 10:
        confirmacion = False
        for i in range(len(elementos)):
            if estado == elementos[i][0]:
                if nuevo_string[posicion] == elementos[i][1]:
                    nuevo_string[posicion] = str(elementos[i][2])
                    estado = elementos[i][4]
                    if(elementos[i][3] == 'r'):
                        posicion+= 1
                        if posicion >= len(nuevo_string):
                            nuevo_string.append("_")
                    else:
                        posicion-= 1
                        if posicion < 0:
                            posicion = 0
                            nuevo_string.appendleft("_")
                    confirmacion = True
        resultado = "".join(nuevo_string)
        resultado.replace("_", " ")
        if confirmacion == False:
            print(f"Resultado: {resultado}")
            error = False
            break

#el primer argumento es el programa y el segundo es la cinta
if len(sys.argv) != 3:
    print("Uso: python simuladornew.py <programa.txt> <cinta.txt>")
    sys.exit(1)

ruta_programa = sys.argv[1]
ruta_cinta = sys.argv[2]

with open(ruta_programa, "r", encoding="utf-8") as archivo:
    elementos = []
    for linea in archivo:
        linea_limpia = linea.strip()
        if linea_limpia:
            palabras = linea_limpia.split()
            elementos.append(palabras)


with open(ruta_cinta, "r", encoding="utf-8") as archivo:
    ejemplo = [linea.rstrip() for linea in archivo]
    if not ejemplo:
            ejemplo.append("_")

#contamos las lineas y evaluamos la primera linea
total_lineas = len(elementos)
total_elementos = len(elementos[0])
inicio = 0
if total_elementos == 1:
    inicio = 2
    print("este es un AFD")
    if VerificarMultipleDefinitios(elementos, inicio):
        print("Multiple definitions!!!")
    else:
        AFD(elementos, ejemplo)
else:
    print("\n|--- Maquina de Turing Determinista ---|")
    if VerificarMultipleDefinitios(elementos, inicio):
        print("Multiple definitions!!!")
    else:
        print(f"Cinta Inicial: {str(ejemplo)}")
        MTD(elementos, ejemplo)
