import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

VIOLETA = COLOR_CAPA[6]
X_CENTRO = (X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2
ANCHO_CELDA = 0.3
Y_TEXTO = 1.1
Y_BYTES = -0.1


class EscenaPresentacion(Scene):
    def construct(self):
        pila = PilaCapas(activa=7)
        self.add(pila)
        panel = panel_capa(
            6,
            agrega="codificación; a veces compresión o cifrado",
            para_que="que los dos extremos interpreten los bytes igual",
        )
        self.play(*pila.activar(6), FadeIn(panel), run_time=0.8)

        caracteres = FilaBytes(MENSAJE, ancho_celda=ANCHO_CELDA, tam=20)
        caracteres.move_to([X_CENTRO, Y_TEXTO, 0])
        bytes_hex = FilaBytes(MENSAJE, ancho_celda=ANCHO_CELDA, tam=13, hexadecimal=True)
        bytes_hex.move_to([X_CENTRO, Y_BYTES, 0])
        rotulo_texto = texto("Texto", tam=16, color=TEXTO_MEDIO)
        rotulo_texto.next_to(caracteres, UP, buff=0.12).align_to(caracteres, LEFT)
        rotulo_bytes = texto("Bytes en UTF-8 (hexadecimal)", tam=16, color=TEXTO_MEDIO)
        rotulo_bytes.next_to(bytes_hex, DOWN, buff=0.12).align_to(bytes_hex, LEFT)

        paso = texto_paso(
            "Texto a bytes",
            "Cada carácter se codifica con UTF-8. N es 4E, o es 6F, el espacio es 20.\n"
            "Este mensaje no tiene acentos, así que cada carácter ocupa un byte.",
        )
        self.play(FadeIn(caracteres), FadeIn(rotulo_texto), FadeIn(paso), run_time=0.6)
        self.play(FadeIn(rotulo_bytes),
                  LaggedStart(*[TransformFromCopy(caracteres.bytes[i], bytes_hex.bytes[i])
                                for i in range(len(MENSAJE))], lag_ratio=0.06),
                  run_time=2.5)
        marcas = VGroup(*[
            SurroundingRectangle(VGroup(caracteres.bytes[i], bytes_hex.bytes[i]),
                                 buff=0, color=VIOLETA, stroke_width=2)
            for i in (0, 1)
        ])
        self.play(Create(marcas), run_time=0.6)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Con acentos sería distinto",
            "En UTF-8 la á ocupa 2 bytes (C3 A1). Por eso el mensaje del ejemplo\n"
            "va sin acentos: 34 caracteres, 34 bytes.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeOut(marcas), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Compresión y cifrado",
            "También se ubican en esta capa: achicar los datos, o cifrarlos\n"
            "para que nadie en el camino los pueda leer.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "En la práctica",
            "Lo hace la aplicación o una biblioteca, no una capa aparte.\n"
            "TLS se ubica aquí o en la capa 5, según quién lo describa.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "En este ejemplo",
            "El mensaje va sin cifrar, para poder seguir\n"
            "los mismos bytes hasta el final.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  caracteres.animate.set_opacity(0.35),
                  rotulo_texto.animate.set_opacity(0.35), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
