import asyncio
import websockets
import json
import numpy as np
import time
import random

# ==========================================
# 🛠️ ZONA DE TRABAJO PARA TU AMIGO (BACKEND)
# ==========================================
def obtener_datos_reales():
    """
    TODO: Aquí es donde tu amigo debe conectar el Arduino y hacer la magia DSP.
    1. Leer puerto serial (pyserial)
    2. Aplicar Filtro FIR (scipy.signal.lfilter)
    3. Calcular FFT (numpy.fft.fft)
    """
    # --- INICIO DE SIMULACIÓN (Borrar cuando haya Arduino) ---
    t = time.time()
    
    # Simulamos una onda (ej. una mezcla de dos frecuencias para que se vea cool)
    x = np.linspace(0, 2 * np.pi, 200) # 200 puntos para la gráfica
    onda = np.sin(x * 2 + t * 5) * 0.5 + np.sin(x * 10 + t * 10) * 0.2
    
    # Añadimos un poco de ruido blanco
    ruido = np.random.normal(0, 0.05, 200)
    onda_final = onda + ruido

    # Simulamos que detecta un instrumento aleatorio
    instrumentos = ["Flauta", "Guitarra", "Piano", "Silencio..."]
    instrumento_actual = random.choice(instrumentos)
    
    # Frecuencia simulada
    frecuencia = round(random.uniform(200.0, 800.0), 1) if instrumento_actual != "Silencio..." else 0.0
    # --- FIN DE SIMULACIÓN ---

    # Este es el diccionario que cumple con el "Contrato" que acordaste con el Frontend
    return {
        "estado": "EN LINEA",
        "instrumento": instrumento_actual,
        "frecuencia_hz": frecuencia,
        "senal_tiempo": onda_final.tolist(), # Convertimos el arreglo de numpy a lista normal
        "fft_frecuencias": [] # Aquí pondrá el arreglo de la FFT más adelante
    }

# ==========================================
# 🌐 SERVIDOR WEBSOCKET (NO TOCAR MUCHO)
# ==========================================
async def enviar_datos(websocket):
    print("🟢 ¡Frontend conectado a Python!")
    try:
        while True:
            # 1. Obtenemos los datos procesados (reales o simulados)
            paquete_datos = obtener_datos_reales()
            
            # 2. Convertimos el diccionario a un texto JSON
            mensaje_json = json.dumps(paquete_datos)
            
            # 3. Lo disparamos por el túnel hacia React
            await websocket.send(mensaje_json)
            
            # 4. Esperamos un poquito para no saturar la computadora (ej. 30 FPS = ~0.033 seg)
            await asyncio.sleep(0.05) 
            
    except websockets.exceptions.ConnectionClosed:
        print("🔴 Frontend desconectado.")

async def main():
    # Levantamos el servidor en el puerto 8080 local
    async with websockets.serve(enviar_datos, "localhost", 8080):
        print("🚀 Servidor DSP corriendo en ws://localhost:8080")
        print("Esperando a que React se conecte...")
        await asyncio.Future()  # Mantiene el servidor corriendo infinitamente

if __name__ == "__main__":
    asyncio.run(main())
