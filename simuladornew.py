import sys
from collections import deque


def VerificarMultipleDefinitios(elementos, inicio):
    definitios = {}
    for i in range(inicio,len(elementos)):
        clave = elementos[i][0]
        valor = elementos[i][1]
        if clave in definitios and definitios[clave] == valor:
            return True
        definitios[clave] = valor
    return False

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
    cinta = [linea.rstrip() for linea in archivo]
    if not cinta:
            cinta.append("_")

#contamos las lineas y evaluamos la primera linea
total_lineas = len(elementos)
total_elementos = len(elementos[0])
inicio = 0
if total_elementos == 3:
    print("\n|--- Automata Finito Determinista ---|")
    if VerificarMultipleDefinitios(elementos, inicio):
        print("Multiple definitions!!!")
    else:
        for entrada in cinta:
            entrada = entrada.strip()
            print(f"Cinta Inicial: {entrada}")
            print(f"Resultado: {mensaje[AFD(elementos, '0', entrada)]}")
else:
    print("\n|--- Maquina de Turing Determinista ---|")
    if VerificarMultipleDefinitios(elementos, inicio):
        print("Multiple definitions!!!")
    else:
        print(f"Cinta Inicial: {str(cinta)}")
        MTD(elementos, cinta)
