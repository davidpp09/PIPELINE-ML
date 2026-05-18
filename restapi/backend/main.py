import asyncio
import websockets
import json
import numpy as np
import serial
import serial.tools.list_ports
import time
import os
import glob
from scipy import signal as sp_signal
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURACIÓN ---
BAUDIOS = 115200
OFFSET_12BITS = 2048
CARPETA_MUESTRAS = os.path.join(os.path.dirname(__file__), 'muestras')
PORT = int(os.environ.get("PORT", 8081))
HOST = "0.0.0.0"

# --- VARIABLES DE ESTADO GLOBALES ---
arduino = None
estado_sistema = "SISTEMA LISTO"
rf_model = None
is_trained = False
X_train = []
COLORES_INSTRUMENTOS = {
    "flauta": "#2ECC71",
    "guitarra": "#E74C3C",
    "teclado": "#3498DB",
    "violin": "#FFA500",
    "tambor": "#A52A2A",
    "esperando": "#AAAAAA"
}

def buscar_puerto_automatico():
    """Busca el puerto COM disponible más probable."""
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
    """Intenta establecer conexión con el ESP32."""
    global arduino
    puerto = buscar_puerto_automatico()
    if puerto:
        try:
            # Si ya hay un objeto serial, intentar cerrarlo limpiamente
            if arduino:
                try: arduino.close()
                except: pass
            
            arduino = serial.Serial(puerto, BAUDIOS, timeout=0.1)
            time.sleep(2)
            arduino.reset_input_buffer()
            print(f"✅ Conectado a ESP32 en {puerto}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar en {puerto}: {e}")
            arduino = None
    return False

def cargar_muestras_locales():
    """Entrena el modelo con las muestras guardadas en disco."""
    global X_train, rf_model, is_trained
    X, y = [], []
    if not os.path.exists(CARPETA_MUESTRAS):
        os.makedirs(CARPETA_MUESTRAS)
        
    archivos = glob.glob(os.path.join(CARPETA_MUESTRAS, "*.npy"))
    
    if len(archivos) < 2:
        print(f"⚠️ IA: Pocas muestras en {CARPETA_MUESTRAS}. Se requiere entrenamiento.")
        return

    for archivo in archivos:
        try:
            huella = np.load(archivo)
            huella_norm = (huella - np.min(huella)) / (np.max(huella) - np.min(huella) + 1e-10)
            X.append(huella_norm)
            etiqueta = os.path.basename(archivo).split('_')[0].lower()
            y.append(etiqueta)
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")
    
    if len(set(y)) < 2:
        return
        
    rf_model = RandomForestClassifier(n_estimators=300, random_state=42)
    rf_model.fit(X, y)
    X_train = X 
    is_trained = True
    print(f"✅ IA Entrenada para: {set(y)}")

# Intentar primera conexión al arrancar
intentar_conexion_serial()

buffer_senal = np.full(512, OFFSET_12BITS)

def leer_sensor_real():
    global buffer_senal, arduino
    if arduino:
        try:
            if arduino.in_waiting > 0:
                raw = arduino.read(arduino.in_waiting).decode('utf-8', errors='ignore').split('\n')
                for d in raw:
                    d = d.strip()
                    if d.isdigit():
                        val = float(d)
                        buffer_senal = np.roll(buffer_senal, -1)
                        buffer_senal[-1] = val
        except Exception as e:
            print(f"🔌 Conexión perdida: {e}")
            arduino = None # Marcar como desconectado para que el hilo de reconexión actúe
    return buffer_senal

def extraer_features(senal):
    senal_centrada = senal - OFFSET_12BITS
    f, t_s, Sxx = sp_signal.spectrogram(senal_centrada, fs=2500, nperseg=512)
    huella = np.mean(Sxx, axis=1)
    huella_norm = (huella - np.min(huella)) / (np.max(huella) - np.min(huella) + 1e-10)
    
    f0 = f[np.argmax(huella)]
    rms = np.sqrt(np.mean(senal_centrada**2))
    energia_fundamental = np.max(huella)
    thd = abs((np.sum(huella) - energia_fundamental) / (energia_fundamental + 1e-10))
    
    return huella_norm.tolist(), huella_norm, f0, rms, thd

async def recibir_comandos(websocket):
    global estado_sistema
    async for mensaje in websocket:
        comando = json.loads(mensaje)
        accion = comando.get("accion")
        if accion == "detectar":
            estado_sistema = "DETECTANDO"
        elif accion == "detener":
            estado_sistema = "SISTEMA LISTO"

async def enviar_datos(websocket):
    global estado_sistema, rf_model, is_trained
    while True:
        try:
            senal = leer_sensor_real()
            vector_ml, huella_visual, f0, rms, thd = extraer_features(senal)
            huella_64 = sp_signal.resample(huella_visual, 64).tolist()

            inst_detectado = "-"
            confianza = 0
            color = COLORES_INSTRUMENTOS["esperando"]

            # LÓGICA DE DETECCIÓN (Solo si está en modo DETECTANDO e IA está lista)
            if estado_sistema == "DETECTANDO" and is_trained:
                prediccion = rf_model.predict([vector_ml])[0]
                confianza = np.max(rf_model.predict_proba([vector_ml])[0]) * 100
                inst_detectado = prediccion.upper()
                color = COLORES_INSTRUMENTOS.get(prediccion.lower(), "#FFFFFF")
            
            # El envío de la señal y métricas DSP es CONTINUO (siempre lo verás en el front)
            paquete = {
                "estado_sistema": estado_sistema, 
                "instrumento": inst_detectado, 
                "color": color,
                "senal_tiempo": senal.tolist()[-100:], 
                "espectro_frecuencias": huella_64,
                "metricas_dsp": {
                    "f0": round(float(f0),1), 
                    "rms": round(float(rms),3), 
                    "thd": round(float(thd),2), 
                    "confianza": round(float(confianza),1)
                },
                "muestras_memoria": len(X_train), 
                "ia_lista": is_trained
            }
            await websocket.send(json.dumps(paquete))
            await asyncio.sleep(0.04) # ~25 FPS

        except websockets.exceptions.ConnectionClosed: break
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

async def gestor_conexiones(websocket):
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
    cargar_muestras_locales()
    # Iniciar la tarea de monitoreo de conexión en segundo plano
    asyncio.create_task(verificar_conexion_esp())
    
    async with websockets.serve(gestor_conexiones, HOST, PORT): 
        print(f"🚀 Servidor WebSocket iniciado en ws://{HOST}:{PORT}")
        await asyncio.Future()

if __name__ == "__main__": 
    asyncio.run(main())
