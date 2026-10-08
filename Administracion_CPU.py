"""
Simulador de Planificación de CPU: Más Corto Primero (SJN / SPN)
Modelo de 5 Estados en S.O.:
  1 Px: Nuevo -> Listo (Carga con prioridad)
  2 Px: Listo -> Exe (Despacho a CPU)
  3 Px: Exe -> Bloqueado (Paso a E/S tras fin de ráfaga)
  4 Px: Bloqueado -> Listo (Fin de E/S tras 30 u.t.)
  6 Px: Exe -> Terminado (Fin de última ráfaga)
  (5 Px no se utiliza por ser planificación sin desalojo)

Datos fijos:
- E/S: 30 unidades de tiempo
- SO: 10 unidades de tiempo
- Intervalos: de 10 en 10 unidades
"""

class Proceso:
    def __init__(self, pid, llegada, rafagas):
        self.pid = pid
        self.llegada = llegada
        self.rafagas = list(rafagas)
        self.indice_rafaga = 0
        self.tiempo_restante_rafaga = self.rafagas[0] if self.rafagas else 0
        
        # Control de Bloqueado y Listo
        self.tiempo_bloqueado_restante = 0
        self.tiempo_llegada_a_listo = -1
        
        # Estados posibles: 'NO_LLEGADO', 'LISTO', 'EXE', 'BLOQUEADO', 'TRANSICION', 'TERMINADO'
        self.estado = 'NO_LLEGADO'
        self.tiempo_terminacion = None

    @property
    def rafaga_actual(self):
        if self.indice_rafaga < len(self.rafagas):
            return self.rafagas[self.indice_rafaga]
        return 0


def simular():
    print("=" * 65)
    print(" ADMINISTRACIÓN DEL PROCESADOR - MÁS CORTO PRIMERO (SJN)")
    print(" DATOS FIJOS: E/S = 30 u.t. | SO = 10 u.t.")
    print("=" * 65)

    # 1. Ingreso de los 4 procesos
    procesos = []
    pids = ['P1', 'P2', 'P3', 'P4']
    for pid in pids:
        print(f"\n--- Configuración de {pid} ---")
        while True:
            try:
                llegada = int(input(f"Momento de entrada de {pid} (múltiplo de 10, ej: 0): "))
                if llegada < 0 or llegada % 10 != 0:
                    print("Debe ser mayor o igual a 0 y múltiplo de 10.")
                    continue
                break
            except ValueError:
                print("Entrada inválida. Ingrese un número entero.")

        while True:
            rafagas_input = input(f"Ráfagas de CPU de {pid} (separadas por espacio, ej: 20 10): ")
            try:
                rafagas = [int(x.strip()) for x in rafagas_input.replace(',', ' ').split() if x.strip()]
                if not rafagas or any(r <= 0 or r % 10 != 0 for r in rafagas):
                    print("Ingrese al menos una ráfaga positiva y múltiplo de 10.")
                    continue
                break
            except ValueError:
                print("Entrada inválida. Ingrese números enteros válidos.")

        procesos.append(Proceso(pid, llegada, rafagas))

    # Estructuras para la gráfica
    tiempos = []
    hist_so = []
    hist_listo = {p.pid: [] for p in procesos}
    hist_exe = {p.pid: [] for p in procesos}
    hist_bloq = {p.pid: [] for p in procesos}
    hist_terminado = []

    # Estado de la CPU:
    # Puede ser ('SO', etiqueta, proceso, tipo_transicion) o ('EXE', proceso) o None
    cpu_ocupada_por = None
    proc_en_cpu = None
    accion_so_actual = ""
    tipo_so_actual = None

    t = 0
    DELTA = 10

    while any(p.estado != 'TERMINADO' for p in procesos):
        # -------------------------------------------------------------
        # 1. RESOLUCIÓN DE EVENTOS AL INICIO DEL INSTANTE t
        # -------------------------------------------------------------

        # Si en el intervalo anterior la CPU estaba en EXE:
        if cpu_ocupada_por == 'EXE':
            if proc_en_cpu.tiempo_restante_rafaga == 0:
                # Terminó la ráfaga de CPU: Excepción de Pregunta 1
                proc_en_cpu.indice_rafaga += 1
                proc_en_cpu.estado = 'TRANSICION'  # Deja de estar en Exe
                
                if proc_en_cpu.indice_rafaga < len(proc_en_cpu.rafagas):
                    # Transición 3: Exe -> Bloqueado
                    cpu_ocupada_por = 'SO'
                    accion_so_actual = f"3 {proc_en_cpu.pid}"
                    tipo_so_actual = 'A_BLOQ'
                else:
                    # Transición 6: Exe -> Terminado
                    cpu_ocupada_por = 'SO'
                    accion_so_actual = f"6 {proc_en_cpu.pid}"
                    tipo_so_actual = 'A_TERM'

        # Si en el intervalo anterior la CPU estaba ejecutando SO:
        elif cpu_ocupada_por == 'SO':
            if tipo_so_actual == 'CARGAR':
                # Terminó 1 Px: pasa a Listo
                proc_en_cpu.estado = 'LISTO'
                proc_en_cpu.tiempo_llegada_a_listo = t
                cpu_ocupada_por = None
                proc_en_cpu = None
            elif tipo_so_actual == 'DESPACHAR':
                # Terminó 2 Px: pasa formalmente a Exe
                proc_en_cpu.estado = 'EXE'
                cpu_ocupada_por = 'EXE'
            elif tipo_so_actual == 'A_BLOQ':
                # Terminó 3 Px: pasa formalmente a Bloqueado con 30 u.t. de E/S
                proc_en_cpu.estado = 'BLOQUEADO'
                proc_en_cpu.tiempo_bloqueado_restante = 30
                cpu_ocupada_por = None
                proc_en_cpu = None
            elif tipo_so_actual == 'DESBLOQUEAR':
                # Terminó 4 Px: pasa formalmente a Listo
                proc_en_cpu.estado = 'LISTO'
                proc_en_cpu.tiempo_llegada_a_listo = t
                cpu_ocupada_por = None
                proc_en_cpu = None
            elif tipo_so_actual == 'A_TERM':
                # Terminó 6 Px: finaliza el proceso
                proc_en_cpu.estado = 'TERMINADO'
                proc_en_cpu.tiempo_terminacion = t
                cpu_ocupada_por = None
                proc_en_cpu = None

            accion_so_actual = ""
            tipo_so_actual = None

        # -------------------------------------------------------------
        # 2. EVALUACIÓN DE LAS 4 PREGUNTAS (SI LA CPU QUEDA LIBRE)
        # -------------------------------------------------------------
        if cpu_ocupada_por is None:
            # PREGUNTA 2: ¿Hay algo nuevo? (Prioridad de carga -> 1 Px)
            nuevos = [p for p in procesos if p.estado == 'NO_LLEGADO' and p.llegada <= t]
            if nuevos:
                nuevos.sort(key=lambda p: (p.llegada, p.pid))
                elegido = nuevos[0]
                elegido.estado = 'TRANSICION'
                proc_en_cpu = elegido
                cpu_ocupada_por = 'SO'
                accion_so_actual = f"1 {elegido.pid}"
                tipo_so_actual = 'CARGAR'

            else:
                # PREGUNTA 3: ¿Hay algo bloqueado que terminó su E/S? (4 Px)
                desbloqueables = [
                    p for p in procesos 
                    if p.estado == 'BLOQUEADO' and p.tiempo_bloqueado_restante <= 0
                ]
                if desbloqueables:
                    desbloqueables.sort(key=lambda p: p.pid)
                    elegido = desbloqueables[0]
                    elegido.estado = 'TRANSICION'
                    proc_en_cpu = elegido
                    cpu_ocupada_por = 'SO'
                    accion_so_actual = f"4 {elegido.pid}"
                    tipo_so_actual = 'DESBLOQUEAR'

                else:
                    # PREGUNTA 4: ¿Hay algo en listo para pasar a exe? (2 Px)
                    candidatos = [p for p in procesos if p.estado == 'LISTO']
                    if candidatos:
                        # Más Corto Primero (SJN) con desempate FIFO
                        candidatos.sort(key=lambda p: (p.rafaga_actual, p.tiempo_llegada_a_listo, p.pid))
                        elegido = candidatos[0]
                        # Permanece en Listo mientras se ejecuta el despacho
                        proc_en_cpu = elegido
                        cpu_ocupada_por = 'SO'
                        accion_so_actual = f"2 {elegido.pid}"
                        tipo_so_actual = 'DESPACHAR'
                        elegido.tiempo_restante_rafaga = elegido.rafaga_actual

        # -------------------------------------------------------------
        # 3. REGISTRO EN LA MATRIZ DEL INTERVALO [t, t + DELTA)
        # -------------------------------------------------------------
        tiempos.append(t)
        hist_so.append(accion_so_actual if cpu_ocupada_por == 'SO' else " ")

        for p in procesos:
            # Durante 2 Px el proceso sigue viéndose en Listo
            en_listo = (p.estado == 'LISTO')
            hist_listo[p.pid].append("X" if en_listo else " ")
            hist_exe[p.pid].append("X" if (cpu_ocupada_por == 'EXE' and proc_en_cpu == p) else " ")
            hist_bloq[p.pid].append("X" if p.estado == 'BLOQUEADO' else " ")

        terminados_en_t = [p.pid for p in procesos if p.estado == 'TERMINADO' and p.tiempo_terminacion == t]
        hist_terminado.append(",".join(terminados_en_t) if terminados_en_t else " ")

        # -------------------------------------------------------------
        # 4. AVANCE DEL TIEMPO (consumo de 10 u.t.)
        # -------------------------------------------------------------
        if cpu_ocupada_por == 'EXE':
            proc_en_cpu.tiempo_restante_rafaga -= DELTA

        # Descuento de tiempo en Bloqueado
        for p in procesos:
            if p.estado == 'BLOQUEADO':
                p.tiempo_bloqueado_restante -= DELTA

        t += DELTA

    # Registro final al terminar la simulación
    tiempos.append(t)
    hist_so.append(" ")
    for p in procesos:
        hist_listo[p.pid].append(" ")
        hist_exe[p.pid].append(" ")
        hist_bloq[p.pid].append(" ")
    terminados_final = [p.pid for p in procesos if p.tiempo_terminacion == t]
    hist_terminado.append(",".join(terminados_final) if terminados_final else " ")

    # -------------------------------------------------------------
    # 5. IMPRESIÓN DE LA GRÁFICA CONTINUA
    # -------------------------------------------------------------
    max_t = max(tiempos) if tiempos else 0
    ANCHO_COL = max(7, len(str(max_t)) + 2)
    ANCHO_ETIQ = 12

    def format_line(label, values):
        linea = label.ljust(ANCHO_ETIQ)
        for v in values:
            linea += f"| {str(v):^{ANCHO_COL - 2}} "
        linea += "|"
        return linea

    print("\n" + "=" * 80)
    print("GRÁFICA DE ADMINISTRACIÓN DEL PROCESADOR")
    print("=" * 80)

    # SO
    print(format_line("SO", hist_so))

    # Listo
    print("Listo")
    for pid in pids:
        print(format_line(f"  {pid}", hist_listo[pid]))

    # Exe
    print("Exe")
    for pid in pids:
        print(format_line(f"  {pid}", hist_exe[pid]))

    # Bloqueado
    print("Bloqueado")
    for pid in pids:
        print(format_line(f"  {pid}", hist_bloq[pid]))

    # Terminado
    print(format_line("Terminado", hist_terminado))

    # Línea de unidades de tiempo (de 10 en 10)
    linea_tiempo = "Tiempo".ljust(ANCHO_ETIQ)
    for ti in tiempos:
        linea_tiempo += f"| {str(ti):^{ANCHO_COL - 2}} "
    linea_tiempo += "|"
    print(linea_tiempo)

    # -------------------------------------------------------------
    # 6. RESUMEN FINAL
    # -------------------------------------------------------------
    print("\n" + "-" * 50)
    print("TIEMPOS DE TERMINACIÓN DE CADA PROCESO:")
    print("-" * 50)
    for p in procesos:
        print(f"El proceso {p.pid} terminó en la unidad de tiempo: {p.tiempo_terminacion}")
    print("-" * 50 + "\n")


if __name__ == "__main__":
    simular()