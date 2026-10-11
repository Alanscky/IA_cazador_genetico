import sys
from pathlib import Path

# Ajuste de rutas tras integrar al proyecto: la raíz para importar y tests/datos para el JSON.
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
DATOS = RAIZ / "tests" / "datos"

from grafos import Grafo

def main():
    # Archivo JSON que contiene la definición del grafo
    archivo_json = DATOS / "grafo.json"

    # Nodo de inicio y nodo objetivo
    id_origen = 0
    id_destino = 5

    print("=== Prueba de la clase Grafo ===")

    # Construir el grafo
    grafo = Grafo(id_origen, id_destino, archivo_json)

    # Comprobar si la inicialización terminó correctamente
    if grafo.id_origen is None or grafo.id_destino is None:
        print("\nNo se pudo inicializar el grafo.")
        return

    print("\nGrafo inicializado correctamente.")
    print(f"Nodo de origen: {grafo.id_origen}")
    print(f"Nodo de destino: {grafo.id_destino}")
    print(f"Total de aristas: {grafo.aristas}")

    # Mostrar los nodos y sus conexiones
    print("\n=== Lista de adyacencia ===")

    for nodo in grafo.listaNodos:
        print(f"\nNodo {nodo.id}:")

        if not nodo.listaVecinos:
            print("  Sin vecinos.")
            continue

        for vecino, costo in nodo.listaVecinos:
            print(f"  -> Nodo {vecino.id}, costo: {costo}")


if __name__ == "__main__":
    main()