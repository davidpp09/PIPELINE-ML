# 🎵 Cómo correr el backend (detector de instrumentos)

Esta carpeta contiene todo lo necesario para correr el **backend** en tu PC y que el
detector funcione con la página web (frontend) que ya está en línea.

> 📌 **Importante:** el backend lo corre **quien tenga la ESP32 conectada** a su PC,
> porque la nube no puede leer un dispositivo físico conectado localmente.

---

## 📦 Qué hay aquí

- `backend_para_compartir.zip` — el backend completo (código + las 370 muestras para
  entrenar el modelo).

---

## ✅ Requisitos

1. **Python 3.10 o superior** → https://www.python.org/downloads/
   (Al instalar en Windows, marca la casilla **"Add Python to PATH"**.)
2. La **ESP32** conectada por USB (o emparejada por Bluetooth).
3. Navegador **Chrome** o **Edge** (Firefox bloquea la conexión local, no lo uses).

---

## 🚀 Pasos

### 1. Descomprimir
Descomprime `backend_para_compartir.zip`. Te quedará una carpeta llamada `backend`.

### 2. Abrir una terminal dentro de esa carpeta
- Entra a la carpeta `backend`.
- Click derecho dentro → **"Abrir en Terminal"** (o abre PowerShell y navega ahí con `cd`).

### 3. Instalar las dependencias (solo la primera vez)
```powershell
pip install -r requirements.txt
```

### 4. Arrancar el backend
```powershell
python main.py
```

Si todo va bien verás algo como:
```
✅ Conectado a ESP32 ...
🚀 Servidor WebSocket iniciado en ws://0.0.0.0:8081
```

> Si no detecta la ESP32 automáticamente, puedes forzar el puerto COM. Por ejemplo,
> si tu ESP32 está en el COM10:
> ```powershell
> $env:ESP32_PORT = "COM10"; python main.py
> ```
> (Para ver en qué COM está: Administrador de dispositivos → Puertos (COM y LPT).)

### 5. Abrir la página web
- Abre la URL del frontend (la de Railway) en **Chrome o Edge**.
- La página se conecta sola a tu backend local.
- Mantén presionado **"detectar"** para grabar 5 segundos y obtener el resultado.

---

## 🛠️ Si algo falla

| Problema | Solución |
|---|---|
| `python no se reconoce...` | Reinstala Python marcando "Add Python to PATH". |
| No conecta la página | Usa **Chrome/Edge**, no Firefox. Verifica que el backend siga corriendo. |
| No detecta la ESP32 | Revisa el cable USB / emparejamiento Bluetooth, o fuerza el puerto con `ESP32_PORT`. |
| El detector no identifica nada | Asegúrate de haber descomprimido la carpeta **completa** (debe incluir la carpeta `muestras` con muchos archivos). |

---

¡Listo! Con el backend corriendo y la página abierta en Chrome/Edge, el sistema
detecta flauta, guitarra, teclado, violín y tambor en tiempo real.
