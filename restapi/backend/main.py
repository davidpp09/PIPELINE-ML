import asyncio
import websockets
import json
import numpy as np
import random
from scipy import signal as sp_signal
from sklearn.ensemble import RandomForestClassifier

# --- MOTOR DE MACHINE LEARNING ---
X_train = [] # Aquí se guardarán las matrices de Fourier
y_train = [] # Aquí las etiquetas ("flauta", "guitarra", etc)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
is_trained = False
estado_sistema = "ESPERANDO COMANDOS..."

# Simulación de hardware (TU COMPAÑERO DEBE CAMBIAR ESTO POR PYSERIAL)
def leer_sensor(tipo, t):
    # TODO: COMPAÑERO, AQUÍ METE LA LECTURA DEL ARDUINO (serial.readline)
    # Por ahora, usamos la matemática perfecta para probar
    t_axis = np.linspace(t, t + 0.1, 256)
    if tipo == "flauta": senal = np.sin(2 * np.pi * 880 * t_axis)
    elif tipo == "guitarra": senal = np.sin(2 * np.pi * 440 * t_axis) + 0.5 * np.sin(2 * np.pi * 880 * t_axis)
    else: senal = sp_signal.square(2 * np.pi * 220 * t_axis)
    return senal + np.random.normal(0, 0.05, 256)

def extraer_features(senal):
    """Pipeline DSP: Convierte el audio crudo en datos para la IA"""
    f, t_s, Sxx = sp_signal.spectrogram(senal, fs=2500, nperseg=64)
    huella = np.mean(Sxx, axis=1)
    
    f0 = f[np.argmax(huella)]
    rms = np.sqrt(np.mean(senal**2))
    energia_fundamental = np.max(huella)
    thd = abs((np.sum(huella) - energia_fundamental) / (energia_fundamental + 1e-10))
    huella_norm = huella / (np.max(huella) + 1e-10)
    
    # El vector final tiene 67 dimensiones: [f0, rms, thd, huella_0, huella_1... huella_63]
    vector_ml = [f0, rms, thd] + huella_norm.tolist()
    return vector_ml, huella_norm, f0, rms, thd

# --- HILO 1: RECIBIR ÓRDENES DE REACT ---
async def recibir_comandos(websocket):
    global estado_sistema, rf_model, is_trained, X_train, y_train
    async for mensaje in websocket:
        comando = json.loads(mensaje)
        accion = comando.get("accion")
        
        if accion == "grabar_datos":
            estado_sistema = f"GRABANDO_{comando.get('instrumento')}"
        elif accion == "entrenar_modelo":
            if len(X_train) > 10:
                print("Entrenando Random Forest...")
                rf_model.fit(X_train, y_train)
                is_trained = True
                estado_sistema = "MODELO_LISTO"
        elif accion == "detectar":
            estado_sistema = "DETECTANDO"
        elif accion == "detener":
            estado_sistema = "ESPERANDO COMANDOS..."

# --- HILO 2: ENVIAR DATOS A REACT ---
async def enviar_datos(websocket):
    global estado_sistema, rf_model, is_trained, X_train, y_train
    t = 0
    while True:
        try:
            if estado_sistema == "ESPERANDO COMANDOS..." or estado_sistema == "MODELO_LISTO":
                ruido = np.random.normal(0, 0.1, 256)
                paquete = {
                    "estado_sistema": estado_sistema, "instrumento": "-", "color": "#888888",
                    "senal_tiempo": ruido.tolist()[:100], "espectro_frecuencias": np.zeros(64).tolist(),
                    "metricas_dsp": {"f0": 0, "rms": 0, "thd": 0, "confianza": 0},
                    "muestras_memoria": len(X_train), "ia_lista": is_trained
                }
                await websocket.send(json.dumps(paquete))
                await asyncio.sleep(0.1)

            elif estado_sistema.startswith("GRABANDO_"):
                # Fase de recolección de dataset (2 segundos por clic)
                inst_target = estado_sistema.split("_")[1]
                for _ in range(20): 
                    senal = leer_sensor(inst_target, t)
                    vector_ml, huella, f0, rms, thd = extraer_features(senal)
                    X_train.append(vector_ml) # Guardamos características
                    y_train.append(inst_target) # Guardamos etiqueta
                    
                    paquete = {
                        "estado_sistema": f"RECOLECTANDO DATOS: {inst_target.upper()}", "instrumento": "APRENDIENDO...", "color": "#F39C12",
                        "senal_tiempo": senal.tolist()[:100], "espectro_frecuencias": huella.tolist(),
                        "metricas_dsp": {"f0": round(float(f0),1), "rms": round(float(rms),3), "thd": round(float(thd),2), "confianza": 0},
                        "muestras_memoria": len(X_train), "ia_lista": is_trained
                    }
                    await websocket.send(json.dumps(paquete))
                    t += 0.015
                    await asyncio.sleep(0.1)
                estado_sistema = "ESPERANDO COMANDOS..."

            elif estado_sistema == "DETECTANDO":
                if not is_trained:
                    estado_sistema = "ESPERANDO COMANDOS..."
                    continue
                
                # Fase 1: Escucha ambiental
                for _ in range(15):
                    await websocket.send(json.dumps({"estado_sistema": "ESCUCHANDO ENTORNO...", "instrumento": "?", "color": "#F1C40F", "senal_tiempo": np.random.normal(0, 0.2, 100).tolist(), "espectro_frecuencias": np.zeros(64).tolist(), "metricas_dsp": {"f0": 0, "rms": 0, "thd": 0, "confianza": 0}, "muestras_memoria": len(X_train), "ia_lista": is_trained}))
                    await asyncio.sleep(0.1)

                # Fase 2: Inferencia de IA
                inst_entrada = random.choice(["flauta", "guitarra", "teclado"]) # Simula lo que toca el usuario
                senal = leer_sensor(inst_entrada, t)
                vector_ml, _, _, _, _ = extraer_features(senal)
                
                # LA IA TOMA LA DECISIÓN AQUÍ
                prediccion = rf_model.predict([vector_ml])[0]
                confianza = np.max(rf_model.predict_proba([vector_ml])[0]) * 100
                colores = {"flauta": "#2ECC71", "guitarra": "#E74C3C", "teclado": "#3498DB"}

                # Mostrar resultado
                for _ in range(30):
                    senal_viva = leer_sensor(inst_entrada, t)
                    _, huella_viva, f0, rms, thd = extraer_features(senal_viva)
                    paquete = {
                        "estado_sistema": "INFERENCIA COMPLETADA", "instrumento": prediccion.upper(), "color": colores[prediccion],
                        "senal_tiempo": senal_viva.tolist()[:100], "espectro_frecuencias": huella_viva.tolist(),
                        "metricas_dsp": {"f0": round(float(f0),1), "rms": round(float(rms),3), "thd": round(float(thd),2), "confianza": round(float(confianza),1)},
                        "muestras_memoria": len(X_train), "ia_lista": is_trained
                    }
                    await websocket.send(json.dumps(paquete))
                    t += 0.015
                    await asyncio.sleep(0.1)
                estado_sistema = "ESPERANDO COMANDOS..."

        except websockets.exceptions.ConnectionClosed: break

async def gestor_conexiones(websocket):
    print("¡Front-end conectado! Pipeline ML activo.")
    tarea_recibir = asyncio.create_task(recibir_comandos(websocket))
    tarea_enviar = asyncio.create_task(enviar_datos(websocket))
    await asyncio.wait([tarea_recibir, tarea_enviar], return_when=asyncio.FIRST_COMPLETED)

async def main():
    async with websockets.serve(gestor_conexiones, "localhost", 8080): await asyncio.Future()

if __name__ == "__main__": asyncio.run(main())