# =============================================================================
# BACKEND DEL DETECTOR DE INSTRUMENTOS
# -----------------------------------------------------------------------------
# Este programa hace 3 trabajos al mismo tiempo (usando asyncio):
#   1. LEE el sensor: el ESP32 manda por serial/Bluetooth cada muestra del ADC
#      de 12 bits (valores 0..4095) como una línea de texto.
#   2. PROCESA la señal (DSP): calcula el espectrograma, la "huella espectral"
#      y métricas como f0 (frecuencia fundamental), RMS y THD.
#   3. CLASIFICA con IA: un Random Forest entrenado con huellas guardadas en
#      disco predice qué instrumento está sonando.
# El resultado se manda al frontend (React) por WebSocket, ~25 veces/segundo.
# =============================================================================

import asyncio            # corre las tareas concurrentes (leer sensor + atender WebSocket)
import websockets          # servidor WebSocket para hablar con el frontend
import json                # los paquetes que viajan por el WebSocket son JSON
import sys
import numpy as np         # arreglos numéricos: la señal y las huellas son np.array

# La consola de Windows usa cp1252 y no puede imprimir emojis; sin esto el
# backend puede caerse al hacer print(). Forzamos UTF-8 en la salida.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import serial                       # comunicación con el ESP32 (puerto COM)
import serial.tools.list_ports      # para listar los puertos COM disponibles
import time
import os
import glob                         # para buscar los archivos .npy de muestras
from scipy import signal as sp_signal              # spectrogram() y resample()
from sklearn.ensemble import RandomForestClassifier  # el modelo de IA

# --- CONFIGURACIÓN ---
BAUDIOS = 115200            # velocidad del puerto serial (debe coincidir con el ESP32)
OFFSET_12BITS = 2048        # centro teórico del ADC de 12 bits (4096 / 2)
CARPETA_MUESTRAS = os.path.join(os.path.dirname(__file__), 'muestras')  # dónde viven los .npy
PORT = int(os.environ.get("PORT", 8081))   # puerto del WebSocket (configurable por env var)
HOST = "0.0.0.0"            # escucha en todas las interfaces de red de la PC

# --- VARIABLES DE ESTADO GLOBALES ---
# (Todo el programa comparte este estado; las tareas asyncio lo leen/escriben)
arduino = None                    # objeto serial.Serial conectado al ESP32 (None = desconectado)
estado_sistema = "SISTEMA LISTO"  # texto de estado que ve el usuario en el frontend
rf_model = None                   # el RandomForestClassifier entrenado
is_trained = False                # True cuando el modelo ya se entrenó con éxito
X_train = []                      # huellas usadas en el último entrenamiento (solo para mostrar el conteo)
conteo_muestras = {}   # {etiqueta: nº de archivos .npy} para mostrar en el front
COLORES_INSTRUMENTOS = {          # color con el que el frontend pinta cada instrumento
    "flauta": "#2ECC71",
    "guitarra": "#E74C3C",
    "teclado": "#3498DB",
    "violin": "#FFA500",
    "tambor": "#A52A2A",
    "esperando": "#AAAAAA"
}

# Variables para la grabación de 5 segundos (se llena cuando el usuario pulsa ESCUCHAR o GRABAR)
buffer_grabacion = []     # aquí se acumulan TODAS las muestras crudas durante los 5 s
inicio_grabacion = 0      # timestamp de cuándo empezó la grabación
DURACION_5S = 5.0         # duración fija de cada grabación

# Tipo de la grabación actual:
#   "deteccion" -> al terminar, predice el instrumento (comportamiento normal)
#   "muestra"   -> al terminar, guarda la huella como muestra de entrenamiento
tipo_grabacion = "deteccion"
etiqueta_grabacion = ""        # etiqueta (instrumento) con la que se guarda la muestra
INSTRUMENTOS_VALIDOS = ["flauta", "guitarra", "teclado", "violin", "tambor"]

# Estimación de la frecuencia de muestreo REAL.
# La fs no es 2500 fija: depende de la velocidad del serial/Bluetooth y tiene jitter.
# La medimos contando cuántas muestras llegan por segundo.
fs_estimada = 2500.0          # valor inicial razonable hasta tener medición
_contador_muestras = 0        # muestras recibidas en la ventana actual
_inicio_ventana_fs = time.time()

# Snapshot "congelado" del último resultado: señal, huella y métricas
# del sonido que realmente se grabó (para que el front quede congelado en él).
senal_resultado = None
espectro_resultado = None
metricas_resultado = None

def buscar_puerto_automatico():
    """Busca el puerto COM disponible más probable.

    Recorre los puertos seriales del sistema y prioriza los que en su
    descripción mencionan chips USB-serial típicos del ESP32 (CP210x, CH340).
    Si ninguno coincide, devuelve el primero que haya.
    """
    puertos = list(serial.tools.list_ports.comports())
    if not puertos:
        return None

    # Priorizar puertos que digan "USB", "CP210", "CH340" o "Arduino"
    for p in puertos:
        desc = p.description.upper()
        if any(keyword in desc for keyword in ["USB", "CP210", "CH340", "ARDUINO", "ESP32"]):
            return p.device

    return puertos[0].device if puertos else None

def intentar_conexion_serial():
    """Intenta abrir el puerto serial hacia el ESP32. Devuelve True si conectó."""
    global arduino
    # Detecta automáticamente el puerto de la ESP32 (USB o Bluetooth).
    # Si defines la variable de entorno ESP32_PORT, se usa ese puerto en su lugar.
    puerto_bluetooth = os.environ.get("ESP32_PORT") or buscar_puerto_automatico()

    if puerto_bluetooth:
        try:
            # Si había una conexión anterior a medio morir, la cerramos primero
            if arduino:
                try: arduino.close()
                except: pass

            # Aumentamos ligeramente el timeout por la latencia del Bluetooth
            arduino = serial.Serial(puerto_bluetooth, BAUDIOS, timeout=1.0)

            # ELIMINAMOS las líneas de setDTR(False) y setRTS(False)
            # ya que causan conflictos en puertos Bluetooth.

            time.sleep(2)                  # darle tiempo al ESP32 de reiniciarse tras abrir el puerto
            arduino.reset_input_buffer()   # descartar datos viejos acumulados en el buffer
            print(f"✅ Conectado a ESP32 vía Bluetooth en {puerto_bluetooth}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar al Bluetooth en {puerto_bluetooth}: {e}")
            arduino = None
    return False

def cargar_muestras_locales():
    """Entrena el modelo con las muestras guardadas en disco.

    Cada archivo .npy es una "huella espectral" (espectrograma promediado en el
    tiempo). La etiqueta del instrumento viene en el NOMBRE del archivo:
    p. ej. "guitarra_1780668808134.npy" -> etiqueta "guitarra".
    """
    global X_train, rf_model, is_trained, conteo_muestras
    X, y = [], []   # X = lista de huellas (features), y = lista de etiquetas
    if not os.path.exists(CARPETA_MUESTRAS):
        os.makedirs(CARPETA_MUESTRAS)

    archivos = glob.glob(os.path.join(CARPETA_MUESTRAS, "*.npy"))

    # Recontamos cuántas muestras hay por instrumento (para mostrarlo en el front).
    conteo = {}
    for archivo in archivos:
        etiqueta = os.path.basename(archivo).split('_')[0].lower()
        conteo[etiqueta] = conteo.get(etiqueta, 0) + 1
    conteo_muestras = conteo

    if len(archivos) < 2:
        print(f"⚠️ IA: Pocas muestras en {CARPETA_MUESTRAS}. Se requiere entrenamiento.")
        return

    for archivo in archivos:
        try:
            huella = np.load(archivo)
            # Normalización min-max a [0, 1]: el clasificador debe aprender la
            # FORMA del espectro (el timbre), no el volumen al que se grabó.
            # El +1e-10 evita división entre cero si la huella es plana.
            huella_norm = (huella - np.min(huella)) / (np.max(huella) - np.min(huella) + 1e-10)
            X.append(huella_norm)
            etiqueta = os.path.basename(archivo).split('_')[0].lower()
            y.append(etiqueta)
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")

    # Un clasificador necesita al menos 2 clases distintas para tener algo que separar
    if len(set(y)) < 2:
        print("⚠️ IA: Se necesitan al menos 2 instrumentos distintos para entrenar.")
        return

    # Random Forest: 300 árboles de decisión que "votan" la clase.
    # random_state=42 hace el entrenamiento reproducible.
    rf_model = RandomForestClassifier(n_estimators=300, random_state=42)
    rf_model.fit(X, y)
    X_train = X
    is_trained = True
    print(f"✅ IA Entrenada para: {set(y)}")


def guardar_muestra(huella_raw, etiqueta):
    """Guarda una huella espectral como nueva muestra de entrenamiento y reentrena.

    `huella_raw` es la huella SIN normalizar (mismo formato que las muestras ya
    existentes en disco; `cargar_muestras_locales` las normaliza al cargarlas).
    Devuelve la ruta del archivo guardado.
    """
    if not os.path.exists(CARPETA_MUESTRAS):
        os.makedirs(CARPETA_MUESTRAS)

    etiqueta = etiqueta.strip().lower()
    # timestamp en ms para no colisionar con archivos existentes
    nombre = f"{etiqueta}_{int(time.time() * 1000)}.npy"
    ruta = os.path.join(CARPETA_MUESTRAS, nombre)
    np.save(ruta, np.asarray(huella_raw))
    print(f"💾 Muestra guardada: {nombre}")

    # Reentrenamos en caliente para que la nueva muestra cuente de inmediato.
    cargar_muestras_locales()
    return ruta

# Intentar primera conexión al arrancar
intentar_conexion_serial()

# Buffer circular con las últimas 512 muestras de la señal (para la vista en vivo).
# Se inicializa en 2048 (el centro del ADC) para que arranque como línea plana.
buffer_senal = np.full(512, OFFSET_12BITS)

def leer_sensor_real():
    """Vacía el buffer del puerto serial y actualiza el buffer de señal.

    - Cada línea de texto que manda el ESP32 es UNA muestra del ADC.
    - Mantiene las últimas 512 muestras en `buffer_senal` (ventana deslizante).
    - Si hay una grabación de 5 s activa, también acumula en `buffer_grabacion`.
    - De paso mide la frecuencia de muestreo REAL (muestras recibidas / segundo).
    """
    global buffer_senal, arduino, buffer_grabacion, estado_sistema
    global fs_estimada, _contador_muestras, _inicio_ventana_fs
    if arduino:
        try:
            # Mientras haya datos en el buffer del Bluetooth
            while arduino.in_waiting > 0:
                # readline() lee hasta encontrar un salto de línea (\n)
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()

                # Validamos que no esté vacío y contenga números o puntos decimales
                # lstrip('-') permite que valores como "-15.4" sean aceptados y graficados
                if linea and linea.lstrip('-').replace('.', '', 1).isdigit():
                    val = float(linea)
                    # np.roll(-1) desplaza todo una posición a la izquierda y
                    # metemos la muestra nueva al final: ventana deslizante.
                    buffer_senal = np.roll(buffer_senal, -1)
                    buffer_senal[-1] = val
                    _contador_muestras += 1

                    # Si estamos grabando, acumulamos
                    if "GRABANDO" in estado_sistema:
                        buffer_grabacion.append(val)

            # Actualizamos la fs estimada (en vivo) cada ~1 segundo.
            # Si asumiéramos fs=2500 fija y la real fuera otra, TODO el eje de
            # frecuencias del espectro saldría mal escalado.
            transcurrido = time.time() - _inicio_ventana_fs
            if transcurrido >= 1.0:
                if _contador_muestras > 0:
                    # Filtro suave (media móvil exponencial): 70% del valor anterior
                    # + 30% de la medición nueva, para evitar saltos por el jitter del BT.
                    fs_medida = _contador_muestras / transcurrido
                    fs_estimada = 0.7 * fs_estimada + 0.3 * fs_medida
                _contador_muestras = 0
                _inicio_ventana_fs = time.time()

        except Exception as e:
            print(f"🔌 Conexión Bluetooth perdida: {e}")
            arduino = None   # la tarea de fondo verificar_conexion_esp() reintentará
    return buffer_senal

def extraer_features(senal, fs=2500):
    """Núcleo de DSP: convierte una señal en el tiempo a su "huella espectral".

    Pasos:
      1. Quitar el offset DC (restar la media).
      2. Espectrograma (FFT por ventanas) -> matriz frecuencia x tiempo.
      3. Promediar en el tiempo -> un solo vector "huella" (energía por banda).
      4. Calcular métricas: f0, RMS y THD.

    Devuelve: (huella_norm como lista, huella_norm np.array, f0, rms, thd, huella sin normalizar)
    """
    # Restamos la media REAL de la señal (no un offset fijo de 2048).
    # El bias del ADC casi nunca es exactamente 2048; el residuo de DC se va
    # al bin 0 del espectro y hace que argmax devuelva f0 ~ 0 (medición falsa).
    senal_centrada = senal - np.mean(senal)
    # nperseg = tamaño de cada ventana de la FFT (define la resolución en frecuencia).
    # No puede ser mayor que la longitud de la señal.
    nperseg = min(512, len(senal_centrada))
    f, t_s, Sxx = sp_signal.spectrogram(senal_centrada, fs=fs, nperseg=nperseg)
    # Sxx es una matriz [frecuencia x tiempo]; al promediar sobre el eje del
    # tiempo obtenemos el espectro promedio = la "huella" del timbre.
    huella = np.mean(Sxx, axis=1)
    # Normalización a [0,1] para que el volumen no afecte la clasificación
    huella_norm = (huella - np.min(huella)) / (np.max(huella) - np.min(huella) + 1e-10)

    # f0 = frecuencia del bin con más energía (la fundamental, aproximadamente)
    f0 = f[np.argmax(huella)]
    # RMS = raíz de la media de los cuadrados = medida de la potencia/volumen
    rms = np.sqrt(np.mean(senal_centrada**2))
    # THD aproximada: energía que NO está en el pico principal, relativa al pico.
    # (Una señal "pura" tipo flauta -> THD baja; una rica en armónicos -> THD alta)
    energia_fundamental = np.max(huella)
    thd = abs((np.sum(huella) - energia_fundamental) / (energia_fundamental + 1e-10))

    # Devolvemos también la huella SIN normalizar para poder guardarla como
    # muestra de entrenamiento en el mismo formato que las existentes.
    return huella_norm.tolist(), huella_norm, f0, rms, thd, huella

async def recibir_comandos(websocket):
    """Tarea que ESCUCHA al frontend: cada botón de la página manda un JSON
    {"accion": ...} y aquí se traduce a cambios en el estado global."""
    global estado_sistema, buffer_grabacion, inicio_grabacion
    global senal_resultado, espectro_resultado, metricas_resultado
    global tipo_grabacion, etiqueta_grabacion
    async for mensaje in websocket:
        comando = json.loads(mensaje)
        accion = comando.get("accion")
        if accion == "detectar":
            # Botón "ESCUCHAR (5s)": arranca una grabación en modo detección
            tipo_grabacion = "deteccion"
            estado_sistema = "GRABANDO 5s..."
            buffer_grabacion = []
            inicio_grabacion = time.time()
            # Descongelar: limpiamos el snapshot anterior
            senal_resultado = espectro_resultado = metricas_resultado = None
        elif accion == "grabar_muestra":
            # Botón "GRABAR": graba 5 s y guarda la huella como muestra de entrenamiento.
            etiqueta = str(comando.get("etiqueta", "")).strip().lower()
            if not etiqueta:
                estado_sistema = "ERROR: FALTA ETIQUETA"
            else:
                tipo_grabacion = "muestra"
                etiqueta_grabacion = etiqueta
                estado_sistema = "GRABANDO 5s..."
                buffer_grabacion = []
                inicio_grabacion = time.time()
                senal_resultado = espectro_resultado = metricas_resultado = None
        elif accion == "detener":
            # Botón "DETENER / RESET": cancela todo y vuelve al estado inicial
            tipo_grabacion = "deteccion"
            estado_sistema = "SISTEMA LISTO"
            buffer_grabacion = []
            senal_resultado = espectro_resultado = metricas_resultado = None

async def enviar_datos(websocket):
    """Tarea principal (bucle a ~25 FPS) que HABLA con el frontend:
      - lee el sensor y procesa la señal en vivo,
      - controla la máquina de estados de la grabación de 5 s,
      - cuando termina la grabación: predice el instrumento o guarda la muestra,
      - manda el paquete JSON con todo (señal, espectro, métricas, estado)."""
    global estado_sistema, rf_model, is_trained, buffer_grabacion, inicio_grabacion
    global senal_resultado, espectro_resultado, metricas_resultado
    global tipo_grabacion
    inst_detectado = "-"
    color = COLORES_INSTRUMENTOS["esperando"]
    confianza = 0

    while True:
        try:
            senal = leer_sensor_real()
            # Usamos siempre los últimos 512 para el espectrograma visual,
            # con la fs REAL estimada (no la asumida de 2500).
            vector_ml_visual, huella_visual, f0, rms, thd, _ = extraer_features(senal, fs=fs_estimada)
            # La huella tiene 257 bins; la re-muestreamos a 64 barras para la gráfica
            huella_64 = sp_signal.resample(huella_visual, 64).tolist()

            # LÓGICA DE DETECCIÓN POR GRABACIÓN (5 segundos)
            if "GRABANDO" in estado_sistema:
                # Mostramos la cuenta regresiva en el estado (ej. "GRABANDO 3.2s")
                tiempo_transcurrido = time.time() - inicio_grabacion
                estado_sistema = f"GRABANDO {round(max(0, DURACION_5S - tiempo_transcurrido), 1)}s"

                if tiempo_transcurrido >= DURACION_5S:
                    # --- Se cumplieron los 5 segundos: procesar la grabación ---
                    estado_sistema = "PROCESANDO..."
                    num_muestras = len(buffer_grabacion)
                    print(f"📊 Grabación finalizada. Muestras capturadas: {num_muestras}")

                    if num_muestras > 512:
                        # Procesamos TODA la grabación para obtener una huella promedio más estable
                        senal_grabada = np.array(buffer_grabacion)
                        # fs REAL de esta grabación: medida exacta = muestras / tiempo real grabado.
                        # Esto es lo más preciso porque conocemos ambos números con certeza.
                        fs_real = num_muestras / max(tiempo_transcurrido, 1e-6)
                        print(f"⏱️  fs real medida en la grabación: {fs_real:.1f} Hz")
                        # extraer_features ya promedia el espectrograma,
                        # así que funcionará bien con señales largas.
                        vector_ml, huella_res, f0_res, rms_res, thd_res, huella_raw = extraer_features(senal_grabada, fs=fs_real)

                        if tipo_grabacion == "muestra":
                            # --- MODO GRABAR MUESTRA: guardar y reentrenar ---
                            guardar_muestra(huella_raw, etiqueta_grabacion)
                            inst_detectado = etiqueta_grabacion.upper()
                            color = COLORES_INSTRUMENTOS.get(etiqueta_grabacion.lower(), "#FFFFFF")
                            estado_sistema = f"MUESTRA GUARDADA: {etiqueta_grabacion.upper()}"
                            confianza = 0
                            # Guardamos versiones reducidas (400 y 64 puntos) para graficar
                            senal_resultado = sp_signal.resample(senal_grabada, 400).tolist()
                            espectro_resultado = sp_signal.resample(huella_res, 64).tolist()
                            metricas_resultado = {
                                "f0": round(float(f0_res), 1),
                                "rms": round(float(rms_res), 3),
                                "thd": round(float(thd_res), 2),
                                "confianza": 0.0
                            }
                        elif is_trained:
                            # --- MODO DETECCIÓN: predecir instrumento ---
                            # predict() da la clase ganadora; predict_proba() da la
                            # fracción de árboles que votó por ella (la "confianza").
                            prediccion = rf_model.predict([vector_ml])[0]
                            confianza = np.max(rf_model.predict_proba([vector_ml])[0]) * 100
                            inst_detectado = prediccion.upper()
                            color = COLORES_INSTRUMENTOS.get(prediccion.lower(), "#FFFFFF")
                            estado_sistema = "RESULTADO LISTO"
                            print(f"🎯 Resultado: {inst_detectado} ({confianza:.1f}%)")

                            # Guardamos el snapshot del sonido grabado para "congelar" el front
                            senal_resultado = sp_signal.resample(senal_grabada, 400).tolist()
                            espectro_resultado = sp_signal.resample(huella_res, 64).tolist()
                            metricas_resultado = {
                                "f0": round(float(f0_res), 1),
                                "rms": round(float(rms_res), 3),
                                "thd": round(float(thd_res), 2),
                                "confianza": round(float(confianza), 1)
                            }
                        else:
                            estado_sistema = "ERROR: IA SIN ENTRENAR"
                            print("⚠️ No se puede detectar: el modelo no está entrenado.")
                    else:
                        # Menos de 512 muestras en 5 s = el sensor casi no mandó datos
                        estado_sistema = "ERROR: POCOS DATOS"
                        print(f"⚠️ Error: Solo se capturaron {num_muestras} muestras.")

                    tipo_grabacion = "deteccion"
                    buffer_grabacion = []

            # El envío de la señal y métricas DSP es CONTINUO
            paquete = {
                "estado_sistema": estado_sistema,
                "instrumento": inst_detectado,
                "color": color,
                "senal_tiempo": senal.tolist()[-400:], # Aumentamos a 400 para que se vea más onda
                "espectro_frecuencias": huella_64,
                "metricas_dsp": {
                    "f0": round(float(f0),1),
                    "rms": round(float(rms),3),
                    "thd": round(float(thd),2),
                    "confianza": round(float(confianza),1)
                },
                "muestras_memoria": len(X_train),
                "ia_lista": is_trained,
                "conteo_muestras": conteo_muestras,
                "instrumentos_validos": INSTRUMENTOS_VALIDOS
            }

            # Si hay un resultado listo, congelamos la señal/huella/métricas del
            # sonido grabado (en vez de la señal en vivo, que ya podría ser silencio).
            if (estado_sistema == "RESULTADO LISTO" or estado_sistema.startswith("MUESTRA GUARDADA")) and senal_resultado is not None:
                paquete["senal_tiempo"] = senal_resultado
                paquete["espectro_frecuencias"] = espectro_resultado
                paquete["metricas_dsp"] = metricas_resultado

            # DEBUG: Imprimir estructura una vez cada 5 s para verificar
            if time.time() - getattr(enviar_datos, "_last_debug", 0) > 5:
                print(f"📡 Enviando JSON: {list(paquete.keys())}")
                print(f"📈 Senal samples: {len(paquete['senal_tiempo'])} | F0: {paquete['metricas_dsp']['f0']}")
                enviar_datos._last_debug = time.time()

            await websocket.send(json.dumps(paquete))
            await asyncio.sleep(0.04) # ~25 FPS

        except websockets.exceptions.ConnectionClosed: break
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

async def gestor_conexiones(websocket):
    """Por cada cliente que se conecta al WebSocket se lanzan 2 tareas en
    paralelo: una que recibe sus comandos y otra que le manda datos.
    Cuando cualquiera de las dos termina (p. ej. se cierra la conexión),
    la atención a ese cliente acaba."""
    print("¡Front-end conectado!")
    await asyncio.wait([
        asyncio.create_task(recibir_comandos(websocket)),
        asyncio.create_task(enviar_datos(websocket))
    ], return_when=asyncio.FIRST_COMPLETED)

async def verificar_conexion_esp():
    """Tarea de fondo que intenta reconectar el ESP32 si se pierde la conexión."""
    global arduino
    while True:
        if arduino is None:
            # print("🔍 Buscando ESP32...") # Opcional: demasiado ruidoso
            intentar_conexion_serial()
        await asyncio.sleep(5) # Reintentar cada 5 segundos

async def main():
    """Punto de entrada: entrena la IA con lo que haya en disco, lanza el
    monitor de reconexión del ESP32 y deja el servidor WebSocket escuchando."""
    cargar_muestras_locales()
    # Iniciar la tarea de monitoreo de conexión en segundo plano
    asyncio.create_task(verificar_conexion_esp())

    async with websockets.serve(gestor_conexiones, HOST, PORT):
        print(f"🚀 Servidor WebSocket iniciado en ws://{HOST}:{PORT}")
        await asyncio.Future()   # esperar para siempre (el servidor no termina solo)

if __name__ == "__main__":
    asyncio.run(main())
