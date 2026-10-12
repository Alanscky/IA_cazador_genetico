import json

class AdaptadorGrafo:
    def __init__(self, grafo):
        """
        Recibe una instancia de la clase Grafo validada y construye 
        el diccionario con el formato requerido.
        """
        self.grafo = grafo

    def generar_diccionario(self):
        """
        Extrae los valores del grafo y los organiza en el formato JSON solicitado.
        """
        # Recolectamos todas las aristas sin duplicar y respetando la estructura interna
        aristas_lista = []
        
        # Recorremos cada nodo del grafo original de forma segura (sin alterarlo)
        for nodo in self.grafo.listaNodos:
            origen_id = nodo.id
            # nodo.listaVecinos contiene tuplas de (nodo_vecino, costo)
            for vecino, costo in nodo.listaVecinos:
                destino_id = vecino.id
                aristas_lista.append([origen_id, destino_id, costo])

        # Estructura final solicitada
        datos_salida = {
            "n": len(self.grafo.listaNodos),
            "inicio": self.grafo.id_origen,
            "meta": self.grafo.id_destino,
            "aristas": aristas_lista
        }
        
        return datos_salida

    def exportar_json(self, nombre_archivo_salida):
        """
        Exporta el diccionario generado a un archivo JSON físico en disco.
        """
        try:
            datos = self.generar_diccionario()
            with open(nombre_archivo_salida, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            print(f"Grafo adaptado y exportado con éxito a '{nombre_archivo_salida}'.")
            return True
        except Exception as e:
            print(f"Error al exportar el archivo JSON adaptado: {e}")
            return False