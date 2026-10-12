"""
Pruebas del clasificador, del presupuesto y de la línea base.
IMPORTANTE: aquí se usan datos controlados (grafos y resultados armados a mano).
No son contraejemplos descubiertos experimentalmente.
"""
import random
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import evaluacion as ev
import grafos
from adaptador import AdaptadorGrafo
from aleatorio import ejecutar_aleatorio
from busqueda import referencia, verificar

DATOS = Path(__file__).resolve().parent / "datos"


def grafo(aristas):
    return {"n": 6, "inicio": 0, "meta": 5, "aristas": aristas}


def solucion(ruta, costo):
    """Resultado falso de un agente que afirma haber encontrado una ruta."""
    return {"estado": "solucion", "ruta": ruta, "costo": costo, "expansiones": 1, "error": None}


def sin_estado(estado):
    return {"estado": estado, "ruta": None, "costo": None, "expansiones": 0, "error": None}


# Grafos controlados
VACIO = grafo([])
# Dos rutas de igual costo (2) y mismo número de aristas: 0-1-5 y 0-2-5.
EMPATE = grafo([[0, 1, 1], [1, 5, 1], [0, 2, 1], [2, 5, 1]])
# Ruta directa cara (0-5 cuesta 9) frente a ruta barata de 2 aristas (0-1-5 cuesta 2).
DIRECTA_CARA = grafo([[0, 5, 9], [0, 1, 1], [1, 5, 1]])


class Base(unittest.TestCase):
    def comprobar(self, agente, g, resultado, esperadas):
        """La verificación propia da `esperadas` y coincide con la del paquete."""
        propias = ev.verificar_propio(agente, g, resultado, referencia(g))
        self.assertEqual(sorted(propias), sorted(esperadas))
        paquete = verificar(agente, g, resultado)["discrepancias"]
        self.assertEqual(sorted(propias), sorted(paquete))


class TestClasificacion(Base):
    def test_sin_ruta(self):
        for agente in ev.AGENTES:
            self.comprobar(agente, VACIO, sin_estado("sin_solucion"), [])
            self.comprobar(agente, VACIO, solucion([0, 5], 1), ["ruta_invalida"])

    def test_falso_sin_solucion(self):
        for agente in ev.AGENTES:
            self.comprobar(agente, EMPATE, sin_estado("sin_solucion"), ["falso_sin_solucion"])

    def test_rutas_alternativas_igual_calidad(self):
        for agente in ev.AGENTES:
            self.comprobar(agente, EMPATE, solucion([0, 1, 5], 2), [])
            self.comprobar(agente, EMPATE, solucion([0, 2, 5], 2), [])

    def test_bfs_se_juzga_por_aristas_no_por_costo(self):
        # 0-5 tiene 1 arista (óptimo para B1) aunque cueste más que 0-1-5.
        self.comprobar("B1", DIRECTA_CARA, solucion([0, 5], 9), [])
        self.comprobar("B1", DIRECTA_CARA, solucion([0, 1, 5], 2), ["no_optimo"])

    def test_ucs_y_a_estrella_se_juzgan_por_costo(self):
        for agente in ("U1", "A1"):
            self.comprobar(agente, DIRECTA_CARA, solucion([0, 1, 5], 2), [])
            self.comprobar(agente, DIRECTA_CARA, solucion([0, 5], 9), ["no_optimo"])

    def test_costo_declarado_incorrecto(self):
        for agente in ev.AGENTES:
            self.comprobar(agente, EMPATE, solucion([0, 1, 5], 3), ["costo_incorrecto"])
            self.comprobar(agente, EMPATE, solucion([0, 1, 5], "2"), ["costo_incorrecto"])
            self.comprobar(agente, EMPATE, solucion([0, 1, 5], True), ["costo_incorrecto"])
        # Costo mal declarado Y ruta no óptima a la vez.
        self.comprobar("U1", DIRECTA_CARA, solucion([0, 5], 2), ["costo_incorrecto", "no_optimo"])

    def test_ruta_invalida(self):
        rutas = ([1, 5],        # no empieza en 0
                 [0, 1],        # no termina en 5
                 [0, 3, 5],     # usa aristas inexistentes
                 [0],           # demasiado corta
                 [0, 7, 5],     # nodo fuera de rango
                 None)          # sin ruta
        for agente in ev.AGENTES:
            for ruta in rutas:
                self.comprobar(agente, EMPATE, solucion(ruta, 2), ["ruta_invalida"])

    def test_limite_y_error_no_son_contraejemplo(self):
        for estado in ("limite", "error"):
            r = sin_estado(estado)
            for agente in ev.AGENTES:
                self.comprobar(agente, EMPATE, r, [])
            self.assertEqual(ev.clasificar(r, [], []), estado)

    def test_estado_desconocido_es_error_del_equipo(self):
        with self.assertRaises(ValueError):
            ev.verificar_propio("B1", EMPATE, sin_estado("otro"), referencia(EMPATE))

    def test_clasificar(self):
        r = solucion([0, 1, 5], 2)
        self.assertEqual(ev.clasificar(r, [], []), "correcto")
        self.assertEqual(ev.clasificar(r, ["no_optimo"], ["no_optimo"]), "contraejemplo")
        self.assertEqual(ev.clasificar(r, ["no_optimo"], []), "revisar")

    def test_coincide_con_verificador_del_paquete(self):
        """Con resultados reales de los agentes en 2000 grafos aleatorios."""
        rng = random.Random(123)
        for _ in range(2000):
            res = ev.evaluar_sin_presupuesto(grafos.grafo_aleatorio(rng))
            for agente, datos in res["agentes"].items():
                self.assertTrue(datos["coinciden"], (agente, res["grafo"], datos))
                self.assertNotEqual(datos["categoria"], "revisar")

    def test_ejemplo_controlado_de_integrante_1(self):
        """grafo.json: B1 regresa 0-2-3-4-5 (4 aristas) cuando 0-1-5 tiene 2."""
        with redirect_stdout(StringIO()):
            g = grafos.Grafo(0, 5, DATOS / "grafo.json")
        crom = grafos.desde_grafo(AdaptadorGrafo(g).generar_diccionario())
        b1 = ev.evaluar_sin_presupuesto(crom)["agentes"]["B1"]
        self.assertEqual(b1["categoria"], "contraejemplo")
        self.assertEqual(b1["discrepancias"], ["no_optimo"])
        self.assertEqual((b1["valor_observado"], b1["valor_optimo"]), (4, 2))


class TestEvaluarGrafo(unittest.TestCase):
    def test_formato_del_contrato(self):
        crom = grafos.desde_grafo(EMPATE)
        copia = list(crom)
        res = ev.evaluar_sin_presupuesto(crom)
        self.assertEqual(crom, copia)  # no modifica el candidato
        self.assertEqual(set(res["agentes"]), {"B1", "U1", "A1"})
        self.assertEqual(res["num_aristas"], 4)
        self.assertEqual(res["heuristica"], [0] * 6)
        self.assertEqual(res["referencia"]["costo_minimo"], 2)
        for datos in res["agentes"].values():
            self.assertEqual(datos["estado"], "solucion")
            self.assertEqual(datos["categoria"], "correcto")

    def test_limite_de_expansiones_cero(self):
        res = ev.evaluar_sin_presupuesto(grafos.desde_grafo(EMPATE), limite_expansiones=0)
        for datos in res["agentes"].values():
            self.assertEqual(datos["categoria"], "limite")


class TestPresupuesto(unittest.TestCase):
    def test_cuenta_repetidos(self):
        e = ev.Evaluador(presupuesto=10)
        crom = grafos.desde_grafo(EMPATE)
        r1, r2 = e.evaluar(crom), e.evaluar(crom)
        self.assertEqual(e.usadas, 2)
        self.assertEqual((r1["num_evaluacion"], r2["num_evaluacion"]), (1, 2))

    def test_no_supera_presupuesto(self):
        e = ev.Evaluador(presupuesto=3)
        crom = grafos.desde_grafo(VACIO)
        for _ in range(3):
            e.evaluar(crom)
        self.assertTrue(e.agotado)
        with self.assertRaises(ev.PresupuestoAgotado):
            e.evaluar(crom)
        self.assertEqual(e.usadas, 3)

    def test_sin_presupuesto_no_cuenta(self):
        e = ev.Evaluador(presupuesto=5)
        ev.evaluar_sin_presupuesto(grafos.desde_grafo(EMPATE))
        self.assertEqual(e.usadas, 0)

    def test_error_del_equipo_se_registra_aparte(self):
        e = ev.Evaluador(presupuesto=5)
        res = e.evaluar([99] * 30)  # cromosoma inválido: falla el código del equipo
        self.assertIsNone(res["agentes"])
        self.assertIn("ValueError", res["incidencia_equipo"])
        self.assertEqual(e.usadas, 1)
        self.assertEqual(len(e.incidencias_equipo), 1)


class RegistroFalso:
    """Sustituto mínimo del Registro de experimentos.py (Integrante 4)."""

    def __init__(self):
        self.evaluaciones, self.progreso = [], []

    def registrar_evaluacion(self, resultado):
        self.evaluaciones.append(resultado)

    def registrar_progreso(self, etiqueta, mejor_aptitud, extra=None):
        self.progreso.append((etiqueta, mejor_aptitud, extra))


class TestAleatorio(unittest.TestCase):
    def correr(self, semilla, presupuesto=50, intervalo=20, aptitud=None):
        e, reg = ev.Evaluador(presupuesto), RegistroFalso()
        salida = ejecutar_aleatorio(semilla, e, reg, intervalo, aptitud)
        return e, reg, salida

    def test_consume_exactamente_el_presupuesto(self):
        e, reg, salida = self.correr(11)
        self.assertEqual(e.usadas, 50)
        self.assertEqual(salida["evaluaciones"], 50)
        self.assertEqual(len(reg.evaluaciones), 50)

    def test_progreso_en_intervalos(self):
        _, reg, _ = self.correr(11)
        evaluaciones = [extra["evaluaciones"] for _, _, extra in reg.progreso]
        self.assertEqual(evaluaciones, [20, 40, 50])  # el último intervalo queda incompleto

    def test_reproducible_con_semilla(self):
        claves = lambda reg: [r["clave"] for r in reg.evaluaciones]
        _, a, _ = self.correr(22)
        _, b, _ = self.correr(22)
        _, c, _ = self.correr(33)
        self.assertEqual(claves(a), claves(b))
        self.assertNotEqual(claves(a), claves(c))

    def test_usa_la_distribucion_comun(self):
        """Los candidatos son exactamente los de grafos.grafo_aleatorio con la misma semilla."""
        _, reg, _ = self.correr(44, presupuesto=10)
        rng = random.Random(44)
        esperados = [grafos.clave(grafos.grafo_aleatorio(rng)) for _ in range(10)]
        self.assertEqual([r["clave"] for r in reg.evaluaciones], esperados)

    def test_registra_mejor_aptitud(self):
        num_aristas = lambda res: res["num_aristas"]  # aptitud de prueba, no la del AG
        _, reg, _ = self.correr(55, aptitud=num_aristas)
        mejores = [m for _, m, _ in reg.progreso]
        self.assertEqual(mejores, sorted(mejores))  # la mejor aptitud nunca baja
        self.assertEqual(mejores[-1], max(r["num_aristas"] for r in reg.evaluaciones))


if __name__ == "__main__":
    unittest.main()
