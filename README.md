# 🎵 Sistema de Detección Acústica de Instrumentos

Detecta qué instrumento está sonando (flauta, guitarra, teclado, violín, tambor)
usando una **ESP32 + sensor MAX**, procesamiento de señales (DSP) y un modelo de IA
(Random Forest). La interfaz web muestra el osciloscopio, el espectrograma y el
instrumento identificado en tiempo real.

---

## 🧩 Arquitectura

El proyecto tiene **dos partes**:

```
┌─────────────── PC del usuario ────────────────┐
│                                                 │
│   ESP32 + sensor MAX  ──(USB / Bluetooth)──►    │
│                                                 │
│   backend/main.py  (lee el sensor, corre la IA) │
│        │                                        │
│        ▼  ws://localhost:8081                   │
│   Navegador  ◄──────────────────────────────────┼──── Frontend (React) hosteado en Railway
│                                                 │
└──────────────────────────────────────────────────┘
```

- **Frontend (React):** la página visual. Se sube a la nube (Railway).
- **Backend (Python):** lee el sensor por puerto serial/Bluetooth y corre el modelo de IA.
  👉 **Debe correr en la PC de cada usuario**, porque la nube no puede acceder a un
  dispositivo físico (ESP32) conectado localmente.

---

## 🚀 Cómo usar la aplicación (para usuarios)

### Paso 1 — Correr el backend en tu PC

> 📁 El código del backend está en la carpeta **[`backend/`](./backend)**.

1. Instala [Python 3.10+](https://www.python.org/downloads/).
2. Conecta tu **ESP32** por USB (o emparéjala por Bluetooth).
3. Abre una terminal en la carpeta del proyecto e instala las dependencias:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. Arranca el backend:

   ```bash
   python backend/main.py
   ```

   El puerto COM se detecta **automáticamente**. Si quieres forzar uno en concreto,
   define la variable de entorno `ESP32_PORT` antes de arrancar:

   ```powershell
   # Windows (PowerShell)
   $env:ESP32_PORT = "COM10"; python backend/main.py
   ```

   Si todo va bien verás:

   ```
   ✅ Conectado a ESP32 ...
   🚀 Servidor WebSocket iniciado en ws://0.0.0.0:8081
   ```

### Paso 2 — Abrir la interfaz

- Abre la URL de Railway (ej. `https://tu-proyecto.up.railway.app`), **o**
- Córrela localmente (ver más abajo).

La página se conecta sola a tu backend local en `ws://localhost:8081`.
Mantén presionado **detectar** para grabar 5 segundos y obtener el resultado.

> ⚠️ **Firefox** a veces bloquea `ws://localhost` desde una página HTTPS. Si no conecta,
> usa **Chrome/Edge** o abre el frontend localmente (`npm run dev`).

---

## 🖥️ Correr el frontend localmente (desarrollo)

Requiere [Node.js 18+](https://nodejs.org/).

```bash
npm install
npm run dev
```

Abre la URL que muestra la terminal (por defecto `http://localhost:5173`).

---

## ☁️ Desplegar el frontend en Railway

1. Sube este repo a GitHub.
2. En [Railway](https://railway.app): **New Project → Deploy from GitHub repo**.
3. En *Settings* confirma los comandos:
   - **Build:** `npm install && npm run build`
   - **Start:** `npm start`
4. Deploy. Railway te dará la URL pública.

> El backend **no** se sube a Railway: cada usuario lo corre en su propia PC (ver arriba).

### Variable de entorno opcional del frontend

| Variable | Default | Descripción |
|---|---|---|
| `VITE_WS_URL` | `ws://localhost:8081` | URL del backend WebSocket. Déjala así para que cada usuario use su backend local. |

Ver [`.env.example`](./.env.example).

---

## 📂 Estructura del proyecto

```
.
├── backend/            # Backend Python (lo corre el usuario en su PC)
│   ├── main.py         # Servidor WebSocket + lectura del sensor + IA
│   ├── requirements.txt
│   └── muestras/       # Muestras .npy para entrenar el modelo
├── src/                # Frontend React
│   ├── App.jsx
│   └── components/     # Osciloscopio, Espectrograma, PanelInstrumento
├── .env.example
└── package.json
```

---

## 🛠️ Tecnologías

- **Frontend:** React 19, Vite, Tailwind CSS, Recharts
- **Backend:** Python, websockets, NumPy, SciPy, scikit-learn (Random Forest), PySerial
- **Hardware:** ESP32 + sensor MAX
