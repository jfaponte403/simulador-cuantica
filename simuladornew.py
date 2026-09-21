# MTD: python simuladornew.py programaMTD.txt cintaMTD.txt
# AFD: python simuladornew.py programaAFD.txt cintaAFD.txt

import sys
from collections import deque


class MultipleDefinitionsError(Exception):
    pass

def verificar_multiples_definiciones(elementos):
    definidas = []
    for estado, simbolo, *_ in elementos:
        if (estado, simbolo) in definidas:
            raise MultipleDefinitionsError(f"Multiple definitions!!! estado {estado} con simbolo {simbolo}")
        definidas.append((estado, simbolo))

def afd(elementos, estado_inicial, cinta):
    transiciones = {}
    finales = []
    for estado, simbolo, siguiente in elementos:
        if '*' in estado:
            estado = estado.strip('*')
            finales.append(estado)
        transiciones[estado, simbolo] = siguiente

    estado = estado_inicial
    for simbolo in cinta:
        if (estado, simbolo) not in transiciones:
            return False
        estado = transiciones[estado, simbolo]
    return estado in finales

mensaje = {True: 'Aceptada', False: 'Rechazada'}

def mtd(elementos, cinta):
    estado = '0' or 'q0'
    posicion = 0
    entrada = cinta[0]
    entrada.replace(" ", "_")
    nuevo_string = deque(entrada)
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
            break

def leer_programa(ruta_programa):
    elementos = []
    with open(ruta_programa, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea_limpia = linea.strip()
            if linea_limpia:
                palabras = linea_limpia.split()
                elementos.append(palabras)
    return elementos

def leer_cinta(ruta_cinta):
    with open(ruta_cinta, "r", encoding="utf-8") as archivo:
        cinta = [linea.rstrip() for linea in archivo]
    if not cinta:
        cinta.append("_")
    return cinta

def main():
    if len(sys.argv) != 3:
        print("Uso: python simuladornew.py <programaMTD.txt> <cintaMTD.txt>")
        sys.exit(1)

    elementos = leer_programa(sys.argv[1])
    cinta = leer_cinta(sys.argv[2])

    es_afd = len(elementos[0]) == 3

    print("\n|--- Automata Finito Determinista ---|" if es_afd else "\n|--- Maquina de Turing Determinista ---|")

    try:
        verificar_multiples_definiciones(elementos)
    except MultipleDefinitionsError as error:
        print(error)
        sys.exit(1)

    if es_afd:
        for entrada in cinta:
            entrada = entrada.strip()
            print(f"Cinta Inicial: {entrada}")
            print(f"Resultado: {mensaje[afd(elementos, '0', entrada)]}")
    else:
        print(f"Cinta Inicial: {str(cinta)}")
        mtd(elementos, cinta)


if __name__ == "__main__":
    main()
