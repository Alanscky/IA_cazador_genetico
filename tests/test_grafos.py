"""Pruebas de formato, validación y reparación. Responsable: Integrante 1.

Los casos de la clase Grafo provienen de los scripts manuales de Integrante 1
(tests/manuales/), convertidos en comprobaciones automáticas.
"""
import json
import random
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import evaluacion  # agrega paquete_docente a la ruta de importación
import grafos
from adaptador import AdaptadorGrafo
from busqueda import validar

DATOS = Path(__file__).resolve().parent / "datos"


def _silencio(funcion, *args, **kwargs):
    """Ejecuta sin mostrar los print() de la clase Grafo."""
    with redirect_stdout(StringIO()):
        return funcion(*args, **kwargs)


def _crom(**aristas):
    """Cromosoma a partir de aristas con nombre 'u_v', por ejemplo _crom(a0_1=2, a1_5=3)."""
    c = [0] * grafos.LONGITUD
    for nombre, w in aristas.items():
        u, v = map(int, nombre[1:].split("_"))
        c[grafos.PARES.index((u, v))] = w
    return c


class TestFormato(unittest.TestCase):
    def test_a_grafo_produce_formato_del_paquete(self):
        g = grafos.a_grafo(_crom(a0_1=2, a1_5=3))
        self.assertEqual(g, {"n": 6, "inicio": 0, "meta": 5, "aristas": [[0, 1, 2], [1, 5, 3]]})
        validar(g)  # el validador del profesor no debe lanzar ValueError

    def test_ida_y_vuelta(self):
        rng = random.Random(1)
        for _ in range(200):
            c = grafos.grafo_aleatorio(rng)
            self.assertEqual(grafos.desde_grafo(grafos.a_grafo(c)), c)

    def test_grafo_vacio_es_valido(self):
        c = [0] * grafos.LONGITUD
        self.assertTrue(grafos.es_valido(c))
        self.assertEqual(grafos.a_grafo(c)["aristas"], [])
        validar(grafos.a_grafo(c))

    def test_desde_grafo_rechaza_fuera_de_dominio(self):
        base = {"n": 6, "inicio": 0, "meta": 5}
        for aristas in ([[0, 0, 1]], [[0, 1, 0]], [[0, 1, 10]], [[0, 1, 1], [0, 1, 2]],
                        [[True, 1, 2]], [[0, 6, 1]]):
            with self.assertRaises(ValueError):
                grafos.desde_grafo(dict(base, aristas=aristas))
        with self.assertRaises(ValueError):
            grafos.desde_grafo({"n": 6, "inicio": 1, "meta": 5, "aristas": []})

    def test_a_grafo_no_modifica_cromosoma(self):
        c = _crom(a0_1=2)
        copia = list(c)
        grafos.a_grafo(c)
        self.assertEqual(c, copia)


class TestValidacionYReparacion(unittest.TestCase):
    def test_rechaza_cromosomas_invalidos(self):
        malos = ([0] * 29, [0] * 31, [10] + [0] * 29, [-1] + [0] * 29,
                 [True] + [0] * 29, [1.0] + [0] * 29, "0" * 30, None)
        for c in malos:
            self.assertFalse(grafos.es_valido(c), c)
            if c is not None:
                with self.assertRaises(ValueError):
                    grafos.a_grafo(c)

    def test_reparar_produce_valido(self):
        malos = ([0] * 29, [0] * 31, [10] + [0] * 29, [-3] + [0] * 29,
                 [True] + [0] * 29, [2.5] + [0] * 29)
        for c in malos:
            copia = list(c)
            r = grafos.reparar(c)
            self.assertTrue(grafos.es_valido(r), c)
            self.assertEqual(c, copia)  # el original no cambia
        self.assertEqual(grafos.reparar([10] + [0] * 29)[0], 9)
        self.assertEqual(grafos.reparar([-3] + [0] * 29)[0], 0)

    def test_reparar_no_cambia_validos(self):
        c = _crom(a0_1=2, a3_5=9)
        self.assertEqual(grafos.reparar(c), c)

    def test_grafo_aleatorio_valido_y_reproducible(self):
        a = [grafos.grafo_aleatorio(random.Random(11)) for _ in range(3)]
        self.assertEqual(a[0], a[1])
        rng = random.Random(22)
        for _ in range(500):
            c = grafos.grafo_aleatorio(rng)
            self.assertTrue(grafos.es_valido(c))
            validar(grafos.a_grafo(c))

    def test_num_aristas_y_clave(self):
        c = _crom(a0_1=2, a1_5=3)
        self.assertEqual(grafos.num_aristas(c), 2)
        self.assertEqual(grafos.clave(c), grafos.clave(list(c)))
        self.assertIsInstance(grafos.clave(c), tuple)


class TestClaseGrafo(unittest.TestCase):
    """Clase Grafo y AdaptadorGrafo de Integrante 1."""

    def _grafo_desde(self, nodos, origen=0, destino=5):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"nodos": nodos}, f)
        return _silencio(grafos.Grafo, origen, destino, f.name)

    def test_carga_ejemplo_y_adaptador(self):
        g = _silencio(grafos.Grafo, 0, 5, DATOS / "grafo.json")
        self.assertEqual(g.aristas, 7)
        d = AdaptadorGrafo(g).generar_diccionario()
        validar(d)
        self.assertEqual(len(d["aristas"]), 7)

    def test_rechaza_entradas_invalidas(self):
        vacios = {str(i): {} for i in range(6)}
        casos = [dict(vacios, **{"0": {"0": 1}}),      # lazo
                 dict(vacios, **{"0": {"1": 0}}),      # costo 0
                 dict(vacios, **{"0": {"1": True}}),   # booleano
                 dict(vacios, **{"0": {"1": 2.0}}),    # no entero
                 {str(i): {} for i in range(5)}]       # falta el nodo 5
        for nodos in casos:
            g = self._grafo_desde(nodos)
            self.assertEqual(g.listaNodos, [], nodos)

    def test_grafo_sin_aristas_es_valido(self):
        g = self._grafo_desde({str(i): {} for i in range(6)})
        self.assertEqual(len(g.listaNodos), 6)
        self.assertEqual(g.aristas, 0)


if __name__ == "__main__":
    unittest.main()
