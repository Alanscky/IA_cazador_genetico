"""
Línea base: búsqueda aleatoria con el mismo dominio, evaluador y presupuesto.
Sin selección por aptitud ni reproducción evolutiva: cada candidato es un 
grafo independiente generado con la misma distribución inicial que el AG.
"""

import random
import grafos


def ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud=None):
    """Genera grafos independientes con grafos.grafo_aleatorio(rng) hasta agotar el presupuesto.

    - rng = random.Random(semilla) es la única fuente de aleatoriedad.
    - Tras cada evaluación: registro.registrar_evaluacion(resultado).
    - Cada `intervalo` evaluaciones (igual a tam_poblacion del AG), y al final
      si queda un intervalo incompleto: registro.registrar_progreso(...).
    - `aptitud`: la misma función de aptitud del AG (genetico.aptitud). Se usa
      SOLO para registrar la mejor aptitud observada, de modo que el progreso
      sea comparable con el del AG; no interviene en la generación.

    Regresa un dict con la semilla y las evaluaciones consumidas.
    """
    if intervalo < 1:
        raise ValueError("intervalo debe ser al menos 1")
    rng = random.Random(semilla)
    mejor = None
    bloque = 0
    while not evaluador.agotado:
        crom = grafos.grafo_aleatorio(rng)
        resultado = evaluador.evaluar(crom)
        registro.registrar_evaluacion(resultado)
        if aptitud is not None and resultado["agentes"] is not None:
            valor = aptitud(resultado)
            if mejor is None or valor > mejor:
                mejor = valor
        if evaluador.usadas % intervalo == 0 or evaluador.agotado:
            bloque += 1
            registro.registrar_progreso(f"intervalo_{bloque}", mejor,
                                        {"evaluaciones": evaluador.usadas})
    return {"semilla": semilla, "evaluaciones": evaluador.usadas}
