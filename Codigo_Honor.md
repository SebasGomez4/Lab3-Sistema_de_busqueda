# Uso de herramientas de IA

Según el código de honor, se declara el uso de IA en este laboratorio.

**Herramientas:** Claude (Anthropic) y Gemini (Google), por chat.

**Para qué se usó**
- Consultar conceptos (complejidad, B+, escalamiento, estadística de las mediciones).
- Generar y corregir código: estructuras de datos, scripts de medición y de gráficas.
- Sugerir métodos estadísticos (media, desviación estándar muestral, IC95% con t de Student,
  coeficiente de variación, pendiente log-log como estimador del exponente).
- Producir las gráficas a partir de los CSV y ayudar a redactar el informe.
- Ayudar a redactar informe y README

**Decisiones tomadas por el estudiante tras revisar el trabajo de la IA**
- Se descartó una estrategia de extrapolación de tiempos (medir con menos operaciones y escalar):
  un tiempo extrapolado es una predicción, no una medición, y asume la complejidad que se quiere
  comprobar. Todos los tiempos reportados son medidos.
- Se descartaron las gráficas en escala logarítmica; se evitó el rango amplio de valores separando
  los experimentos por estructura, cada uno con su propio M y N.
- Se reemplazó el B+ simplificado del script inicial por un B+ completo (nodos internos, splits en cascada,
  hojas enlazadas).

**Verificación del estudiante**
- Los datos son reales: se corrieron los scripts en mi equipo y los CSV de `resultados_lab3/` salen de esas corridas.
- Las gráficas representan los datos: cada PNG se genera desde su CSV con `comun_lab.py`.
- Las conclusiones corresponden a los resultados: ver informe, sección de interpretación.
