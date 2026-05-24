import serial
import numpy as np
import time
import os
import glob
import tkinter as tk
from scipy import signal as sp_signal
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- CONFIGURACIÓN ---
PUERTO = 'COM11' 
BAUDIOS = 115200
CARPETA_DATA = 'muestras_ia'
OFFSET_12BITS = 2048  # Centro para resolución de 4096 niveles

def entrenar_modelo():
    X, y = [], []
    archivos = glob.glob(os.path.join(CARPETA_DATA, "*.npy"))
    
    if len(archivos) < 6:
        print(f"⚠️ IA: Insuficientes muestras ({len(archivos)}). Usa el nuevo recolector 12-bits.")
        return None

    for archivo in archivos:
        try:
            huella = np.load(archivo)
            # Normalización robusta (Z-Score simplificado)
            huella_norm = (huella - np.min(huella)) / (np.max(huella) - np.min(huella) + 1e-10)
            X.append(huella_norm)
            etiqueta = os.path.basename(archivo).split('_')[0].lower()
            y.append(etiqueta)
        except Exception as e:
            print(f"Error cargando {archivo}: {e}")
    
    if len(set(y)) < 2:
        return None
        
    clf = RandomForestClassifier(n_estimators=300, random_state=42)
    clf.fit(X, y)
    print(f"✅ IA 12-BITS Entrenada para: {set(y)}")
    return clf

try:
    arduino = serial.Serial(PUERTO, BAUDIOS, timeout=0.1)
    time.sleep(2)
    arduino.reset_input_buffer()
except:
    arduino = None
    print(f"❌ Error en puerto {PUERTO}")

modelo_ia = entrenar_modelo()
grabando = False
muestras_acumuladas = []

# --- PREPARACIÓN DE VENTANAS ---
plt.style.use('dark_background')

# Ventana Monitor: Ahora con rango 0-4095
fig_mon, ax_mon = plt.subplots(figsize=(8, 3))
fig_mon.canvas.manager.set_window_title('Monitor ESP32 - 12 Bits')
y_data = np.full(400, OFFSET_12BITS)
line, = ax_mon.plot(y_data, color='#FF00FF') # Color magenta para distinguir 12 bits
ax_mon.set_ylim(0, 4095) 
ax_mon.set_title("MONITOR 12-BITS | MANTÉN 'R' PARA IDENTIFICAR")

fig_res, ax_res = plt.subplots(figsize=(6, 4))
fig_res.canvas.manager.set_window_title('Espectrograma Pro')

def procesar_deteccion():
    global muestras_acumuladas, grabando
    if not modelo_ia or len(muestras_acumuladas) < 512:
        grabando = False
        return

    try:
        sig = np.array(muestras_acumuladas[:2048])
        # MEJORA: Mayor resolución espectral para 12 bits
        f, t, Sxx = sp_signal.spectrogram(sig, fs=2500, nperseg=512)
        
        # FILTRO DE SILENCIO: Evita falsos positivos si no hay suficiente energía
        if np.mean(Sxx) < 0.05:
            if root.winfo_exists():
                lbl_resultado.config(text="AMBIENTE / SILENCIO", fg="white")
            return

        huella_actual = np.mean(Sxx, axis=1) 
        huella_norm = (huella_actual - np.min(huella_actual)) / (np.max(huella_actual) - np.min(huella_actual) + 1e-10)
        
        resultado_raw = modelo_ia.predict([huella_norm])[0].lower()
        
        colores = {
            "flauta": "#2ECC71", "guitarra": "#E74C3C", "teclado": "#3498DB",
            "violin": "#FFA500", "tambor": "#A52A2A"
        }
        color_final = colores.get(resultado_raw, "#FFFFFF")

        if root.winfo_exists():
            lbl_resultado.config(text=f"IDENTIFICADO: {resultado_raw.upper()}", fg=color_final)
        
        ax_res.clear()
        # Usamos escala logarítmica para resaltar armónicos de alta resolución
        ax_res.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
        ax_res.set_title(f"FIRMA ESPECTRAL: {resultado_raw.upper()}", color=color_final, fontweight='bold')
        fig_res.canvas.draw_idle() 

    except Exception as e:
        print(f"Error: {e}")
    finally:
        grabando = False
        muestras_acumuladas = []

def on_key(event):
    global grabando, muestras_acumuladas
    if event.key == 'r' or event.key == 'R':
        if event.name == 'key_press_event' and not grabando:
            grabando = True
            muestras_acumuladas = []
            if root.winfo_exists():
                lbl_resultado.config(text="ANALIZANDO...", fg="#FFD700")
        elif event.name == 'key_release_event':
            procesar_deteccion()

def update(frame):
    global y_data
    if not root.winfo_exists() or not plt.fignum_exists(fig_mon.number): 
        return line,

    if arduino and arduino.in_waiting > 0:
        try:
            # Lectura masiva para evitar lag en el monitor
            raw = arduino.read(arduino.in_waiting).decode('utf-8', errors='ignore').split('\n')
            for d in raw:
                d = d.strip()
                if d.isdigit():
                    val = float(d)
                    y_data = np.roll(y_data, -1); y_data[-1] = val
                    if grabando:
                        muestras_acumuladas.append(val - OFFSET_12BITS)
        except: pass
    line.set_ydata(y_data)
    return line,

# Interfaz
root = tk.Tk()
root.title("Status Detector 12-Bits")
root.geometry("350x120")

def cerrar_todo():
    try:
        ani.event_source.stop()
        plt.close('all')
        if root.winfo_exists(): root.destroy()
        if arduino: arduino.close()
    except: pass

root.protocol("WM_DELETE_WINDOW", cerrar_todo)
lbl_resultado = tk.Label(root, text="Monitor listo (12 bits)", font=("Arial", 12, "bold"), fg="gray")
lbl_resultado.pack(expand=True)

fig_mon.canvas.mpl_connect('key_press_event', on_key)
fig_mon.canvas.mpl_connect('key_release_event', on_key)

ani = FuncAnimation(fig_mon, update, interval=20, cache_frame_data=False)
plt.show()
