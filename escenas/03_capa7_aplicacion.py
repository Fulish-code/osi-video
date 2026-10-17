import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

AZUL = COLOR_CAPA[7]
X_CENTRO = (X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2


class EscenaAplicacion(Scene):
    def construct(self):
        pila = PilaCapas(activa=None)
        self.add(pila)
        panel = panel_capa(
            7,
            agrega="un encabezado del protocolo de la aplicación",
            para_que="que los dos programas se entiendan por la red",
        )
        self.play(*pila.activar(7), FadeIn(panel), run_time=0.8)

        ventana = RoundedRectangle(width=7.4, height=2.0, corner_radius=0.1,
                                   stroke_color=TEXTO_TENUE, stroke_width=1.5)
        ventana.move_to([X_CENTRO, 0.75, 0])
        barra = Line(ventana.get_corner(UL) + DOWN * 0.45, ventana.get_corner(UR) + DOWN * 0.45,
                     color=TEXTO_TENUE, stroke_width=1)
        nombre_ventana = texto("Chat · PC A", tam=16, color=TEXTO_MEDIO)
        nombre_ventana.move_to(ventana.get_corner(UL) + DOWN * 0.225 + RIGHT * 0.2,
                               aligned_edge=LEFT)
        contenido = texto(MENSAJE, tam=22)
        burbuja = SurroundingRectangle(contenido, buff=0.18, corner_radius=0.12,
                                       color=AZUL, stroke_width=1.5)
        mensaje = VGroup(burbuja, contenido)
        mensaje.move_to(ventana.get_center() + DOWN * 0.22)
        chat = VGroup(ventana, barra, nombre_ventana, mensaje)

        paso = texto_paso(
            "El mensaje en el programa de chat",
            "En PC A se escribe el mensaje en una aplicación de chat.",
        )
        self.play(FadeIn(VGroup(ventana, barra, nombre_ventana)), FadeIn(paso), run_time=0.6)
        self.play(FadeIn(mensaje), run_time=0.6)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "La capa 7 no es el programa",
            "Es el protocolo que el programa usa para hablar por la red.\n"
            "Aquí, el del chat. En otros casos, HTTP, SMTP o DNS.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        tipo = campo(f"tipo: {CHAT_TIPO}", 1.8, AZUL, tam=18, alto=0.6)
        largo = campo(f"largo: {CHAT_LARGO}", 1.8, AZUL, tam=18, alto=0.6)
        datos = Rectangle(width=5.3, height=0.6, stroke_color=BORDE_DATOS,
                          stroke_width=1, fill_color=CAJA_DATOS, fill_opacity=1)
        texto_datos = texto(MENSAJE, tam=17).move_to(datos)
        empaquetado = VGroup(tipo, largo, VGroup(datos, texto_datos)).arrange(RIGHT, buff=0)
        empaquetado.move_to([X_CENTRO, -0.95, 0])
        llave = Brace(VGroup(tipo, largo), DOWN, buff=0.1, color=AZUL)
        rotulo_llave = texto("encabezado del chat", tam=15, color=AZUL)
        rotulo_llave.next_to(llave, DOWN, buff=0.06)

        nuevo = texto_paso(
            "El mensaje según el protocolo",
            "El protocolo del chat le pone adelante un encabezado propio:\n"
            "qué tipo de mensaje es y cuántos bytes mide el texto.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.play(FadeIn(datos), FadeIn(tipo, shift=RIGHT * 0.2),
                  FadeIn(largo, shift=RIGHT * 0.2), run_time=0.6)
        self.play(TransformFromCopy(contenido, texto_datos), run_time=0.8)
        self.play(GrowFromCenter(llave), FadeIn(rotulo_llave), run_time=0.5)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Simplificación",
            "Este protocolo es inventado para el ejemplo. Desde aquí se cuentan\n"
            "solo los 34 bytes del texto, para que los números sean simples.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
