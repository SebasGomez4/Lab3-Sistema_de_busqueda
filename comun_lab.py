"""
Utilidades comunes de los experimentos lab_*.py (mismo estilo que benchmark_estructuras.py):
estructuras con la misma interfaz, mediciones, CSV y gráficas con eje X equidistante.

Variables de entorno opcionales:
  LAB_PERFIL=rapido   perfil rápido: ~la mitad de los puntos de cada escalera (siempre incluye el
                      primero y el último), 3 repeticiones y sin los grupos redundantes
  LAB_REPS=5          repeticiones por punto (por defecto 5; 3 en el perfil rápido)
  LAB_PRESUPUESTO=570 segundos máximos por script; si se agota, el script deja de abrir
                      nuevos N y grafica lo que ya midió (por defecto 570 s < 10 min)
  LAB_MOSTRAR=1       abre las ventanas de las gráficas (por defecto solo guarda los PNG)
  LAB_NUCLEO=2        núcleo lógico al que se fija el proceso (requiere psutil); -1 = no fijar.
                      Por defecto 2 (o 0 si hay menos de 8 núcleos). Las versiones anteriores fijaban el ÚLTIMO
                      núcleo, que en CPU híbridas Intel (12.ª gen) es un núcleo de eficiencia.

BPLUS_REAL = True  -> B+ completo (nodos internos + hojas enlazadas) de estructuras.py
BPLUS_REAL = False -> el BPlus simplificado del script base (lista de hojas)
"""
import gc
import os
import random
import statistics
import sys
import time
from bisect import bisect_left, bisect_right, insort

import matplotlib
if not os.environ.get("LAB_MOSTRAR"):
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from estructuras import BMas

PERFIL = os.environ.get("LAB_PERFIL", "completo")      # "completo" | "rapido"
REPETICIONES = int(os.environ.get("LAB_REPS", 3 if PERFIL == "rapido" else 5))
PRESUPUESTO_S = float(os.environ.get("LAB_PRESUPUESTO", 570))
BPLUS_REAL = True
ORDEN_BPLUS = 64          # máx. hijos por nodo (B+ real)
CAPACIDAD_HOJA = 100      # capacidad por hoja (B+ simplificado)
SEMILLA = 2026
CARPETA = "resultados_lab3"
_T0 = time.time()


def reducir_ruido():
    """Reduce la interferencia del sistema: prioridad alta y un solo núcleo (si psutil existe)."""
    acciones = []
    try:
        import psutil
        p = psutil.Process()
        try:
            p.nice(psutil.HIGH_PRIORITY_CLASS if os.name == "nt" else -5)
            acciones.append("prioridad alta")
        except Exception:
            pass
        try:
            n = psutil.cpu_count() or 1
            pedido = os.environ.get("LAB_NUCLEO", "auto")
            if pedido == "-1":
                acciones.append("sin fijar núcleo (LAB_NUCLEO=-1)")
            else:
                # auto: núcleo lógico 2 (en CPU híbridas de Intel los primeros son núcleos de rendimiento y
                # los últimos de eficiencia: NO se usa el último); LAB_NUCLEO=<n> fuerza otro
                nucleo = int(pedido) if pedido != "auto" else (2 if n >= 8 else 0)
                p.cpu_affinity([nucleo])
                acciones.append(f"fijado al núcleo lógico {nucleo} de {n}")
        except Exception:
            pass
    except ImportError:
        acciones.append("sin psutil (opcional: pip install psutil)")
    print("Control de ruido: gc desactivado durante cada medición, gc.freeze, calentamiento, "
          "tiempo de CPU registrado; " + ", ".join(acciones) + ".")


reducir_ruido()


def agotado():
    return time.time() - _T0 > PRESUPUESTO_S


def escalera(ladder):
    """Perfil rápido: se queda con un punto de cada dos (y siempre con el último)."""
    ladder = list(ladder)
    if PERFIL != "rapido" or len(ladder) <= 4:
        return ladder
    sub = ladder[::2]
    if sub[-1] != ladder[-1]:
        sub.append(ladder[-1])
    return sub


def reiniciar_reloj():
    """Cada grupo de un experimento tiene su propio presupuesto de tiempo."""
    global _T0
    _T0 = time.time()


def ejecutar_grupos(grupos, omitir_rapido=()):
    """
    grupos: {nombre: función}. Uso: python lab_x.py [grupo ...]; sin argumentos corre todos,
    uno tras otro, cada uno con su propio presupuesto (LAB_PRESUPUESTO) y sus propias gráficas.
    """
    pedidos = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not pedidos:
        pedidos = [g for g in grupos if not (PERFIL == "rapido" and g in omitir_rapido)]
        if PERFIL == "rapido" and omitir_rapido:
            print(f"Perfil rápido: se omiten los grupos redundantes {', '.join(omitir_rapido)} "
                  "(se pueden pedir por nombre).")
    for g in pedidos:
        if g not in grupos:
            sys.exit(f"Grupo desconocido: {g}. Disponibles: {', '.join(grupos)}")
    print(f"Grupos disponibles: {', '.join(grupos)}  |  se ejecutan: {', '.join(pedidos)}")
    for g in pedidos:
        print("\n" + "=" * 78)
        print(f"GRUPO: {g}")
        print("=" * 78)
        reiniciar_reloj()
        grupos[g]()


# --------------------------------------------------------------------------- #
# Estructuras (todas guardan enteros y exponen insertar/buscar/rango/listar)
# --------------------------------------------------------------------------- #
class Lista:
    def __init__(self):
        self.datos = []

    def insertar(self, valor):
        self.datos.append(valor)

    def buscar(self, valor):
        return valor in self.datos

    def rango(self, lo, hi):
        return sorted(x for x in self.datos if lo <= x <= hi)

    def listar(self):
        return sorted(self.datos)


class ListaOrdenada:
    """Lista mantenida en orden: búsqueda binaria O(log N), inserción O(N) (insort)."""

    def __init__(self):
        self.datos = []

    def insertar(self, valor):
        insort(self.datos, valor)

    def buscar(self, valor):
        d = self.datos
        i = bisect_left(d, valor)
        return i < len(d) and d[i] == valor

    def rango(self, lo, hi):
        d = self.datos
        return d[bisect_left(d, lo):bisect_right(d, hi)]

    def listar(self):
        return list(self.datos)


def lista_ordenada_desde(ids):
    """Construye la Lista ordenada de una vez (sorted) para los experimentos de búsqueda."""
    s = ListaOrdenada()
    s.datos = sorted(ids)
    return s


class NodoABB:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None


class ABB:
    """ABB iterativo (el del script base) + rango, listar y altura."""

    def __init__(self):
        self.raiz = None

    def insertar(self, valor):
        if self.raiz is None:
            self.raiz = NodoABB(valor)
            return
        actual = self.raiz
        while True:
            if valor < actual.valor:
                if actual.izquierda is None:
                    actual.izquierda = NodoABB(valor)
                    return
                actual = actual.izquierda
            else:
                if actual.derecha is None:
                    actual.derecha = NodoABB(valor)
                    return
                actual = actual.derecha

    def buscar(self, valor):
        actual = self.raiz
        while actual is not None:
            if valor == actual.valor:
                return True
            actual = actual.izquierda if valor < actual.valor else actual.derecha
        return False

    def listar(self):
        res, pila, x = [], [], self.raiz
        while pila or x is not None:
            while x is not None:
                pila.append(x)
                x = x.izquierda
            x = pila.pop()
            res.append(x.valor)
            x = x.derecha
        return res

    def rango(self, lo, hi):
        res, pila, x = [], [], self.raiz
        while pila or x is not None:
            while x is not None:
                if x.valor >= lo:
                    pila.append(x)
                    x = x.izquierda
                else:
                    x = x.derecha
            if not pila:
                break
            x = pila.pop()
            if x.valor > hi:
                break
            res.append(x.valor)
            x = x.derecha
        return res

    def altura(self):
        if self.raiz is None:
            return 0
        mx, pila = 0, [(self.raiz, 1)]
        while pila:
            x, d = pila.pop()
            mx = max(mx, d)
            if x.izquierda is not None:
                pila.append((x.izquierda, d + 1))
            if x.derecha is not None:
                pila.append((x.derecha, d + 1))
        return mx


class BPlusSimple:
    """El BPlus del script base (lista de hojas + búsqueda binaria), con rango y listar."""

    def __init__(self, capacidad=CAPACIDAD_HOJA):
        self.capacidad = capacidad
        self.hojas = [[]]

    def _obtener_hoja_idx(self, valor):
        low, high = 0, len(self.hojas) - 1
        ans = high
        while low <= high:
            mid = (low + high) // 2
            hoja = self.hojas[mid]
            if not hoja or valor <= hoja[-1]:
                ans = mid
                high = mid - 1
            else:
                low = mid + 1
        return ans

    def insertar(self, valor):
        idx = self._obtener_hoja_idx(valor)
        hoja = self.hojas[idx]
        if not hoja or valor <= hoja[-1]:
            hoja.insert(bisect_left(hoja, valor), valor)
            if len(hoja) > self.capacidad:
                mitad = len(hoja) // 2
                nueva = hoja[mitad:]
                del hoja[mitad:]
                self.hojas.insert(idx + 1, nueva)
            return
        hoja = self.hojas[-1]
        hoja.append(valor)
        if len(hoja) > self.capacidad:
            mitad = len(hoja) // 2
            nueva = hoja[mitad:]
            del hoja[mitad:]
            self.hojas.append(nueva)

    def buscar(self, valor):
        hoja = self.hojas[self._obtener_hoja_idx(valor)]
        pos = bisect_left(hoja, valor)
        return pos < len(hoja) and hoja[pos] == valor

    def rango(self, lo, hi):
        idx = self._obtener_hoja_idx(lo)
        res = []
        for i in range(idx, len(self.hojas)):
            hoja = self.hojas[i]
            if not hoja:
                continue
            a = bisect_left(hoja, lo) if i == idx else 0
            b = bisect_right(hoja, hi)
            res.extend(hoja[a:b])
            if b < len(hoja):
                break
        return res

    def listar(self):
        return [x for h in self.hojas for x in h]

    def altura(self):
        return 2   # índice de hojas + hojas


class BPlusReal(BMas):
    """B+ completo de estructuras.py; guarda enteros como registros (valor,)."""

    def __init__(self, orden=ORDEN_BPLUS):
        super().__init__(orden=orden)

    def insertar(self, valor):
        super().insertar((valor,))


def crear_bplus(k=None):
    """k = orden (B+ real) o capacidad de hoja (B+ simplificado)."""
    if BPLUS_REAL:
        return BPlusReal(orden=k or ORDEN_BPLUS)
    return BPlusSimple(capacidad=k or CAPACIDAD_HOJA)


def BPlus():
    return crear_bplus()


def _claves(res):
    return [r[0] if isinstance(r, tuple) else r for r in res]


def autoprueba():
    """Las tres estructuras deben coincidir en buscar, rango y listar."""
    rng = random.Random(1)
    for N in (1, 2, 10, 300, 3000):
        ids = list(range(N))
        rng.shuffle(ids)
        ests = [Lista(), ListaOrdenada(), ABB(), BPlus()]
        for s in ests:
            for x in ids:
                s.insertar(x)
        for s in ests:
            assert _claves(s.listar()) == list(range(N)), type(s).__name__
            assert s.buscar(N // 2) and not s.buscar(N + 5) and not s.buscar(-1)
            for _ in range(20):
                lo = rng.randint(0, N)
                hi = lo + rng.randint(0, N)
                esperado = [x for x in range(N) if lo <= x <= hi]
                assert _claves(s.rango(lo, hi)) == esperado, (type(s).__name__, N, lo, hi)
    print("Autoprueba OK (Lista, ABB y B+ coinciden). "
          f"B+ usado: {'completo (estructuras.py)' if BPLUS_REAL else 'simplificado'}.")


# --------------------------------------------------------------------------- #
# Bloques cronometrados y verificación de correctitud
# --------------------------------------------------------------------------- #
def bloque_construccion(fabrica, ids):
    def f():
        s = fabrica()
        ins = s.insertar
        for x in ids:
            ins(x)
        return s
    return f


def bloque_busqueda(s, consultas):
    assert all(s.buscar(x) for x in consultas[:200]), "búsqueda incorrecta"
    buscar = s.buscar
    for x in consultas[:5000]:      # calentamiento (no se cronometra)
        buscar(x)

    def f():
        for x in consultas:
            buscar(x)
    return f


def bloque_rango(s, los, ancho):
    for lo in los[:3]:
        assert len(s.rango(lo, lo + ancho)) == ancho + 1, "rango incorrecto"
    rango = s.rango
    for lo in los[:50]:             # calentamiento (no se cronometra)
        rango(lo, lo + ancho)

    def f():
        for lo in los:
            rango(lo, lo + ancho)
    return f


def bloque_listado(s, N, K):
    assert _claves(s.listar()) == list(range(N)), "listado incorrecto"
    listar = s.listar

    def f():
        for _ in range(K):
            listar()
    return f


def cronometrar(f):
    """Devuelve (tiempo de pared, tiempo de CPU) de f(), con el recolector de basura apagado."""
    gc.collect()
    gc.freeze()          # lo ya construido no entra al recolector
    gc.disable()
    c0 = time.process_time()
    t0 = time.perf_counter()
    r = f()
    t = time.perf_counter() - t0
    c = time.process_time() - c0
    gc.enable()
    gc.unfreeze()
    del r
    return t, c


def fmt_n(n):
    n = float(n)
    if n >= 1e6:
        return f"{n / 1e6:g}M"
    if n >= 1e3:
        return f"{n / 1e3:g}K"
    return f"{n:g}"


def medir(filas, estructura, N, param, f, extra=None, reps=None):
    """
    Repite REPETICIONES veces el bloque f (todo medido, nada extrapolado), guarda las filas e
    imprime promedio y desviación. param = M (o Q, o K, o N) del bloque.
    """
    reps = reps or REPETICIONES
    tiempos = []
    for r in range(reps):
        if r >= 1 and agotado():
            print("  (presupuesto agotado: menos repeticiones en este punto)")
            break
        t, c = cronometrar(f)
        tiempos.append(t)
        fila = {"estructura": estructura, "N": N, "param": param, "repeticion": r + 1,
                "tiempo": t, "tiempo_cpu": c}
        if extra:
            fila.update(extra)
        filas.append(fila)
    prom = statistics.mean(tiempos)
    desv = statistics.stdev(tiempos) if len(tiempos) > 1 else 0.0
    marca = "ok " if 1 <= prom <= 300 else ("<1s" if prom < 1 else ">5m")
    ruido = "  RUIDO>5%" if prom > 0 and desv / prom > 0.05 else ""
    print(f"  {estructura:<22} N={fmt_n(N):>6} param={fmt_n(param):>6}  promedio = {prom:8.4f} s | "
          f"desviación = {desv:7.4f} s  [{marca}]{ruido}  ({time.time() - _T0:4.0f} s)", flush=True)


# --------------------------------------------------------------------------- #
# Resultados y gráficas (mismo formato que benchmark_estructuras.py)
# --------------------------------------------------------------------------- #
def estilo_de(nombre):
    """Misma paleta del script base: ABB azul, B+ naranja, Lista verde."""
    if nombre.startswith("Lista ordenada"):
        return "#17becf", "-"
    if nombre.startswith("Lista"):
        return "#2ca02c", "-"
    if nombre.startswith("B+"):
        return ("#9467bd", "--") if "ordenado" in nombre else ("#ff7f0e", "-")
    if nombre.startswith("ABB"):
        return ("#d62728", "--") if "ordenado" in nombre else ("#1f77b4", "-")
    return "#7f7f7f", "-"


def guardar_resultados(filas, prefijo):
    os.makedirs(CARPETA, exist_ok=True)
    df = pd.DataFrame(filas)
    df.to_csv(f"{CARPETA}/{prefijo}.csv", index=False)
    g = df.groupby(["estructura", "N", "param"], as_index=False).agg(
        n=("tiempo", "size"), media=("tiempo", "mean"), std=("tiempo", "std"),
        mediana=("tiempo", "median"), minimo=("tiempo", "min"), maximo=("tiempo", "max"),
        media_cpu=("tiempo_cpu", "mean"))
    g["cv"] = g["std"] / g["media"]
    tcrit = g["n"].apply(lambda n: stats.t.ppf(0.975, n - 1) if n > 1 else np.nan)
    g["ic95_semiancho"] = tcrit * g["std"] / np.sqrt(g["n"])
    g["en_rango_1_300s"] = (g["media"] >= 1) & (g["media"] <= 300)
    g.to_csv(f"{CARPETA}/resumen_{prefijo}.csv", index=False, float_format="%.6g")
    print(f"\nCSV: {CARPETA}/{prefijo}.csv  y  {CARPETA}/resumen_{prefijo}.csv")
    print(f"Puntos con media en 1–300 s: {int(g['en_rango_1_300s'].sum())} de {len(g)}. "
          f"Puntos con media > 30 s: {int((g['media'] > 30).sum())}. "
          f"Repeticiones por punto: {int(g['n'].min())}–{int(g['n'].max())}.")
    ruidosos = g[g["cv"] > 0.05]
    if len(ruidosos):
        print(f"AVISO: {len(ruidosos)} puntos con coeficiente de variación > 5% (ruido del equipo): "
              "cierre programas y repita; ver 'cv' en el resumen.")
    pend = []
    for est, d in g.groupby("estructura"):
        if d["N"].nunique() >= 3 and (d["media"] > 0).all():
            r = stats.linregress(np.log10(d["N"].astype(float)), np.log10(d["media"]))
            pend.append({"estructura": est, "pendiente_loglog_tiempo_vs_N": round(r.slope, 3),
                         "error_estandar": round(r.stderr, 3), "r2": round(r.rvalue ** 2, 4),
                         "n_puntos": len(d)})
    if pend:
        pdf = pd.DataFrame(pend)
        pdf.to_csv(f"{CARPETA}/pendientes_{prefijo}.csv", index=False)
        print("\nPendiente del tiempo vs N en log-log, solo como cálculo (≈0: O(log N) | ≈1: O(N) | ≈2: O(N²)):")
        print(pdf.to_string(index=False))
    return df


def cerrar_figura(fig, archivo):
    fig.tight_layout()
    ruta = f"{CARPETA}/{archivo}"
    fig.savefig(ruta, dpi=300)
    print("  ->", ruta)
    if os.environ.get("LAB_MOSTRAR"):
        plt.show()
    plt.close(fig)


def graficas_estandar(df, prefijo, titulo, zoom=None, aislar=None, xlabel="Tamaño de entrada N",
                      nota_extra="", param_label=""):
    """
    Gráficas del script base, en segundos y escala lineal (sin escala logarítmica):
      01 comparación general | 02 zoom en `zoom` | 03 `aislar` | 04 media y desviación estándar
    """
    g = df.groupby(["estructura", "N"], as_index=False).agg(
        media=("tiempo", "mean"), std=("tiempo", "std"), n=("tiempo", "size"),
        param=("param", "first")).fillna({"std": 0})
    ns = sorted(g["N"].unique())
    xmap = {n: i for i, n in enumerate(ns)}
    ests = list(dict.fromkeys(df["estructura"]))
    R = int(g["n"].max())
    nota = f"Media de R={R} repeticiones; todos los tiempos son medidos. {nota_extra}".strip()

    def dibujar(archivo, estructuras, tit, barras=False):
        estructuras = [e for e in estructuras if e in ests]
        if not estructuras:
            return
        fig, ax = plt.subplots(figsize=(10, 6))
        for e in estructuras:
            d = g[g.estructura == e].sort_values("N")
            x = [xmap[n] for n in d["N"]]
            color, ls = estilo_de(e)
            p = fmt_n(d["param"].iloc[0]) if d["param"].nunique() == 1 and etiquetar_param else None
            lab = f"{e} ({etiquetar_param}={p})" if p else e
            if barras:
                ax.errorbar(x, d["media"], yerr=d["std"], marker="o", capsize=4, color=color,
                            ls=ls, label=lab)
            else:
                ax.plot(x, d["media"], marker="o", color=color, ls=ls, label=lab)
        ax.set_xticks(range(len(ns)))
        ax.set_xticklabels([fmt_n(n) for n in ns])
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Tiempo promedio (segundos)")
        ax.set_title(tit)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        fig.text(0.5, 0.005, nota, ha="center", fontsize=7, style="italic", color="#444")
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        ruta = f"{CARPETA}/{prefijo}_{archivo}"
        fig.savefig(ruta, dpi=300)
        print("  ->", ruta)
        if os.environ.get("LAB_MOSTRAR"):
            plt.show()
        plt.close(fig)

    etiquetar_param = param_label
    print("\nGenerando gráficas...")
    dibujar("01_comparacion_general.png", ests, titulo)
    if zoom:
        dibujar("02_zoom.png", zoom, f"Escalabilidad de {' y '.join(zoom)} (zoom)")
    if aislar:
        dibujar("03_aislada.png", aislar, f"Escalabilidad de {' y '.join(aislar)}")
    dibujar("04_desviacion_estandar.png", ests, "Tiempo promedio y desviación estándar", barras=True)


def grafica_altura(df, prefijo, titulo, zoom=None):
    """Altura de los árboles: izquierda todo (lineal), derecha zoom en los balanceados."""
    d = df.dropna(subset=["altura"])
    if d.empty:
        return
    g = d.groupby(["estructura", "N"], as_index=False)["altura"].mean()
    ns = sorted(g["N"].unique())
    xmap = {n: i for i, n in enumerate(ns)}
    paneles = 2 if zoom else 1
    fig, axs = plt.subplots(1, paneles, figsize=(14 if zoom else 8, 6))
    axs = np.atleast_1d(axs)
    a = axs[0]
    b = axs[1] if zoom else None
    xs = np.linspace(0, len(ns) - 1, 100)
    nn = np.interp(xs, range(len(ns)), ns)
    for ax, ests, refs in [(a, list(dict.fromkeys(g["estructura"])), True)] + (
            [(b, [e for e in zoom if e in set(g["estructura"])], False)] if zoom else []):
        for e in ests:
            x = g[g.estructura == e].sort_values("N")
            color, ls = estilo_de(e)
            ax.plot([xmap[n] for n in x["N"]], x["altura"], marker="o", color=color, ls=ls, label=e)
        ax.plot(xs, np.log2(nn) + 1, ":", color="gray", label="log₂(N)+1 (balanceado)")
        if refs:
            ax.plot(xs, nn, "-.", color="gray", alpha=0.6, label="N (degenerado)")
        ax.set_xticks(range(len(ns)))
        ax.set_xticklabels([fmt_n(n) for n in ns])
        ax.set_xlabel("Tamaño de entrada N")
        ax.set_ylabel("Altura del árbol (niveles)")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
    a.set_title("Altura del árbol")
    if zoom:
        b.set_title("Altura del árbol (zoom en los árboles balanceados)")
    cerrar_figura(fig, f"{prefijo}_05_altura.png")
