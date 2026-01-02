import tkinter as tk
from tkinter import filedialog, messagebox
import json
from PIL import Image

class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Trama - LoomETec")
        
        self.columnas = 24 
        self.filas = 24
        self.size_pixel = 18
        self.color_seleccionado = "#000000" 
        
        self.matriz_datos = [["#FFFFFF" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.matriz_ids = [[None for _ in range(self.columnas)] for _ in range(self.filas)]

        self.setup_ui()
        self.actualizar_interfaz()

    def setup_ui(self):
        self.panel = tk.Frame(self.root, padx=10, pady=10, width=160)
        self.panel.pack(side=tk.LEFT, fill=tk.Y)
        self.panel.pack_propagate(False)

        tk.Label(self.panel, text="Color Activo", font=("Arial", 10, "bold")).pack()
        self.indicator = tk.Frame(self.panel, height=20, bg=self.color_seleccionado)
        self.indicator.pack(fill=tk.X, pady=2)
        
        tk.Button(self.panel, text="Negro", bg="black", fg="black", command=lambda: self.set_color("#000000")).pack(fill=tk.X)
        tk.Button(self.panel, text="Blanco", bg="white", command=lambda: self.set_color("#FFFFFF")).pack(fill=tk.X)

        tk.Label(self.panel, text="Ajustar Largo", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(self.panel, text="Agrandar", command=lambda: self.ajustar_tamano(4)).pack(fill=tk.X)
        tk.Button(self.panel, text="Achicar", command=lambda: self.ajustar_tamano(-4)).pack(fill=tk.X)
        
        tk.Label(self.panel, text="Exportar", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(self.panel, text="Limpiar", command=self.limpiar_lienzo).pack(fill=tk.X)
        tk.Button(self.panel, text="Descargar PNG", command=self.guardar_png, bg="#c8e6c9").pack(fill=tk.X, pady=2)
        tk.Button(self.panel, text="Descargar JSON", command=self.guardar_json, bg="#e1f5fe").pack(fill=tk.X, pady=2)

        self.cv = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.cv.pack(side=tk.RIGHT)

        self.cv.bind("<Button-1>", lambda e: self.pintar(e, self.color_seleccionado))
        self.cv.bind("<B1-Motion>", lambda e: self.pintar(e, self.color_seleccionado))
        self.cv.bind("<Button-2>", lambda e: self.pintar(e, "#FFFFFF"))
        self.cv.bind("<Button-3>", lambda e: self.pintar(e, "#FFFFFF"))

    def set_color(self, hex_color):
        self.color_seleccionado = hex_color
        self.indicator.config(bg=hex_color)

    def actualizar_interfaz(self):
        self.cv.delete("all")
        self.cv.config(width=self.columnas * self.size_pixel, height=self.filas * self.size_pixel)
        self.matriz_ids = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        for f in range(self.filas):
            for c in range(self.columnas):
                x1, y1 = c * self.size_pixel, f * self.size_pixel
                x2, y2 = x1 + self.size_pixel, y1 + self.size_pixel
                rect_id = self.cv.create_rectangle(x1, y1, x2, y2, fill=self.matriz_datos[f][c], outline="#eeeeee")
                self.matriz_ids[f][c] = rect_id
        self.root.geometry("") 

    def ajustar_tamano(self, cambio):
        nuevo_largo = self.filas + cambio
        if nuevo_largo < 24:
            messagebox.showwarning("Límite", "El tamaño mínimo es 24.")
            return
        if cambio > 0:
            for _ in range(cambio):
                self.matriz_datos.append(["#FFFFFF" for _ in range(self.columnas)])
        else:
            if messagebox.askyesno("Confirmar", "¿Eliminar 4 filas?"):
                self.matriz_datos = self.matriz_datos[:cambio]
            else: return
        self.filas = nuevo_largo
        self.actualizar_interfaz()

    def pintar(self, event, color):
        c, f = event.x // self.size_pixel, event.y // self.size_pixel
        if 0 <= c < self.columnas and 0 <= f < self.filas:
            self.cv.itemconfig(self.matriz_ids[f][c], fill=color)
            self.matriz_datos[f][c] = color

    def generar_matriz_sincronizada(self):
        num_franjas_f = (self.filas // 4) + 1
        num_franjas_c = (self.columnas // 4) + 1
        total_f, total_c = self.filas + num_franjas_f, self.columnas + num_franjas_c
        
        matriz = [["#FFFFFF" for _ in range(total_c)] for _ in range(total_f)]
        
        f_dibujo = 0
        for f in range(total_f):
            es_fila_franja = (f % 5 == 0)
            c_dibujo = 0
            for c in range(total_c):
                es_col_franja = (c % 5 == 0)
                
                if es_fila_franja or es_col_franja:
                    matriz[f][c] = "#FFFFFF" if (f + c) % 2 == 0 else "#000000"
                else:
                    if f_dibujo < self.filas and c_dibujo < self.columnas:
                        matriz[f][c] = self.matriz_datos[f_dibujo][c_dibujo]
                    c_dibujo += 1
            if not es_fila_franja:
                f_dibujo += 1
        return matriz, total_f, total_c

    def guardar_png(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".png")
        if archivo:
            m, tf, tc = self.generar_matriz_sincronizada()
            img = Image.new("RGB", (tc, tf))
            for f in range(tf):
                for c in range(tc):
                    color_hex = m[f][c].lstrip('#')
                    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    img.putpixel((c, f), rgb)
            img.save(archivo)
            messagebox.showinfo("PNG", "Imagen exportada con franjas sincronizadas.")

    def guardar_json(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".json")
        if archivo:
            m, tf, tc = self.generar_matriz_sincronizada()
            datos_binarios = [[1 if p == "#000000" else 0 for p in fila] for fila in m]
            with open(archivo, 'w') as f:
                json.dump({"dimensiones": [tc, tf], "datos": datos_binarios}, f)
            messagebox.showinfo("JSON", "Datos exportados con éxito.")

    def limpiar_lienzo(self):
        self.matriz_datos = [["#FFFFFF" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.actualizar_interfaz()

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()