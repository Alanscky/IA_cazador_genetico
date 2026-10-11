"""Experimentos, registros, resúmenes y contraejemplos.

Responsable: Integrante 4
Contrato: ver CONTRATO.md, secciones 2, 4 y 6.

==============================================================================
GUÍA PARA EL INTEGRANTE 4 (borrar esta guía cuando termine)
==============================================================================
La revisión de la primera versión está en revisiones/experimetos_integrante4_comentado.py.

Qué ya existe y puede usar:

  evaluacion.py (Integrante 3) — YA FUNCIONA
    evaluacion.Evaluador(presupuesto=PRESUPUESTO)  -> uno NUEVO por ejecución
    evaluador.usadas / evaluador.incidencias_equipo
    evaluacion.evaluar_sin_presupuesto(crom)       -> para reproducir (no gasta las 1000)
    evaluacion.VERSION_PAQUETE                     -> "1.0.0"
    El dict de cada evaluación está en CONTRATO.md, sección 2.

  aleatorio.py (Integrante 3) — YA FUNCIONA, sirve para probar todo este archivo
    aleatorio.ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud)
      intervalo = genetico.CONFIG["tam_poblacion"]  (mientras sea None, usar 20)
      aptitud   = genetico.aptitud                  (mientras no exista, None)

  genetico.py (Integrante 2) — PENDIENTE
    genetico.ejecutar_ag(semilla, evaluador, registro, genetico.CONFIG)

  grafos.py (Integrante 1) — YA FUNCIONA
    grafos.desde_grafo(dict) -> cromosoma (para reproducir contraejemplos)
    grafos.a_texto(crom)     -> texto legible

Reglas que vienen de las instrucciones del proyecto:
  - NUNCA inventar resultados. Sin hallazgo -> None / "no encontrado".
  - La mediana del primer hallazgo se calcula SOLO con las ejecuciones que sí
    encontraron algo, y se informa junto al número de ejecuciones sin hallazgo.
  - Un contraejemplo solo existe si categoria == "contraejemplo".
  - "limite", "error", "revisar" e incidencias del equipo se cuentan aparte.
  - Las ejecuciones de prueba van a resultados/desarrollo/; solo las 10
    oficiales van a resultados/principal/.

Cómo probar sin esperar al Integrante 2:
    python3 main.py aleatorio --semilla 11
    python3 -m unittest tests.test_experimentos -v
==============================================================================
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SEMILLAS = (11, 22, 33, 44, 55)
PRESUPUESTO = 1000
METODOS = ("ag", "aleatorio")
AGENTES = ("B1", "U1", "A1")
DIR_PRINCIPAL = RAIZ / "resultados" / "principal"
DIR_DESARROLLO = RAIZ / "resultados" / "desarrollo"
DIR_CONTRAEJEMPLOS = RAIZ / "contraejemplos"
MAX_CONTRAEJEMPLOS = 6


class Registro:
    """Acumula lo que pasa en UNA ejecución (método + semilla)."""

    def __init__(self, metodo, semilla, config):
        self.metodo = metodo
        self.semilla = semilla
        self.config = config
        self.progreso = []                      # filas para progreso.csv
        self.primer_hallazgo = {"B1": None, "U1": None, "A1": None}  # None = "no encontrado"
        self.claves_vistas = set()              # grafos distintos
        self.incidencias = {"limite": 0, "error": 0, "revisar": 0, "equipo": 0}
        self.candidatos = []                    # posibles contraejemplos (resultado completo)

    def registrar_evaluacion(self, resultado):
        """Se llama después de CADA evaluación (lo hacen aleatorio.py y genetico.py).

        TODO(Integrante 4):
          - Si resultado["agentes"] is None: falló el código del equipo ->
            sumar a incidencias["equipo"] y terminar (no hay nada más que leer).
          - Agregar resultado["clave"] a claves_vistas.
          - Para cada agente en resultado["agentes"]:
              categoria "limite" / "error" / "revisar" -> sumar a incidencias
              categoria "contraejemplo":
                  si primer_hallazgo[agente] es None -> guardar resultado["num_evaluacion"]
                  guardar en candidatos: (agente, resultado) — los datos para el
                  JSON del contraejemplo ya vienen en `resultado`.
        """
        raise NotImplementedError

    def registrar_progreso(self, etiqueta, mejor_aptitud, extra=None):
        """Una fila de progreso: generación del AG o intervalo del aleatorio.

        TODO(Integrante 4): guardar etiqueta, mejor aptitud, evaluaciones usadas
        (viene en extra["evaluaciones"]) y hallazgos acumulados por agente.
        `mejor_aptitud` puede ser None (aleatorio sin aptitud) o una tupla:
        convertirla a texto o lista para poder escribirla en CSV/JSON.
        """
        raise NotImplementedError

    def resumen(self, evaluaciones_usadas, segundos):
        """Dict serializable con lo que pide el requisito 9.

        TODO(Integrante 4): método, semilla, evaluaciones usadas, primer hallazgo
        por agente (None si no hubo), número de grafos distintos (len(claves_vistas)),
        incidencias, número de candidatos y tiempo en segundos.
        """
        raise NotImplementedError

    def guardar(self, carpeta):
        """Escribe config.json, progreso.csv y resumen.json en `carpeta`.

        TODO(Integrante 4): crear la carpeta si no existe y usar encoding="utf-8".
        config.json debe incluir la configuración, la semilla, el presupuesto,
        el límite de expansiones y evaluacion.VERSION_PAQUETE.
        """
        raise NotImplementedError


def ejecutar_una(metodo, semilla, carpeta_base=DIR_DESARROLLO, config=None):
    """Corre un método con una semilla, con un Evaluador NUEVO de PRESUPUESTO evaluaciones.

    TODO(Integrante 4):
        evaluador = evaluacion.Evaluador(presupuesto=PRESUPUESTO)
        registro = Registro(metodo, semilla, config)
        inicio = time.perf_counter()
        si metodo == "aleatorio": aleatorio.ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud)
        si metodo == "ag":        genetico.ejecutar_ag(semilla, evaluador, registro, config)
        segundos = time.perf_counter() - inicio
        guardar en carpeta_base / f"{metodo}_s{semilla}"
    Regresa el Registro (lo usa comparar()).
    """
    raise NotImplementedError


def comparar(carpeta_base=DIR_PRINCIPAL):
    """Las 10 ejecuciones oficiales (2 métodos x 5 semillas) y la comparación.

    TODO(Integrante 4): por método y agente, calcular:
      - ejecuciones con hallazgo (de 5)
      - mediana de la evaluación del primer hallazgo SOLO entre las exitosas
        (mediana_exitosas) y número de ejecuciones sin hallazgo
      - grafos distintos, incidencias y tiempo total
    Guardar comparacion.json y comparacion.csv en carpeta_base, imprimir la
    tabla y guardar los contraejemplos seleccionados en contraejemplos/.
    """
    raise NotImplementedError


def mediana_exitosas(valores):
    """Mediana ignorando None. Regresa (mediana | None, num_sin_hallazgo).

    Ejemplo: mediana_exitosas([10, None, 30, None, 50]) -> (30, 2)
    Se puede usar statistics.median (biblioteca estándar).
    """
    raise NotImplementedError


def seleccionar_contraejemplos(registros):
    """Hasta 6 casos sin duplicados exactos; uno por agente detectado cuando sea posible.

    TODO(Integrante 4): recorrer los candidatos de todos los registros; para que
    no haya duplicados, comparar (agente, resultado["clave"]). Empezar por un caso
    de cada agente y completar hasta MAX_CONTRAEJEMPLOS. Se puede preferir el de
    menos aristas (resultado["num_aristas"]) como el más fácil de explicar.
    """
    raise NotImplementedError


def guardar_contraejemplo(caso, ruta):
    """JSON con lo que pide el requisito 11.

    Campos: método, semilla, número de evaluación, agente, grafo, heurística (A1),
    referencia, resultado del agente (estado, ruta, costo, expansiones),
    discrepancias, explicación, versión del paquete y límite de expansiones.
    Casi todo viene en el resultado del evaluador: resultado["grafo"],
    resultado["heuristica"], resultado["referencia"], resultado["agentes"][agente],
    resultado["limite_expansiones"], resultado["num_evaluacion"].
    La explicación puede armarse con las discrepancias y con
    valor_observado / valor_optimo.
    """
    raise NotImplementedError


def reproducir(ruta_json):
    """Vuelve a evaluar un contraejemplo FUERA del ciclo evolutivo.

    TODO(Integrante 4): leer el JSON, convertir con grafos.desde_grafo(),
    evaluar con evaluacion.evaluar_sin_presupuesto() y confirmar que el agente
    vuelve a dar la misma ruta, costo y discrepancias. Imprimir el resultado.
    Estas reproducciones NO cuentan en las 1000 evaluaciones.
    """
    raise NotImplementedError
