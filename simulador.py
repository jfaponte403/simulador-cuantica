#!/usr/bin/env python3
"""
Simulador de Teoría de la Computación: AFD y MTD.

El simulador identifica por sí mismo el tipo de máquina leyendo la estructura
del archivo de definición:

  * AFD: cada transición tiene 3 campos:  estado  símbolo  destino
  * MTD: cada transición tiene 5 campos:  estado  leído  destino  escrito  dir
         (dir = L, R o S) y se declara el símbolo 'blanco'.

FORMATO DEL ARCHIVO DE DEFINICIÓN (.txt)
  Las líneas que empiezan con '#' son comentarios. Los símbolos son de un
  solo carácter y se separan con espacios.

      estados: q0 q1 q2
      alfabeto: a b
      inicial: q0
      finales: q2
      blanco: _            (solo MTD)
      cinta: X Y           (solo MTD, opcional: símbolos extra de la cinta)
      transiciones:
      q0 a q1              (AFD)      /     q0 a q1 X R     (MTD)

FORMATO DEL ARCHIVO DE CINTAS (.txt)
  Una cadena por línea. Las líneas vacías y las que empiezan con '#' se
  ignoran. Para la cadena vacía se escribe  ε  (o la palabra 'epsilon').

USO
  python simulador.py                                  # ejemploAFD/cintasAFD y ejemploMTD/cintasMTD
  python simulador.py ejemploMTD.txt cintasMTD.txt     # una máquina y sus cintas
  python simulador.py ejemploMTD.txt cintasMTD.txt --traza
"""

import argparse
import os
import sys
from dataclasses import dataclass, field


class ErrorDefinicion(Exception):
    """La definición de la máquina o de las cintas es inválida."""


@dataclass
class Resultado:
    aceptada: bool
    motivo: str
    traza: list = field(default_factory=list)
    pasos: int = 0


# --------------------------------------------------------------------------
# Lectura de archivos
# --------------------------------------------------------------------------


def _lineas_utiles(ruta):
    """Genera (n° de línea, texto) sin comentarios ni líneas vacías."""
    with open(ruta, encoding="utf-8-sig") as f:
        for n, linea in enumerate(f, 1):
            t = linea.strip()
            if t and not t.startswith("#"):
                yield n, t


def leer_definicion(ruta: str) -> dict:
    d = {"transiciones": []}
    listas = {"estados": "estados", "alfabeto": "alfabeto",
              "finales": "finales", "cinta": "simbolos_cinta"}
    unicos = {"inicial", "blanco"}
    en_transiciones = False

    for n, linea in _lineas_utiles(ruta):
        if en_transiciones:
            campos = [c for c in linea.split() if c != "->"]
            d["transiciones"].append(campos)
            continue
        if ":" not in linea:
            raise ErrorDefinicion(f"Línea {n}: se esperaba 'clave: valores'.")
        clave, _, valor = linea.partition(":")
        clave, valores = clave.strip().lower(), valor.split()
        if clave == "transiciones":
            en_transiciones = True
        elif clave in listas:
            d[listas[clave]] = valores
        elif clave in unicos:
            if len(valores) != 1:
                raise ErrorDefinicion(f"Línea {n}: '{clave}' requiere un único valor.")
            d[clave] = valores[0]
        else:
            raise ErrorDefinicion(f"Línea {n}: clave desconocida '{clave}'.")

    for clave in ("estados", "alfabeto", "inicial", "finales"):
        if clave not in d:
            raise ErrorDefinicion(f"Falta el campo obligatorio '{clave}:'.")
    if not en_transiciones:
        raise ErrorDefinicion("Falta la sección 'transiciones:'.")

    simbolos = list(d["alfabeto"]) + d.get("simbolos_cinta", [])
    if "blanco" in d:
        simbolos.append(d["blanco"])
    for s in simbolos:
        if len(s) != 1:
            raise ErrorDefinicion(f"El símbolo '{s}' debe tener un solo carácter.")
    return d


def leer_cintas(ruta: str) -> list:
    cintas = []
    for _, linea in _lineas_utiles(ruta):
        cintas.append("" if linea.lower() in ("ε", "epsilon") else linea)
    return cintas


# --------------------------------------------------------------------------
# Detección automática del tipo de máquina
# --------------------------------------------------------------------------


def detectar_tipo(d: dict) -> str:
    """Devuelve 'AFD' o 'MTD' según la estructura de la definición."""
    longitudes = {len(f) for f in d["transiciones"]}
    tiene_blanco = "blanco" in d

    if longitudes == {3}:
        if tiene_blanco:
            raise ErrorDefinicion(
                "Definición ambigua: transiciones de 3 campos (AFD) "
                "pero se declara 'blanco' (propio de una MTD).")
        return "AFD"
    if longitudes == {5}:
        if not tiene_blanco:
            raise ErrorDefinicion(
                "Transiciones de 5 campos (MTD) pero falta 'blanco:'.")
        return "MTD"
    if not longitudes:
        return "MTD" if tiene_blanco else "AFD"
    raise ErrorDefinicion(
        f"Transiciones con longitudes inválidas {sorted(longitudes)}: "
        "use 3 campos (AFD) o 5 campos (MTD).")


# --------------------------------------------------------------------------
# AFD
# --------------------------------------------------------------------------


class AFD:
    def __init__(self, d: dict):
        self.estados = set(d["estados"])
        self.alfabeto = set(d["alfabeto"])
        self.inicial = d["inicial"]
        self.finales = set(d["finales"])
        self.delta = {}

        if self.inicial not in self.estados:
            raise ErrorDefinicion("El estado inicial no pertenece a 'estados'.")
        if not self.finales <= self.estados:
            raise ErrorDefinicion("Hay estados finales fuera de 'estados'.")

        for q, a, p in d["transiciones"]:
            if q not in self.estados or p not in self.estados:
                raise ErrorDefinicion(f"Estado desconocido en: {q} {a} {p}")
            if a not in self.alfabeto:
                raise ErrorDefinicion(f"Símbolo '{a}' fuera del alfabeto.")
            if (q, a) in self.delta:
                raise ErrorDefinicion(
                    f"No determinista: más de una transición para ({q}, {a}).")
            self.delta[(q, a)] = p

    def completo(self) -> bool:
        return all((q, a) in self.delta for q in self.estados for a in self.alfabeto)

    def simular(self, cadena: str, max_pasos: int = 0) -> Resultado:
        q = self.inicial
        traza = [f"({q}, {cadena or 'ε'})"]
        for i, a in enumerate(cadena):
            if a not in self.alfabeto:
                return Resultado(False, f"símbolo '{a}' no pertenece al alfabeto",
                                 traza, i)
            if (q, a) not in self.delta:
                return Resultado(False, f"sin transición para ({q}, {a})", traza, i)
            q = self.delta[(q, a)]
            traza.append(f"({q}, {cadena[i + 1:] or 'ε'})")
        ok = q in self.finales
        return Resultado(ok, f"termina en '{q}' ({'final' if ok else 'no final'})",
                         traza, len(cadena))


# --------------------------------------------------------------------------
# MTD
# --------------------------------------------------------------------------


class MTD:
    DIRECCIONES = {"L": -1, "R": 1, "S": 0}

    def __init__(self, d: dict):
        self.estados = set(d["estados"])
        self.alfabeto = set(d["alfabeto"])
        self.blanco = d["blanco"]
        self.inicial = d["inicial"]
        self.finales = set(d["finales"])
        self.simbolos_cinta = (self.alfabeto | set(d.get("simbolos_cinta", []))
                               | {self.blanco})
        self.delta = {}

        if self.blanco in self.alfabeto:
            raise ErrorDefinicion("El blanco no puede estar en el alfabeto de entrada.")
        if self.inicial not in self.estados:
            raise ErrorDefinicion("El estado inicial no pertenece a 'estados'.")
        if not self.finales <= self.estados:
            raise ErrorDefinicion("Hay estados finales fuera de 'estados'.")

        for q, a, p, b, mov in d["transiciones"]:
            if q not in self.estados or p not in self.estados:
                raise ErrorDefinicion(f"Estado desconocido en: {q} {a} {p} {b} {mov}")
            if a not in self.simbolos_cinta or b not in self.simbolos_cinta:
                raise ErrorDefinicion(
                    f"Símbolo fuera del alfabeto de cinta en: {q} {a} {p} {b} {mov}")
            if mov not in self.DIRECCIONES:
                raise ErrorDefinicion(f"Dirección inválida '{mov}' (use L, R o S).")
            if (q, a) in self.delta:
                raise ErrorDefinicion(
                    f"No determinista: más de una transición para ({q}, {a}).")
            self.delta[(q, a)] = (p, b, mov)

    def _configuracion(self, cinta, cabezal, q) -> str:
        celdas = set(cinta) | {cabezal}
        partes = []
        for i in range(min(celdas), max(celdas) + 1):
            s = cinta.get(i, self.blanco)
            partes.append(f"[{q}]{s}" if i == cabezal else s)
        return "".join(partes)

    def simular(self, cadena: str, max_pasos: int = 10_000) -> Resultado:
        for a in cadena:
            if a not in self.alfabeto:
                return Resultado(False, f"símbolo '{a}' no pertenece al alfabeto")

        cinta = {i: a for i, a in enumerate(cadena)}
        cabezal, q, pasos = 0, self.inicial, 0
        traza = [self._configuracion(cinta, cabezal, q)]

        while True:
            if q in self.finales:
                return Resultado(True, f"alcanza el estado final '{q}'", traza, pasos)
            leido = cinta.get(cabezal, self.blanco)
            if (q, leido) not in self.delta:
                return Resultado(False, f"se detiene sin transición para ({q}, {leido})",
                                 traza, pasos)
            if pasos >= max_pasos:
                return Resultado(False, f"límite de {max_pasos} pasos excedido "
                                 "(posible ciclo infinito)", traza, pasos)
            q, escribe, mov = self.delta[(q, leido)]
            if escribe == self.blanco:
                cinta.pop(cabezal, None)
            else:
                cinta[cabezal] = escribe
            cabezal += self.DIRECCIONES[mov]
            pasos += 1
            traza.append(self._configuracion(cinta, cabezal, q))


# --------------------------------------------------------------------------
# Ejecución
# --------------------------------------------------------------------------


def construir(definicion: dict):
    tipo = detectar_tipo(definicion)
    return tipo, (AFD(definicion) if tipo == "AFD" else MTD(definicion))


def procesar(ruta_def: str, ruta_cintas: str, traza: bool, max_pasos: int) -> None:
    definicion = leer_definicion(ruta_def)
    tipo, maquina = construir(definicion)
    cintas = leer_cintas(ruta_cintas)

    print(f"\n=== {os.path.basename(ruta_def)} | tipo detectado: {tipo} ===")
    if tipo == "AFD" and not maquina.completo():
        print("Aviso: el AFD es parcial (las transiciones faltantes rechazan).")

    aceptadas = 0
    for c in cintas:
        r = maquina.simular(c, max_pasos)
        aceptadas += r.aceptada
        if traza:
            for i, paso in enumerate(r.traza):
                print(f"    {i:>3}: {paso}")
        veredicto = "ACEPTADA " if r.aceptada else "RECHAZADA"
        print(f"  '{c or 'ε'}' -> {veredicto} ({r.motivo}; {r.pasos} pasos)")
    print(f"Resumen: {aceptadas} aceptadas, {len(cintas) - aceptadas} rechazadas "
          f"de {len(cintas)} cintas.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Simulador de AFD y MTD con detección automática del tipo.")
    ap.add_argument("definicion", nargs="?", help="archivo .txt con la máquina")
    ap.add_argument("cintas", nargs="?", help="archivo .txt con las cadenas a evaluar")
    ap.add_argument("--traza", action="store_true", help="muestra la traza paso a paso")
    ap.add_argument("--max-pasos", type=int, default=10_000,
                    help="límite de pasos para la MTD (por defecto 10000)")
    args = ap.parse_args(argv)

    if bool(args.definicion) != bool(args.cintas):
        ap.error("indique ambos archivos (definición y cintas) o ninguno")

    if args.definicion:
        pares = [(args.definicion, args.cintas)]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        pares = [(os.path.join(base, "ejemploAFD.txt"), os.path.join(base, "cintasAFD.txt")),
                 (os.path.join(base, "ejemploMTD.txt"), os.path.join(base, "cintasMTD.txt"))]

    codigo = 0
    for ruta_def, ruta_cintas in pares:
        try:
            procesar(ruta_def, ruta_cintas, args.traza, args.max_pasos)
        except OSError as e:
            print(f"\nError al leer archivo: {e}", file=sys.stderr)
            codigo = 1
        except ErrorDefinicion as e:
            print(f"\nError en '{os.path.basename(ruta_def)}': {e}", file=sys.stderr)
            codigo = 1
    return codigo


if __name__ == "__main__":
    sys.exit(main())
