import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import colorsys

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

# Qué tan parecido debe ser el color al morado
# Valores más altos = detecta más tonos morados
TOLERANCIA = 0.12

# Saturación mínima para considerar un color morado
SATURACION_MINIMA = 0.25

# Luminosidad mínima y máxima
LUMINOSIDAD_MINIMA = 0.10
LUMINOSIDAD_MAXIMA = 0.95

# --------------------------------------------------
# DETECTAR SI UN COLOR ES MORADO
# --------------------------------------------------

def es_morado(r, g, b):
    # Convertir RGB a HSV
    h, s, v = colorsys.rgb_to_hsv(
        r / 255,
        g / 255,
        b / 255
    )

    # El morado suele encontrarse aproximadamente
    # entre 260° y 310° de tono.
    tono = h * 360

    return (
        (260 <= tono <= 310)
        and s >= SATURACION_MINIMA
        and LUMINOSIDAD_MINIMA <= v <= LUMINOSIDAD_MAXIMA
    )


# --------------------------------------------------
# PROCESAR UNA IMAGEN
# --------------------------------------------------

def quitar_morado(ruta_entrada, ruta_salida):
    imagen = Image.open(ruta_entrada).convert("RGBA")

    pixeles = imagen.load()

    for y in range(imagen.height):
        for x in range(imagen.width):
            r, g, b, a = pixeles[x, y]

            if es_morado(r, g, b):
                # Convertir el morado en transparente
                pixeles[x, y] = (r, g, b, 0)

    imagen.save(ruta_salida)


# --------------------------------------------------
# SELECCIONAR CARPETA Y PROCESAR IMÁGENES
# --------------------------------------------------

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory(
        title="Selecciona la carpeta de imágenes"
    )

    if not carpeta:
        return

    carpeta_salida = os.path.join(carpeta, "sin_morado")
    os.makedirs(carpeta_salida, exist_ok=True)

    extensiones = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp"
    )

    procesadas = 0
    errores = 0

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(extensiones):

            ruta_entrada = os.path.join(carpeta, archivo)
            nombre, extension = os.path.splitext(archivo)

            # Guardar todo como PNG para conservar transparencia
            ruta_salida = os.path.join(
                carpeta_salida,
                nombre + ".png"
            )

            try:
                quitar_morado(ruta_entrada, ruta_salida)
                procesadas += 1
            except Exception as e:
                print(f"Error en {archivo}: {e}")
                errores += 1

    messagebox.showinfo(
        "Proceso terminado",
        f"Imágenes procesadas: {procesadas}\n"
        f"Errores: {errores}\n\n"
        f"Guardadas en:\n{carpeta_salida}"
    )


# --------------------------------------------------
# VENTANA
# --------------------------------------------------

ventana = tk.Tk()
ventana.title("Quitar color morado")
ventana.geometry("350x180")
ventana.resizable(False, False)

etiqueta = tk.Label(
    ventana,
    text="Selecciona una carpeta para quitar\n"
         "el color morado de sus imágenes.",
    font=("Arial", 11),
    pady=20
)

etiqueta.pack()

boton = tk.Button(
    ventana,
    text="Seleccionar carpeta",
    command=seleccionar_carpeta,
    font=("Arial", 11),
    padx=15,
    pady=8
)

boton.pack()

ventana.mainloop()

