import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import xml.etree.ElementTree as ET
import re
from geopy.distance import geodesic

def limpiar_kml(kml_content):
    kml_content = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', '', kml_content)
    kml_content = re.sub(r'<(/?)(\w+):', r'<\1', kml_content)
    kml_content = re.sub(r'&(?!amp;)', '&amp;', kml_content)
    kml_content = re.sub(r'(</kml>).*', r'</kml>', kml_content, flags=re.DOTALL)
    return kml_content

def extraer_coordenadas(path):
    contenido = ''
    if path.endswith(".kmz"):
        with zipfile.ZipFile(path, 'r') as z:
            kml_file = [f for f in z.namelist() if f.endswith('.kml')][0]
            with z.open(kml_file) as f:
                contenido = f.read().decode("utf-8")
    elif path.endswith(".kml"):
        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read()

    limpio = limpiar_kml(contenido)
    root = ET.fromstring(limpio)

    puntos = []
    for placemark in root.findall(".//Placemark"):
        name_elem = placemark.find("name")
        coord_elem = placemark.find(".//coordinates")
        if name_elem is not None and coord_elem is not None:
            nombre = name_elem.text.strip()
            coords = coord_elem.text.strip().split(',')
            if len(coords) >= 2:
                lon = float(coords[0])
                lat = float(coords[1])
                puntos.append((nombre, lat, lon))
    return puntos

def ordenar_por_proximidad(coords):
    if not coords:
        return []
    visitados = [coords[0]]
    no_visitados = coords[1:]
    while no_visitados:
        ultimo = visitados[-1]
        siguiente = min(no_visitados, key=lambda x: geodesic((ultimo[1], ultimo[2]), (x[1], x[2])).meters)
        visitados.append(siguiente)
        no_visitados.remove(siguiente)
    return visitados

def seleccionar_archivo():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos KMZ o KML", "*.kmz *.kml")])
    if not ruta:
        return
    try:
        puntos = extraer_coordenadas(ruta)
        ordenados = ordenar_por_proximidad(puntos)
        txt_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt")])
        if txt_path:
            with open(txt_path, "w", encoding="utf-8") as f:
                for nombre, lat, lon in ordenados:
                    f.write(f"{nombre}, {lat}, {lon}\n")
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{txt_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo procesar:\n{str(e)}")

# Interfaz Gráfica
ventana = tk.Tk()
ventana.title("Extractor de Coordenadas KML/KMZ")
ventana.geometry("400x200")

etiqueta = tk.Label(ventana, text="Selecciona un archivo KMZ o KML", font=("Calibri", 14))
etiqueta.pack(pady=20)

boton = tk.Button(ventana, text="Seleccionar archivo", command=seleccionar_archivo, font=("Calibri", 12))
boton.pack()

ventana.mainloop()
