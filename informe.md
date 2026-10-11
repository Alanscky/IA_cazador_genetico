# Informe: cazador genético de defectos

> Extensión requerida: entre 1000 y 1500 palabras, sin contar tablas ni referencias.
> Las tablas deben coincidir con los archivos de `resultados/principal/`.
> Prioricen explicar SU trabajo sobre describir los algoritmos en general.

## 1. Representación y factibilidad
<!-- Cromosoma, interpretación, conversión, cómo evitan/reparan/rechazan inválidos.
     Diferencia entre grafo sin solución y cromosoma mal formado. -->

## 2. Función de aptitud
<!-- Componentes, prioridades, casos sin solución, criterio de simplicidad, por qué no se usa el tiempo. -->

## 3. Operadores y proceso evolutivo
<!-- Población inicial, selección, cruce, mutación, reemplazo, empates, duplicados, elitismo.
     Tabla de parámetros (debe coincidir con config.json). -->

## 4. Evaluación semántica e incidencias

Todos los candidatos, tanto del algoritmo genético como de la línea base, pasan por un único evaluador común (`evaluacion.py`). Por cada grafo se obtiene la referencia del paquete docente (`referencia()`), se ejecutan B1, U1 y A1 con un límite de 100 expansiones y cada resultado se verifica dos veces.

**Verificación propia.** Implementamos `verificar_propio()` sin usar el verificador del paquete. Primero se revisa que la ruta empiece en 0, termine en 5, tenga al menos dos nodos y use solo aristas existentes; si no, la discrepancia es `ruta_invalida` y no se revisa nada más, porque el costo de una ruta inexistente no tiene sentido. Con una ruta válida se recalcula su costo y se compara con el declarado (`costo_incorrecto`; también se rechaza un costo que no sea entero, incluido un booleano). Para la optimalidad comparamos solo el valor que cada algoritmo debe minimizar: el número de aristas en B1 y el costo total en U1 y A1. Así, dos rutas distintas con el mismo valor se aceptan como alternativas de igual calidad, y una ruta de B1 más cara que otra no se considera error si tiene el mínimo de aristas. Si un agente afirma que no hay ruta y la referencia indica que sí existe, se registra `falso_sin_solucion`.

**Doble verificación.** El resultado también se pasa por `verificar()` del paquete. Solo se clasifica como `contraejemplo` cuando ambas verificaciones encuentran exactamente las mismas discrepancias. Si no coinciden, la categoría es `revisar` y no cuenta como hallazgo. En las pruebas con 2000 grafos aleatorios las dos verificaciones coincidieron siempre.

**Ejecuciones incompletas.** Usamos cinco categorías separadas: `correcto`, `contraejemplo`, `revisar`, `limite` y `error`. Los estados `limite` y `error` del paquete nunca se consideran contraejemplos, porque alcanzar el límite no demuestra que no haya solución ni que exista un defecto. Si falla el código del propio equipo (por ejemplo, un cromosoma inválido), la excepción se registra en una lista aparte (`incidencias_equipo`) y no se atribuye al agente. Además, se comprueba que el grafo no cambie entre la ejecución de un agente y otra. TODO: número de incidencias de cada tipo en la comparación oficial.

**Presupuesto.** El contador vive en el evaluador, no en cada método: cada llamada a `Evaluador.evaluar()` consume una evaluación aunque el grafo esté repetido, y la evaluación 1001 se rechaza con `PresupuestoAgotado`. Las reproducciones de contraejemplos y la depuración usan `evaluar_sin_presupuesto()`, que no consume las 1000.

**Línea base aleatoria.** `aleatorio.py` genera grafos independientes con la misma función que crea la población inicial del AG (`grafos.grafo_aleatorio`), con un `random.Random(semilla)` propio, hasta agotar el presupuesto. No usa selección ni reproducción. Registra el progreso cada `tam_poblacion` evaluaciones, para que sea comparable con las generaciones del AG, y recibe la función de aptitud solo para anotar la mejor aptitud observada, nunca para decidir qué grafo generar.

## 5. Comparación experimental
<!-- Tabla por método y agente: ejecuciones con hallazgo (x/5), mediana de la evaluación del
     primer hallazgo (solo exitosas), ejecuciones sin hallazgo, grafos distintos, incidencias, tiempo. -->

## 6. Contraejemplos representativos
<!-- 1 o 2 casos explicados: grafo, resultado de referencia, resultado del agente, por qué incumple. -->

## 7. Limitaciones
<!-- Lo que NO demuestran los resultados (p. ej., la ausencia de hallazgos no prueba corrección,
     un contraejemplo no es necesariamente mínimo). -->

## 8. Interpretación conceptual
<!-- Búsqueda de soluciones (grafos) frente a búsqueda de rutas (agentes); paradigma evolutivo
     frente a enfoques lógicos, probabilísticos y de aprendizaje.
     Párrafo breve: McCarthy; por qué detectar fallos no demuestra comprensión (Turing, Searle). -->

## 9. Contribuciones
| Integrante | Qué hizo | Archivos o resultados que lo evidencian | Revisó a |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | Alan Martínez Martínez | Evaluador común con verificación semántica propia, doble verificación contra el paquete, clasificación de incidencias y control de presupuesto; línea base aleatoria; pruebas del clasificador, del presupuesto y de la línea base | `evaluacion.py`, `aleatorio.py`, `tests/test_evaluacion.py` (23 pruebas), `tests/salida_pruebas.txt` | - |
| 4 | | | |

## 10. Recursos externos
- Paquete docente `busqueda` versión 1.0.0 (profesor): `ejecutar`, `referencia`, `verificar` y `heuristica`, usados sin modificar desde `evaluacion.py`.
- Biblioteca estándar de Python: `random`, `json`, `unittest`, `pathlib`.


## Referencias
<!-- Fuentes REALES consultadas (McCarthy et al., 1955; Turing, 1950; Searle, 1980; libro de texto del curso...). -->
