"""
Editor de Trama - LoomETec
Versión Kivy para Windows, iOS y Android
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import json
from PIL import Image
from kivy.utils import platform

class PixelCanvas(Widget):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.columnas = 24
        self.filas = 24
        self.size_pixel = 20
        self.matriz_datos = [["#FFFFFF" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.rectangles = []
        
        self.bind(pos=self.actualizar_canvas, size=self.actualizar_canvas)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pintar(touch)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.pintar(touch)
            return True
        return super().on_touch_move(touch)
    
    def pintar(self, touch):
        x_rel = touch.x - self.x
        y_rel = self.height - (touch.y - self.y)
        
        c = int(x_rel // self.size_pixel)
        f = int(y_rel // self.size_pixel)
        
        if 0 <= c < self.columnas and 0 <= f < self.filas:
            color = self.app_ref.color_seleccionado
            self.matriz_datos[f][c] = color
            self.actualizar_celda(f, c)
    
    def actualizar_celda(self, f, c):
        if f < len(self.rectangles) and c < len(self.rectangles[f]):
            rect_data = self.rectangles[f][c]
            color_hex = self.matriz_datos[f][c].lstrip('#')
            r = int(color_hex[0:2], 16) / 255.0
            g = int(color_hex[2:4], 16) / 255.0
            b = int(color_hex[4:6], 16) / 255.0
            rect_data['color'].rgba = (r, g, b, 1)
    
    def actualizar_canvas(self, *args):
        self.canvas.clear()
        self.rectangles = []
        
        self.size = (self.columnas * self.size_pixel, self.filas * self.size_pixel)
        
        with self.canvas:
            for f in range(self.filas):
                fila_rects = []
                for c in range(self.columnas):
                    color_hex = self.matriz_datos[f][c].lstrip('#')
                    r = int(color_hex[0:2], 16) / 255.0
                    g = int(color_hex[2:4], 16) / 255.0
                    b = int(color_hex[4:6], 16) / 255.0
                    
                    color_obj = Color(r, g, b, 1)
                    
                    x1 = self.x + c * self.size_pixel
                    y1 = self.y + self.height - (f + 1) * self.size_pixel
                    
                    rect = Rectangle(pos=(x1, y1), size=(self.size_pixel, self.size_pixel))
                    
                    fila_rects.append({'color': color_obj, 'rect': rect})
                    
                    Color(0.93, 0.93, 0.93, 1)
                    Rectangle(pos=(x1, y1), size=(self.size_pixel, 1))
                    Rectangle(pos=(x1, y1), size=(1, self.size_pixel))
                
                self.rectangles.append(fila_rects)
    
    def limpiar(self):
        self.matriz_datos = [["#FFFFFF" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.actualizar_canvas()
    
    def ajustar_tamano(self, cambio):
        nuevo_largo = self.filas + cambio
        if nuevo_largo < 24:
            return False
        
        if cambio > 0:
            for _ in range(cambio):
                self.matriz_datos.append(["#FFFFFF" for _ in range(self.columnas)])
        else:
            self.matriz_datos = self.matriz_datos[:cambio]
        
        self.filas = nuevo_largo
        self.actualizar_canvas()
        return True


class EditorTramaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_seleccionado = "#000000"
    
    def build(self):
        self.title = "Editor de Trama - LoomETec"
        
        layout_principal = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        
        # Panel lateral
        panel = BoxLayout(orientation='vertical', size_hint=(0.25, 1), spacing=5)
        
        # Indicador de color
        panel.add_widget(Label(text='Color Activo', size_hint_y=0.1, bold=True))
        self.color_indicator = Widget(size_hint_y=0.08)
        with self.color_indicator.canvas:
            self.indicator_color = Color(0, 0, 0, 1)
            self.indicator_rect = Rectangle(pos=self.color_indicator.pos, size=self.color_indicator.size)
        self.color_indicator.bind(pos=self.actualizar_indicator, size=self.actualizar_indicator)
        panel.add_widget(self.color_indicator)
        
        # Botones de color
        btn_negro = Button(text='Negro', size_hint_y=0.1, background_color=(0.2, 0.2, 0.2, 1))
        btn_negro.bind(on_press=lambda x: self.set_color("#000000"))
        panel.add_widget(btn_negro)
        
        btn_blanco = Button(text='Blanco', size_hint_y=0.1, background_color=(1, 1, 1, 1), color=(0, 0, 0, 1))
        btn_blanco.bind(on_press=lambda x: self.set_color("#FFFFFF"))
        panel.add_widget(btn_blanco)
        
        # Ajustar tamaño
        panel.add_widget(Label(text='Ajustar Largo', size_hint_y=0.1, bold=True))
        
        btn_agrandar = Button(text='Agrandar', size_hint_y=0.1)
        btn_agrandar.bind(on_press=lambda x: self.canvas_widget.ajustar_tamano(4))
        panel.add_widget(btn_agrandar)
        
        btn_achicar = Button(text='Achicar', size_hint_y=0.1)
        btn_achicar.bind(on_press=lambda x: self.canvas_widget.ajustar_tamano(-4))
        panel.add_widget(btn_achicar)
        
        # Exportar
        panel.add_widget(Label(text='Exportar', size_hint_y=0.1, bold=True))
        
        btn_limpiar = Button(text='Limpiar', size_hint_y=0.1)
        btn_limpiar.bind(on_press=lambda x: self.canvas_widget.limpiar())
        panel.add_widget(btn_limpiar)
        
        btn_png = Button(text='Guardar PNG', size_hint_y=0.1, background_color=(0.78, 0.9, 0.79, 1))
        btn_png.bind(on_press=self.guardar_png)
        panel.add_widget(btn_png)
        
        btn_json = Button(text='Guardar JSON', size_hint_y=0.1, background_color=(0.88, 0.96, 0.99, 1))
        btn_json.bind(on_press=self.guardar_json)
        panel.add_widget(btn_json)
        
        panel.add_widget(Widget(size_hint_y=0.2))
        
        # Canvas con scroll
        scroll = ScrollView(size_hint=(0.75, 1), do_scroll_x=True, do_scroll_y=True)
        self.canvas_widget = PixelCanvas(app_ref=self)
        scroll.add_widget(self.canvas_widget)
        
        layout_principal.add_widget(panel)
        layout_principal.add_widget(scroll)
        
        return layout_principal
    
    def actualizar_indicator(self, *args):
        self.indicator_rect.pos = self.color_indicator.pos
        self.indicator_rect.size = self.color_indicator.size
    
    def set_color(self, hex_color):
        self.color_seleccionado = hex_color
        color_hex = hex_color.lstrip('#')
        r = int(color_hex[0:2], 16) / 255.0
        g = int(color_hex[2:4], 16) / 255.0
        b = int(color_hex[4:6], 16) / 255.0
        self.indicator_color.rgba = (r, g, b, 1)
    
    def generar_matriz_sincronizada(self):
        matriz_datos = self.canvas_widget.matriz_datos
        filas = self.canvas_widget.filas
        columnas = self.canvas_widget.columnas
        
        num_franjas_f = (filas // 4) + 1
        num_franjas_c = (columnas // 4) + 1
        total_f = filas + num_franjas_f
        total_c = columnas + num_franjas_c
        
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
                    if f_dibujo < filas and c_dibujo < columnas:
                        matriz[f][c] = matriz_datos[f_dibujo][c_dibujo]
                    c_dibujo += 1
            if not es_fila_franja:
                f_dibujo += 1
        
        return matriz, total_f, total_c
    
    def guardar_png(self, instance):
        try:
            # Determinar ruta según plataforma
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
                archivo = '/sdcard/Download/trama_export.png'
            elif platform == 'ios':
                import os
                archivo = os.path.join(os.path.expanduser('~'), 'Documents', 'trama_export.png')
            else:
                archivo = 'trama_export.png'
            
            m, tf, tc = self.generar_matriz_sincronizada()
            img = Image.new("RGB", (tc, tf))
            
            for f in range(tf):
                for c in range(tc):
                    color_hex = m[f][c].lstrip('#')
                    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    img.putpixel((c, f), rgb)
            
            img.save(archivo)
            self.mostrar_popup("PNG", f"Imagen guardada en:\n{archivo}")
        except Exception as e:
            self.mostrar_popup("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_json(self, instance):
        try:
            if platform == 'android':
                archivo = '/sdcard/Download/trama_export.json'
            elif platform == 'ios':
                import os
                archivo = os.path.join(os.path.expanduser('~'), 'Documents', 'trama_export.json')
            else:
                archivo = 'trama_export.json'
            
            m, tf, tc = self.generar_matriz_sincronizada()
            datos_binarios = [[1 if p == "#000000" else 0 for p in fila] for fila in m]
            
            with open(archivo, 'w') as f:
                json.dump({"dimensiones": [tc, tf], "datos": datos_binarios}, f)
            
            self.mostrar_popup("JSON", f"Datos guardados en:\n{archivo}")
        except Exception as e:
            self.mostrar_popup("Error", f"No se pudo guardar: {str(e)}")
    
    def mostrar_popup(self, titulo, mensaje):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=mensaje))
        btn_cerrar = Button(text='Cerrar', size_hint_y=0.3)
        content.add_widget(btn_cerrar)
        
        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.4))
        btn_cerrar.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    EditorTramaApp().run()