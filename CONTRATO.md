# Contrato entre módulos

Este documento fija **qué recibe y qué regresa cada parte**. Si alguien necesita cambiar un formato, se acuerda en equipo y se actualiza aquí **antes** de cambiar el código.

> Las decisiones marcadas como **PROPUESTA** son un punto de partida. El integrante responsable puede cambiarlas, pero debe documentarlo aquí y avisar.

## Flujo general

```
grafos.py ──(cromosoma)──► evaluacion.Evaluador ──(resultado)──► genetico.aptitud()
   ▲                              │                                    │
   │ grafo_aleatorio(rng)         │ cuenta presupuesto                 ▼
   ├──────── genetico.py          ▼                             selección / cruce /
   └──────── aleatorio.py     experimentos.Registro              mutación / reemplazo
```

## 1. Cromosoma (`grafos.py`, Integrante 1)

**PROPUESTA:** lista de 30 enteros, uno por cada par dirigido `(u, v)` con `u != v`, en el orden de `grafos.PARES`.

- `0`: no hay arista `u → v`.
- `1..9`: hay arista con ese costo.

| Función | Recibe | Regresa |
|---|---|---|
| `a_grafo(crom)` | cromosoma | dict en formato del paquete: `{"n":6,"inicio":0,"meta":5,"aristas":[[u,v,w],...]}` |
| `desde_grafo(g)` | dict del paquete | cromosoma |
| `es_valido(crom)` | cromosoma | `bool` |
| `reparar(crom)` | cromosoma (posiblemente inválido) | cromosoma válido (copia nueva) |
| `grafo_aleatorio(rng)` | `random.Random` | cromosoma válido. **Única distribución inicial, la usan el AG y el aleatorio** |
| `num_aristas(crom)` | cromosoma | `int` |
| `clave(crom)` | cromosoma | `tuple` inmutable, para detectar duplicados |

## 2. Resultado de una evaluación (`evaluacion.py`, Integrante 3)

`Evaluador.evaluar(crom)` regresa un dict con esta forma:

```python
{
  "num_evaluacion": 37,             # 1..1000 dentro de la ejecución
  "clave": (0, 3, 0, ...),          # grafos.clave(crom)
  "grafo": {...},                   # dict del paquete
  "num_aristas": 7,
  "heuristica": [0, 0, 0, 0, 0, 0],  # la que usa A1 (para guardar en contraejemplos)
  "limite_expansiones": 100,
  "incidencia_equipo": None,        # texto del error si falló el código del equipo
  "referencia": {"existe_ruta": True, "distancia_minima_aristas": 2, "costo_minimo": 5},
  "agentes": {
    "B1": {
      "estado": "solucion",         # solucion | sin_solucion | limite | error
      "ruta": [0, 1, 5], "costo": 5, "expansiones": 2, "error": None,
      "categoria": "correcto",      # correcto | contraejemplo | revisar | limite | error
      "discrepancias": [],          # de la verificación PROPIA del equipo
      "discrepancias_paquete": [],  # de busqueda.verificar()
      "coinciden": True,            # ¿la verificación propia y la del paquete dicen lo mismo?
      "valor_observado": 2,         # B1: núm. de aristas de su ruta; U1/A1: costo real (None si no aplica)
      "valor_optimo": 2             # según la referencia (None si no hay ruta)
    },
    "U1": {...},
    "A1": {...}
  }
}
```

Reglas:
- **Cada llamada a `evaluar()` consume 1 evaluación**, aunque el grafo sea repetido.
- Si se llama con el presupuesto agotado, lanza `PresupuestoAgotado`.
- `limite` y `error` **nunca** son `contraejemplo`.
- `contraejemplo` exige que la verificación propia y la del paquete encuentren las mismas discrepancias. Si no coinciden, la categoría es `revisar` y **no** se cuenta como hallazgo.
- Si falla el código del equipo (por ejemplo, un cromosoma inválido), la evaluación **sí se cuenta**, `"agentes"` es `None`, `"incidencia_equipo"` trae el mensaje y el error queda en `Evaluador.incidencias_equipo`. Quien use el resultado (aptitud, registro) debe revisar `resultado["agentes"] is None`.
- Una excepción en el código del equipo o en el adaptador **no** se atribuye al agente. Se registra como incidencia del equipo.
- Las reproducciones y la depuración usan `evaluar_sin_presupuesto()`, que **no** cuenta para las 1000.

## 3. Aptitud (`genetico.py`, Integrante 2)

`aptitud(resultado) -> tuple`. Se compara con `>`: mayor es mejor. Usar una tupla permite fijar prioridades, por ejemplo `(componente_principal, ..., -num_aristas)`. La simplicidad debe ser el criterio secundario. **La fórmula la diseña el equipo.**

## 4. Registro (`experimentos.py`, Integrante 4)

Tanto el AG como el aleatorio reciben un objeto `Registro` y llaman:

- `registro.registrar_evaluacion(resultado)` después de **cada** evaluación.
- `registro.registrar_progreso(etiqueta, mejor_aptitud, extra)`: el AG lo llama una vez por generación; el aleatorio, cada `tam_poblacion` evaluaciones, como intervalo equivalente.

Llamada de la línea base: `aleatorio.ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud)`. `aptitud` es `genetico.aptitud`; solo se usa para registrar la mejor aptitud, no para generar.

El `Registro` lleva la primera evaluación con contraejemplo por agente, los grafos distintos, las incidencias y los candidatos a contraejemplo.

## 5. Aleatoriedad

- Cada ejecución crea **un** `random.Random(semilla)` y lo pasa hacia abajo.
- **Prohibido** usar `random.random()`, `random.choice()` y demás funciones globales del módulo `random`.
- El paquete docente no tiene aleatoriedad.

## 6. Archivos de salida

```
resultados/principal/<metodo>_s<semilla>/config.json
resultados/principal/<metodo>_s<semilla>/progreso.csv
resultados/principal/<metodo>_s<semilla>/resumen.json
resultados/principal/comparacion.json
resultados/principal/comparacion.csv
resultados/desarrollo/...                 # todo lo que NO es la comparación oficial
contraejemplos/caso_XX.json + indice.md
```
