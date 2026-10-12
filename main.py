"""Punto de entrada de consola (integración grupal).

Ejemplos:
    python main.py ag --semilla 11
    python main.py aleatorio --semilla 11
    python main.py comparar
    python main.py reproducir contraejemplos/caso_01.json
"""
import argparse

import experimentos


def construir_parser():
    p = argparse.ArgumentParser(description="Cazador genético de defectos en B1, U1 y A1")
    sub = p.add_subparsers(dest="comando", required=True)

    for metodo in experimentos.METODOS:
        s = sub.add_parser(metodo, help=f"Una ejecución de desarrollo con el método '{metodo}'")
        s.add_argument("--semilla", type=int, default=11)

    sub.add_parser("comparar", help="Comparación oficial: 2 métodos x 5 semillas")

    r = sub.add_parser("reproducir", help="Vuelve a evaluar un contraejemplo guardado")
    r.add_argument("archivo")
    return p


def main(argv=None):
    args = construir_parser().parse_args(argv)
    if args.comando in experimentos.METODOS:
        experimentos.ejecutar_una(args.comando, args.semilla)
    elif args.comando == "comparar":
        experimentos.comparar()
    elif args.comando == "reproducir":
        experimentos.reproducir(args.archivo)


if __name__ == "__main__":
    main()
