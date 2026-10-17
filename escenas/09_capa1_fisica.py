import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

ROJO = COLOR_CAPA[1]
NARANJA = COLOR_CAPA[2]

BYTES_MAC = MAC_ROUTER_A.split(":")
BYTES_SENAL = BYTES_MAC[:2]

ANCHO_BIT = 0.5
X_BITS = -3.3
Y_TRAMA = 1.65
Y_HEX = 0.95
Y_BYTE = 0.4
Y_BITS = -0.05
Y_ALTO = -0.75
Y_BAJO = -1.65


def bits_de(byte_hex):
    return format(int(byte_hex, 16), "08b")


class EscenaFisica(Scene):
    def construct(self):
        pila = PilaCapas(activa=2)
        self.add(pila)
        panel = panel_capa(
            1,
            agrega="ningún encabezado: convierte la trama en señal",
            para_que="mover bits de un equipo al siguiente por un medio físico",
        )
        self.play(*pila.activar(1), FadeIn(panel), run_time=0.8)

        trama = trama_compacta()
        trama.move_to([X_BITS, Y_TRAMA, 0], aligned_edge=LEFT)
        marca = SurroundingRectangle(trama[0], buff=0.06, color=NARANJA,
                                     stroke_width=2)

        hex_bytes = VGroup(*[mono(b, tam=22) for b in BYTES_MAC])
        hex_bytes.arrange(RIGHT, buff=0.35)
        hex_bytes.move_to([X_BITS, Y_HEX, 0], aligned_edge=LEFT)
        puntos = mono("…", tam=22, color=TEXTO_TENUE).next_to(hex_bytes[-1], RIGHT, buff=0.3)
        fila_hex = VGroup(hex_bytes, puntos)

        paso = texto_paso(
            "La trama son bytes",
            f"Lo primero que sale es la MAC destino: {MAC_ROUTER_A}.\n"
            "La capa 1 recibe la trama entera como una fila de bytes.",
        )
        self.play(FadeIn(trama), FadeIn(paso), run_time=0.8)
        self.play(Create(marca), FadeIn(fila_hex), run_time=0.8)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        bits = VGroup()
        for i, b in enumerate(BYTES_SENAL):
            for j, bit in enumerate(bits_de(b)):
                x = X_BITS + ANCHO_BIT * (8 * i + j + 0.5)
                bits.add(mono(bit, tam=24).move_to([x, Y_BITS, 0]))
        etiquetas_byte = VGroup(*[
            mono(b, tam=18, color=TEXTO_MEDIO)
            .move_to([X_BITS + ANCHO_BIT * (8 * i + 4), Y_BYTE, 0])
            for i, b in enumerate(BYTES_SENAL)
        ])
        separador = DashedLine([X_BITS + 8 * ANCHO_BIT, Y_BYTE + 0.2, 0],
                               [X_BITS + 8 * ANCHO_BIT, Y_BAJO - 0.15, 0],
                               color=TEXTO_TENUE, stroke_width=1)

        nuevo = texto_paso(
            "Cada byte son 8 bits",
            f"{BYTES_SENAL[0]} en binario es {bits_de(BYTES_SENAL[0])} "
            f"y {BYTES_SENAL[1]} es {bits_de(BYTES_SENAL[1])}.\n"
            "Se siguen solo estos dos bytes; el resto de la trama sigue igual.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  hex_bytes[2:].animate.set_color(TEXTO_TENUE),
                  puntos.animate.set_color(TEXTO_TENUE),
                  *[TransformFromCopy(hex_bytes[i], etiquetas_byte[i])
                    for i in range(len(BYTES_SENAL))],
                  LaggedStart(*[FadeIn(b) for b in bits], lag_ratio=0.05),
                  run_time=1.2)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        cadena = "".join(bits_de(b) for b in BYTES_SENAL)
        puntos_senal = []
        for k, bit in enumerate(cadena):
            y = Y_ALTO if bit == "1" else Y_BAJO
            puntos_senal.append([X_BITS + ANCHO_BIT * k, y, 0])
            puntos_senal.append([X_BITS + ANCHO_BIT * (k + 1), y, 0])
        senal = VMobject(stroke_color=ROJO, stroke_width=3)
        senal.set_points_as_corners(puntos_senal)

        etiqueta_alto = mono("alto", tam=14, color=TEXTO_MEDIO)
        etiqueta_alto.next_to([X_BITS, Y_ALTO, 0], LEFT, buff=0.15)
        etiqueta_bajo = mono("bajo", tam=14, color=TEXTO_MEDIO)
        etiqueta_bajo.next_to([X_BITS, Y_BAJO, 0], LEFT, buff=0.15)
        eje = DashedLine([X_BITS, (Y_ALTO + Y_BAJO) / 2, 0],
                         [X_BITS + ANCHO_BIT * 16, (Y_ALTO + Y_BAJO) / 2, 0],
                         color=BORDE_DATOS, stroke_width=1)
        flecha_tiempo = texto("tiempo →", tam=14, color=TEXTO_TENUE)
        flecha_tiempo.next_to(eje, RIGHT, buff=0.15)

        nuevo = texto_paso(
            "Bits a señal",
            "En un cable de cobre cada bit se vuelve un nivel de voltaje.\n"
            "Aquí, alto para 1 y bajo para 0, uno detrás de otro en el tiempo.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeIn(etiqueta_alto), FadeIn(etiqueta_bajo),
                  FadeIn(eje), FadeIn(flecha_tiempo), FadeIn(separador),
                  run_time=0.6)
        paso = nuevo
        self.play(Create(senal), run_time=2.5, rate_func=linear)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Simplificación",
            "Ethernet real usa codificaciones más elaboradas y antes de la trama\n"
            "manda un preámbulo para que el receptor se sincronice.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        medios = VGroup()
        for nombre, como in [("Cobre", "variaciones de voltaje"),
                             ("Fibra óptica", "pulsos de luz"),
                             ("Wi-Fi", "ondas de radio")]:
            contenido = VGroup(texto(nombre, tam=20),
                               texto(como, tam=17, color=TEXTO_MEDIO))
            contenido.arrange(DOWN, buff=0.1)
            caja = RoundedRectangle(width=3.1, height=1.0, corner_radius=0.08,
                                    stroke_color=TEXTO_TENUE, stroke_width=1.5)
            contenido.move_to(caja)
            medios.add(VGroup(caja, contenido))
        medios.arrange(RIGHT, buff=0.3)
        medios.move_to([(X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2, -0.1, 0])
        medios[0][0].set_stroke(ROJO)

        nuevo = texto_paso(
            "El medio puede cambiar",
            "Por fibra los bits viajan como luz y por Wi-Fi como ondas de radio.\n"
            "La trama que se manda es la misma.",
        )
        senal_y_bits = VGroup(fila_hex, etiquetas_byte, bits, separador, senal, etiqueta_alto,
                              etiqueta_bajo, eje, flecha_tiempo)
        self.play(FadeOut(senal_y_bits), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(medios), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Esta capa no interpreta nada",
            "No sabe qué es una MAC ni una IP. Solo manda y recibe señales.\n"
            "Darles sentido a esos bits le toca a la capa 2 del otro lado.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
