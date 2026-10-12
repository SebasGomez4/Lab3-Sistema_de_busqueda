"""
PARÁMETRO M: con N fijo el tiempo total debe crecer linealmente con M (pendiente log-log = 1).
Todo medido. Muestra cómo escala el tiempo con M en cada estructura (pendiente medida).
Uso: python lab_param_M.py
"""
import random
from comun_lab import *

CASOS = {   # estructura: (N fijo, [M1, M2, M3] = M1 x 1, 2, 3)
    "Lista": (10_000, [35_000, 70_000, 105_000]),
    "ABB": (100_000, [1_000_000, 2_000_000, 3_000_000]),
    "B+": (100_000, [1_500_000, 3_000_000, 4_500_000]),
}
FABRICAS = {"Lista": Lista, "ABB": ABB, "B+": BPlus}

autoprueba()
random.seed(SEMILLA)
filas = []

for nombre, (N, Ms) in CASOS.items():
    if agotado():
        print("Presupuesto agotado: no se miden las estructuras restantes.")
        break
    print(f"\n{nombre}  (N = {N})")
    ids = list(range(N))
    random.shuffle(ids)
    s = FABRICAS[nombre]()
    for x in ids:
        s.insertar(x)
    for k, M in enumerate(Ms, 1):
        consultas = random.choices(range(N), k=M)
        medir(filas, nombre, N, M, bloque_busqueda(s, consultas), extra={"factor_M": k})

df = guardar_resultados(filas, "param_M")

g = df.groupby(["estructura", "N", "factor_M", "param"], as_index=False).agg(
    media=("tiempo", "mean"), std=("tiempo", "std")).fillna({"std": 0})
fig, ax = plt.subplots(figsize=(10, 6))
for e in dict.fromkeys(g["estructura"]):
    d = g[g.estructura == e].sort_values("factor_M")
    if len(d) < 2:
        continue
    pend = np.polyfit(np.log10(d["param"]), np.log10(d["media"]), 1)[0]
    print(f"Pendiente log-log tiempo vs M ({e}): {pend:.3f}  (teórica: 1)")
    c, _ = estilo_de(e)
    ax.errorbar(d["factor_M"], d["media"], yerr=d["std"], marker="o", capsize=4, color=c,
                label=f"{e} (N={fmt_n(d['N'].iloc[0])}, M inicial={fmt_n(d['param'].iloc[0])}) "
                      f"pendiente = {pend:.2f}")
    ax.plot(d["factor_M"], d["media"].iloc[0] * d["factor_M"], ":", color=c, alpha=0.6)
ax.plot([], [], ":", color="gray", label="Crecimiento lineal ideal (punteado)")
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(["M", "2M", "3M"])
ax.set_xlabel("Número de búsquedas (múltiplo del M inicial de cada estructura)")
ax.set_ylabel("Tiempo promedio (segundos)")
ax.set_title("Tiempo de búsqueda según el número de búsquedas M (N fijo)")
ax.legend(fontsize=8)
ax.grid(True, linestyle="--", alpha=0.7)
print("\nGenerando gráficas...")
cerrar_figura(fig, "param_M_01_escala_con_M.png")
