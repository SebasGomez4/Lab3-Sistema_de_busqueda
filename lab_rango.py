"""
CONSULTA POR RANGO MASIVA: cada consulta devuelve 5.001 estudiantes consecutivos. Un grupo por
estructura, cada una con su propio Q y N para que cada punto dure 1-30 s:
  lista : Q = 1.500 consultas,  N de 10K a 100K  (recorre toda la lista en cada consulta)
  abb   : Q = 2.000 consultas,  N de 10K a 1M
  bplus : Q = 30.000 consultas, N de 10K a 1M    (hojas enlazadas: muy rápido por consulta)
Todo medido, sin extrapolar. Los grupos no se comparan entre sí en segundos (Q distinto).
Uso: python lab_rango.py [lista] [abb] [bplus]      (sin argumentos: los tres)
"""
import random
from comun_lab import *

ANCHO = 5_000
LADDER_LISTA = [10_000, 20_000, 30_000, 40_000, 50_000, 60_000, 70_000, 85_000, 100_000]
LADDER_ARBOL = [10_000, 25_000, 50_000, 100_000, 200_000, 300_000, 500_000, 750_000, 1_000_000]

autoprueba()


def grupo(nombre, fabrica, ladder, Q, prefijo, titulo):
    random.seed(SEMILLA)
    filas = []
    for N in ladder:
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        ids = list(range(N))
        random.shuffle(ids)
        s = fabrica()
        for x in ids:
            s.insertar(x)
        los = random.choices(range(N - ANCHO), k=Q)
        medir(filas, nombre, N, Q, bloque_rango(s, los, ANCHO))
        del s
    df = guardar_resultados(filas, prefijo)
    graficas_estandar(df, prefijo, titulo, param_label="Q",
                      nota_extra=f"Q = {Q:,} consultas de {ANCHO + 1:,} estudiantes cada una.".replace(",", "."))


ejecutar_grupos({
    "lista": lambda: grupo("Lista", Lista, LADDER_LISTA, 1_500, "rango_lista",
                           "Tiempo de consulta por rango de la Lista según el tamaño de entrada"),
    "abb": lambda: grupo("ABB", ABB, LADDER_ARBOL, 2_000, "rango_abb",
                         "Tiempo de consulta por rango del ABB según el tamaño de entrada"),
    "bplus": lambda: grupo("B+", BPlus, LADDER_ARBOL, 30_000, "rango_bplus",
                           "Tiempo de consulta por rango del B+ según el tamaño de entrada"),
})
