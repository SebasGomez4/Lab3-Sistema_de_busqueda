"""
BÚSQUEDA con IDs ALEATORIOS, en dos grupos con parámetros propios para que cada punto dure 1-30 s:
  lista   : M = 10.000 búsquedas, N de 40K a 200K  (la búsqueda es O(N): M debe ser pequeño)
  arboles : M = 2.000.000 búsquedas, N de 5K a 1M  (ABB y B+ comparten M: se comparan entre sí)
Todo medido, sin extrapolar. Los grupos no se comparan entre sí en segundos (M distinto).
Uso: python lab_busqueda_aleatoria.py [lista] [arboles]      (sin argumentos: ambos)
"""
import random
from comun_lab import *

autoprueba()


def grupo_lista():
    NS = [40_000, 60_000, 80_000, 100_000, 125_000, 150_000, 200_000]
    M = 10_000
    random.seed(SEMILLA)
    filas = []
    for N in NS:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        ids = list(range(N))
        random.shuffle(ids)
        s = Lista()
        for x in ids:
            s.insertar(x)
        medir(filas, "Lista", N, M, bloque_busqueda(s, random.choices(range(N), k=M)))
        del s
    df = guardar_resultados(filas, "busqueda_aleatoria_lista")
    graficas_estandar(df, "busqueda_aleatoria_lista", "Tiempo de búsqueda de la Lista según el tamaño de entrada",
                      param_label="M")


def grupo_arboles():
    NS = [5_000, 10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]
    M = 2_000_000
    random.seed(SEMILLA)
    filas = []
    for N in NS:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        ids = list(range(N))
        random.shuffle(ids)
        consultas = random.choices(range(N), k=M)
        for nombre, fabrica in (("ABB", ABB), ("B+", BPlus)):
            s = fabrica()
            for x in ids:
                s.insertar(x)
            medir(filas, nombre, N, M, bloque_busqueda(s, consultas),
                  extra={"altura": s.altura() if nombre == "ABB" else None})
            del s
    df = guardar_resultados(filas, "busqueda_aleatoria_arboles")
    graficas_estandar(df, "busqueda_aleatoria_arboles", "Tiempo de búsqueda de ABB y B+ según el tamaño de entrada",
                      param_label="M")


ejecutar_grupos({"lista": grupo_lista, "arboles": grupo_arboles})
