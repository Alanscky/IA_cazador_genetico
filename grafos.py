import json
from nodo import Nodo

class Grafo:
    def __init__(self, id_origen, id_destino, nombreJson):
        self.aristas = 0
        self.listaNodos = []
        self.id_origen = None
        self.id_destino = None

        # 1. Validación de argumentos de entrada (id_origen e id_destino deben estar entre 0 y 5)
        if not isinstance(id_origen, int) or not (0 <= id_origen <= 5):
            print("Error: El id_origen proporcionado no es un entero válido entre 0 y 5.")
            return
        if not isinstance(id_destino, int) or not (0 <= id_destino <= 5):
            print("Error: El id_destino proporcionado no es un entero válido entre 0 y 5.")
            return

        # Leemos el archivo .json de forma segura
        try:
            with open(nombreJson, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except Exception as e:
            print(f"Error al leer o decodificar el archivo JSON: {e}")
            return

        nodos_dict = datos.get("nodos")
        if not isinstance(nodos_dict, dict):
            print("Error: El JSON no contiene una estructura 'nodos' válida.")
            return

        # 2. Construcción atómica: Si falla algo, el grafo no se inicializa parcialmente
        if self._construirGrafo(nodos_dict):
            # Validar que los IDs de origen y destino existan en los nodos creados
            origen_nodo = next((n for n in self.listaNodos if n.id == id_origen), None)
            destino_nodo = next((n for n in self.listaNodos if n.id == id_destino), None)

            if not origen_nodo:
                print(f"Error: El nodo origen ({id_origen}) no existe dentro de los 6 nodos del grafo.")
                return
            if not destino_nodo:
                print(f"Error: El nodo destino ({id_destino}) no existe dentro de los 6 nodos del grafo.")
                return

            self.id_origen = id_origen
            self.id_destino = id_destino
            print("Grafo creado e inicializado con éxito.")
        else:
            print("Error: El grafo no pudo ser construido debido a fallas en las restricciones.")
            # Limpieza para evitar dejar un estado parcialmente utilizable
            self.listaNodos = []
            self.aristas = 0

    def _construirGrafo(self, nodos):
        # Exigir exactamente los identificadores del 0 al 5
        esperados = {0, 1, 2, 3, 4, 5}
        
        # Verificar que las llaves principales correspondan exactamente a los 6 nodos requeridos
        keys_convertidas = set()
        for k in nodos.keys():
            if not isinstance(k, str) or not k.isdigit():
                print(f"Error: Identificador de nodo no numérico o inválido en JSON: {k}")
                return False
            keys_convertidas.add(int(k))

        if keys_convertidas != esperados:
            print(f"Error: El grafo debe constar exactamente de los nodos 0 a 5. Encontrados: {sorted(list(keys_convertidas))}")
            return False

        nodos_mapeo = {}
        for i in range(6):
            nodos_mapeo[i] = Nodo(i)

        total_aristas = 0

        # Procesar aristas y restricciones de vecinos
        for id_origen_str, vecinos in nodos.items():
            origen_id = int(id_origen_str)
            nodo_origen = nodos_mapeo[origen_id]

            if not isinstance(vecinos, dict):
                print(f"Error: Los vecinos del nodo {origen_id} deben estructurarse en un objeto/diccionario.")
                return False

            for id_destino_str, costo in vecinos.items():
                if not isinstance(id_destino_str, str) or not id_destino_str.isdigit():
                    print(f"Error: ID de destino inválido: {id_destino_str}")
                    return False

                destino_id = int(id_destino_str)
                if destino_id < 0 or destino_id > 5:
                    print(f"Error: El ID de destino {destino_id} está fuera del rango 0-5.")
                    return False

                # Rechazar booleanos explícitamente (en Python isinstance(True, int) es True)
                if isinstance(costo, bool) or not isinstance(costo, int):
                    print(f"Error: El costo '{costo}' debe ser estrictamente un número entero (no booleano).")
                    return False

                if not (1 <= costo <= 9):
                    print(f"Error: El costo {costo} debe estar entre 1 y 9.")
                    return False

                nodo_destino = nodos_mapeo[destino_id]

                # Intentar añadir la arista evaluando reglas de negocio
                resultado = nodo_origen.addVecino(nodo_destino, costo)

                if resultado == 0:
                    print(f"Error: Se prohíbe conectar al nodo {origen_id} consigo mismo.")
                    return False
                elif resultado == 2:
                    print(f"Error: Se detectó una arista duplicada hacia el mismo destino desde el nodo {origen_id}.")
                    return False
                elif resultado == 1:
                    total_aristas += 1
                    if total_aristas > 30:
                        print("Error: Se ha superado el límite máximo de 30 aristas permitidas.")
                        return False

        self.listaNodos = [nodos_mapeo[i] for i in range(6)]
        self.aristas = total_aristas
        return True




# Parte 2: representación genética (cromosoma)
# Funciones que usan aleatorio.py, evaluacion.py y genetico.py.
N = 6
INICIO = 0
META = 5
COSTO_MIN = 1
COSTO_MAX = 9

# Un gen por cada par dirigido (u, v) con u != v, en orden fijo -> 30 genes.
# Valor del gen: 0 = no hay arista u -> v; 1..9 = hay arista con ese costo.
PARES = [(u, v) for u in range(N) for v in range(N) if u != v]
LONGITUD = len(PARES)  # 30
_INDICE = {par: i for i, par in enumerate(PARES)}

# Probabilidad de que cada par tenga arista al generar al azar.
# DECISIÓN DE DISEÑO: con 30 pares, 0.3 da en promedio ~9 aristas.
# Debe justificarse en el informe (es la distribución común del AG y del aleatorio).
PROB_ARISTA = 0.3


def _es_entero(x):
    """Entero de verdad: rechaza bool, aunque en Python isinstance(True, int) es True."""
    return isinstance(x, int) and not isinstance(x, bool)


def es_valido(crom):
    """True si el cromosoma respeta el dominio: lista de 30 enteros entre 0 y 9.

    Un grafo SIN ruta de 0 a 5 sigue siendo válido: no es un cromosoma mal formado.
    Lazos y duplicados son imposibles por construcción (un gen por par u != v).
    """
    return (isinstance(crom, (list, tuple)) and len(crom) == LONGITUD and
            all(_es_entero(g) and 0 <= g <= COSTO_MAX for g in crom))


def reparar(crom):
    """Regresa una copia válida del cromosoma; no modifica el original.

    Estrategia:
    - Longitud: se recorta a 30 genes o se completa con 0 (sin arista).
    - Genes que no son enteros (incluido bool): se vuelven 0.
    - Enteros menores que 0: se vuelven 0; mayores que 9: se recortan a 9.
    """
    genes = list(crom)[:LONGITUD] + [0] * max(0, LONGITUD - len(crom))
    return [min(max(g, 0), COSTO_MAX) if _es_entero(g) else 0 for g in genes]


def a_grafo(crom):
    """Convierte un cromosoma al dict que espera el paquete docente.

    Regresa {"n": 6, "inicio": 0, "meta": 5, "aristas": [[u, v, w], ...]}.
    Lanza ValueError si el cromosoma no es válido. No modifica `crom`.
    """
    if not es_valido(crom):
        raise ValueError("Cromosoma inválido: se esperan 30 enteros entre 0 y 9")
    aristas = [[u, v, w] for (u, v), w in zip(PARES, crom) if w > 0]
    return {"n": N, "inicio": INICIO, "meta": META, "aristas": aristas}


def desde_grafo(g):
    """Convierte un dict en formato del paquete a cromosoma.

    Sirve para cargar contraejemplos guardados. Lanza ValueError si el dict no
    cumple el dominio (mismas reglas que el paquete docente).
    """
    if not isinstance(g, dict) or set(g) != {"n", "inicio", "meta", "aristas"}:
        raise ValueError("Se requieren exactamente las claves n, inicio, meta y aristas")
    if (g["n"], g["inicio"], g["meta"]) != (N, INICIO, META) or not all(
            _es_entero(g[k]) for k in ("n", "inicio", "meta")):
        raise ValueError("Dominio obligatorio: n=6, inicio=0, meta=5")
    if not isinstance(g["aristas"], (list, tuple)):
        raise ValueError("aristas debe ser una lista")
    crom = [0] * LONGITUD
    for arista in g["aristas"]:
        if (not isinstance(arista, (list, tuple)) or len(arista) != 3 or
                not all(_es_entero(x) for x in arista)):
            raise ValueError(f"Arista inválida: {arista!r}")
        u, v, w = arista
        if (u, v) not in _INDICE or not COSTO_MIN <= w <= COSTO_MAX:
            raise ValueError(f"Arista fuera del dominio: {arista!r}")
        i = _INDICE[(u, v)]
        if crom[i] != 0:
            raise ValueError(f"Arista duplicada: {u} -> {v}")
        crom[i] = w
    return crom


def grafo_aleatorio(rng, prob_arista=PROB_ARISTA):
    """Genera un cromosoma válido al azar usando SOLO `rng` (random.Random).

    Cada par tiene arista con probabilidad `prob_arista`; el costo es uniforme en 1..9.
    Es la distribución inicial COMÚN: la usan genetico.py y aleatorio.py.
    """
    return [rng.randint(COSTO_MIN, COSTO_MAX) if rng.random() < prob_arista else 0
            for _ in range(LONGITUD)]


def num_aristas(crom):
    """Cantidad de aristas presentes (genes distintos de 0)."""
    return sum(1 for g in crom if g != 0)


def clave(crom):
    """Representación inmutable y canónica, para detectar duplicados."""
    return tuple(crom)


def a_texto(crom):
    """Salida textual legible del grafo."""
    aristas = [f"{u}->{v} ({w})" for (u, v), w in zip(PARES, crom) if w > 0]
    return f"{len(aristas)} aristas: " + (", ".join(aristas) if aristas else "ninguna")
