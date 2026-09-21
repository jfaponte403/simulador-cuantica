import os
import subprocess
import sys
import tempfile
import unittest

# El simulador real, ejecutado como script: python simuladornew.py <programa> <cinta>
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMULADOR = os.path.join(RAIZ, "simuladornew.py")


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Directorio temporal limpio por test para los archivos de programa y cinta
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def ejecutar(self, programa, cinta):
        ruta_programa = os.path.join(self.tmp.name, "programa.txt")
        ruta_cinta = os.path.join(self.tmp.name, "cinta.txt")
        with open(ruta_programa, "w", encoding="utf-8") as archivo:
            archivo.write(programa)
        with open(ruta_cinta, "w", encoding="utf-8") as archivo:
            archivo.write(cinta)

        proceso = subprocess.run(
            [sys.executable, SIMULADOR, ruta_programa, ruta_cinta],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.salida = proceso.stdout
        # El resultado de cada cinta, sin los blancos "_" de los extremos
        resultados = []
        for linea in proceso.stdout.splitlines():
            if linea.startswith("Resultado: "):
                resultados.append(linea[len("Resultado: "):].strip("_"))
        return proceso.returncode, resultados


class TestMTDHardcore(BaseTestCase):
    def ejecutar_mtd(self, programa, cinta, esperado):
        status, resultados = self.ejecutar(programa, cinta)
        self.assertEqual(status, 0, self.salida)
        self.assertEqual(resultados, [esperado], self.salida)

    # ---------- Faciles ----------

    def test_facil_invertir_bits(self):
        programa = (
            "0 0 1 r 0\n"
            "0 1 0 r 0\n"
        )
        self.ejecutar_mtd(programa, "10110", "01001")

    def test_facil_reemplazar_a_por_b(self):
        programa = (
            "0 a b r 0\n"
            "0 b b r 0\n"
        )
        self.ejecutar_mtd(programa, "aabab", "bbbbb")

    def test_facil_incrementar_binario(self):
        programa = (
            "0 1 1 r 0\n"
            "0 0 0 r 0\n"
            "0 _ _ l 1\n"
            "1 0 1 r 2\n"
            "1 1 0 l 1\n"
            "1 _ 1 r 2\n"
        )
        self.ejecutar_mtd(programa, "1011", "1100")

    def test_facil_decrementar_binario(self):
        # Va al final y resta 1 propagando el "prestamo" hacia la izquierda
        programa = (
            "0 0 0 r 0\n"
            "0 1 1 r 0\n"
            "0 _ _ l 1\n"
            "1 1 0 r 2\n"
            "1 0 1 l 1\n"
        )
        self.ejecutar_mtd(programa, "1000", "0111")

    # ---------- Medios ----------

    def test_medio_suma_unaria(self):
        # 111+11 = 11111: cambia el "+" por 1 y borra el ultimo 1
        programa = (
            "0 1 1 r 0\n"
            "0 + 1 r 0\n"
            "0 _ _ l 1\n"
            "1 1 _ r 2\n"
        )
        self.ejecutar_mtd(programa, "111+11", "11111")

    def test_medio_mover_a_la_izquierda_desde_el_inicio(self):
        # Obliga al simulador a crecer la cinta por la izquierda
        programa = (
            "0 1 1 l 1\n"
            "1 _ X r 2\n"
        )
        self.ejecutar_mtd(programa, "1", "X1")

    def test_medio_transiciones_desordenadas_y_con_lineas_vacias(self):
        # Mismo incremento binario pero con las reglas en otro orden
        programa = (
            "\n"
            "1 _ 1 r 2\n"
            "\n"
            "0 _ _ l 1\n"
            "1 1 0 l 1\n"
            "   \n"
            "0 0 0 r 0\n"
            "1 0 1 r 2\n"
            "0 1 1 r 0\n"
        )
        self.ejecutar_mtd(programa, "1111", "10000")

    # ---------- Dificiles ----------

    def test_dificil_palindromo(self):
        # Borra extremos iguales; deja "S" si es palindromo y "N" si no
        programa = (
            "0 a _ r 1\n"
            "0 b _ r 2\n"
            "0 _ S r 9\n"
            # Recuerda "a": va al final
            "1 a a r 1\n"
            "1 b b r 1\n"
            "1 _ _ l 3\n"
            # Recuerda "b": va al final
            "2 a a r 2\n"
            "2 b b r 2\n"
            "2 _ _ l 4\n"
            # Compara el ultimo simbolo con "a"
            "3 a _ l 5\n"
            "3 b N r 9\n"
            "3 _ S r 9\n"
            # Compara el ultimo simbolo con "b"
            "4 b _ l 5\n"
            "4 a N r 9\n"
            "4 _ S r 9\n"
            # Regresa al inicio
            "5 a a l 5\n"
            "5 b b l 5\n"
            "5 _ _ r 0\n"
        )
        casos = {
            "abba": "S",
            "aba": "S",
            "a": "S",
            "abab": "N",
            "ab": "N",
        }
        for cinta, esperado in casos.items():
            with self.subTest(cinta=cinta):
                status, resultados = self.ejecutar(programa, cinta)
                self.assertEqual(status, 0, self.salida)
                # Solo queda la marca, rodeada de blancos
                self.assertEqual([r.strip("_ab") for r in resultados], [esperado], self.salida)

    def test_dificil_copiar_unario(self):
        # 11 -> 11#11: marca cada 1 con X, escribe una copia al final y restaura
        programa = (
            "0 1 1 r 0\n"
            "0 _ # l 1\n"
            "1 1 1 l 1\n"
            "1 _ _ r 2\n"
            "2 1 X r 3\n"
            "2 # # l 5\n"
            "3 1 1 r 3\n"
            "3 # # r 3\n"
            "3 _ 1 l 4\n"
            "4 1 1 l 4\n"
            "4 # # l 4\n"
            "4 X X r 2\n"
            "5 X 1 l 5\n"
            "5 _ _ r 6\n"
        )
        self.ejecutar_mtd(programa, "11", "11#11")

    def test_dificil_ordenar_a_antes_que_b(self):
        # Busca cada "ba" y lo cambia por "ab" hasta que la cadena queda ordenada
        programa = (
            "0 a a r 0\n"
            "0 b b r 1\n"
            "1 b b r 1\n"
            "1 a b l 2\n"
            "2 b a l 3\n"
            "3 a a l 3\n"
            "3 b b l 3\n"
            "3 _ _ r 0\n"
        )
        self.ejecutar_mtd(programa, "babab", "aabbb")

    def test_dificil_incrementar_numero_largo(self):
        # Cinta de 12 simbolos: el acarreo recorre toda la cinta
        programa = (
            "0 1 1 r 0\n"
            "0 0 0 r 0\n"
            "0 _ _ l 1\n"
            "1 0 1 r 2\n"
            "1 1 0 l 1\n"
            "1 _ 1 r 2\n"
        )
        self.ejecutar_mtd(programa, "1" * 12, "1" + "0" * 12)

    def test_dificil_maquina_que_nunca_se_detiene(self):
        # Rebota para siempre entre dos celdas: debe cortar por el tope de pasos
        programa = (
            "0 1 1 r 1\n"
            "1 _ _ l 0\n"
        )
        status, resultados = self.ejecutar(programa, "1")

        self.assertEqual(status, 0, self.salida)
        self.assertEqual(resultados, [])
        self.assertIn("La maquina no se detuvo despues de 10000 pasos", self.salida)


class TestAFDHardcore(BaseTestCase):
    def ejecutar_afd(self, programa, casos):
        cinta = "".join(entrada + "\n" for entrada, _ in casos)
        esperado = ["Aceptada" if acepta else "Rechazada" for _, acepta in casos]

        status, resultados = self.ejecutar(programa, cinta)

        self.assertEqual(status, 0, self.salida)
        self.assertEqual(resultados, esperado, self.salida)

    # ---------- Faciles ----------

    def test_facil_termina_en_1(self):
        programa = (
            "0 0 0\n"
            "0 1 1\n"
            "*1 0 0\n"
            "*1 1 1\n"
        )
        casos = [
            ("1", True),
            ("0", False),
            ("101", True),
            ("110", False),
            ("0001", True),
        ]
        self.ejecutar_afd(programa, casos)

    def test_facil_exactamente_ab(self):
        programa = (
            "0 a 1\n"
            "1 b 2\n"
            "*2 a 3\n"
            "*2 b 3\n"
        )
        casos = [
            ("ab", True),
            ("a", False),
            ("b", False),
            ("aba", False),
            ("ba", False),
        ]
        self.ejecutar_afd(programa, casos)

    def test_facil_cantidad_par_de_ceros(self):
        programa = (
            "*0 0 1\n"
            "*0 1 0\n"
            "1 0 0\n"
            "1 1 1\n"
        )
        casos = [
            ("00", True),
            ("0", False),
            ("1111", True),
            ("10100", False),
            ("010010", True),
        ]
        self.ejecutar_afd(programa, casos)

    # ---------- Medios ----------

    def test_medio_contiene_101(self):
        programa = (
            "0 0 0\n"
            "0 1 1\n"
            "1 0 2\n"
            "1 1 1\n"
            "2 0 0\n"
            "2 1 3\n"
            "*3 0 3\n"
            "*3 1 3\n"
        )
        casos = [
            ("101", True),
            ("0101", True),
            ("100", False),
            ("1101", True),
            ("110011", False),
            ("1001010", True),
        ]
        self.ejecutar_afd(programa, casos)

    def test_medio_simbolo_fuera_del_alfabeto_rechaza(self):
        programa = (
            "*0 0 0\n"
            "*0 1 0\n"
        )
        casos = [
            ("0110", True),
            ("012", False),
            ("a", False),
            ("1x1", False),
        ]
        self.ejecutar_afd(programa, casos)

    def test_medio_cadena_vacia_en_estado_inicial_final(self):
        # Binario divisible por 3; la cadena vacia termina en el estado 0 (final)
        programa = (
            "*0 0 0\n"
            "*0 1 1\n"
            "1 0 2\n"
            "1 1 0\n"
            "2 0 1\n"
            "2 1 2\n"
        )
        casos = [
            ("", True),
            ("0", True),
            ("11", True),
            ("110", True),
            ("111", False),
            ("1001", True),
            ("1010", False),
        ]
        self.ejecutar_afd(programa, casos)

    # ---------- Dificiles ----------

    def test_dificil_final_marcado_en_una_sola_linea(self):
        # El estado 1 solo lleva "*" en una de sus transiciones
        programa = (
            "0 a 1\n"
            "1 a 1\n"
            "*1 b 0\n"
        )
        casos = [
            ("a", True),
            ("aa", True),
            ("ab", False),
            ("aba", True),
            ("b", False),
        ]
        self.ejecutar_afd(programa, casos)

    def test_dificil_binario_divisible_por_5_cadenas_largas(self):
        # Estado = valor mod 5; el oraculo es int(cadena, 2) % 5
        programa = "".join(
            f"{'*' if estado == 0 else ''}{estado} {bit} {(estado * 2 + bit) % 5}\n"
            for estado in range(5)
            for bit in (0, 1)
        )
        entradas = ["0", "101", "1010", "1111", "10100", "111", "1100100"]
        entradas += [format(n, "b") for n in (5 ** 20, 5 ** 20 + 1, 2 ** 64 - 1, 3 ** 40)]
        casos = [(entrada, int(entrada, 2) % 5 == 0) for entrada in entradas]
        self.ejecutar_afd(programa, casos)

    def test_dificil_tercer_simbolo_desde_el_final_es_1(self):
        # 8 estados: el estado guarda los ultimos 3 bits leidos
        programa = "".join(
            f"{'*' if estado & 4 else ''}{estado} {bit} {((estado << 1) | bit) & 7}\n"
            for estado in range(8)
            for bit in (0, 1)
        )
        entradas = ["100", "1", "11", "011", "0100", "1011", "0101", "111000", "000111"]
        casos = [(entrada, len(entrada) >= 3 and entrada[-3] == "1") for entrada in entradas]
        self.ejecutar_afd(programa, casos)

    def test_dificil_estados_con_nombres_largos(self):
        # Identificador: empieza con letra y sigue con letras o digitos
        programa = (
            "0 a ID\n"
            "0 b ID\n"
            "*ID a ID\n"
            "*ID b ID\n"
            "*ID 0 ID\n"
            "*ID 1 ID\n"
        )
        casos = [
            ("a", True),
            ("b01a", True),
            ("0ab", False),
            ("ab1c", False),
            ("", False),
        ]
        self.ejecutar_afd(programa, casos)


if __name__ == "__main__":
    unittest.main()
