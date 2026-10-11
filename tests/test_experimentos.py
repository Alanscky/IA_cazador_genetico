"""Pruebas de registros, resúmenes y reproducción. Responsable: Integrante 4."""
import unittest

PENDIENTE = "Pendiente: implementar"


class TestResumen(unittest.TestCase):
    @unittest.skip(PENDIENTE)
    def test_mediana_solo_exitosas(self):
        """mediana_exitosas([10, None, 30, None, 50]) -> (30, 2)."""

    @unittest.skip(PENDIENTE)
    def test_no_encontrado_queda_como_none(self):
        """Sin hallazgo, primer_hallazgo queda None ('no encontrado'), nunca un número inventado."""


class TestContraejemplos(unittest.TestCase):
    @unittest.skip(PENDIENTE)
    def test_sin_duplicados_y_maximo_seis(self):
        """seleccionar_contraejemplos() no repite grafos y regresa como máximo 6."""

    @unittest.skip(PENDIENTE)
    def test_reproduccion(self):
        """Un contraejemplo guardado se reproduce con evaluar_sin_presupuesto()."""


if __name__ == "__main__":
    unittest.main()
