import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

X_IZQUIERDA = -6.6

PROBLEMAS = [
    "Que los dos extremos interpreten los bytes igual.",
    "Que dos conversaciones no se mezclen.",
    "Que un dato grande se pueda partir y volver a armar.",
    "Que se encuentre el destino entre millones de equipos.",
    "Que el dato cruce redes distintas.",
    "Que los bits se conviertan en una señal real en un cable.",
]


def pila_chica(nombre, x):
    filas = VGroup()
    for n in range(7, 0, -1):
        caja = Rectangle(width=2.4, height=0.42, stroke_color=COLOR_CAPA[n],
                         stroke_width=1.5, fill_color=COLOR_CAPA[n], fill_opacity=0.25)
        etiqueta = texto(f"{n}  {NOMBRE_CAPA[n]}", tam=16).move_to(caja)
        filas.add(VGroup(caja, etiqueta))
    filas.arrange(DOWN, buff=0.24)
    filas.move_to([x, 0.6, 0])
    rotulo = texto(nombre, tam=20, color=TEXTO_MEDIO).next_to(filas, UP, buff=0.15)
    return VGroup(rotulo, filas)


class EscenaProblema(Scene):
    def construct(self):
        titulo = texto("Para que 34 bytes lleguen intactos a otra máquina hay que resolver:",
                       tam=24)
        titulo.move_to([X_IZQUIERDA, 3.3, 0], aligned_edge=LEFT)
        items = VGroup(*[texto(p, tam=22, color=TEXTO) for p in PROBLEMAS])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        items.next_to(titulo, DOWN, buff=0.45, aligned_edge=LEFT).shift(RIGHT * 0.3)

        self.play(FadeIn(titulo), run_time=0.6)
        for item in items:
            self.play(FadeIn(item, shift=RIGHT * 0.15), run_time=0.5)
            self.wait(tiempo_lectura(item) * 0.7)

        paso = texto_paso(
            "Son problemas distintos",
            "Se pueden resolver por separado, y cada uno con su propia información de control.\n"
            "Por eso se separan en capas.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(FadeIn(paso), run_time=0.6)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        pc_a = pila_chica("PC A", -3.0)
        servidor = pila_chica("Servidor", 3.0)
        pares = VGroup(*[
            DashedLine(pc_a[1][i][0].get_right(), servidor[1][i][0].get_left(),
                       color=TEXTO_TENUE, stroke_width=1.2, dash_length=0.1)
            for i in range(7)
        ])

        nuevo = texto_paso(
            "Cada capa habla con su par",
            "La capa 4 de PC A le escribe a la capa 4 del servidor:\n"
            "lo que una agrega, la otra lo lee y lo quita.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(FadeOut(titulo), FadeOut(items), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(pc_a), FadeIn(servidor), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        self.play(LaggedStart(*[Create(p) for p in pares], lag_ratio=0.1), run_time=1.2)
        self.play(pares[3].animate.set_color(COLOR_CAPA[4]).set_stroke(width=2.5),
                  run_time=0.5)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        flechas = VGroup()
        for i in range(6):
            arriba, abajo = pc_a[1][i][0], pc_a[1][i + 1][0]
            flechas.add(DoubleArrow(arriba.get_bottom(), abajo.get_top(),
                                    buff=0.02, stroke_width=2, tip_length=0.08,
                                    max_tip_length_to_length_ratio=0.5,
                                    color=TEXTO_MEDIO))
        nuevo = texto_paso(
            "Cada capa solo conoce a sus vecinas",
            "Usa lo que le entrega la capa de abajo y atiende a la de arriba.\n"
            "No necesita saber cómo trabajan las demás.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(cambiar_texto(paso, nuevo), pares.animate.set_opacity(0.3),
                  LaggedStart(*[FadeIn(f) for f in flechas], lag_ratio=0.1),
                  run_time=1.0)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "OSI es un modelo de referencia",
            "Sirve para ordenar las ideas. Internet usa TCP/IP, que agrupa\n"
            "estas mismas funciones en menos capas. Se ve en el mapa que sigue.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
