"""Evaluador común: integra el paquete docente, verifica y cuenta el presupuesto.
    El paquete docente se encuentra en ./paquete_docente y no se modifica.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "paquete_docente"))

import busqueda  # noqa: E402  (paquete docente)
from busqueda import (ejecutar, heuristica, referencia, verificar,  # noqa: E402
                      VERSION as VERSION_PAQUETE)

import grafos  # noqa: E402

AGENTES = ("B1", "U1", "A1")
LIMITE_EXPANSIONES = 100  # valor predeterminado del paquete; registrar si se cambia
INICIO, META = 0, 5

# Códigos de discrepancia (los mismos que usa el paquete docente).
RUTA_INVALIDA = "ruta_invalida"
COSTO_INCORRECTO = "costo_incorrecto"
FALSO_SIN_SOLUCION = "falso_sin_solucion"
NO_OPTIMO = "no_optimo"


class PresupuestoAgotado(Exception):
    """Se pidió evaluar con el presupuesto ya consumido."""




# Verificación semántica propia (requisito 4)

def _pesos(g):
    """Diccionario {(u, v): costo} con las aristas del grafo."""
    return {(u, v): w for u, v, w in g["aristas"]}


def _es_entero(x):
    return isinstance(x, int) and not isinstance(x, bool)


def ruta_valida(g, ruta):
    """True si la ruta empieza en 0, termina en 5 y solo usa aristas existentes."""
    if not isinstance(ruta, list) or len(ruta) < 2:
        return False
    if not all(_es_entero(u) and 0 <= u < 6 for u in ruta):
        return False
    if ruta[0] != INICIO or ruta[-1] != META:
        return False
    pesos = _pesos(g)
    return all((u, v) in pesos for u, v in zip(ruta, ruta[1:]))


def costo_real(g, ruta):
    """Suma de los costos de las aristas de una ruta válida."""
    pesos = _pesos(g)
    return sum(pesos[u, v] for u, v in zip(ruta, ruta[1:]))


def valor_optimo(agente, ref):
    """Lo que el agente debe optimizar: aristas para B1, costo para U1/A1."""
    if not ref["existe_ruta"]:
        return None
    return ref["distancia_minima_aristas"] if agente == "B1" else ref["costo_minimo"]


def valor_observado(agente, g, resultado):
    """Aristas (B1) o costo real (U1/A1) de la ruta del agente; None si no aplica."""
    ruta = resultado.get("ruta")
    if resultado.get("estado") != "solucion" or not ruta_valida(g, ruta):
        return None
    return len(ruta) - 1 if agente == "B1" else costo_real(g, ruta)


def verificar_propio(agente, g, resultado, ref):
    """Verificación semántica PROPIA del equipo.

    Revisa inicio y fin de la ruta, aristas existentes, costo declarado,
    existencia de solución y optimalidad (B1 por aristas; U1/A1 por costo).
    Acepta rutas alternativas de igual calidad: solo compara el VALOR
    (aristas o costo), nunca la lista de nodos.

    Regresa la lista de discrepancias. Para 'limite' y 'error' regresa [].
    Lanza ValueError si el estado es desconocido (error del equipo, no del agente).
    """
    if agente not in AGENTES:
        raise ValueError(f"Agente desconocido: {agente!r}")
    estado = resultado.get("estado")
    if estado in ("limite", "error"):
        return []
    if estado == "sin_solucion":
        return [FALSO_SIN_SOLUCION] if ref["existe_ruta"] else []
    if estado != "solucion":
        raise ValueError(f"Estado de resultado desconocido: {estado!r}")

    ruta = resultado.get("ruta")
    if not ruta_valida(g, ruta):
        # Si la ruta no es válida, no tiene sentido revisar costo ni optimalidad.
        return [RUTA_INVALIDA]
    fallos = []
    costo = resultado.get("costo")
    if not _es_entero(costo) or costo != costo_real(g, ruta):
        fallos.append(COSTO_INCORRECTO)
    if valor_observado(agente, g, resultado) != valor_optimo(agente, ref):
        fallos.append(NO_OPTIMO)
    return fallos


def clasificar(resultado, discrepancias, discrepancias_paquete):
    """Categoría de un resultado.

    - 'limite' / 'error': incidencias, nunca contraejemplo.
    - 'contraejemplo': la verificación propia Y la del paquete encuentran
      exactamente las mismas discrepancias.
    - 'revisar': las dos verificaciones no coinciden; no se cuenta como
      hallazgo hasta revisarlo a mano.
    - 'correcto': ninguna de las dos encuentra discrepancias.
    """
    estado = resultado.get("estado")
    if estado in ("limite", "error"):
        return estado
    if set(discrepancias) != set(discrepancias_paquete):
        return "revisar"
    return "contraejemplo" if discrepancias else "correcto"



# Evaluación de un candidato

def evaluar_grafo(crom, limite_expansiones=LIMITE_EXPANSIONES):
    """Evalúa un cromosoma con los tres agentes y arma el dict del contrato.

    NO cuenta presupuesto (eso lo hace Evaluador). La usan el Evaluador
    y las reproducciones de contraejemplos.
    Lanza ValueError si el cromosoma no es válido (error del equipo).
    """
    g = grafos.a_grafo(crom)
    ref = referencia(g)
    copia = json.dumps(g, sort_keys=True)
    agentes = {}
    for agente in AGENTES:
        r = ejecutar(agente, g, limite_expansiones)
        propias = verificar_propio(agente, g, r, ref)
        paquete = verificar(agente, g, r)["discrepancias"]
        agentes[agente] = {
            "estado": r["estado"],
            "ruta": r["ruta"],
            "costo": r["costo"],
            "expansiones": r["expansiones"],
            "error": r["error"],
            "categoria": clasificar(r, propias, paquete),
            "discrepancias": propias,
            "discrepancias_paquete": paquete,
            "coinciden": set(propias) == set(paquete),
            "valor_observado": valor_observado(agente, g, r),
            "valor_optimo": valor_optimo(agente, ref),
        }
    if json.dumps(g, sort_keys=True) != copia:
        raise RuntimeError("El grafo cambió durante la evaluación")
    return {
        "clave": grafos.clave(crom),
        "grafo": g,
        "num_aristas": grafos.num_aristas(crom),
        "heuristica": list(heuristica(g)),
        "limite_expansiones": limite_expansiones,
        "referencia": ref,
        "agentes": agentes,
    }


class Evaluador:
    """Evaluador con presupuesto. Se crea UNO NUEVO por cada ejecución (método + semilla)."""

    def __init__(self, presupuesto=1000, limite_expansiones=LIMITE_EXPANSIONES):
        self.presupuesto = presupuesto
        self.limite_expansiones = limite_expansiones
        self.usadas = 0
        self.incidencias_equipo = []  # excepciones del código propio (no del agente)

    @property
    def restantes(self):
        return self.presupuesto - self.usadas

    @property
    def agotado(self):
        return self.usadas >= self.presupuesto

    def evaluar(self, crom):
        """Consume 1 evaluación (aunque sea repetido) y regresa el dict del contrato.

        Lanza PresupuestoAgotado si ya no quedan evaluaciones.
        Si falla el código del equipo, la evaluación igual se cuenta (no se
        puede ampliar el presupuesto), se registra en incidencias_equipo y se
        regresa un dict con "agentes": None e "incidencia_equipo" con el mensaje.
        """
        if self.agotado:
            raise PresupuestoAgotado(f"Presupuesto de {self.presupuesto} evaluaciones agotado")
        self.usadas += 1
        try:
            resultado = evaluar_grafo(crom, self.limite_expansiones)
            resultado["incidencia_equipo"] = None
        except Exception as exc:  # error del equipo, NO del agente objetivo
            mensaje = f"{type(exc).__name__}: {exc}"
            self.incidencias_equipo.append({"num_evaluacion": self.usadas, "error": mensaje})
            resultado = {"clave": None, "grafo": None, "num_aristas": None,
                         "heuristica": None, "limite_expansiones": self.limite_expansiones,
                         "referencia": None, "agentes": None, "incidencia_equipo": mensaje}
        resultado["num_evaluacion"] = self.usadas
        return resultado


def evaluar_sin_presupuesto(crom, limite_expansiones=LIMITE_EXPANSIONES):
    """Evaluación para depuración y reproducción. No cuenta para las 1000."""
    return evaluar_grafo(crom, limite_expansiones)
