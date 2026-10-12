"""
TAMAÑOS PEQUEÑOS: costos constantes y punto de cruce Lista/árbol.
M común = 2.000.000 búsquedas para las tres estructuras; todo medido, sin extrapolar.
Con N tan pequeño los árboles apenas llegan a 1 s: se reporta tal cual.
Uso: python lab_n_pequenos.py
"""
import random
from comun_lab import *

NS = escalera([10, 20, 50, 100, 200, 300, 500, 700, 1_000])
M = 2_000_000

autoprueba()
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
    for nombre, fabrica in (("Lista", Lista), ("ABB", ABB), ("B+", BPlus)):
        s = fabrica()
        for x in ids:
            s.insertar(x)
        medir(filas, nombre, N, M, bloque_busqueda(s, consultas))

df = guardar_resultados(filas, "n_pequenos")
graficas_estandar(df, "n_pequenos", "Tiempo de búsqueda con tamaños de entrada pequeños",
                  zoom=("ABB", "B+"), aislar=("Lista",),
                  nota_extra=f"M = {M:,} búsquedas en todas las curvas.".replace(",", "."))

g = df.groupby(["estructura", "N"], as_index=False)["tiempo"].mean()
l = g[g.estructura == "Lista"].set_index("N")["tiempo"]
ns = sorted(g["N"].unique())
fig, ax = plt.subplots(figsize=(10, 6))
for e in ("ABB", "B+"):
    t = g[g.estructura == e].set_index("N")["tiempo"]
    r = (l / t).dropna()
    c, _ = estilo_de(e)
    ax.plot([ns.index(n) for n in r.index], r.values, marker="o", color=c, label=f"Lista ÷ {e}")
ax.axhline(1, color="gray", ls=":", label="Empate (cociente = 1)")
ax.set_xticks(range(len(ns)))
ax.set_xticklabels([fmt_n(n) for n in ns])
ax.set_xlabel("Tamaño de entrada N")
ax.set_ylabel("Cociente de tiempos (> 1: la Lista es más lenta)")
ax.set_title("¿Desde qué N gana el árbol a la Lista?")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.7)
cerrar_figura(fig, "n_pequenos_05_cociente.png")
