"""Algoritmo genético propio (sin bibliotecas de AG).

Responsable: Integrante 2
Contrato: ver CONTRATO.md, secciones 1, 2, 3 y 5.

==============================================================================
GUÍA PARA EL INTEGRANTE 2 (borrar esta guía cuando termine)
==============================================================================
Qué ya existe y puede usar (no hay que reprogramarlo):

  grafos.py (Integrante 1)
    grafos.LONGITUD                -> 30 genes por cromosoma
    grafos.grafo_aleatorio(rng)    -> cromosoma válido al azar (población inicial)
    grafos.es_valido(crom)         -> True/False
    grafos.reparar(crom)           -> copia válida (para después de cruzar o mutar)
    grafos.num_aristas(crom)       -> criterio de simplicidad
    grafos.clave(crom)             -> tupla para detectar duplicados
    Un cromosoma es una lista de 30 enteros: 0 = sin arista, 1..9 = costo.

  evaluacion.py (Integrante 3)
    evaluador.evaluar(crom)        -> dict de resultado (CONTRATO.md, sección 2).
                                      Cada llamada gasta 1 evaluación (de 1000).
    evaluador.agotado              -> True cuando ya no quedan evaluaciones
    evaluador.restantes            -> cuántas quedan
    evaluacion.PresupuestoAgotado  -> se lanza si se evalúa con el presupuesto agotado

  experimentos.py (Integrante 4)
    registro.registrar_evaluacion(resultado)                  -> después de CADA evaluación
    registro.registrar_progreso(etiqueta, mejor_aptitud, extra) -> al cerrar CADA generación

Reglas que vienen de las instrucciones del proyecto:
  - Usar SOLO `rng` (random.Random(semilla)). Prohibido random.random(),
    random.choice(), etc. del módulo global.
  - La misma CONFIG para las 5 semillas de la comparación principal.
  - La selección debe depender de la aptitud; el cruce debe combinar a los dos
    padres; la mutación debe introducir variación.
  - Documentar empates, duplicados y elitismo (si se usa).
  - La aptitud NO puede basarse solo en el tiempo de ejecución.
  - Entre candidatos igual de útiles, debe ganar el más simple (p. ej. menos aristas).

Cómo probar sin esperar a nadie:
    python3 -m unittest tests.test_genetico -v
    (quitar el @unittest.skip de cada prueba al implementarla)
==============================================================================
"""
import random

import grafos

# -----------------------------------------------------------------------------
# Configuración ÚNICA para la comparación principal (la misma en las 5 semillas)
# -----------------------------------------------------------------------------
# TODO(Integrante 2): fijar valores y justificarlos en el informe (sección 3).
# Esta configuración se guarda en config.json de cada ejecución (Integrante 4).
# Ojo: "tam_poblacion" también es el intervalo de progreso de la línea base,
# para que ambos métodos se comparen en bloques del mismo tamaño.
CONFIG = {
    "tam_poblacion": None,        # individuos por generación (la población inicial cuenta en las 1000)
    "seleccion": None,            # nombre del mecanismo, p. ej. "torneo"
    "tam_torneo": None,           # si usa torneo; si no, quitar esta clave
    "prob_cruce": None,           # probabilidad de cruzar a dos padres
    "prob_mutacion": None,        # documentar si es por gen o por individuo
    "elitismo": None,             # cuántos mejores pasan sin cambios (0 si no se usa)
    "reemplazo": None,            # descripción, p. ej. "generacional con elitismo"
    "parada": "presupuesto agotado (1000 evaluaciones)",
    "limite_expansiones": 100,    # límite del paquete docente; no cambiar sin avisar
}


# -----------------------------------------------------------------------------
# Aptitud
# -----------------------------------------------------------------------------
def aptitud(resultado):
    """Aptitud de un candidato a partir del dict del Evaluador. Mayor es mejor.

    Recibe el dict de evaluador.evaluar() (CONTRATO.md, sección 2). Lo útil:
        resultado["agentes"]                     -> dict por agente, o None (ver abajo)
        resultado["agentes"]["B1"]["categoria"]  -> 'correcto' | 'contraejemplo' |
                                                    'revisar' | 'limite' | 'error'
        resultado["agentes"]["B1"]["discrepancias"]   -> lista de códigos
        resultado["agentes"]["B1"]["valor_observado"] -> aristas (B1) o costo (U1/A1)
        resultado["agentes"]["B1"]["valor_optimo"]    -> lo mínimo posible (None si no hay ruta)
        resultado["referencia"]["existe_ruta"]
        resultado["num_aristas"]                 -> para el criterio de simplicidad

    Regresa una TUPLA comparable con > : (prioridad principal, ..., simplicidad).
    Python compara tuplas elemento por elemento, así que el primer elemento manda
    y los siguientes solo desempatan. Para "menos aristas es mejor", usar
    -num_aristas.

    Casos que DEBE manejar:
      - resultado["agentes"] is None: falló el código del equipo. Darle la peor
        aptitud posible; no es un hallazgo.
      - categoria 'limite' o 'error': incidencias, NO defectos. No premiarlas
        como contraejemplo.
      - categoria 'revisar': las dos verificaciones no coinciden. No premiarla
        como contraejemplo.
      - grafos sin ruta (existe_ruta False): son válidos. Decidir y justificar
        cómo se valoran.

    Decisiones de diseño que hay que justificar en el informe:
      - ¿Vale más encontrar fallos en varios agentes a la vez?
      - ¿Se da una señal gradual cuando el agente acierta pero "por poco"
        (p. ej. según la diferencia entre valor_observado y valor_optimo)?
        Una señal gradual ayuda al AG a avanzar antes del primer hallazgo.
      - ¿Se premian más los agentes que todavía no tienen hallazgo?

    Debe ser una función pura: el mismo resultado siempre da la misma aptitud,
    y no debe gastar evaluaciones.
    """
    raise NotImplementedError


# -----------------------------------------------------------------------------
# Operadores
# -----------------------------------------------------------------------------
def poblacion_inicial(rng, tam):
    """Regresa `tam` cromosomas generados con grafos.grafo_aleatorio(rng).

    Debe usar grafos.grafo_aleatorio: es la MISMA distribución que usa la línea
    base aleatoria (requisito 6). No inventar otra distribución aquí.
    """
    raise NotImplementedError


def seleccionar(rng, poblacion, aptitudes):
    """Elige UN progenitor de `poblacion`.

    `aptitudes[i]` es la aptitud (tupla) de `poblacion[i]`.
    La probabilidad de elegir a un individuo debe depender de su aptitud.
    Con aptitudes en forma de tupla, el torneo es lo más sencillo, porque solo
    necesita comparar con >; la ruleta necesita convertir la tupla a un número.
    Documentar cómo se resuelven los empates.
    Regresa el cromosoma elegido (no hace falta copiarlo si cruzar() no lo modifica).
    """
    raise NotImplementedError


def cruzar(rng, padre1, padre2):
    """Combina información de ambos progenitores. Regresa (hijo1, hijo2).

    Los hijos deben ser LISTAS NUEVAS: no modificar padre1 ni padre2.
    Cada gen es un par (u, v) del grafo, así que intercambiar genes entre padres
    intercambia aristas. Ideas: un punto de corte, dos puntos, uniforme o por
    nodo de origen (los genes de un mismo nodo están juntos en grafos.PARES).
    Si los hijos pueden salir inválidos, repararlos con grafos.reparar().
    """
    raise NotImplementedError


def mutar(rng, crom, prob):
    """Introduce variación. Regresa una COPIA nueva; no modifica `crom`.

    Ejemplos de mutación sobre un gen: poner o quitar una arista (0 <-> 1..9) o
    cambiar su costo. Documentar si `prob` se aplica por gen o por individuo.
    El resultado debe ser válido (grafos.es_valido); si no, grafos.reparar().
    """
    raise NotImplementedError


def reemplazar(poblacion, aptitudes, hijos, aptitudes_hijos, config):
    """Arma la siguiente generación. Regresa (nueva_poblacion, nuevas_aptitudes).

    Documentar:
      - Elitismo: cuántos mejores de la generación anterior pasan sin cambios.
        Un élite que pasa sin cambios NO necesita volver a evaluarse: ya tiene
        su aptitud. Si se vuelve a evaluar, gasta presupuesto.
      - Empates: con aptitudes iguales, ¿quién se queda?
      - Duplicados: ¿se permiten individuos repetidos (misma grafos.clave)?
        Evaluar un duplicado también cuenta para las 1000.
    """
    raise NotImplementedError


# -----------------------------------------------------------------------------
# Ciclo principal
# -----------------------------------------------------------------------------
def ejecutar_ag(semilla, evaluador, registro, config=CONFIG):
    """Ejecuta el AG hasta agotar el presupuesto del evaluador.

    Lo llama experimentos.ejecutar_una("ag", semilla) con un Evaluador NUEVO de
    1000 evaluaciones y un Registro nuevo.

    Esquema:
        rng = random.Random(semilla)        # ÚNICA fuente de aleatoriedad
        poblacion = poblacion_inicial(rng, config["tam_poblacion"])
        evaluar a cada individuo:
            resultado = evaluador.evaluar(crom)
            registro.registrar_evaluacion(resultado)   # SIEMPRE, después de cada evaluación
            guardar aptitud(resultado)
        registro.registrar_progreso("generacion_0", mejor_aptitud, {...})
        mientras not evaluador.agotado:
            seleccionar, cruzar, mutar -> hijos
            evaluar a cada hijo (igual que arriba)
            si el presupuesto se agota a mitad de generación, se detiene ahí
            (comprobar evaluador.agotado ANTES de cada evaluar())
            reemplazar
            registro.registrar_progreso(f"generacion_{g}", mejor_aptitud, {...})

    En `extra` del progreso conviene incluir al menos {"evaluaciones": evaluador.usadas}.

    Regresa un dict con datos para el resumen, por ejemplo:
        {"semilla": semilla, "evaluaciones": evaluador.usadas, "generaciones": g}
    """
    raise NotImplementedError
