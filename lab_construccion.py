"""
CONSTRUCCIÓN: insertar N estudiantes con IDs aleatorios, de N = 500K a 1,5M en pasos de 100K.
Dos grupos, para que la Lista (órdenes de magnitud más rápida) no aplaste la gráfica de los árboles:
  arboles : ABB y B+ (superan 1 s desde ~600K-700K en un equipo rápido)
  lista   : la Lista no llega a 1 s con N <= 1,5M: se documenta como hallazgo, no se fuerza el tiempo
  lista_grande : la Lista con N de 4M a 10M, para MEDIR (no extrapolar) dónde cruza 1 s.
                 Memoria: el pico llega a ~800 MB con N = 10M.
Todo medido, sin extrapolar. Memoria: con N = 1,5M el pico es de unos 400 MB.
Uso: python lab_construccion.py [arboles] [lista] [lista_grande]      (sin argumentos: todos)
"""
import random
from comun_lab import *

NS = list(range(500_000, 1_500_001, 100_000))

autoprueba()


def grupo(estructuras, prefijo, titulo, ladder=None):
    random.seed(SEMILLA)
    filas = []
    for N in (ladder or NS):
        if agotado():
            print("Presupuesto agotado: no se miden los N restantes.")
            break
        print(f"\nN = {N}")
        ids = list(range(N))
        random.shuffle(ids)
        for nombre, fabrica in estructuras:
            medir(filas, nombre, N, N, bloque_construccion(fabrica, ids))
    df = guardar_resultados(filas, prefijo)
    graficas_estandar(df, prefijo, titulo)


ejecutar_grupos({
    "arboles": lambda: grupo((("ABB", ABB), ("B+", BPlus)), "construccion_arboles",
                             "Tiempo de construcción de ABB y B+ según el tamaño de entrada"),
    "lista": lambda: grupo((("Lista", Lista),), "construccion_lista",
                           "Tiempo de construcción de la Lista según el tamaño de entrada"),
    "lista_grande": lambda: grupo((("Lista", Lista),), "construccion_lista_grande",
                                  "Tiempo de construcción de la Lista con N muy grande",
                                  ladder=[4_000_000, 5_000_000, 6_000_000, 7_000_000,
                                          8_000_000, 9_000_000, 10_000_000]),
})
