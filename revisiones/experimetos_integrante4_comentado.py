# =============================================================================
# REVISIÓN DEL INTEGRANTE 4 — primera versión de experimentos.py
# =============================================================================
# Este es el código ORIGINAL que entregó el Integrante 4, sin cambios en la
# lógica, con comentarios de revisión marcados como "# REVISIÓN:".
#
# NO SE USA EN EL PROYECTO. El código nuevo va en ../experimentos.py (esqueleto).
# Esta carpeta (revisiones/) NO debe ir en el .zip de la entrega.
#
# RESUMEN DE LA REVISIÓN
#   1. [GRAVE] Simula hallazgos: inventa un error de A* en la evaluación 404 de
#      cada semilla y lo guarda como contraejemplo. Las instrucciones prohíben
#      resultados fabricados y casos ficticios. Debe eliminarse por completo.
#   2. El ciclo de 1000 iteraciones no sirve para el AG (que avanza por
#      generaciones) y duplica el control del presupuesto, que ya lleva
#      evaluacion.Evaluador.
#   3. Usa random.seed() global; el contrato pide random.Random(semilla) propio.
#   4. Solo registra "hubo defecto sí/no": falta qué agente falló, la primera
#      evaluación de cada agente, grafos distintos, incidencias, tiempo y
#      progreso por generación (requisitos 9 y 10).
#   5. El resumen decide el éxito según si EXISTE un archivo, e imprime una
#      mediana fija (404). Archivos viejos contarían como hallazgos.
#   6. Escribe en la carpeta actual en vez de resultados/ y contraejemplos/.
#   7. El nombre del archivo tiene un error: "experimetos.py".
#
# QUÉ SE RESCATA
#   - Los campos del contraejemplo (casi coinciden con el requisito 11).
#   - La idea de recorrer métodos x semillas y el formato del resumen impreso.
#
# Ver CONTRATO.md (secciones 2, 4 y 6) y los comentarios de ../experimentos.py.
# =============================================================================

raise SystemExit("Archivo de revisión: no se ejecuta (generaría contraejemplos falsos).")

import json
import random
import os

def ejecutar_experimentos():
    print("Iniciando orquestación del proyecto...")

    semillas = [11, 22, 33, 44, 55]
    # REVISIÓN: correcto. Ya existe como experimentos.SEMILLAS en el esqueleto.
    metodos = ["busqueda_aleatoria", "algoritmo_genetico"]
    # REVISIÓN: los métodos se llaman "aleatorio" y "ag" (experimentos.METODOS),
    # y sus módulos son aleatorio.py y genetico.py.

    for metodo in metodos:
        print(f"\n========== Iniciando pruebas para: {metodo.upper()} ==========")

        for semilla in semillas:
            print(f"\n--- Ejecutando {metodo} con semilla {semilla} ---")
            # REVISIÓN: este cuerpo debe convertirse en ejecutar_una(metodo, semilla).

            random.seed(semilla)
            # REVISIÓN: [3] No usar la semilla global. Cada método crea su propio
            # random.Random(semilla); aquí solo se le pasa el número `semilla`.

            registro_experimento = {
                "metadatos": {
                    "metodo": metodo,
                    "semilla": semilla,
                    "limite_evaluaciones": 1000
                },
                # REVISIÓN: faltan la configuración completa (parámetros del AG,
                # límite de expansiones, versión del paquete). Va en config.json.
                "progreso": {},
                # REVISIÓN: el progreso debe ser una fila por GENERACIÓN (AG) o por
                # INTERVALO (aleatorio) con la mejor aptitud, no una por evaluación.
                # Lo recibe Registro.registrar_progreso().
                "resumen": {
                    "incidencias_limite": 0,
                    "defectos_encontrados": False
                    # REVISIÓN: [4] falta, POR AGENTE (B1, U1, A1), la evaluación del
                    # primer hallazgo (None si no hubo), grafos distintos, incidencias
                    # limite/error/revisar/equipo, evaluaciones usadas y tiempo.
                }
            }

            for iteracion in range(1000):
                # REVISIÓN: [2] Este ciclo debe desaparecer. Se crea UN evaluador:
                #     evaluador = evaluacion.Evaluador(presupuesto=1000)
                # y se llama UNA vez al método, que gasta las 1000 evaluaciones:
                #     aleatorio.ejecutar_aleatorio(semilla, evaluador, registro, intervalo, aptitud)
                #     genetico.ejecutar_ag(semilla, evaluador, registro, config)
                # El método llama a registro.registrar_evaluacion() en cada evaluación.
                # Además, range(1000) empieza en 0; el evaluador numera de 1 a 1000.


                registro_experimento["progreso"][f"evaluacion_{iteracion}"] = "Simulacion OK"
                # REVISIÓN: [1] valor simulado; no registra nada real.

                # simula que en la iteración 404 detecta un error
                if iteracion == 404:
                    # REVISIÓN: [1] GRAVE. Hallazgo inventado. Un contraejemplo solo
                    # existe si el evaluador lo clasifica así:
                    #     resultado["agentes"][agente]["categoria"] == "contraejemplo"
                    # (y resultado["agentes"] no es None).
                    # marcamos en el registro general que sí encontramos un error
                    registro_experimento["resumen"]["defectos_encontrados"] = True

                    datos_contraejemplo = {
                        "metodo_descubridor": metodo,
                        "semilla": semilla,
                        "numero_evaluacion": iteracion,
                        # REVISIÓN: usar resultado["num_evaluacion"].
                        "grafo_defectuoso": "AQUI_IRA_EL_GRAFO_REAL",
                        # REVISIÓN: resultado["grafo"].
                        "algoritmo_objetivo": "A*",
                        # REVISIÓN: el agente ("B1", "U1" o "A1").
                        "resultado_referencia": "Costo 10",
                        # REVISIÓN: [1] dato inventado. Usar resultado["referencia"].
                        "resultado_objetivo": "Costo 15",
                        # REVISIÓN: [1] dato inventado. Usar resultado["agentes"][agente]
                        # (estado, ruta, costo, expansiones, discrepancias).
                        "explicacion": "A* devolvió una ruta más cara que la óptima."
                        # REVISIÓN: generarla a partir de las discrepancias y de
                        # valor_observado / valor_optimo.
                        # REVISIÓN: FALTAN (requisito 11 y README del paquete):
                        #   "heuristica": resultado["heuristica"],
                        #   "limite_expansiones": resultado["limite_expansiones"],
                        #   "version_paquete": evaluacion.VERSION_PAQUETE,
                        #   parámetros del experimento (config).
                    }

                    nombre_contra = f"contraejemplo_{metodo}_semilla_{semilla}.json"
                    # REVISIÓN: [6] guardar en contraejemplos/caso_XX.json, máximo 6
                    # en total y sin duplicados (seleccionar_contraejemplos()). Aquí se
                    # sobrescribe uno por método y semilla, y solo para un agente.
                    with open(nombre_contra, "w") as archivo_contra:
                        # REVISIÓN: falta encoding="utf-8".
                        json.dump(datos_contraejemplo, archivo_contra, indent=4)

            # guarda el archivo general
            nombre_archivo = f"{metodo}_semilla_{semilla}.json"
            # REVISIÓN: [6] guardar en resultados/principal/<metodo>_s<semilla>/
            # como config.json, progreso.csv y resumen.json (Registro.guardar()).
            with open(nombre_archivo, "w") as archivo:
                json.dump(registro_experimento, archivo, indent=4)
            # REVISIÓN: falta medir el tiempo de cada ejecución (time.perf_counter()).


# este bloque genera el resumen comparativo
def generar_resumen():
    # REVISIÓN: debe convertirse en comparar() y guardar además
    # resultados/principal/comparacion.json y comparacion.csv.
    print("\n\n=======================================================")
    print("          RESUMEN COMPARATIVO DE RESULTADOS")
    print("=======================================================")

    metodos = ["busqueda_aleatoria", "algoritmo_genetico"]
    semillas = [11, 22, 33, 44, 55]

    for metodo in metodos:
        exitos = 0
        # REVISIÓN: [4] el conteo debe ser POR MÉTODO Y POR AGENTE, no uno general.

        # revisamos semilla por semilla si se creó el archivo de contraejemplo
        for semilla in semillas:
            nombre_contra = f"contraejemplo_{metodo}_semilla_{semilla}.json"
            if os.path.exists(nombre_contra):  # Preguntamos: ¿Existe este archivo?
                # REVISIÓN: [5] la existencia de un archivo no prueba un hallazgo
                # (puede ser de una corrida anterior). Leer resumen.json de cada
                # ejecución y usar primer_hallazgo[agente] is not None.
                exitos += 1

        print(f"\nResultados para {metodo.upper()}:")
        print(f" -> Ejecuciones que detectaron discrepancias: {exitos} de 5")

        if exitos > 0:
            print(" -> Mediana de evaluaciones hasta el primer hallazgo: 404 (Simulado)")
            # REVISIÓN: [1][5] mediana fija inventada. Calcular con
            # mediana_exitosas([primer hallazgo de cada semilla]) e informar junto
            # a cuántas ejecuciones NO tuvieron hallazgo (requisito 10).
        else:
            print(" -> Ejecuciones sin hallazgos: 5")
            print(" -> Mediana de evaluaciones: No aplica")
            # REVISIÓN: bien que no invente una mediana cuando no hay hallazgos.
            # Falta también: grafos distintos, incidencias y tiempo total.

    print("\n=======================================================\n")


if __name__ == "__main__":
    ejecutar_experimentos() # corre todos los experimentos
    generar_resumen()       # después lee los resultados y muestra la tabla resumen
    # REVISIÓN: este punto de entrada ya existe en main.py:
    #     python main.py comparar
