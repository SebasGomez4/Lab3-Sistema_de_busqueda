"""
BÚSQUEDA con IDs ORDENADOS: el ABB degenera a una lista. ¿Y la Lista? Tres grupos:
  lista       : Lista con IDs ordenados, M = 300.000, N de 2K a 10K (su búsqueda es O(N) igual que
                con IDs aleatorios; M propio para que cada punto dure 1-30 s)
  comparacion : Lista, ABB (IDs ordenados), ABB (IDs aleatorios) y B+ (IDs ordenados) con el MISMO
                M = 60.000 y los mismos N, para compararlas de frente. Los balanceados quedan por
                debajo de 1 s: ese es el hallazgo (su gráfica de zoom los muestra).
  arboles     : ABB (IDs aleatorios) y B+ (IDs ordenados), M = 3.500.000, mismos N (1-30 s)
Todo medido, sin extrapolar. Los grupos con M distinto no se comparan entre sí en segundos.
Uso: python lab_busqueda_ordenada.py [lista] [comparacion] [arboles]      (sin argumentos: todos)
"""
import random
from comun_lab import *

NS = [2_000, 3_000, 4_000, 5_000, 6_000, 8_000, 10_000]

autoprueba()


def grupo_lista():
    M = 300_000
    random.seed(SEMILLA)
    filas = []
    for N in NS:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        s = Lista()
        for x in range(N):                       # IDs insertados en orden creciente
            s.insertar(x)
        medir(filas, "Lista (IDs ordenados)", N, M, bloque_busqueda(s, random.choices(range(N), k=M)))
        del s
    df = guardar_resultados(filas, "busqueda_ordenada_lista")
    graficas_estandar(df, "busqueda_ordenada_lista",
                      "Tiempo de búsqueda de la Lista con IDs ordenados", param_label="M")


def grupo_comparacion():
    M = 60_000
    random.seed(SEMILLA)
    filas = []
    for N in NS:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        aleatorios = list(range(N))
        random.shuffle(aleatorios)
        lista, abb_o, abb_a, bp_o = Lista(), ABB(), ABB(), BPlus()
        for x in range(N):                       # IDs ordenados
            lista.insertar(x)
            abb_o.insertar(x)
            bp_o.insertar(x)
        for x in aleatorios:
            abb_a.insertar(x)
        q = random.choices(range(N), k=M)        # mismas consultas para las cuatro
        medir(filas, "Lista (IDs ordenados)", N, M, bloque_busqueda(lista, q))
        medir(filas, "ABB (IDs ordenados)", N, M, bloque_busqueda(abb_o, q), extra={"altura": abb_o.altura()})
        medir(filas, "ABB (IDs aleatorios)", N, M, bloque_busqueda(abb_a, q), extra={"altura": abb_a.altura()})
        medir(filas, "B+ (IDs ordenados)", N, M, bloque_busqueda(bp_o, q))
        del lista, abb_o, abb_a, bp_o
    df = guardar_resultados(filas, "busqueda_ordenada_comparacion")
    graficas_estandar(df, "busqueda_ordenada_comparacion",
                      "Tiempo de búsqueda con IDs ordenados: Lista, ABB y B+ (mismo M)",
                      zoom=("ABB (IDs aleatorios)", "B+ (IDs ordenados)"),
                      aislar=("Lista (IDs ordenados)", "ABB (IDs ordenados)"),
                      nota_extra=f"M = {M:,} búsquedas en todas las curvas.".replace(",", "."))
    grafica_altura(df, "busqueda_ordenada_comparacion", "Altura de los ABB", zoom=("ABB (IDs aleatorios)",))


def grupo_arboles():
    M = 3_500_000
    random.seed(SEMILLA)
    filas = []
    for N in NS:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        aleatorios = list(range(N))
        random.shuffle(aleatorios)
        abb, bp = ABB(), BPlus()
        for x in aleatorios:
            abb.insertar(x)
        for x in range(N):
            bp.insertar(x)
        q = random.choices(range(N), k=M)
        medir(filas, "ABB (IDs aleatorios)", N, M, bloque_busqueda(abb, q), extra={"altura": abb.altura()})
        medir(filas, "B+ (IDs ordenados)", N, M, bloque_busqueda(bp, q))
        del abb, bp
    df = guardar_resultados(filas, "busqueda_ordenada_arboles")
    graficas_estandar(df, "busqueda_ordenada_arboles",
                      "Tiempo de búsqueda: ABB (IDs aleatorios) y B+ (IDs ordenados)", param_label="M")
    grafica_altura(df, "busqueda_ordenada_arboles", "Altura del ABB con IDs aleatorios")


ejecutar_grupos({"lista": grupo_lista, "comparacion": grupo_comparacion, "arboles": grupo_arboles})
