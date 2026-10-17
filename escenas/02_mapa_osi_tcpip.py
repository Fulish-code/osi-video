import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

X_IZQUIERDA = -6.6
X_PILA = -1.6
ANCHO_FILA = 6.0
ALTO_FILA = 0.6

GRUPOS_TCPIP = [
    ("Aplicación", [7, 6, 5]),
    ("Transporte", [4]),
    ("Internet", [3]),
    ("Acceso a red", [2, 1]),
]


class EscenaMapa(Scene):
    def construct(self):
        filas = {}
        pila = VGroup()
        for n in range(7, 0, -1):
            caja = Rectangle(width=ANCHO_FILA, height=ALTO_FILA,
                             stroke_color=COLOR_CAPA[n], stroke_width=1.5,
                             fill_color=COLOR_CAPA[n], fill_opacity=0.22)
            franja = Rectangle(width=0.16, height=ALTO_FILA, stroke_width=0,
                               fill_color=COLOR_CAPA[n], fill_opacity=1)
            franja.align_to(caja, LEFT)
            nombre = texto(f"{n}  {NOMBRE_CAPA[n]}", tam=22)
            nombre.next_to(franja, RIGHT, buff=0.3)
            pdu = texto(PDU_CAPA[n], tam=19, color=TEXTO_MEDIO)
            pdu.move_to(caja.get_right() + LEFT * 0.25, aligned_edge=RIGHT)
            fila = VGroup(caja, franja, nombre, pdu)
            filas[n] = fila
            pila.add(fila)
        pila.arrange(DOWN, buff=0.1).move_to([X_PILA, 0.55, 0])
        rotulo_pdu = texto("PDU", tam=16, color=TEXTO_TENUE)
        rotulo_pdu.next_to(pila, UP, buff=0.2).align_to(filas[7][3], RIGHT)
        rotulo_osi = texto("Modelo OSI", tam=16, color=TEXTO_TENUE)
        rotulo_osi.next_to(pila, UP, buff=0.2).align_to(pila, LEFT)

        paso = texto_paso(
            "Las 7 capas",
            "De arriba abajo es el orden en que se arma lo que sale de PC A.\n"
            "PDU es el nombre que recibe la unidad de datos en cada capa.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(FadeIn(rotulo_osi), FadeIn(rotulo_pdu), FadeIn(paso), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(f, shift=DOWN * 0.1) for f in pila],
                              lag_ratio=0.15), run_time=1.5)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Segmento, paquete, trama, bits",
            "Los nombres de las capas 4 a 1 se usan en todo el video.\n"
            "En 7, 6 y 5 se habla simplemente de datos.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(cambiar_texto(paso, nuevo),
                  *[filas[n][3].animate.set_color(TEXTO) for n in (4, 3, 2, 1)],
                  run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        grupos = VGroup()
        for nombre, capas in GRUPOS_TCPIP:
            arriba, abajo = filas[capas[0]], filas[capas[-1]]
            alto = arriba.get_top()[1] - abajo.get_bottom()[1]
            caja = Rectangle(width=2.6, height=alto, stroke_color=TEXTO_MEDIO,
                             stroke_width=1.5)
            caja.next_to(pila, RIGHT, buff=0.35)
            caja.set_y((arriba.get_top()[1] + abajo.get_bottom()[1]) / 2)
            grupos.add(VGroup(caja, texto(nombre, tam=20).move_to(caja)))
        rotulo_tcpip = texto("TCP/IP", tam=16, color=TEXTO_TENUE)
        rotulo_tcpip.next_to(grupos, UP, buff=0.2).align_to(grupos, LEFT)

        nuevo = texto_paso(
            "Cómo lo agrupa TCP/IP",
            "Aplicación junta 7, 6 y 5. Transporte es la 4, Internet la 3\n"
            "y acceso a red junta 2 y 1. Las funciones son las mismas.",
            x_izquierda=X_IZQUIERDA,
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(rotulo_tcpip),
                  LaggedStart(*[FadeIn(g, shift=LEFT * 0.15) for g in grupos],
                              lag_ratio=0.2), run_time=1.2)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        pila_fija = PilaCapas(activa=None)
        nuevo = texto_paso(
            "Desde aquí, la pila queda a la izquierda",
            "La capa que se explica se resalta y las demás se atenúan.",
        )
        self.play(FadeOut(grupos), FadeOut(rotulo_tcpip), FadeOut(rotulo_osi),
                  FadeOut(rotulo_pdu), FadeOut(paso), run_time=0.5)
        self.play(*[ReplacementTransform(filas[n], pila_fija.filas[n]) for n in range(7, 0, -1)],
                  run_time=1.2)
        self.remove(*[pila_fija.filas[n] for n in range(7, 0, -1)])
        self.add(pila_fija)
        self.play(FadeIn(nuevo), run_time=0.6)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))
