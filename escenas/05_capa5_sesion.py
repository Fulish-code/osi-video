import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

TURQUESA = COLOR_CAPA[5]
X_PC_A, X_SERVIDOR = -2.4, 5.4
Y_ARRIBA, Y_ABAJO = 1.6, -2.2

DIALOGO = [
    ("pc", "srv", "abrir el diálogo", 1.05),
    ("srv", "pc", "aceptado", 0.45),
    ("pc", "srv", MENSAJE, -0.2),
    ("srv", "pc", "más mensajes…", -0.85),
    ("pc", "srv", "cerrar el diálogo", -1.65),
]


class EscenaSesion(Scene):
    def construct(self):
        pila = PilaCapas(activa=6)
        self.add(pila)
        panel = panel_capa(
            5,
            agrega="control del diálogo, si se usa",
            para_que="ordenar la conversación entre los dos extremos",
        )
        self.play(*pila.activar(5), FadeIn(panel), run_time=0.8)

        def extremo(nombre, x):
            rotulo = texto(nombre, tam=19)
            rotulo.move_to([x, Y_ARRIBA + 0.2, 0])
            linea = Line([x, Y_ARRIBA, 0], [x, Y_ABAJO, 0],
                         color=TEXTO_TENUE, stroke_width=1.5)
            return VGroup(rotulo, linea)

        pc_a = extremo("PC A", X_PC_A)
        servidor = extremo("Servidor", X_SERVIDOR)
        x_de = {"pc": X_PC_A, "srv": X_SERVIDOR}

        flechas = []
        for desde, hacia, etiqueta, y in DIALOGO:
            flecha = Arrow([x_de[desde], y, 0], [x_de[hacia], y, 0], buff=0.05,
                           stroke_width=2, tip_length=0.15, color=TURQUESA)
            nombre = texto(etiqueta, tam=16, color=TEXTO)
            nombre.next_to(flecha, UP, buff=0.06)
            flechas.append(VGroup(flecha, nombre))
        flechas[2][0].set_color(COLOR_CAPA[7])

        tiempo = texto("tiempo ↓", tam=14, color=TEXTO_TENUE)
        tiempo.next_to(pc_a[1], LEFT, buff=0.15).align_to(pc_a[1], DOWN)

        paso = texto_paso(
            "Apertura, intercambio y cierre",
            "Antes de intercambiar mensajes el diálogo se abre,\n"
            "y al terminar se cierra.",
        )
        self.play(FadeIn(pc_a), FadeIn(servidor), FadeIn(tiempo), FadeIn(paso), run_time=0.6)
        for f in flechas:
            self.play(GrowArrow(f[0]), FadeIn(f[1]), run_time=0.6)
            self.wait(0.4)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Qué resuelve",
            "Quién habla y cuándo, y desde dónde retomar si se corta a la mitad\n"
            "de algo largo (puntos de control).",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "En TCP/IP casi nunca existe aparte",
            "Abrir y cerrar la conexión lo hace TCP en la capa 4.\n"
            "El resto lo resuelve la aplicación, si lo necesita.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
