🖥️ Simulador de Planificación de CPU (SJN / SPN)

Este proyecto es un simulador desarrollado en Python que modela la administración de procesos en una CPU utilizando el algoritmo de planificación Más Corto Primero (SJN - Shortest Job Next / SPN - Shortest Process Next) sin desalojo.

Es una herramienta educativa diseñada para visualizar el ciclo de vida de los procesos dentro del sistema operativo basándose en un modelo de 5 estados.

⚙️ Características del Modelo

El simulador implementa transiciones realistas gestionadas por el Sistema Operativo (SO), con las siguientes reglas y tiempos fijos:

Modelo de Estados:

Nuevo -> Listo: Carga del proceso en memoria (Transición 1).

Listo -> Ejecución: Despacho a CPU (Transición 2).

Ejecución -> Bloqueado: Paso a E/S tras finalizar una ráfaga (Transición 3).

Bloqueado -> Listo: Fin de E/S y retorno a la cola de listos (Transición 4).

Ejecución -> Terminado: Finalización de la última ráfaga (Transición 6).
(Nota: La transición 5 no se utiliza al ser un algoritmo sin desalojo).

Tiempos Constantes:

Operaciones de E/S: 30 unidades de tiempo (u.t.).

Intervención del SO: 10 u.t. por cada transición de estado.

Intervalos de reloj: El simulador avanza en bloques de 10 u.t.

🚀 Funcionalidades

Ingreso interactivo: Permite configurar 4 procesos (P1 a P4) definiendo sus tiempos de llegada (múltiplos de 10) y sus respectivas ráfagas de CPU.

Algoritmo SJN: Toma decisiones de despacho evaluando dinámicamente qué proceso en la cola de "Listos" tiene la ráfaga de CPU más corta. Desempata por orden de llegada (FIFO).

Gráfica Temporal: Genera automáticamente un diagrama en consola (tipo Gantt) que detalla instante a instante qué proceso está en el SO, en Listo, en Ejecución, Bloqueado o Terminado.

Resumen de Métricas: Calcula e imprime el tiempo exacto de terminación para cada uno de los procesos.

🛠️ Tecnologías

Lenguaje: Python 3.x

Librerías: No requiere dependencias externas (utiliza la biblioteca estándar de Python).

💻 Instrucciones de Uso

Clona el repositorio en tu máquina local:

git clone https://github.com/agustinagronecatracchia/tu-repositorio-cpu.git


Navega al directorio del proyecto:

cd tu-repositorio-cpu


Ejecuta el script principal:

python Administracion_CPU.py


Sigue las instrucciones en pantalla para ingresar los tiempos de llegada y ráfagas (separadas por espacio) para cada uno de los 4 procesos.
