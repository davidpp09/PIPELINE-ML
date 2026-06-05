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
- Pulsa **🎤 ESCUCHAR (5s)** para grabar 5 segundos y obtener el resultado.

---

## 🧠 Grabar muestras para mejorar la detección

Puedes "enseñarle" instrumentos al sistema grabando muestras tuyas:

1. Con el backend corriendo y la página abierta, ve a la sección
   **"🧠 Entrenar (grabar muestra)"** del panel izquierdo.
2. Elige el instrumento en el desplegable (flauta, guitarra, teclado, violín, tambor).
   El número entre paréntesis es cuántas muestras tienes ya de cada uno.
3. Pulsa **● GRABAR** y toca ese instrumento durante los 5 segundos.
4. La muestra se guarda en tu carpeta `muestras/` y **tu modelo se reentrena solo**.
   Cuantas más grabes (varias por instrumento), mejor detecta **en tu PC**.

> 💡 Las muestras que grabas quedan **en tu PC**. Para que cuenten en el modelo de
> todos, hay que enviárselas a David (ver abajo).

### 📤 Enviar tus muestras nuevas a David

Cuando hayas grabado varias muestras y quieras compartirlas:

1. En la carpeta `backend`, corre:
   ```powershell
   python enviar_muestras.py
   ```
2. Se crea un archivo **`mis_muestras.zip`** que contiene **solo las muestras que
   grabaste tú** (no las 370 originales).
3. Envíale ese `mis_muestras.zip` a David. Él las junta, reentrena el modelo y
   reparte una versión mejorada.

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
