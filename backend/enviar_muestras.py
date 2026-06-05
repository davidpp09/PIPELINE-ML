"""
Empaqueta SOLO las muestras NUEVAS que grabaste en tu PC, para enviárselas
a quien junta el modelo (David).

Cómo funciona:
- El backend trae un archivo `muestras_base.txt` con la lista de muestras
  originales (las 370 que venían en el zip).
- Este script busca en `muestras/` los archivos .npy que NO están en esa lista
  (es decir, los que grabaste tú con el botón "GRABAR") y los mete en
  `mis_muestras.zip`.

Uso (desde la carpeta backend):
    python enviar_muestras.py

Luego envía el archivo `mis_muestras.zip` que se genera.
"""
import os
import sys
import glob
import zipfile

# La consola de Windows usa cp1252 por defecto y no puede imprimir emojis.
# Forzamos UTF-8 en la salida para que los mensajes no rompan el script.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CARPETA = os.path.dirname(os.path.abspath(__file__))
CARPETA_MUESTRAS = os.path.join(CARPETA, "muestras")
ARCHIVO_BASE = os.path.join(CARPETA, "muestras_base.txt")
SALIDA = os.path.join(CARPETA, "mis_muestras.zip")


def cargar_base():
    """Lee la lista de muestras originales (las que NO hay que reenviar)."""
    if not os.path.exists(ARCHIVO_BASE):
        print("⚠️ No encontré muestras_base.txt; se enviarán TODAS las muestras.")
        return set()
    with open(ARCHIVO_BASE, "r", encoding="utf-8") as f:
        return {linea.strip() for linea in f if linea.strip()}


def main():
    base = cargar_base()
    todas = glob.glob(os.path.join(CARPETA_MUESTRAS, "*.npy"))
    nuevas = [f for f in todas if os.path.basename(f) not in base]

    if not nuevas:
        print("ℹ️ No hay muestras nuevas que enviar. Graba algún instrumento")
        print("   con el botón '● GRABAR' de la página y vuelve a correr este script.")
        return

    # Resumen por instrumento
    conteo = {}
    for f in nuevas:
        etiqueta = os.path.basename(f).split("_")[0].lower()
        conteo[etiqueta] = conteo.get(etiqueta, 0) + 1

    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        for f in nuevas:
            z.write(f, arcname=os.path.basename(f))

    print(f"✅ Listo: {len(nuevas)} muestras nuevas empaquetadas en:")
    print(f"   {SALIDA}")
    print(f"   Detalle: {conteo}")
    print("\n👉 Envía el archivo 'mis_muestras.zip' a David para que las junte.")


if __name__ == "__main__":
    main()
