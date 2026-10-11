class Nodo:
    def __init__(self, id_nodo):
        self.id = id_nodo
        # Lista de tuplas: (nodo_vecino, costo)
        self.listaVecinos = []

    def addVecino(self, nodo_vecino, costo):
        """
        Añade un nodo vecino con su respectivo costo.
        Retorna:
        0: Si intenta conectarse a sí mismo.
        1: Si la conexión fue exitosa.
        2: Si la conexión ya existe previamente.
        """
        if nodo_vecino.id == self.id:
            return 0  # Prohibido conectar a un nodo consigo mismo

        # Verificar si ya existe la arista hacia este mismo destino
        for nv, _ in self.listaVecinos:
            if nv.id == nodo_vecino.id:
                return 2  # Conexión duplicada

        self.listaVecinos.append((nodo_vecino, costo))
        return 1