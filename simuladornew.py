# MTD: python simuladornew.py programaMTD.txt cintaMTD.txt
# AFD: python simuladornew.py programaAFD.txt cintaAFD.txt

import sys
from collections import deque


class MultipleDefinitionsError(Exception):
    pass

def VerificarMultipleDefinitios(elementos):
    definidas = set()
    for estado, simbolo, *_ in elementos:
        if (estado, simbolo) in definidas:
            raise MultipleDefinitionsError(f"Multiple definitions!!! estado {estado} con simbolo {simbolo}")
        definidas.add((estado, simbolo))

def AFD(elementos, q0, cinta):
    d = {}
    F = set()
    for q, s, n in elementos:
        if '*' in q:
            q = q.strip('*')
            F.add(q)
        d[q, s] = n

    q = q0
    for simbolo in cinta:
        #si no hay transicion definida la cinta se rechaza
        if (q, simbolo) not in d:
            return False
        q = d[q, simbolo]
    return q in F

mensaje = {True: 'Aceptada', False: 'Rechazada'}

def MTD(elementos, cinta):
    estado = '0' or 'q0'
    posicion = 0
    input = cinta[0]
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

def LeerPrograma(ruta_programa):
    elementos = []
    with open(ruta_programa, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea_limpia = linea.strip()
            if linea_limpia:
                palabras = linea_limpia.split()
                elementos.append(palabras)
    return elementos

def LeerCinta(ruta_cinta):
    with open(ruta_cinta, "r", encoding="utf-8") as archivo:
        cinta = [linea.rstrip() for linea in archivo]
    if not cinta:
        cinta.append("_")
    return cinta

def main():
    #el primer argumento es el programa y el segundo es la cinta
    if len(sys.argv) != 3:
        print("Uso: python simuladornew.py <programaMTD.txt> <cintaMTD.txt>")
        sys.exit(1)

    elementos = LeerPrograma(sys.argv[1])
    cinta = LeerCinta(sys.argv[2])

    #contamos los elementos de la primera linea para saber si es AFD o MTD
    es_afd = len(elementos[0]) == 3
    print("\n|--- Automata Finito Determinista ---|" if es_afd else "\n|--- Maquina de Turing Determinista ---|")
    try:
        VerificarMultipleDefinitios(elementos)
    except MultipleDefinitionsError as error:
        print(error)
        sys.exit(1)

    if es_afd:
        for entrada in cinta:
            entrada = entrada.strip()
            print(f"Cinta Inicial: {entrada}")
            print(f"Resultado: {mensaje[AFD(elementos, '0', entrada)]}")
    else:
        print(f"Cinta Inicial: {str(cinta)}")
        MTD(elementos, cinta)


if __name__ == "__main__":
    main()
