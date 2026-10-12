# Laboratorio 3: Sistema de búsqueda — Lista vs ABB vs B+

**Autor:** (nombre) · **Curso:** Estructuras de datos · **Universidad de Antioquia** · **Fecha:** octubre de 2026

> Las secciones marcadas **COMPLETAR** dependen de los resultados medidos en el equipo del autor
> (`resultados_lab3/resumen_*.csv` y `pendientes_*.csv`). Todo lo demás describe el método y ya es definitivo.

## 1. Problema y objetivo
Una institución necesita administrar estudiantes (ID, nombre, edad, promedio) con tres operaciones:
buscar por ID, insertar y listar en orden ascendente de ID. El objetivo es estudiar
**experimentalmente** cómo tres estrategias de almacenamiento (Lista, ABB, B+) afectan el tiempo de
ejecución al crecer el tamaño de los datos, y contrastar lo medido con la complejidad teórica.

## 2. Estructuras y algoritmos
| Estructura | Inserción | Búsqueda | Rango / listado |
|---|---|---|---|
| Lista (sin ordenar) | `append`, O(1) | recorrido lineal `x in datos`, O(N) | filtrar y ordenar, O(N + k log k) / O(N log N) |
| ABB (iterativo) | O(h) | O(h); h ≈ log N con IDs aleatorios, h = N con IDs ordenados | recorrido inorden con poda, O(h + k) |
| B+ (orden 64) | O(log N), con splits en cascada | O(log N): `bisect` en cada nodo | hojas enlazadas: O(log N + k) |

Detalles de implementación (`estructuras.py`): el B+ tiene nodos internos con claves separadoras y hojas
enlazadas; al desbordarse, un nodo se divide por la mitad y la clave sube al padre (si la raíz se divide,
el árbol crece un nivel). El ABB es iterativo (sin recursión), de modo que con IDs ordenados no se
desborda la pila. Una autoprueba verifica que las estructuras den exactamente los mismos resultados en
búsqueda, rango y listado.

## 3. Metodología
### 3.1 Hardware y software
- **Sistema operativo:** Windows 11 (10.0.26200).
- **Procesador:** 12th Gen Intel Core i5-12500H (familia 6, modelo 154), 4 núcleos de rendimiento con 2 hilos y 8 núcleos de eficiencia: 12 núcleos y 16 procesadores lógicos (arquitectura híbrida «Alder Lake»).
- **Memoria:** 16 GB DDR4.
- **Software:** Python 3.12.10 (CPython, MSC v.1943, 64 bits); numpy, pandas, matplotlib, scipy y psutil (**COMPLETAR** versiones con `python registrar_entorno.py`).
- **Condiciones de la medición:** **COMPLETAR** (equipo conectado a la corriente, programas cerrados, modo de energía, núcleo al que se fijó el proceso: ver sección 7).

### 3.2 Qué se mide (por experimento)
Se cronometra el **tiempo total, en segundos, de un bloque de operaciones**; los datos y las consultas se
generan antes y fuera del cronómetro. El tiempo se reporta tal cual se midió: no se extrapola ni se escala.

| Experimento | Bloque cronometrado | Parámetros |
|---|---|---|
| Construcción | insertar N IDs (permutación aleatoria de 0…N−1) en una estructura vacía | N |
| Búsqueda | M búsquedas de IDs existentes elegidos al azar, sobre una estructura ya construida | N, M |
| Rango | Q consultas, cada una devuelve 5.001 estudiantes consecutivos (ID inicial al azar) | N, Q |
| Parámetro M | la misma búsqueda con M, 2M y 3M, N fijo | M |
| Orden del B+ | M búsquedas con B+ de orden 4 a 256, N fijo | orden |
| N pequeños | M búsquedas con N de 10 a 1.000 y M común | N, M |

### 3.3 Tamaños de entrada y justificación
La Lista tiene búsqueda O(N) y los árboles O(log N): con el mismo M, la Lista tarda minutos donde un
árbol tarda fracciones de segundo. Para que cada medición dure entre 1 y 30 s (rango de la guía:
1 s a 5 min), cada estructura —o grupo de estructuras de velocidad parecida— usa **su propio M y su propia
escalera de N**, y tiene su propia gráfica. Los grupos con M distinto **no se comparan en segundos**; se
comparan por la forma de la curva y por la pendiente. Donde un grupo comparte M (por ejemplo, N pequeños
y la comparación con IDs ordenados), las estructuras más rápidas quedan por debajo de 1 s y se reporta tal cual.

La tabla final de M, Q y N por grupo está en `README.md`.

### 3.4 Repeticiones, datos y consultas
- **R = 5** repeticiones por punto en el perfil completo y **R = 3** en el perfil rápido (la guía sugiere 5, 10 o más).
  Todos los CSV entregados son del perfil completo (R = 5 por punto).
- IDs: permutación aleatoria de 0…N−1 (semilla fija `2026`, reproducible). Consultas: `random.choices` sobre
  IDs existentes (solo aciertos). Rango: ID inicial uniforme, ancho fijo de 5.000.
- Las 5 repeticiones de un punto **reutilizan los mismos datos y las mismas consultas**: la desviación
  estándar mide el ruido del equipo, no la variabilidad entre conjuntos de datos distintos.

### 3.5 Medición y control de ruido
`time.perf_counter()` sobre el bloque; antes de cada medición `gc.collect()` y `gc.freeze()`, y el
recolector de basura se desactiva durante el bloque; calentamiento sin cronometrar (5.000 búsquedas o
50 rangos); se registra también el tiempo de CPU (`process_time`); prioridad alta y un solo núcleo si
`psutil` está instalado; programas cerrados y equipo conectado a la corriente. Los puntos con
coeficiente de variación mayor a 5% se marcan.

### 3.6 Valores atípicos y estadísticas
No se descartan mediciones: con R = 5 una regla estadística (por ejemplo 1,5·IQR) tiene poca potencia.
Se reportan media, desviación estándar muestral (n−1), mediana, mínimo, máximo, coeficiente de variación
(σ/media) y el intervalo de confianza del 95 % con t de Student (`ic95_semiancho`). Para contrastar con la
teoría se calcula la **pendiente de la regresión de log(tiempo) contra log(N)** (`pendientes_*.csv`): ≈ 0 indica
O(log N), ≈ 1 indica O(N), ≈ 2 indica O(N²). Para O(log N) en el rango de N usado, la pendiente teórica
no es 0 sino ≈ ln(log₂N₂/log₂N₁)/ln(N₂/N₁) (por ejemplo ≈ 0,09 entre 5K y 1M).

## 4. Resultados
Todos los resultados son del **perfil completo (R = 5 repeticiones por punto)**, medidos en el equipo del autor.
Cada tabla muestra la media, la desviación estándar muestral, el intervalo de confianza del 95 % (t de Student, 4 grados
de libertad) y el coeficiente de variación. «µs/op» es el tiempo total dividido entre M (o Q): una conversión de unidades
de lo medido, válida porque el tiempo por operación no depende de M (sección 4.5). Las gráficas están en `resultados_lab3/`.

### 4.1 Búsqueda con IDs aleatorios
Gráficas: `busqueda_aleatoria_lista_*`, `busqueda_aleatoria_arboles_*`.

**Lista (M = 10.000 búsquedas)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 40.000 | 10.000 | 2,729 | 0,074 | 0,091 | 2,7 | 272,88 |
| 60.000 | 10.000 | 3,819 | 0,258 | 0,320 | 6,8 | 381,88 |
| 80.000 | 10.000 | 8,958 | 0,203 | 0,252 | 2,3 | 895,77 |
| 100.000 | 10.000 | 13,659 | 0,227 | 0,281 | 1,7 | 1365,93 |
| 125.000 | 10.000 | 18,675 | 0,378 | 0,469 | 2,0 | 1867,51 |
| 150.000 | 10.000 | 24,429 | 0,510 | 0,634 | 2,1 | 2442,88 |
| 200.000 | 10.000 | 31,284 | 4,451 | 5,527 | 14,2 | 3128,44 |

**ABB (M = 2.000.000 búsquedas)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | altura | µs/búsqueda |
|---|---|---|---|---|---|---|---|
| 5.000 | 2.000.000 | 1,799 | 0,002 | 0,002 | 0,1 | 30 | 0,90 |
| 10.000 | 2.000.000 | 2,027 | 0,018 | 0,023 | 0,9 | 29 | 1,01 |
| 25.000 | 2.000.000 | 2,476 | 0,012 | 0,015 | 0,5 | 31 | 1,24 |
| 50.000 | 2.000.000 | 3,059 | 0,017 | 0,022 | 0,6 | 43 | 1,53 |
| 100.000 | 2.000.000 | 3,719 | 0,012 | 0,014 | 0,3 | 41 | 1,86 |
| 250.000 | 2.000.000 | 4,217 | 0,009 | 0,012 | 0,2 | 42 | 2,11 |
| 500.000 | 2.000.000 | 5,289 | 0,026 | 0,032 | 0,5 | 50 | 2,64 |
| 1.000.000 | 2.000.000 | 6,416 | 0,018 | 0,023 | 0,3 | 51 | 3,21 |

**B+ (M = 2.000.000 búsquedas)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 5.000 | 2.000.000 | 1,191 | 0,014 | 0,018 | 1,2 | 0,60 |
| 10.000 | 2.000.000 | 1,224 | 0,019 | 0,024 | 1,6 | 0,61 |
| 25.000 | 2.000.000 | 1,377 | 0,025 | 0,031 | 1,8 | 0,69 |
| 50.000 | 2.000.000 | 1,637 | 0,014 | 0,017 | 0,8 | 0,82 |
| 100.000 | 2.000.000 | 1,900 | 0,023 | 0,029 | 1,2 | 0,95 |
| 250.000 | 2.000.000 | 2,199 | 0,023 | 0,028 | 1,0 | 1,10 |
| 500.000 | 2.000.000 | 2,604 | 0,026 | 0,032 | 1,0 | 1,30 |
| 1.000.000 | 2.000.000 | 3,086 | 0,023 | 0,028 | 0,7 | 1,54 |

Lectura: con N = 100.000 una búsqueda cuesta 1366 µs en la Lista, 1,86 µs en el ABB y 0,95 µs en el B+
(la Lista es ≈ 735 veces más lenta que el ABB y ≈ 1437 veces más lenta que el B+). El B+ gana
al ABB en todo el rango y su ventaja crece con N: 1,51 veces con N = 5K y 2,08 veces con N = 1M.
La Lista no escala de forma lineal pura: el costo por elemento recorrido (tiempo / M / (N/2)) es ≈ 13–14 ns con N = 40K y 60K, sube a
≈ 22 ns con N = 80K y queda en ≈ 27–33 ns desde N = 100K (el tiempo se multiplica por ≈ 2,3 entre 60K y 80K aunque N solo crece 1,33 veces).
Es consistente con que el recorrido deja de caber en la caché, pero **no se verificó** esa causa.
El punto N = 200K tiene CV = 14 % (repeticiones de 24,3 a 35,0 s; ver sección 7).

### 4.2 Búsqueda con IDs ordenados
Gráficas: `busqueda_ordenada_comparacion_*`, `busqueda_ordenada_lista_*`, `busqueda_ordenada_arboles_*`.

**Comparación de frente, M = 60.000 para las cuatro curvas**

*Lista (IDs ordenados)*

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % |
|---|---|---|---|---|---|
| 2.000 | 60.000 | 0,462 | 0,002 | 0,003 | 0,5 |
| 3.000 | 60.000 | 0,691 | 0,000 | 0,001 | 0,1 |
| 4.000 | 60.000 | 0,918 | 0,001 | 0,001 | 0,1 |
| 5.000 | 60.000 | 1,146 | 0,000 | 0,001 | 0,0 |
| 6.000 | 60.000 | 1,379 | 0,001 | 0,001 | 0,0 |
| 8.000 | 60.000 | 1,836 | 0,001 | 0,002 | 0,1 |
| 10.000 | 60.000 | 2,289 | 0,001 | 0,002 | 0,1 |

*ABB (IDs ordenados)* — degenera: la altura es N

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | altura |
|---|---|---|---|---|---|---|
| 2.000 | 60.000 | 3,019 | 0,001 | 0,002 | 0,0 | 2000 |
| 3.000 | 60.000 | 4,532 | 0,005 | 0,006 | 0,1 | 3000 |
| 4.000 | 60.000 | 6,044 | 0,001 | 0,001 | 0,0 | 4000 |
| 5.000 | 60.000 | 7,574 | 0,004 | 0,005 | 0,1 | 5000 |
| 6.000 | 60.000 | 9,124 | 0,007 | 0,009 | 0,1 | 6000 |
| 8.000 | 60.000 | 12,271 | 0,010 | 0,013 | 0,1 | 8000 |
| 10.000 | 60.000 | 15,532 | 0,043 | 0,054 | 0,3 | 10000 |

*ABB (IDs aleatorios)*

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | altura |
|---|---|---|---|---|---|---|
| 2.000 | 60.000 | 0,047 | 0,001 | 0,001 | 1,3 | 24 |
| 3.000 | 60.000 | 0,050 | 0,001 | 0,001 | 1,1 | 30 |
| 4.000 | 60.000 | 0,049 | 0,000 | 0,000 | 0,7 | 25 |
| 5.000 | 60.000 | 0,053 | 0,000 | 0,000 | 0,7 | 29 |
| 6.000 | 60.000 | 0,056 | 0,001 | 0,002 | 2,5 | 29 |
| 8.000 | 60.000 | 0,058 | 0,001 | 0,001 | 1,9 | 31 |
| 10.000 | 60.000 | 0,056 | 0,000 | 0,000 | 0,5 | 28 |

*B+ (IDs ordenados)*

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % |
|---|---|---|---|---|---|
| 2.000 | 60.000 | 0,030 | 0,001 | 0,001 | 1,9 |
| 3.000 | 60.000 | 0,034 | 0,000 | 0,000 | 0,8 |
| 4.000 | 60.000 | 0,034 | 0,000 | 0,000 | 0,5 |
| 5.000 | 60.000 | 0,035 | 0,000 | 0,000 | 0,7 |
| 6.000 | 60.000 | 0,036 | 0,001 | 0,001 | 1,9 |
| 8.000 | 60.000 | 0,037 | 0,001 | 0,001 | 2,5 |
| 10.000 | 60.000 | 0,038 | 0,001 | 0,001 | 2,5 |

**Lista con IDs ordenados, M = 300.000** (rango 1–30 s)

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 2.000 | 300.000 | 2,307 | 0,001 | 0,001 | 0,0 | 7,69 |
| 3.000 | 300.000 | 3,449 | 0,001 | 0,002 | 0,0 | 11,50 |
| 4.000 | 300.000 | 4,612 | 0,004 | 0,005 | 0,1 | 15,37 |
| 5.000 | 300.000 | 5,754 | 0,001 | 0,002 | 0,0 | 19,18 |
| 6.000 | 300.000 | 6,902 | 0,002 | 0,003 | 0,0 | 23,01 |
| 8.000 | 300.000 | 9,178 | 0,004 | 0,005 | 0,0 | 30,59 |
| 10.000 | 300.000 | 11,489 | 0,004 | 0,005 | 0,0 | 38,30 |

**ABB (IDs aleatorios) y B+ (IDs ordenados), M = 3.500.000** (rango 1–30 s)

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | altura |
|---|---|---|---|---|---|---|
| 2.000 | 3.500.000 | 2,818 | 0,011 | 0,014 | 0,4 | 24 |
| 3.000 | 3.500.000 | 3,166 | 0,014 | 0,018 | 0,5 | 26 |
| 4.000 | 3.500.000 | 3,426 | 0,010 | 0,013 | 0,3 | 28 |
| 5.000 | 3.500.000 | 3,334 | 0,014 | 0,018 | 0,4 | 28 |
| 6.000 | 3.500.000 | 3,300 | 0,014 | 0,018 | 0,4 | 30 |
| 8.000 | 3.500.000 | 3,727 | 0,023 | 0,028 | 0,6 | 34 |
| 10.000 | 3.500.000 | 3,386 | 0,022 | 0,028 | 0,7 | 34 |

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % |
|---|---|---|---|---|---|
| 2.000 | 3.500.000 | 1,781 | 0,013 | 0,016 | 0,7 |
| 3.000 | 3.500.000 | 2,097 | 0,048 | 0,059 | 2,3 |
| 4.000 | 3.500.000 | 2,164 | 0,015 | 0,019 | 0,7 |
| 5.000 | 3.500.000 | 2,175 | 0,024 | 0,030 | 1,1 |
| 6.000 | 3.500.000 | 2,191 | 0,015 | 0,019 | 0,7 |
| 8.000 | 3.500.000 | 2,230 | 0,038 | 0,047 | 1,7 |
| 10.000 | 3.500.000 | 2,204 | 0,024 | 0,029 | 1,1 |

Lectura: con N = 10.000 el ABB con IDs ordenados tarda 278 veces más que con IDs aleatorios
(64 veces con N = 2.000). Su costo por nodo visitado es constante (≈ 50 ns con N = 2K y ≈ 52 ns con N = 10K,
suponiendo N/2 nodos por búsqueda), así que el tiempo es proporcional a la altura. La Lista (también O(N)) es ≈ 6,8 veces más rápida
que el ABB degenerado, porque recorre en C (`x in datos`) y el ABB persigue punteros en código Python. El B+ con IDs ordenados es
61 veces más rápido que la Lista con N = 10K. Las alturas del ABB con IDs aleatorios (24–34) son 2–3 veces la altura mínima log₂N+1.

### 4.3 Construcción (insertar N estudiantes)
Gráficas: `construccion_arboles_*`, `construccion_lista_*`, `construccion_lista_grande_*`.

**ABB**

| N | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/inserción |
|---|---|---|---|---|---|
| 500.000 | 1,058 | 0,012 | 0,014 | 1,1 | 2,12 |
| 600.000 | 1,495 | 0,007 | 0,009 | 0,5 | 2,49 |
| 700.000 | 1,889 | 0,045 | 0,056 | 2,4 | 2,70 |
| 800.000 | 2,242 | 0,072 | 0,089 | 3,2 | 2,80 |
| 900.000 | 2,582 | 0,099 | 0,123 | 3,8 | 2,87 |
| 1.000.000 | 2,991 | 0,107 | 0,133 | 3,6 | 2,99 |
| 1.100.000 | 3,370 | 0,164 | 0,204 | 4,9 | 3,06 |
| 1.200.000 | 3,826 | 0,171 | 0,212 | 4,5 | 3,19 |
| 1.300.000 | 4,169 | 0,152 | 0,188 | 3,6 | 3,21 |
| 1.400.000 | 4,457 | 0,187 | 0,232 | 4,2 | 3,18 |
| 1.500.000 | 5,337 | 0,414 | 0,514 | 7,8 | 3,56 |

**B+**

| N | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/inserción |
|---|---|---|---|---|---|
| 500.000 | 0,842 | 0,064 | 0,080 | 7,6 | 1,68 |
| 600.000 | 1,002 | 0,012 | 0,014 | 1,2 | 1,67 |
| 700.000 | 1,220 | 0,004 | 0,004 | 0,3 | 1,74 |
| 800.000 | 1,447 | 0,013 | 0,016 | 0,9 | 1,81 |
| 900.000 | 1,649 | 0,010 | 0,013 | 0,6 | 1,83 |
| 1.000.000 | 1,888 | 0,008 | 0,010 | 0,4 | 1,89 |
| 1.100.000 | 2,095 | 0,029 | 0,036 | 1,4 | 1,90 |
| 1.200.000 | 2,344 | 0,056 | 0,070 | 2,4 | 1,95 |
| 1.300.000 | 2,597 | 0,023 | 0,028 | 0,9 | 2,00 |
| 1.400.000 | 2,911 | 0,043 | 0,053 | 1,5 | 2,08 |
| 1.500.000 | 3,374 | 0,085 | 0,105 | 2,5 | 2,25 |

**Lista (N hasta 1,5M): hallazgo, todos los tiempos < 1 s**

| N | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/inserción |
|---|---|---|---|---|---|
| 500.000 | 0,068 | 0,003 | 0,004 | 4,8 | 0,14 |
| 600.000 | 0,083 | 0,002 | 0,002 | 1,9 | 0,14 |
| 700.000 | 0,118 | 0,012 | 0,014 | 9,9 | 0,17 |
| 800.000 | 0,143 | 0,017 | 0,021 | 12,0 | 0,18 |
| 900.000 | 0,177 | 0,016 | 0,020 | 9,0 | 0,20 |
| 1.000.000 | 0,178 | 0,012 | 0,015 | 6,8 | 0,18 |
| 1.100.000 | 0,185 | 0,005 | 0,006 | 2,6 | 0,17 |
| 1.200.000 | 0,212 | 0,002 | 0,003 | 1,2 | 0,18 |
| 1.300.000 | 0,233 | 0,002 | 0,002 | 0,8 | 0,18 |
| 1.400.000 | 0,257 | 0,009 | 0,012 | 3,7 | 0,18 |
| 1.500.000 | 0,271 | 0,002 | 0,003 | 0,9 | 0,18 |

**Lista con N muy grande**

| N | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/inserción |
|---|---|---|---|---|---|
| 4.000.000 | 0,780 | 0,011 | 0,013 | 1,4 | 0,20 |
| 5.000.000 | 1,021 | 0,038 | 0,047 | 3,7 | 0,20 |
| 6.000.000 | 1,202 | 0,036 | 0,045 | 3,0 | 0,20 |
| 7.000.000 | 1,385 | 0,008 | 0,010 | 0,6 | 0,20 |
| 8.000.000 | 1,591 | 0,005 | 0,006 | 0,3 | 0,20 |
| 9.000.000 | 1,801 | 0,004 | 0,005 | 0,2 | 0,20 |
| 10.000.000 | 2,020 | 0,012 | 0,015 | 0,6 | 0,20 |

Lectura: el B+ construye entre 20 y 39 % más rápido que el ABB. La Lista pasa de 1 s entre N = 4M (0,78 s) y N = 5M (1,02 s), medido, no extrapolado.
El costo por inserción de los árboles crece con N (ABB de 2,1 a 3,6 µs; B+ de 1,7 a 2,2 µs); el de la Lista es casi constante (0,14–0,20 µs). La Lista es 15–20 veces más rápida que el ABB y 9–12 veces más rápida que el B+.

### 4.4 Consulta por rango (cada consulta devuelve 5.001 estudiantes)
Gráficas: `rango_lista_*`, `rango_abb_*`, `rango_bplus_*`.

**Lista (Q = 1.500)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/consulta |
|---|---|---|---|---|---|---|
| 10.000 | 1.500 | 2,934 | 0,015 | 0,018 | 0,5 | 1955,94 |
| 20.000 | 1.500 | 3,990 | 0,023 | 0,029 | 0,6 | 2659,92 |
| 30.000 | 1.500 | 5,194 | 0,015 | 0,019 | 0,3 | 3462,68 |
| 40.000 | 1.500 | 6,525 | 0,042 | 0,052 | 0,6 | 4350,01 |
| 50.000 | 1.500 | 8,577 | 0,135 | 0,167 | 1,6 | 5718,08 |
| 60.000 | 1.500 | 10,776 | 0,050 | 0,062 | 0,5 | 7183,95 |
| 70.000 | 1.500 | 13,321 | 0,083 | 0,103 | 0,6 | 8880,39 |
| 85.000 | 1.500 | 16,779 | 0,126 | 0,156 | 0,8 | 11186,22 |
| 100.000 | 1.500 | 20,230 | 0,279 | 0,346 | 1,4 | 13486,63 |

**ABB (Q = 2.000)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/consulta |
|---|---|---|---|---|---|---|
| 10.000 | 2.000 | 2,943 | 0,119 | 0,148 | 4,1 | 1471,70 |
| 25.000 | 2.000 | 3,410 | 0,041 | 0,051 | 1,2 | 1704,90 |
| 50.000 | 2.000 | 3,643 | 0,031 | 0,038 | 0,8 | 1821,25 |
| 100.000 | 2.000 | 3,654 | 0,041 | 0,051 | 1,1 | 1827,16 |
| 200.000 | 2.000 | 3,870 | 0,031 | 0,038 | 0,8 | 1934,88 |
| 300.000 | 2.000 | 4,232 | 0,037 | 0,045 | 0,9 | 2115,79 |
| 500.000 | 2.000 | 4,580 | 0,048 | 0,060 | 1,1 | 2290,24 |
| 750.000 | 2.000 | 4,828 | 0,032 | 0,040 | 0,7 | 2413,90 |
| 1.000.000 | 2.000 | 4,960 | 0,052 | 0,065 | 1,1 | 2480,13 |

**B+ (Q = 30.000)**

| N | M/Q | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/consulta |
|---|---|---|---|---|---|---|
| 10.000 | 30.000 | 3,706 | 0,055 | 0,068 | 1,5 | 123,53 |
| 25.000 | 30.000 | 6,956 | 0,015 | 0,019 | 0,2 | 231,88 |
| 50.000 | 30.000 | 9,720 | 0,028 | 0,035 | 0,3 | 324,01 |
| 100.000 | 30.000 | 10,690 | 0,077 | 0,096 | 0,7 | 356,33 |
| 200.000 | 30.000 | 8,784 | 0,130 | 0,161 | 1,5 | 292,80 |
| 300.000 | 30.000 | 9,154 | 0,296 | 0,367 | 3,2 | 305,14 |
| 500.000 | 30.000 | 9,807 | 0,079 | 0,098 | 0,8 | 326,91 |
| 750.000 | 30.000 | 10,434 | 0,163 | 0,203 | 1,6 | 347,81 |
| 1.000.000 | 30.000 | 10,987 | 0,094 | 0,117 | 0,9 | 366,23 |

Lectura: la consulta por rango cuesta ≈ 1,5–2,5 ms en el ABB y ≈ 0,12–0,37 ms en el B+ (el B+ es de 5 a 12 veces más rápido por consulta), mientras que la Lista pasa de 2,0 a 13,5 ms
y sigue creciendo con N. El tiempo por consulta del B+ queda en 0,29–0,37 ms para N ≥ 50K (casi constante, como predice O(log N + k) con k fijo), pero **no es monótono**:
baja de 0,36 ms con N = 100K a 0,29 ms con N = 200K (ver sección 7).

### 4.5 Parámetros
Gráficas: `param_M_*`, `param_orden_bplus_*`.

**Parámetro M (N fijo; M, 2M, 3M)**

| Estructura | N | M | media (s) | desv. (s) | IC95 % (±s) | µs/búsqueda |
|---|---|---|---|---|---|---|
| Lista | 10.000 | 35.000 | 1,450 | 0,002 | 0,003 | 41,437 |
| Lista | 10.000 | 70.000 | 2,911 | 0,005 | 0,006 | 41,581 |
| Lista | 10.000 | 105.000 | 4,346 | 0,004 | 0,005 | 41,387 |
| ABB | 100.000 | 1.000.000 | 1,710 | 0,012 | 0,015 | 1,710 |
| ABB | 100.000 | 2.000.000 | 3,415 | 0,017 | 0,021 | 1,708 |
| ABB | 100.000 | 3.000.000 | 5,155 | 0,029 | 0,035 | 1,718 |
| B+ | 100.000 | 1.500.000 | 1,423 | 0,029 | 0,036 | 0,949 |
| B+ | 100.000 | 3.000.000 | 2,855 | 0,030 | 0,037 | 0,952 |
| B+ | 100.000 | 4.500.000 | 4,319 | 0,041 | 0,051 | 0,960 |

El tiempo por búsqueda no depende de M (Lista 41,4–41,6 µs; ABB 1,708–1,718 µs; B+ 0,949–0,960 µs) y las pendientes log-log tiempo–M son
1,000 (Lista), 1,004 (ABB) y 1,010 (B+): el tiempo total es lineal en M. Esto justifica comparar estructuras por tiempo por operación cuando M difiere.

**Orden del B+ (N = 100.000, M = 2.000.000)**

| Estructura | altura | media (s) | desv. (s) | IC95 % (±s) | µs/búsqueda |
|---|---|---|---|---|---|
| B+ (orden=4) | 11 | 3,989 | 0,050 | 0,062 | 1,994 |
| B+ (orden=8) | 7 | 3,228 | 0,015 | 0,018 | 1,614 |
| B+ (orden=16) | 5 | 2,500 | 0,046 | 0,057 | 1,250 |
| B+ (orden=32) | 4 | 2,138 | 0,027 | 0,033 | 1,069 |
| B+ (orden=64) | 3 | 1,922 | 0,022 | 0,028 | 0,961 |
| B+ (orden=128) | 3 | 1,871 | 0,009 | 0,011 | 0,936 |
| B+ (orden=256) | 3 | 1,849 | 0,020 | 0,024 | 0,924 |
| ABB (referencia) | 43 | 3,771 | 0,014 | 0,017 | 1,886 |

Lectura: la altura baja de 11 a 3 niveles al subir el orden de 4 a 64 y el tiempo baja de 3,99 s a 1,92 s; desde el orden 64 la altura ya no cambia (3) y el tiempo mejora solo 4 %.
Con orden 4 el B+ es **más lento** que el ABB (3,99 s frente a 3,77 s) aunque su altura es 11 contra 43: cada nivel del B+ cuesta ≈ 181 ns (llamada a `bisect` + indexación) frente a ≈ 44 ns por nodo en el ABB.
El orden 64 usado en los demás experimentos queda a 4 % del mejor valor medido.

### 4.6 Tamaños pequeños (costos constantes y punto de cruce)
Gráficas: `n_pequenos_*` (incluye `n_pequenos_05_cociente.png`). **M común = 2.000.000 búsquedas para las tres estructuras**, N de 10 a 1.000, R = 5.
Esta corrida se ejecutó con el proceso fijado al núcleo lógico 2 de 16 (núcleo de rendimiento), según el mensaje de consola; los valores absolutos
**no son comparables** con los de otros experimentos (ver sección 7), pero las comparaciones dentro de este experimento sí lo son.

**Lista**

| N | M | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 10 | 2.000.000 | 0,123 | 0,0009 | 0,0011 | 0,7 | 0,062 |
| 20 | 2.000.000 | 0,164 | 0,0022 | 0,0027 | 1,3 | 0,082 |
| 50 | 2.000.000 | 0,266 | 0,0055 | 0,0069 | 2,1 | 0,133 |
| 100 | 2.000.000 | 0,443 | 0,0020 | 0,0024 | 0,4 | 0,221 |
| 200 | 2.000.000 | 0,805 | 0,0016 | 0,0020 | 0,2 | 0,402 |
| 300 | 2.000.000 | 1,287 | 0,0158 | 0,0196 | 1,2 | 0,643 |
| 500 | 2.000.000 | 2,259 | 0,0064 | 0,0079 | 0,3 | 1,130 |
| 700 | 2.000.000 | 3,100 | 0,0258 | 0,0320 | 0,8 | 1,550 |
| 1000 | 2.000.000 | 4,123 | 0,0319 | 0,0396 | 0,8 | 2,061 |

**ABB**

| N | M | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 10 | 2.000.000 | 0,260 | 0,0019 | 0,0023 | 0,7 | 0,130 |
| 20 | 2.000.000 | 0,346 | 0,0029 | 0,0036 | 0,8 | 0,173 |
| 50 | 2.000.000 | 0,396 | 0,0033 | 0,0041 | 0,8 | 0,198 |
| 100 | 2.000.000 | 0,509 | 0,0051 | 0,0063 | 1,0 | 0,255 |
| 200 | 2.000.000 | 0,519 | 0,0028 | 0,0035 | 0,5 | 0,259 |
| 300 | 2.000.000 | 0,772 | 0,0018 | 0,0022 | 0,2 | 0,386 |
| 500 | 2.000.000 | 0,793 | 0,0053 | 0,0066 | 0,7 | 0,397 |
| 700 | 2.000.000 | 0,812 | 0,0031 | 0,0038 | 0,4 | 0,406 |
| 1000 | 2.000.000 | 0,842 | 0,0035 | 0,0043 | 0,4 | 0,421 |

**B+**

| N | M | media (s) | desv. (s) | IC95 % (±s) | CV % | µs/búsqueda |
|---|---|---|---|---|---|---|
| 10 | 2.000.000 | 0,362 | 0,0022 | 0,0027 | 0,6 | 0,181 |
| 20 | 2.000.000 | 0,381 | 0,0023 | 0,0028 | 0,6 | 0,191 |
| 50 | 2.000.000 | 0,408 | 0,0023 | 0,0028 | 0,6 | 0,204 |
| 100 | 2.000.000 | 0,486 | 0,0071 | 0,0088 | 1,5 | 0,243 |
| 200 | 2.000.000 | 0,510 | 0,0095 | 0,0118 | 1,9 | 0,255 |
| 300 | 2.000.000 | 0,520 | 0,0019 | 0,0024 | 0,4 | 0,260 |
| 500 | 2.000.000 | 0,557 | 0,0028 | 0,0034 | 0,5 | 0,278 |
| 700 | 2.000.000 | 0,570 | 0,0020 | 0,0025 | 0,4 | 0,285 |
| 1000 | 2.000.000 | 0,580 | 0,0029 | 0,0036 | 0,5 | 0,290 |

**Tiempo por búsqueda y cocientes** (cociente > 1: la primera estructura es más lenta)

| N | Lista (µs) | ABB (µs) | B+ (µs) | Lista ÷ ABB | Lista ÷ B+ | ABB ÷ B+ |
|---|---|---|---|---|---|---|
| 10 | 0,062 | 0,130 | 0,181 | 0,47 | 0,34 | 0,72 |
| 20 | 0,082 | 0,173 | 0,191 | 0,47 | 0,43 | 0,91 |
| 50 | 0,133 | 0,198 | 0,204 | 0,67 | 0,65 | 0,97 |
| 100 | 0,221 | 0,255 | 0,243 | 0,87 | 0,91 | 1,05 |
| 200 | 0,402 | 0,259 | 0,255 | 1,55 | 1,58 | 1,02 |
| 300 | 0,643 | 0,386 | 0,260 | 1,67 | 2,47 | 1,48 |
| 500 | 1,130 | 0,397 | 0,278 | 2,85 | 4,06 | 1,42 |
| 700 | 1,550 | 0,406 | 0,285 | 3,82 | 5,44 | 1,42 |
| 1000 | 2,061 | 0,421 | 0,290 | 4,90 | 7,11 | 1,45 |

Lectura: con N ≤ 100 la Lista es igual o más rápida que los árboles (0,062 µs frente a 0,130 µs del ABB y 0,181 µs del B+ con N = 10). El cociente Lista ÷ ABB pasa de 0,87 con N = 100 a 1,55 con N = 200
(la Lista se vuelve más lenta que los árboles **entre N = 100 y N = 200**; una interpolación lineal de los cocientes da ≈ 120, como orientación). Con N = 500 la Lista es 2,8 veces más lenta que el ABB y 4,1 veces más lenta que el B+;
con N = 1.000, 4,9 y 7,1 veces. El ajuste lineal de la Lista da un costo fijo de ≈ 0,03 µs más ≈ 4,2 ns por elemento recorrido, mientras que los árboles tienen un costo mínimo de 0,13 µs (ABB) y 0,18 µs (B+) por búsqueda.
Entre los árboles, el ABB es más rápido que el B+ con N ≤ 50 (cociente ABB ÷ B+ de 0,72 a 0,97), empatan con N = 100–200 y el B+ gana con N ≥ 300 (1,42–1,48 veces).
Solo 4 de los 27 puntos (Lista con N ≥ 300) superan 1 s: con N tan pequeño y M = 2.000.000 las demás mediciones duran de 0,12 a 0,84 s, y se reportan tal cual.

## 5. Interpretación y comparación con la teoría
**Pendientes log-log medidas frente a las teóricas** (la teórica de O(log N) y O(N log N) depende del rango de N; se calcula con la regresión sobre los mismos extremos):

| Experimento (rango de N) | Estructura | Pendiente medida | Pendiente teórica |
|---|---|---|---|
| Búsqueda aleatoria (5K–1M) | ABB | 0,24 | 0,09 (O(log N)) |
| Búsqueda aleatoria (5K–1M) | B+ | 0,19 | 0,09 |
| Búsqueda aleatoria (40K–200K) | Lista | 1,65 | 1,00 |
| Búsqueda ordenada (2K–10K) | Lista | 0,995 | 1,00 |
| Búsqueda ordenada (2K–10K) | ABB (IDs ordenados) | 1,016 | 1,00 (altura = N) |
| Búsqueda ordenada (2K–10K) | ABB (IDs aleatorios) / B+ | 0,13 / 0,12 | ≈ 0,12 (O(log N)) |
| Construcción (500K–1,5M) | ABB / B+ | 1,38 / 1,24 | 1,07 (O(N log N)) |
| Construcción (500K–1,5M) | Lista | 1,24 | 1,00 |
| Construcción (4M–10M) | Lista | 1,015 | 1,00 |
| Rango (10K–100K / 10K–1M) | Lista / ABB / B+ | 0,87 / 0,11 / 0,17 | 1 (sin el costo fijo de ordenar) / ≈ 0,1 / ≈ 0 |
| Búsqueda N pequeños (10–1K) | Lista / ABB / B+ | 0,79 / 0,26 / 0,11 | 1,00 / 0,24 / 0,24 |
| Parámetro M | Lista / ABB / B+ | 1,00 / 1,00 / 1,01 | 1,00 |

**1. ¿Se comportan como predice la teoría?** Sí en la forma, con diferencias en el nivel. Con N pequeño (2K–10K) las pendientes del ABB y del B+ (0,13 y 0,12) coinciden con la teórica (≈ 0,12).
Con N grande (5K–1M) son ≈ 2–2,6 veces mayores que la teórica (0,24 y 0,19 contra 0,09), y la construcción tiene pendientes de 1,38 y 1,24 contra 1,07. Una explicación plausible es la jerarquía
de memoria (más fallos de caché al crecer la estructura), pero **no se verificó**. El B+ se desvía menos que el ABB. Las Listas son lineales donde se midió con un régimen estable
(pendientes 0,995 y 1,015), salvo el escalón entre 60K y 100K de la búsqueda aleatoria.

**2. ¿Cuándo deja el ABB de ser O(log N)?** Con IDs insertados en orden creciente: la altura es N (2.000 a 10.000 niveles frente a 24–34), la pendiente es 1,016 y el tiempo es
64–278 veces el de IDs aleatorios.

**3. Altura y tiempo.** En el ABB ordenado el costo por nodo es constante (≈ 50 ns), luego el tiempo es proporcional a la altura. En el B+ el tiempo baja al reducir la altura
(11 → 3 niveles: 3,99 → 1,92 s) y se estabiliza cuando la altura no cambia (orden ≥ 64). La altura no basta para comparar estructuras: el B+ de orden 4 (altura 11) es más lento que el ABB aleatorio (altura 43).

**4–5. Datos ordenados y diferencias frente a los aleatorios.** El ABB es el único afectado: se degrada hasta 278 veces con N = 10K. El B+ con IDs ordenados es incluso algo más rápido que el ABB con IDs aleatorios
(0,030–0,038 s frente a 0,047–0,058 s con M = 60.000). La Lista no depende del orden: su búsqueda cuesta ≈ 38 µs (IDs ordenados, N = 10K) frente a ≈ 41 µs (IDs aleatorios, N = 10K, experimento del parámetro M),
una diferencia del 8 % entre scripts distintos. Las diferencias se ven con claridad ya con N = 2.000: Lista 15 veces más lenta que el B+ y ABB ordenado 64 veces más lento que el aleatorio. Entre la Lista y los árboles con IDs aleatorios, la Lista deja de ganar entre N = 100 y N = 200; con N = 500 ya es 2,8–4,1 veces más lenta y con N = 1.000, 4,9–7,1 veces. Entre ABB y B+ las diferencias aparecen con N ≥ 300 (1,4–1,5 veces).

**6. ¿Costos constantes con entradas pequeñas?** Sí. Con N ≤ 100 la Lista, que es O(N), es tan rápida o más que los árboles O(log N): su costo por elemento es de apenas ≈ 4 ns, mientras que cada árbol paga un costo mínimo por búsqueda (≈ 0,13 µs el ABB y ≈ 0,18 µs el B+) que no depende de N. El B+ es incluso más lento que el ABB con N ≤ 50: sus llamadas a `bisect` e indexaciones por nodo pesan más que el recorrido de punteros del ABB mientras el árbol es pequeño. La pendiente log-log del B+ (0,11) queda por debajo de la teórica (0,24) porque con N < 64 cabe en una sola hoja.

## 6. Hallazgos principales
1. **Búsqueda:** con N = 100K, Lista ≈ 1366 µs, ABB ≈ 1,86 µs, B+ ≈ 0,95 µs por búsqueda; el B+ supera al ABB en todo el rango y su ventaja crece con N (1,5× → 2,1×).
2. **Orden de inserción:** el ABB con IDs ordenados degenera (altura = N): hasta 278 veces más lento con N = 10K; el B+ y la Lista no se ven afectados.
3. **Construcción:** el B+ es 20–39 % más rápido que el ABB; la Lista es 9–20 veces más rápida que los árboles y pasa de 1 s entre N = 4M y 5M (medido).
4. **Rango:** el B+ es 5–12 veces más rápido que el ABB y su tiempo por consulta es casi constante en N; la Lista crece con N (2,0 → 13,5 ms).
5. **Parámetro M:** el tiempo es lineal en M (pendiente 1,00–1,01) y el tiempo por operación no cambia con M.
6. **Orden del B+:** el mejor rendimiento se alcanza con orden ≥ 64 (altura 3); con orden 4 el B+ es más lento que el ABB.
7. **Punto de cruce:** con M común, la Lista es igual o más rápida que los árboles hasta N ≈ 100 y más lenta desde N = 200 (hasta 7 veces con N = 1.000); el B+ supera al ABB desde N ≈ 300.
8. **Teoría y medición:** la forma coincide con O(N) y O(log N); en N grande las pendientes de los árboles son mayores que la teórica, lo que apunta a efectos de memoria (no verificado).

## 7. Limitaciones del experimento
- **Un solo árbol por punto.** Las 5 repeticiones reutilizan el mismo árbol, los mismos datos y las mismas consultas, así que la desviación mide ruido del equipo, no variabilidad entre árboles.
  Evidencia: el mismo ABB aleatorio con N = 100K, construido en tres scripts con permutaciones distintas, dio 1,712, 1,860 y 1,886 µs por búsqueda
  (diferencia de ≈ 10 %, con CV intra-punto < 1 %); el B+ dio 0,950, 0,953 y 0,961 µs (≈ 1 %). En el ABB aleatorio con M = 3,5M, el tiempo no es monótono en N
  (3,43 s con N = 4K, 3,33 s con 5K, 3,30 s con 6K y 3,73 s con 8K), por el mismo motivo. Las barras de error del ABB aleatorio subestiman la incertidumbre real.
- **Repetibilidad entre scripts.** El ABB con IDs ordenados y M = 60.000 se midió en dos scripts: las medias difieren entre 0,2 % y 2,4 % (el CV intra-punto es ≤ 0,3 %).
- **Variación del equipo.** Lista, N = 200K, búsqueda aleatoria: las 5 repeticiones van de 24,3 a 35,0 s (CV = 14 %), mientras el tiempo de CPU sigue al de pared (cociente 0,997), por lo que
  no es interferencia de otros procesos. La causa (frecuencia de la CPU, temperatura, memoria) **no se verificó**. Es además el único punto sobre 30 s. No hay un efecto sistemático de la primera repetición: es la más rápida en 25 % de los puntos (20 % esperado por azar) y su diferencia mediana frente a las demás es de −0,06 %.
- **Puntos bajo 1 s.** 53 de 190 puntos están por debajo de 1 s (30 de los 163 de los otros experimentos y 23 de los 27 de N pequeños); todos son hallazgos de velocidad (ABB aleatorio y B+ con M = 60.000, Lista en construcción, Lista con N pequeño, B+ con N = 500K en construcción Lista con N = 4M y N pequeños con M = 2.000.000).
- **B+ en rango no monótono.** El tiempo por consulta baja de N = 100K a N = 200K; con un solo árbol por N no se puede distinguir si es efecto de la forma del árbol o de la memoria.
- Solo búsquedas con IDs existentes; los IDs son 0…N−1, sin huecos.
- M, Q y N distintos por grupo: no hay comparación directa en segundos entre grupos (se compara por tiempo por operación y por pendiente).
- `x in datos`, `bisect` y `sorted` se ejecutan en C, mientras que ABB y B+ son código Python: en otro lenguaje la distancia entre estructuras podría cambiar (por ejemplo, la ventaja de ≈ 6,8 veces de la Lista sobre el ABB degenerado).
- Un solo equipo; los valores absolutos no se extrapolan a otro hardware (sí las tendencias).
- Rango de N acotado por el tiempo: la Lista se mide solo hasta donde cabe en ~30 s.
- **Núcleo de ejecución.** La corrida de `n_pequenos` quedó fijada al núcleo lógico 2 de 16 (núcleo de rendimiento; mensaje de consola). Para los otros 14 experimentos **no se verificó** el núcleo: si `psutil` estaba instalado, las versiones de `comun_lab.py` usadas para las corridas fijaron el proceso al **último** núcleo lógico (el 15 de 16). En una CPU híbrida
  de 12.ª generación esos núcleos son de eficiencia, más lentos que los de rendimiento: afecta los valores absolutos (no las tendencias ni las comparaciones dentro de una misma corrida).
  **COMPLETAR** tras revisar el mensaje «Control de ruido» de la consola de cada corrida (indica el núcleo o «sin psutil»).
- Los valores absolutos de `n_pequenos` no se comparan con los de los demás experimentos (posible diferencia de núcleo): por ejemplo, el ABB tarda ≈ 0,42 µs por búsqueda con N = 1.000 aquí, frente a ≈ 0,78 µs con N = 2.000 en la comparación con IDs ordenados, lo que sugiere (no prueba) un núcleo más lento en esa corrida.

## 8. Reproducibilidad
`pip install -r requirements.txt` y `python correr_todo.py` (ver `README.md`). Las gráficas están
versionadas en `resultados_lab3/`; no hace falta correr los experimentos para verlas.
