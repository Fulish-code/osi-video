import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

Y_EQUIPOS = 0.6
X_PC_A, X_SERVIDOR = -5.0, 5.0
X_IZQUIERDA = -6.6


def equipo(nombre, x):
    caja = RoundedRectangle(width=2.0, height=1.0, corner_radius=0.1,
                            stroke_color=TEXTO_TENUE, stroke_width=1.5)
    caja.move_to([x, Y_EQUIPOS, 0])
    return VGroup(caja, texto(nombre, tam=22).move_to(caja))


def burbuja(x):
    contenido = texto(MENSAJE, tam=18)
    caja = SurroundingRectangle(contenido, buff=0.18, corner_radius=0.12,
                                color=COLOR_CAPA[7], stroke_width=1.5)
    grupo = VGroup(caja, contenido)
    grupo.move_to([x, Y_EQUIPOS + 1.3, 0])
    grupo.set_x(min(max(x, -7.1 + grupo.width / 2 + 0.3), 7.1 - grupo.width / 2 - 0.3))
    return grupo


class EscenaGancho(Scene):
    def construct(self):
        pc_a = equipo("PC A", X_PC_A)
        servidor = equipo("Servidor", X_SERVIDOR)
        red = RoundedRectangle(width=4.6, height=1.6, corner_radius=0.12,
                               stroke_color=TEXTO_TENUE, stroke_width=1.5,
                               fill_color=CAJA_DATOS, fill_opacity=1)
        red.move_to([0, Y_EQUIPOS, 0])
        rotulo_red = texto("la red", tam=20, color=TEXTO_MEDIO).move_to(red)
        enlace_izq = Line(pc_a[0].get_right(), red.get_left(), color=TEXTO_TENUE, stroke_width=1.5)
        enlace_der = Line(red.get_right(), servidor[0].get_left(), color=TEXTO_TENUE, stroke_width=1.5)

        mensaje_origen = burbuja(X_PC_A)

        self.play(FadeIn(pc_a), FadeIn(servidor), FadeIn(enlace_izq), FadeIn(enlace_der),
                  FadeIn(red), FadeIn(rotulo_red), run_time=0.8)
        self.play(FadeIn(mensaje_origen), run_time=0.6)
        self.wait(1.0)

        punto = Square(side_length=0.2, stroke_width=0, fill_color=COLOR_CAPA[7],
                       fill_opacity=1).move_to(pc_a[0].get_right())
        self.play(FadeIn(punto), run_time=0.2)
        self.play(punto.animate.move_to(red.get_left()), run_time=0.6, rate_func=linear)
        self.remove(punto)
        self.wait(0.4)
        punto.move_to(red.get_right())
        self.add(punto)
        self.play(punto.animate.move_to(servidor[0].get_left()), run_time=0.6, rate_func=linear)
        self.play(FadeOut(punto), FadeIn(burbuja(X_SERVIDOR)), run_time=0.5)

        paso = texto_paso(
            "Escribes un mensaje y llega en milisegundos.",
            "¿Qué pasó en medio?",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(FadeIn(paso), run_time=0.8)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[0], paso[1]))

        nuevo = texto_paso(
            "Se va a seguir este mensaje exacto",
            "Qué se le agrega en cada capa al salir de PC A, qué se verifica en el camino\n"
            "y cómo se vuelve a armar en el servidor, aunque algo salga mal.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
