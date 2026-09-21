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
        )
        # El resultado de la cinta, sin los blancos "_" de los extremos
        resultado = ""
        for linea in proceso.stdout.splitlines():
            if linea.startswith("Resultado: "):
                resultado = linea[len("Resultado: "):].strip("_")
        return proceso.returncode, resultado


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

        status, resultado = self.ejecutar(programa, cinta)

        self.assertEqual(status, 0)
        self.assertEqual(resultado, "1011")

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

        status, resultado = self.ejecutar(programa, cinta)

        self.assertEqual(status, 0)
        self.assertEqual(resultado, "1000")


if __name__ == "__main__":
    unittest.main()
