import asyncio
import websockets
import json
import numpy as np
import random
from scipy import signal as sp_signal

INSTRUMENTOS = ["flauta", "guitarra", "teclado"]

def generar_senal(tipo, t):
    t_axis = np.linspace(t, t + 0.1, 256)
    if tipo == "flauta":
        senal = np.sin(2 * np.pi * 880 * t_axis)
    elif tipo == "guitarra":
        senal = np.sin(2 * np.pi * 440 * t_axis) + 0.5 * np.sin(2 * np.pi * 880 * t_axis)
    else:
        senal = sp_signal.square(2 * np.pi * 220 * t_axis)
    return senal + np.random.normal(0, 0.05, 256)

async def enviar_datos(websocket):
    print("¡Cliente React conectado! Iniciando ciclo de detección...")
    t = 0
    try:
        while True:
            # --- FASE 1: ESCUCHANDO ---
            for _ in range(50): 
                ruido = np.random.normal(0, 0.2, 100)
                datos = {
                    "instrumento": "ESCUCHANDO...",
                    "color": "#F1C40F", 
                    "senal_tiempo": ruido.tolist(), 
                    "espectro_frecuencias": np.zeros(64).tolist(),
                    "metricas_dsp": { "f0": 0, "rms": round(float(np.sqrt(np.mean(ruido**2))), 3), "thd": 0, "confianza": 0 }
                }
                await websocket.send(json.dumps(datos))
                await asyncio.sleep(0.1)

            # --- FASE 2: DETECCIÓN Y RESULTADO ---
            inst = random.choice(INSTRUMENTOS)
            confianza_ia = random.uniform(89.5, 98.9) # Simulamos el predict_proba del Random Forest
            
            for _ in range(40): 
                senal = generar_senal(inst, t)
                f, t_s, Sxx = sp_signal.spectrogram(senal, fs=2500, nperseg=64)
                huella = np.mean(Sxx, axis=1)
                
                # --- CÁLCULOS DSP REALES ---
                frecuencia_pico = f[np.argmax(huella)] # Frecuencia con más energía (f0)
                rms = np.sqrt(np.mean(senal**2)) # Potencia de la señal
                energia_total = np.sum(huella)
                energia_fundamental = np.max(huella)
                thd = abs((energia_total - energia_fundamental) / (energia_fundamental + 1e-10)) # Distorsión armónica
                
                huella_norm = huella / (np.max(huella) + 1e-10)

                datos = {
                    "instrumento": inst.upper(),
                    "color": {"flauta": "#2ECC71", "guitarra": "#E74C3C", "teclado": "#3498DB"}[inst],
                    "senal_tiempo": senal.tolist()[:100],
                    "espectro_frecuencias": huella_norm.tolist(),
                    "metricas_dsp": {
                        "f0": round(float(frecuencia_pico), 1),
                        "rms": round(float(rms), 3),
                        "thd": round(float(thd), 2),
                        "confianza": round(float(confianza_ia), 1)
                    }
                }
                await websocket.send(json.dumps(datos))
                t += 0.015 
                await asyncio.sleep(0.1)

    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado")

async def main():
    async with websockets.serve(enviar_datos, "localhost", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())