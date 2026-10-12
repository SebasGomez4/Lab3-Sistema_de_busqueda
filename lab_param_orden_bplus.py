"""
PARÁMETRO DEL B+: orden (máx. hijos por nodo; capacidad de hoja si BPLUS_REAL=False).
N y M fijos; el ABB es la referencia. Todo medido, sin escalar.
Uso: python lab_param_orden_bplus.py
"""
import random
from comun_lab import *

N = 100_000
M = 2_000_000
PARAMETROS = [4, 8, 16, 32, 64, 128, 256] if BPLUS_REAL else [10, 25, 50, 100, 250, 500, 1000]
NOMBRE_PARAM = "orden" if BPLUS_REAL else "capacidad de hoja"

autoprueba()
random.seed(SEMILLA)
filas = []
ids = list(range(N))
random.shuffle(ids)
consultas = random.choices(range(N), k=M)

print(f"\nN = {N}, M = {M}")
for k in PARAMETROS:
    if agotado():
        print("Presupuesto agotado: no se miden los parámetros restantes.")
        break
    s = crear_bplus(k)
    for x in ids:
        s.insertar(x)
    medir(filas, f"B+ ({NOMBRE_PARAM}={k})", N, M, bloque_busqueda(s, consultas),
          extra={"param_k": k, "altura": s.altura()})
    del s
abb = ABB()
for x in ids:
    abb.insertar(x)
medir(filas, "ABB (referencia)", N, M, bloque_busqueda(abb, consultas), extra={"altura": abb.altura()})

df = guardar_resultados(filas, "param_orden_bplus")

bp = df[df["estructura"].str.startswith("B+")].groupby("param_k", as_index=False).agg(
    media=("tiempo", "mean"), std=("tiempo", "std"), altura=("altura", "first")).fillna({"std": 0})
ref = df[df["estructura"].str.startswith("ABB")]
etq = [str(int(k)) for k in bp["param_k"]]
fig, (a, b) = plt.subplots(1, 2, figsize=(14, 6))
a.errorbar(range(len(bp)), bp["media"], yerr=bp["std"], marker="o", capsize=4, color="#ff7f0e",
           label=f"B+ (N={fmt_n(N)}, M={fmt_n(M)})")
a.axhline(ref["tiempo"].mean(), color="#1f77b4", ls="--", label="ABB (mismos N y M)")
b.plot(range(len(bp)), bp["altura"], marker="o", color="#ff7f0e", label="Altura del B+ (niveles)")
b.axhline(ref["altura"].iloc[0], color="#1f77b4", ls="--", label="Altura del ABB")
for ax, yl, t in ((a, "Tiempo promedio (segundos)", "Tiempo de búsqueda según el orden del B+"),
                  (b, "Altura (niveles)", "Altura según el orden del B+ (el ABB tiene altura ~40)")):
    ax.set_xticks(range(len(bp)))
    ax.set_xticklabels(etq)
    ax.set_xlabel(f"{NOMBRE_PARAM.capitalize()} del B+")
    ax.set_ylabel(yl)
    ax.set_title(t)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
a.set_ylim(bottom=0)
b.set_ylim(0, 15)
print("\nGenerando gráficas...")
cerrar_figura(fig, "param_orden_bplus_01.png")
