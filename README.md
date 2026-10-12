# Laboratorio 3 — Lista vs ABB vs B+

Estudio experimental de tres estructuras de almacenamiento (Lista, ABB, B+) para un sistema de
búsqueda de estudiantes: cómo escala el tiempo de búsqueda, inserción y consulta por rango.

## Contenido del repositorio
| Ruta | Qué es |
|---|---|
| `estructuras.py`, `comun_lab.py` | Estructuras de datos y utilidades de medición/gráficas |
| `lab_*.py` | Un script por experimento (ver tabla abajo) |
| `correr_todo.py`, `registrar_entorno.py` | Corre todo y registra tiempos y hardware |
| `resultados_lab3/` | CSV de resultados y **gráficas PNG** (no hace falta volver a correr para verlas) |
| `informe/informe.md` | Informe: método, resultados, interpretación y limitaciones |
| `USO_DE_IA.md`, `CODIGO_DE_HONOR.md` | Declaración de uso de IA y código de honor |

Un script por experimento, en el estilo de `benchmark_estructuras.py`: eje X equidistante, segundos
en escala lineal, CSV + PNG a 300 dpi. **Todos los tiempos son medidos** (nada extrapolado) y no hay
gráficas logarítmicas. Cada script importa `comun_lab.py` y `estructuras.py`.

## Grupos: cada estructura (o par que comparte M) con sus propios M y N
Para que cada punto dure 1–30 s, la Lista, el ABB y el B+ no comparten parámetros cuando sus
velocidades son muy distintas. Cada grupo genera sus propias gráficas y corre con su propio
presupuesto de tiempo (570 s). Los grupos no se comparan entre sí en segundos (M o Q distinto); se
comparan por la forma de la curva y por la pendiente.

| Script | Grupos (comando) | Parámetros |
|---|---|---|
| `lab_busqueda_aleatoria.py` | `lista` | M = 10.000, N de 40K a 200K |
| | `arboles` (ABB y B+) | M = 2.000.000, N de 5K a 1M |
| `lab_busqueda_ordenada.py` | `lista` (Lista con IDs ordenados) | M = 300.000, N de 2K a 10K |
| | `comparacion` (Lista, ABB ordenado, ABB aleatorio y B+ ordenado) | M común = 60.000, mismos N |
| | `arboles` (ABB aleatorio y B+ ordenado) | M = 3.500.000, mismos N |
| `lab_rango.py` (5.001 estudiantes por consulta) | `lista` | Q = 1.500, N de 10K a 100K |
| | `abb` | Q = 2.000, N de 10K a 1M |
| | `bplus` | Q = 30.000, N de 10K a 1M |
| `lab_construccion.py` | `arboles` (ABB y B+) | N de 500K a 1,5M, paso 100K |
| | `lista` (hallazgo: < 1 s) | mismos N |
| | `lista_grande` (mide dónde cruza 1 s; ~800 MB de memoria) | N de 4M a 10M |
| `lab_lista_ordenada.py` (OPCIONAL: lista mantenida en orden + bisect, otra estructura) | `busqueda` | M = 4.000.000, N de 5K a 1M |
| | `construccion` (insort uno a uno, cuadrático) | N de 150K a 400K |
| | `comparacion` (Lista vs Lista ordenada, mismo M) | M = 10.000, N de 50K a 200K |
| `lab_n_pequenos.py` | (único) | M común = 2.000.000, N de 10 a 1K |
| `lab_param_M.py` | (único) | M, 2M, 3M con N fijo |
| `lab_param_orden_bplus.py` | (único) | N = 100K, M = 2.000.000, orden 4 a 256 |

`lab_n_pequenos` es el único con M común, porque su pregunta (punto de cruce entre estructuras)
solo se responde comparando las tres al mismo M; con N tan pequeño los árboles quedan cerca o
por debajo de 1 s, y eso forma parte del hallazgo.

## Cómo correr
```bash
pip install -r requirements.txt
python correr_todo.py --rapido              # perfil rápido: ~la mitad de los puntos y 3 repeticiones (ver abajo)
python correr_todo.py                       # perfil completo: los 7 experimentos, 5 repeticiones
# o, uno por uno:
python estructuras.py                       # verifica el B+ completo
python lab_n_pequenos.py                    # el más corto; úselo para probar
python lab_busqueda_aleatoria.py lista      # un grupo
python lab_busqueda_aleatoria.py            # todos los grupos del script, uno tras otro
```
Cierre todos los demás programas, conecte el equipo a la corriente y no lo use mientras corre.
Opcionales: `LAB_REPS=5` (repeticiones), `LAB_PRESUPUESTO=570` (segundos máximos por grupo; al agotarse
deja de abrir nuevos N y grafica lo medido), `LAB_MOSTRAR=1` (abre las ventanas).
Resultados en `resultados_lab3/`.

## Perfiles de ejecución
| Perfil | Puntos por escalera | Repeticiones | Grupos | Tiempo total (mi entorno) |
|---|---|---|---|---|
| `completo` (por defecto) | todos | 5 | todos | ~32 min |
| `rapido` (`--rapido` o `LAB_PERFIL=rapido`) | uno de cada dos (siempre el primero y el último) | 3 | sin los redundantes (`lista` de la búsqueda ordenada) | ~13 min |

Tiempos medidos por script en el perfil rápido (mi entorno): `lab_n_pequenos` 1,0 min, `lab_param_M` 1,2,
`lab_param_orden_bplus` 0,6, `lab_busqueda_aleatoria` 3,0, `lab_busqueda_ordenada` 2,4, `lab_rango` 2,5,
`lab_construccion` 2,2. Un equipo más lento tardará más (los árboles ~1,6 a 2 veces y la construcción de la
Lista, hasta 4 veces, según lo observado). El perfil usado en cada corrida queda en
`resultados_lab3/tiempos_scripts.csv`. Ojo: con 3 repeticiones la desviación estándar es poco fiable y la
guía sugiere 5 o más; declare en el informe qué perfil se usó en cada experimento.

## Control de ruido
`gc.collect()` + `gc.freeze()` + `gc.disable()` durante cada medición; calentamiento sin cronometrar;
datos y consultas generados fuera del cronómetro; tiempo de CPU registrado junto al de pared; prioridad
alta y un solo núcleo si `psutil` está instalado (`LAB_NUCLEO=<n>` elige el núcleo; `-1` no fija; por defecto el 2: en CPU
híbridas Intel el último núcleo es de eficiencia); aviso si el coeficiente de variación de un punto supera 5%.

## B+
`BPLUS_REAL = True` (en `comun_lab.py`) usa el B+ completo de `estructuras.py` (nodos internos,
splits en cascada, hojas enlazadas). `False` usa el `BPlus` simplificado del script base.
Use el mismo valor en TODOS los experimentos del informe.

(Pendiente: hardware/software, justificación de tamaños, tratamiento de atípicos, conclusiones,
uso de IA y código de honor.)
