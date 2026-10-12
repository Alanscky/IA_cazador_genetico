"""Pruebas de operadores y aptitud. Responsable: Integrante 2."""
import unittest

PENDIENTE = "Pendiente: implementar"


class TestOperadores(unittest.TestCase):
    @unittest.skip(PENDIENTE)
    def test_cruce_preserva_dominio(self):
        """Los hijos del cruce son válidos y combinan genes de ambos padres."""

    @unittest.skip(PENDIENTE)
    def test_mutacion_preserva_dominio(self):
        """La mutación produce cromosomas válidos y no modifica el original."""

    @unittest.skip(PENDIENTE)
    def test_seleccion_depende_de_aptitud(self):
        """Con muchas repeticiones, los más aptos se eligen más veces."""


class TestAptitud(unittest.TestCase):
    @unittest.skip(PENDIENTE)
    def test_contraejemplo_supera_a_correcto(self):
        """Un resultado con discrepancia verificada tiene mayor aptitud."""

    @unittest.skip(PENDIENTE)
    def test_limite_no_cuenta_como_defecto(self):
        """'limite' y 'error' no reciben aptitud de contraejemplo."""

    @unittest.skip(PENDIENTE)
    def test_desempate_por_simplicidad(self):
        """Con igual utilidad, gana el de menos aristas."""


class TestReproducibilidad(unittest.TestCase):
    @unittest.skip(PENDIENTE)
    def test_misma_semilla_mismo_resultado(self):
        """Dos ejecuciones con semilla fija (y presupuesto pequeño) producen registros idénticos."""


if __name__ == "__main__":
    unittest.main()
