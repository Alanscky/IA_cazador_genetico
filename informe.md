# Informe: cazador genético de defectos

> Extensión requerida: entre 1000 y 1500 palabras, sin contar tablas ni referencias.
> Las tablas deben coincidir con los archivos de `resultados/principal/`.
> Prioricen explicar SU trabajo sobre describir los algoritmos en general.

## 1. Representación y factibilidad
La representación estructural del grafo y sus componentes constituye la base sobre la cual operan tanto la línea base aleatoria como el algoritmo genético y el sistema de evaluación. Para garantizar un dominio acotado, determinista y robusto, el diseño se estructuró en dos módulos principales: nodo.py y grafos.py, complementados por una capa de adaptación en adaptador.py.

Cada grafo consta estrictamente de 6 nodos, cuyos identificadores únicos son números enteros comprendidos entre 0 y 5. La clase Nodo (nodo.py) modela cada vértice individual almacenando su identificador y una lista de sus vecinos representada mediante tuplas de la forma (nodo_vecino, costo). Para cumplir con las restricciones del sistema, la inserción de aristas en la clase Nodo implementa validaciones estrictas:

Se prohíbe de manera absoluta que un nodo se enlace consigo mismo, retornando un código de error específico si se intenta.

Se verifica que la conexión hacia un mismo destino no se encuentre duplicada previamente en la lista de adyacencia del nodo origen.

Por su parte, la clase Grafo (grafos.py) gestiona la lectura y validación exhaustiva de los datos desde un archivo JSON. El proceso de construcción es estrictamente atómico: si el archivo o la estructura presentan cualquier anomalía, el grafo no se inicializa de forma parcial, evitando estados intermedios corruptos o utilizables. Las reglas de validación aplicadas durante la construcción son:

Validación de identidad: Se exige que el diccionario de nodos contenga exactamente las claves correspondientes a los enteros del 0 al 5, rechazando identificadores no numéricos, fuera de rango o duplicados.

Control de aristas: El grafo admite un total acumulado de entre 0 y 30 aristas en todo el sistema. Cada arista posee un origen, un destino válido dentro del rango de 0 a 5, y un costo numérico entero estrictamente comprendido entre 1 y 9. Se rechazan explícitamente tipos de datos incorrectos, tales como valores booleanos (aprovechando que en Python True o False son subclsases de enteros).

Invariabilidad y robustez: Los argumentos de entrada para el nodo inicial y el nodo meta también se validan rigurosamente para asegurar que pertenezcan al conjunto de 6 nodos existentes. Asimismo, se garantiza que la evaluación posterior no altere ni corrompa el grafo original, manteniendo la integridad estructural intacta durante los recorridos y consultas de los agentes.

Adicionalmente, para estandarizar la comunicación con los módulos externos de optimización y pruebas, se implementó la clase AdaptadorGrafo en adaptador.py. Esta capa extra extrae la información del grafo validado sin alterar su estructura y genera un diccionario estructurado bajo el formato requerido:

{
    "n": 6,
    "inicio": 0,
    "meta": 5,
    "aristas": [
        [0, 1, 2],
        [0, 2, 4],
        [1, 3, 3]
    ]
}

Esta separación de responsabilidades asegura que la representación de los grafos sea desacoplada, segura ante entradas maliciosas o mal formadas, y totalmente compatible con los componentes de evaluación semántica.

## 2. Función de aptitud
La función de aptitud guía la búsqueda evolutiva recompensando o penalizando a los individuos en función del cumplimiento de los objetivos de optimización y factibilidad. Sus componentes principales evalúan la existencia de una ruta válida entre el nodo inicial y el nodo meta, la longitud de la ruta y la minimización de los recursos consumidos (número de aristas para la línea base B1 o costo total acumulado para U1 y A1).

Las prioridades del diseño priorizan la robustez frente a grafos desconectados o sin ruta (dado que el enunciado especifica que no es obligatoria una ruta entre inicio y meta). En los casos sin solución, la aptitud penaliza penaliza el cromosoma para guiar al algoritmo fuera de trayectorias inválidas, diferenciando claramente entre un grafo estructuralmente mal formado y un grafo válido que simplemente carece de un camino factible entre el origen y el destino. El criterio de simplicidad penaliza soluciones redundantes con bucles innecesarios. Se excluye deliberadamente el tiempo de ejecución de la función de aptitud para mantener la métrica determinista y dependiente exclusivamente de la topología y los costos de las aristas.

Justificación de la Probabilidad de Arista (PROB_ARISTA = 0.3)
En un grafo dirigido de N=6 nodos, el número total de pares ordenados posibles sin auto-conexiones (aristas donde u

=v) está dado por la fórmula:

Total de pares=N×(N−1)=6×5=30 pares
Este valor coincide exactamente con el límite superior de aristas permitido por las restricciones del sistema (entre 0 y 30 aristas). Al definir PROB_ARISTA = 0.3 (30% de probabilidad para cada par dirigido de manera independiente), se establecen las siguientes ventajas clave:

Densidad esperada óptima:
El número esperado de aristas generadas aleatoriamente en un grafo inicial se calcula como:

E[aristas]=30×0.3=9 aristas
Un promedio de 9 aristas sobre un total de 30 posibles representa una densidad moderada (≈30%). Esto evita dos extremos problemáticos:

Grafos excesivamente dispersos (probabilidades muy bajas, ej. 0.05 o 0.1): Provocarían que una gran cantidad de grafos carecieran por completo de rutas entre el nodo origen (0) y el nodo meta (5), dificultando la convergencia del algoritmo genético y generando un exceso de casos triviales "sin solución".

Grafos excesivamente densos (probabilidades altas, ej. 0.8 o 0.9): Saturarían el límite de las 30 aristas y crearían caminos alternativos múltiples muy complejos que elevarían innecesariamente el costo computacional de búsqueda de los agentes sin aportar diversidad estructural significativa.

Equilibrio entre conectividad y complejidad:
Con una probabilidad del 30%, se garantiza una topología rica en ciclos (cumpliendo la restricción de que un nodo puede formar parte de uno o varios ciclos) y rutas alternativas con costos enteros variables entre 1 y 9, permitiendo que tanto la línea base aleatoria (aleatorio.py) como los operadores de cruce y mutación del algoritmo genético exploren un espacio de estados desafiante pero con una probabilidad razonable de encontrar soluciones factibles.

Distribución común y reproducible:
Al ser la misma probabilidad utilizada tanto en la generación de la población inicial del algoritmo genético como en la línea base aleatoria (grafo_aleatorio), se asegura una comparabilidad experimental justa, partiendo exactamente de la misma distribución de probabilidad estocástica.

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
| 1 | José Eduardo Velázquez González | Análisis de requisitos, diseño e implementación de la estructura "grafo", los nodos que conforman el mismo y el adaptador para adaptarlo al formato solicitado. Además de una serie de pruebas para determinar el buen funcionamiento | `adaptador.py`, `grafos.py`, `nodo.py`, `tests/test_grafos.py` (14 pruebas) | - |
| 2 | | | |
| 3 | Alan Martínez Martínez | Evaluador común con verificación semántica propia, doble verificación contra el paquete, clasificación de incidencias y control de presupuesto; línea base aleatoria; pruebas del clasificador, del presupuesto y de la línea base | `evaluacion.py`, `aleatorio.py`, `tests/test_evaluacion.py` (23 pruebas), `tests/salida_pruebas.txt` | - |
| 4 | | | |

## 10. Recursos externos
- Paquete docente `busqueda` versión 1.0.0 (profesor): `ejecutar`, `referencia`, `verificar` y `heuristica`, usados sin modificar desde `evaluacion.py`.
- Biblioteca estándar de Python: `random`, `json`, `unittest`, `pathlib`.


## Referencias
<!-- Fuentes REALES consultadas (McCarthy et al., 1955; Turing, 1950; Searle, 1980; libro de texto del curso...). -->
