# Cazador genético de defectos en agentes de búsqueda

Algoritmo genético que evoluciona grafos dirigidos de 6 nodos para encontrar incumplimientos de especificación en B1 (BFS), U1 (UCS) y A1 (A\*), comparado contra una búsqueda aleatoria (línea base) con el mismo presupuesto de evaluaciones.

## Integrantes

| Integrante | Nombre | Responsabilidad principal |
|---|---|---|
| 1 | Velázquez González José Eduardo | `grafos.py`, `nodo.py`, `adaptador.py`: representación, conversión y validación |
| 2 | NOMBRE | `genetico.py`: algoritmo genético y aptitud |
| 3 | Alan Martínez Martínez | `evaluacion.py` y `aleatorio.py`: evaluación semántica y línea base |
| 4 | Yenifer Quintero Tolentino | `experimentos.py`: orquestación, registros y contraejemplos |

## Requisitos

- Python TODO (versión usada; el paquete pide 3.10 o superior y recomienda 3.11).
- Probado en: macOS (zsh), TODO (agregar los demás sistemas del equipo).
- Solo biblioteca estándar. No hay que instalar nada con pip.
- Paquete docente versión 1.0.0 (`busqueda.VERSION`).

## Estructura

```
IA_cazador_genetico/
├── paquete_docente/      # paquete del profesor (paquete_estudiantes.zip), SIN modificar
├── grafos.py             # clase Grafo + cromosoma, conversión, validación, reparación
├── nodo.py               # clase Nodo (nodo y sus vecinos)
├── adaptador.py          # exporta un Grafo al formato del paquete (dict o JSON)
├── evaluacion.py         # evaluador común, verificación propia, presupuesto
├── genetico.py           # algoritmo genético y aptitud
├── aleatorio.py          # línea base aleatoria
├── experimentos.py       # ejecuciones, registros, resúmenes, contraejemplos
├── main.py               # comandos de consola
├── CONTRATO.md           # formato de datos entre módulos
├── tests/
│   ├── test_*.py         # pruebas automáticas
│   ├── datos/            # datos controlados para pruebas (p. ej. grafo.json)
│   ├── manuales/         # scripts de prueba manual de la clase Grafo y el adaptador
│   └── salida_pruebas.txt
├── resultados/
│   ├── principal/        # las 10 ejecuciones de la comparación oficial
│   └── desarrollo/       # ejecuciones de depuración (no son la comparación)
├── contraejemplos/       # hasta 6 casos + indice.md
├── informe.md
└── uso_ia.md
```

## Paquete docente

Descomprimir `paquete_estudiantes.zip` y colocar el contenido de su carpeta `estudiantes/` dentro de `paquete_docente/`, de modo que exista `paquete_docente/busqueda/__init__.py`. `evaluacion.py` lo agrega a la ruta de importación automáticamente.

Comprobar la instalación:

```bash
cd paquete_docente
python -m unittest -v test_contrato
cd ..
```

## Comandos

Todos se ejecutan desde la raíz del proyecto. En sistemas donde el comando sea `python3`, sustituir `python`.

```bash
# Pruebas propias (y guardar la evidencia)
python -m unittest discover -s tests -v 2> tests/salida_pruebas.txt

# Pruebas manuales de la clase Grafo y el adaptador
python tests/manuales/test1Grafo.py
python tests/manuales/test2Adaptador.py

# Una ejecución de cada método (se guarda en resultados/desarrollo/)
python main.py ag --semilla 11
python main.py aleatorio --semilla 11

# Comparación oficial: 2 métodos x semillas 11, 22, 33, 44, 55 (resultados/principal/)
python main.py comparar

# Volver a evaluar un contraejemplo
python main.py reproducir contraejemplos/caso_01.json
```

## Módulo de grafos

`grafos.py` tiene dos partes:

1. **Clase `Grafo`** (con `nodo.py` y `adaptador.py`): carga un grafo desde un archivo JSON y valida todas las restricciones del dominio. Se usa para cargar y comprobar grafos escritos a mano.
2. **Representación genética**: funciones sobre cromosomas que usan el algoritmo genético y la línea base (ver `CONTRATO.md`).

### Clase `Nodo` (`nodo.py`)

Representa un nodo individual. Guarda su identificador (`id`) y una lista de tuplas `(nodo_vecino, costo)`.

`addVecino(nodo_vecino, costo)` regresa:
- `0`: intento de auto-conexión (prohibido).
- `1`: conexión añadida con éxito.
- `2`: conexión duplicada (ya existía).

### Clase `Grafo` (`grafos.py`)

Lee un archivo JSON y valida las restricciones: exactamente los nodos 0 a 5, costos enteros de 1 a 9 (se rechazan booleanos), sin lazos ni aristas duplicadas y como máximo 30 aristas. La construcción es atómica: si algo falla, el grafo no queda parcialmente construido.

Formato del JSON de entrada:

```json
{
    "nodos": {
        "0": { "1": 2, "2": 4 },
        "1": { "3": 3, "5": 8 },
        "2": { "3": 1 },
        "3": { "4": 5 },
        "4": { "5": 2 },
        "5": {}
    }
}
```

Uso:

```python
from grafos import Grafo

mi_grafo = Grafo(id_origen=0, id_destino=5, nombreJson="tests/datos/grafo.json")
if mi_grafo.listaNodos:
    print(f"Grafo cargado con éxito. Total de aristas: {mi_grafo.aristas}")
```

### Clase `AdaptadorGrafo` (`adaptador.py`)

Convierte un `Grafo` al formato que espera el paquete docente, como diccionario o como archivo JSON.

```python
from grafos import Grafo
from adaptador import AdaptadorGrafo

mi_grafo = Grafo(id_origen=0, id_destino=5, nombreJson="tests/datos/grafo.json")
if mi_grafo.listaNodos:
    adaptador = AdaptadorGrafo(mi_grafo)
    datos = adaptador.generar_diccionario()
    # {"n": 6, "inicio": 0, "meta": 5, "aristas": [[0, 1, 2], [0, 2, 4], ...]}
    adaptador.exportar_json("resultados/desarrollo/grafo_adaptado.json")
```

### Representación genética

Un cromosoma es una lista de 30 enteros, uno por cada par dirigido `(u, v)` con `u != v` (orden en `grafos.PARES`): `0` = sin arista, `1..9` = costo de la arista.

| Función | Uso |
|---|---|
| `a_grafo(crom)` | cromosoma → dict del paquete |
| `desde_grafo(g)` | dict del paquete → cromosoma |
| `es_valido(crom)` / `reparar(crom)` | validación y reparación del dominio |
| `grafo_aleatorio(rng)` | distribución inicial común del AG y la línea base |
| `num_aristas(crom)`, `clave(crom)`, `a_texto(crom)` | simplicidad, duplicados y salida textual |

## Módulo de evaluación y línea base

### Evaluador común (`evaluacion.py`)

Todos los candidatos, del AG y de la línea base, se evalúan aquí. Por cada grafo:

1. Obtiene la referencia del paquete docente (existencia de ruta, mínimo de aristas, costo mínimo).
2. Ejecuta B1, U1 y A1 con un límite de 100 expansiones.
3. Verifica cada resultado con una **verificación propia** y con `verificar()` del paquete.
4. Clasifica el resultado en una categoría:

| Categoría | Significado |
|---|---|
| `correcto` | Ninguna verificación encuentra discrepancias |
| `contraejemplo` | Las dos verificaciones encuentran las mismas discrepancias |
| `revisar` | Las verificaciones no coinciden; no se cuenta como hallazgo |
| `limite` | El agente agotó sus expansiones; no es defecto ni ausencia de solución |
| `error` | El agente lanzó una excepción; incidencia, no contraejemplo |

Códigos de discrepancia: `ruta_invalida`, `costo_incorrecto`, `falso_sin_solucion`, `no_optimo`. B1 se juzga por número de aristas; U1 y A1, por costo total.

```python
import grafos, evaluacion as ev

e = ev.Evaluador(presupuesto=1000)           # uno nuevo por cada ejecución
resultado = e.evaluar(cromosoma)             # consume 1 evaluación, aunque se repita
resultado["agentes"]["U1"]["categoria"]      # 'correcto', 'contraejemplo', ...

ev.evaluar_sin_presupuesto(cromosoma)        # depuración y reproducción: no consume presupuesto
```

Si falla el código del equipo, la evaluación se cuenta igual, `resultado["agentes"]` es `None` y el error queda en `e.incidencias_equipo`, sin atribuirse al agente.

### Línea base aleatoria (`aleatorio.py`)

```python
from aleatorio import ejecutar_aleatorio
ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud)
```

Genera grafos independientes con `grafos.grafo_aleatorio(rng)` (la misma distribución inicial que el AG) hasta agotar el presupuesto. No usa selección ni reproducción. Registra el progreso cada `intervalo` evaluaciones (igual al tamaño de población del AG). `aptitud` solo se usa para registrar la mejor aptitud observada.


## Dónde se escriben los resultados

TODO: describir los archivos de `resultados/principal/` y `contraejemplos/`.

## Tiempo de ejecución

TODO: tiempo medido de `python main.py comparar` y equipo usado (CPU, sistema operativo).
