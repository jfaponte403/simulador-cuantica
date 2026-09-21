import os
import subprocess
import sys
import tempfile
import unittest

# El simulador real, ejecutado como script: python simuladornew.py <programa> <cinta>
SIMULADOR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "simuladornew.py")


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Directorio temporal limpio por test para los archivos de programa y cinta
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def ejecutar(self, programa, cinta):
        ruta_programa = os.path.join(self.tmp.name, "programaMTD.txt")
        ruta_cinta = os.path.join(self.tmp.name, "cintaMTD.txt")
        with open(ruta_programa, "w", encoding="utf-8") as archivo:
            archivo.write(programa)
        with open(ruta_cinta, "w", encoding="utf-8") as archivo:
            archivo.write(cinta)

        proceso = subprocess.run(
            [sys.executable, SIMULADOR, ruta_programa, ruta_cinta],
            capture_output=True,
            text=True,
        )
        # El resultado de cada cinta, sin los blancos "_" de los extremos
        resultados = []
        for linea in proceso.stdout.splitlines():
            if linea.startswith("Resultado: "):
                resultados.append(linea[len("Resultado: "):].strip("_"))
        return proceso.returncode, resultados


class TestSimulador(BaseTestCase):
    def test_uno_igual_uno(self):
        self.assertEqual(1, 1)

    def test_mtd_suma_uno_a_1010(self):
        programa = (
            "0 1 1 r 0\n"
            "0 0 0 r 0\n"
            "0 _ _ l 1\n"
            "\n"
            "1 0 1 r 2\n"
            "1 1 0 l 1\n"
            "1 _ 1 r 2\n"
        )
        cinta = "1010"

        status, resultados = self.ejecutar(programa, cinta)

        self.assertEqual(status, 0)
        self.assertEqual(resultados, ["1011"])

    def test_mtd_suma_uno_a_111(self):
        programa = (
            "0 1 1 r 0\n"
            "0 0 0 r 0\n"
            "0 _ _ l 1\n"
            "\n"
            "1 0 1 r 2\n"
            "1 1 0 l 1\n"
            "1 _ 1 r 2\n"
        )
        cinta = "111"

        status, resultados = self.ejecutar(programa, cinta)

        self.assertEqual(status, 0)
        self.assertEqual(resultados, ["1000"])

    def test_afd_acepta_cantidad_de_unos_multiplo_de_tres(self):
        # Formato: estado simbolo siguiente; "*" marca el estado final
        programa = (
            "0 1 1\n"
            "1 1 2\n"
            "2 1 3\n"
            "*3 1 1\n"
        )
        cinta = (
            "1\n"
            "11\n"
            "111\n"
            "1111\n"
            "11111\n"
            "111111\n"
            "1111111\n"
            "11111111\n"
        )

        status, resultados = self.ejecutar(programa, cinta)

        expected = [
            "Rechazada",  # 1
            "Rechazada",  # 11
            "Aceptada",   # 111
            "Rechazada",  # 1111
            "Rechazada",  # 11111
            "Aceptada",   # 111111
            "Rechazada",  # 1111111
            "Rechazada",  # 11111111
        ]

        self.assertEqual(status, 0)
        self.assertEqual(resultados, expected)


if __name__ == "__main__":
    unittest.main()
