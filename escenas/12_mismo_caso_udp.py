import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

VERDE = COLOR_CAPA[4]
ROJO = COLOR_CAPA[1]

ANCHO_CELDA = 0.29
ALTO = 0.5
Y_LLEGADA = 1.2
Y_ENTREGADO = -0.6
X_CENTRO = (X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2

CAMPOS_UDP = [("Puerto\norigen", 1.55), ("Puerto\ndestino", 1.55),
              ("Longitud", 1.2), ("Checksum", 1.55)]


def datagrama(contenido):
    encabezado = campo("UDP", 0.9, VERDE, tam=16, alto=ALTO)
    datos = FilaBytes(contenido, ancho_celda=ANCHO_CELDA, alto_celda=ALTO, tam=18)
    datos.next_to(encabezado, RIGHT, buff=0)
    return VGroup(encabezado, datos)


class EscenaUDP(Scene):
    def construct(self):
        pila = PilaCapas(activa=None)
        self.add(pila)
        panel = panel_libre(
            "El mismo caso con UDP",
            ["Mismos tres trozos y mismo orden de llegada que en TCP.",
             "Ahora viajan como datagramas UDP."],
            VERDE,
        )

        inicio, contenido = SEGMENTOS[0]
        valores = [str(PUERTO_ORIGEN), str(PUERTO_DESTINO),
                   str(8 + len(contenido)), f"0x{checksum_udp(contenido):04X}"]
        casillas = VGroup(*[campo(v, ancho, VERDE, tam=20, alto=ALTO)
                            for v, (_, ancho) in zip(valores, CAMPOS_UDP)])
        casillas.arrange(RIGHT, buff=0)
        datos = FilaBytes(contenido, ancho_celda=ANCHO_CELDA, alto_celda=ALTO, tam=20)
        datos.next_to(casillas, RIGHT, buff=0.2)
        fila = VGroup(casillas, datos).move_to([X_CENTRO, Y_LLEGADA, 0])
        nombres = VGroup(*[
            Paragraph(*nombre.split("\n"), font=FUENTE, font_size=16,
                      color=TEXTO_MEDIO, alignment="center", line_spacing=0.8)
            .next_to(casilla, UP, buff=0.12)
            for (nombre, _), casilla in zip(CAMPOS_UDP, casillas)
        ])

        paso = texto_paso(
            "Encabezado UDP: 8 bytes",
            "Puertos, longitud y checksum. No hay número de secuencia ni ACK:\n"
            "UDP no sabe en qué orden salieron los datos.",
        )
        self.play(*pila.activar(4), FadeIn(panel), FadeIn(fila), FadeIn(nombres),
                  FadeIn(paso), run_time=0.8)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Simplificación",
            "Una aplicación real sobre UDP no partiría el mensaje así.\n"
            "Se parte igual que en TCP para poder comparar.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        rotulo_entregado = texto("Lo que recibe la aplicación, en orden de llegada",
                                 tam=16, color=TEXTO_MEDIO)
        rotulo_entregado.move_to([X_ZONA_PRINCIPAL + 0.1, Y_ENTREGADO + 0.5, 0],
                                 aligned_edge=LEFT)
        self.play(FadeOut(fila), FadeOut(nombres), FadeIn(rotulo_entregado),
                  run_time=0.6)

        entregado = VGroup()
        contenido_de = dict(SEGMENTOS)

        def entregar(seq, titulo, descripcion):
            nonlocal paso
            d = datagrama(contenido_de[seq]).move_to([X_CENTRO, Y_LLEGADA, 0])
            nuevo = texto_paso(titulo, descripcion)
            self.play(cambiar_texto(paso, nuevo), FadeIn(d), run_time=0.6)
            paso = nuevo
            datos = d[1]
            if len(entregado) == 0:
                destino_x = X_ZONA_PRINCIPAL + 0.1
            else:
                destino_x = entregado.get_right()[0] + 0.12
            self.play(FadeOut(d[0]),
                      datos.animate.move_to([destino_x, Y_ENTREGADO, 0], aligned_edge=LEFT),
                      run_time=0.9)
            entregado.add(datos)
            revisar_encuadre(self)
            self.wait(tiempo_lectura(paso[1]))

        entregar(24, "Llega primero el tercero",
                 "UDP se lo entrega a la aplicación apenas llega.\n"
                 "No tiene forma de saber que había otros antes.")

        perdido = datagrama(contenido_de[0]).move_to([X_CENTRO, Y_LLEGADA, 0])
        perdido.set_opacity(0.35)
        tachado = Line(perdido.get_corner(DL), perdido.get_corner(UR),
                       color=ROJO, stroke_width=3)
        etiqueta_perdido = texto("perdido en el camino", tam=16, color=ROJO)
        etiqueta_perdido.next_to(perdido, DOWN, buff=0.15)
        nuevo = texto_paso(
            "El primero se perdió",
            "Nadie lo reenvía. El receptor ni siquiera sabe que existió.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(perdido), run_time=0.6)
        paso = nuevo
        self.play(Create(tachado), FadeIn(etiqueta_perdido), run_time=0.6)
        self.wait(tiempo_lectura(paso[1]))
        self.play(FadeOut(VGroup(perdido, tachado, etiqueta_perdido)), run_time=0.5)

        entregar(12, "Llega el segundo",
                 "Se entrega detrás del anterior, porque llegó después.")

        original = FilaBytes(MENSAJE, ancho_celda=ANCHO_CELDA, alto_celda=ALTO, tam=18)
        original.move_to([X_ZONA_PRINCIPAL + 0.1, Y_LLEGADA, 0], aligned_edge=LEFT)
        rotulo_original = texto("Enviado por PC A", tam=16, color=TEXTO_MEDIO)
        rotulo_original.next_to(original, UP, buff=0.12).align_to(original, LEFT)

        nuevo = texto_paso(
            "Resultado",
            "Desordenado y sin el principio. UDP entregó lo que llegó, como llegó.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(original),
                  FadeIn(rotulo_original), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Cuándo conviene UDP",
            "Si la aplicación necesita orden o reenvío, lo hace ella (QUIC lo hace).\n"
            "En voz o video en vivo un dato tardío ya no sirve: por eso usan UDP.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
