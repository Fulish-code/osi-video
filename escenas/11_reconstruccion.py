import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

ROJO = COLOR_CAPA[1]
NARANJA = COLOR_CAPA[2]
AMARILLO = COLOR_CAPA[3]
VERDE = COLOR_CAPA[4]

X_CENTRO = (X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2
Y_TRAMA = 1.25
Y_LISTA = 0.45
ALTO_LINEA = 0.42

ANCHO_BYTE = 0.29
SEPARACION_HUECOS = 0.15
ORDEN_LLEGADA = [24, 0, 12]


def linea_verificacion(que, resultado):
    izquierda = texto(que, tam=18, color=TEXTO_MEDIO)
    derecha = texto(resultado, tam=18)
    derecha.next_to(izquierda, RIGHT, buff=0.35)
    return VGroup(izquierda, derecha)


def lista(lineas):
    grupo = VGroup(*lineas).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    grupo.move_to([X_ZONA_PRINCIPAL + 0.1, Y_LISTA, 0], aligned_edge=UL)
    return grupo


class EscenaReconstruccion(Scene):
    def construct(self):
        pila = PilaCapas(activa=None)
        self.add(pila)
        panel = panel_libre(
            "Reconstrucción en el servidor",
            ["Se sube por la pila: cada capa verifica lo que agregó su par en PC A",
             "y lo quita antes de pasar el resto a la capa de arriba."],
            TEXTO_TENUE,
        )

        bits = "0011110001010010"
        puntos = []
        for k, bit in enumerate(bits):
            y = Y_TRAMA + (0.3 if bit == "1" else -0.3)
            puntos += [[X_CENTRO - 4 + 0.5 * k, y, 0], [X_CENTRO - 4 + 0.5 * (k + 1), y, 0]]
        senal = VMobject(stroke_color=ROJO, stroke_width=3)
        senal.set_points_as_corners(puntos)

        trama = tira([
            ("Ethernet", 1.7, NARANJA),
            ("IP", 1.2, AMARILLO),
            ("TCP", 1.0, VERDE),
            ("datos", 1.8, None),
            ("FCS", 0.9, NARANJA),
        ], alto=0.55, tam=18)
        trama.move_to([X_CENTRO, Y_TRAMA, 0])

        paso = texto_paso(
            "Capa 1: señal a bits",
            "La tarjeta de red del servidor lee la señal del cable\n"
            "y la vuelve a convertir en bits. Con esos bits arma la trama.",
        )
        self.play(*pila.activar(1), FadeIn(panel), FadeIn(paso), run_time=0.8)
        self.play(Create(senal), run_time=1.5, rate_func=linear)
        self.play(ReplacementTransform(senal, trama), run_time=1.0)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        verif_2 = lista([
            linea_verificacion("FCS recalculado contra el FCS recibido", "✓ coinciden"),
            linea_verificacion(f"MAC destino {MAC_SERVIDOR}", "✓ es la propia"),
            linea_verificacion(f"EtherType {ETHERTYPE_IPV4}", "→ se entrega a IPv4"),
        ])
        nuevo = texto_paso(
            "Capa 2: verificar la trama",
            "Si el FCS no coincidiera, la trama se descartaría aquí mismo.\n"
            "Si la MAC destino fuera de otro equipo, también.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(2), run_time=0.6)
        paso = nuevo
        for linea in verif_2:
            self.play(FadeIn(linea), run_time=0.5)
            self.wait(1.2)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        paquete = VGroup(trama[1], trama[2], trama[3])
        nuevo = texto_paso(
            "Se quitan el encabezado y el FCS",
            "Ya cumplieron su función. Lo que sube a la capa 3 es el paquete.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeOut(trama[0], shift=UP * 0.4), FadeOut(trama[4], shift=UP * 0.4),
                  verif_2.animate.set_color(TEXTO_TENUE), run_time=0.8)
        self.play(paquete.animate.move_to([X_CENTRO, Y_TRAMA, 0]), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        verif_3 = lista([
            linea_verificacion("Checksum del encabezado IP", "✓ coincide"),
            linea_verificacion(f"IP destino {IP_SERVIDOR}", "✓ es la propia"),
            linea_verificacion(f"Protocolo {PROTOCOLO_TCP}", "→ se entrega a TCP"),
        ])
        nuevo = texto_paso(
            "Capa 3: verificar el paquete",
            "El TTL ya no importa: el paquete llegó a destino.\n"
            "Se quita el encabezado IP y sube el segmento.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(3),
                  FadeOut(verif_2), run_time=0.6)
        paso = nuevo
        for linea in verif_3:
            self.play(FadeIn(linea), run_time=0.5)
            self.wait(1.2)
        self.play(FadeOut(trama[1], shift=UP * 0.4),
                  verif_3.animate.set_color(TEXTO_TENUE), run_time=0.6)
        segmento = VGroup(trama[2], trama[3])
        self.play(segmento.animate.move_to([X_CENTRO, Y_TRAMA, 0]), run_time=0.6)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Lo mismo con cada trama",
            "Las tres tramas pasan por estos pasos. Lo que cambia es la capa 4:\n"
            "los segmentos no llegaron en el orden en que salieron.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeOut(verif_3), FadeOut(segmento),
                  run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        huecos = {}
        x = X_CENTRO - (ANCHO_BYTE * len(MENSAJE) + 2 * SEPARACION_HUECOS) / 2
        for inicio, contenido in SEGMENTOS:
            ancho = ANCHO_BYTE * len(contenido)
            marco = DashedVMobject(
                Rectangle(width=ancho, height=0.5, stroke_color=TEXTO_TENUE,
                          stroke_width=1.5),
                num_dashes=30)
            marco.move_to([x, Y_TRAMA, 0], aligned_edge=LEFT)
            falta = texto("falta", tam=15, color=TEXTO_TENUE).move_to(marco)
            fin = inicio + len(contenido) - 1
            rotulo = mono(f"seq {inicio} (bytes {inicio} a {fin})", tam=13,
                          color=TEXTO_MEDIO)
            rotulo.next_to(marco, UP, buff=0.12)
            huecos[inicio] = VGroup(marco, falta, rotulo)
            x += ancho + SEPARACION_HUECOS
        todos_huecos = VGroup(*huecos.values())

        nuevo = texto_paso(
            "Capa 4: armar el mensaje",
            "Cada segmento va en la posición que marca su número de secuencia.\n"
            "En el camino se perdió el de seq 0 y el de seq 12 se demoró.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(4),
                  FadeIn(todos_huecos), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        eventos = [
            (24, "Llega seq 24. Checksum ✓, se guarda.", "ACK 0"),
            (None, "En PC A vence el tiempo de espera y reenvía seq 0.", None),
            (0, "Llega seq 0 (reenviado). Checksum ✓, se guarda.", "ACK 12"),
            (12, "Llega seq 12. Checksum ✓, se guarda.", "ACK 34"),
        ]
        textos_paso = [
            ("Llega primero el de seq 24",
             "Se guarda, pero faltan los bytes 0 a 23 y no se puede entregar nada.\n"
             "Responde ACK 0: sigue esperando el byte 0."),
            ("PC A reenvía el segmento de seq 0",
             "TCP no pide un segmento puntual: el ACK solo dice qué byte espera.\n"
             "Como el byte 0 no se confirmó a tiempo, PC A lo vuelve a mandar."),
            ("Llega el de seq 0",
             "Los bytes 0 a 11 ya están. Responde ACK 12: ahora espera el byte 12.\n"
             "El de seq 24 sigue guardado hasta que se llene el hueco del medio."),
            ("Llega el de seq 12",
             "No queda ningún hueco. ACK 34: recibió del byte 0 al 33.\n"
             "Recién ahora la capa 4 puede entregar los datos."),
        ]
        contenido_de = dict(SEGMENTOS)
        datos_recibidos = {}
        lineas_eventos = VGroup()
        for i, ((seq, que, ack), (titulo, desc)) in enumerate(zip(eventos, textos_paso)):
            linea = texto(que, tam=17)
            if ack:
                etiqueta_ack = mono(ack, tam=17, color=VERDE)
                etiqueta_ack.next_to(linea, RIGHT, buff=0.4)
                linea = VGroup(linea, etiqueta_ack)
            linea.move_to([X_ZONA_PRINCIPAL + 0.1, Y_LISTA - 0.25 - ALTO_LINEA * i, 0],
                          aligned_edge=LEFT)
            lineas_eventos.add(linea)

            nuevo = texto_paso(titulo, desc)
            anteriores = [l.animate.set_color(TEXTO_TENUE) for l in lineas_eventos[:-1]]
            self.play(cambiar_texto(paso, nuevo), FadeIn(linea), *anteriores, run_time=0.7)
            paso = nuevo

            if seq is not None:
                datos = FilaBytes(contenido_de[seq], ancho_celda=ANCHO_BYTE,
                                  alto_celda=0.5, tam=12, hexadecimal=True)
                destino = huecos[seq][0]
                datos.move_to(destino).shift(DOWN * 0.75)
                self.play(FadeIn(datos, shift=UP * 0.2), run_time=0.4)
                self.play(datos.animate.move_to(destino),
                          FadeOut(huecos[seq][1]),
                          huecos[seq][0].animate.set_stroke(VERDE),
                          run_time=0.7)
                datos_recibidos[seq] = datos
            if i == 3:
                revisar_encuadre(self)
            self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Otra forma de reenviar",
            "Con tres ACK repetidos, PC A reenvía sin esperar el tiempo.\n"
            "Aquí hubo uno solo (ACK 0), por eso reenvió al vencer el tiempo.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        recibido = FilaBytes(MENSAJE, ancho_celda=ANCHO_BYTE, alto_celda=0.5,
                             tam=12, hexadecimal=True)
        recibido.move_to([X_CENTRO, Y_TRAMA, 0])
        nuevo = texto_paso(
            "Se entregan los 34 bytes",
            f"Juntos, en orden y al programa correcto: el del puerto {PUERTO_DESTINO}.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeOut(lineas_eventos),
                  FadeOut(VGroup(*[h[0] for h in huecos.values()])),
                  FadeOut(VGroup(*[h[2] for h in huecos.values()])),
                  ReplacementTransform(VGroup(*[datos_recibidos[s] for s, _ in SEGMENTOS]),
                                       recibido),
                  run_time=1.0)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Capa 5: la sesión sigue abierta",
            "Este mensaje no cierra el diálogo. La conexión queda abierta\n"
            "para los mensajes que vengan después.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(5), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        texto_recibido = FilaBytes(MENSAJE, ancho_celda=ANCHO_BYTE, alto_celda=0.5, tam=15)
        texto_recibido.move_to(recibido)
        nuevo = texto_paso(
            "Capa 6: bytes a texto",
            "Cada byte se lee con UTF-8: 4E es N, 6F es o, 73 es s.\n"
            "Como el mensaje no tiene acentos, cada carácter ocupa un byte.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(6), run_time=0.8)
        paso = nuevo
        self.play(LaggedStart(*[
            Transform(recibido.bytes[i][1], texto_recibido.bytes[i][1])
            for i in range(len(MENSAJE))
        ], lag_ratio=0.05), run_time=2.0)
        self.wait(tiempo_lectura(paso[1]))

        caja_chat = RoundedRectangle(width=7.0, height=1.2, corner_radius=0.1,
                                     stroke_color=COLOR_CAPA[7], stroke_width=1.5)
        caja_chat.move_to([X_CENTRO, Y_TRAMA - 1.75, 0])
        rotulo_chat = texto("Programa de chat en el servidor", tam=15, color=TEXTO_MEDIO)
        rotulo_chat.next_to(caja_chat, UP, buff=0.08).align_to(caja_chat, LEFT)
        mensaje_chat = texto(MENSAJE, tam=26).move_to(caja_chat)
        chat = VGroup(caja_chat, rotulo_chat, mensaje_chat)
        nuevo = texto_paso(
            "Capa 7: el chat recibe el mensaje",
            "El protocolo del chat entrega el texto a la aplicación.",
        )
        self.play(cambiar_texto(paso, nuevo), *pila.activar(7), run_time=0.8)
        paso = nuevo
        self.play(FadeIn(chat), run_time=0.8)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        original = FilaBytes(MENSAJE, ancho_celda=0.29, alto_celda=0.5, tam=20)
        final = FilaBytes(MENSAJE, ancho_celda=0.29, alto_celda=0.5, tam=20)
        original.move_to([X_CENTRO, 1.35, 0])
        final.move_to([X_CENTRO, -0.15, 0])
        rotulo_original = texto("Enviado por PC A", tam=16, color=TEXTO_MEDIO)
        rotulo_original.next_to(original, UP, buff=0.12).align_to(original, LEFT)
        rotulo_final = texto("Recibido en el servidor", tam=16, color=TEXTO_MEDIO)
        rotulo_final.next_to(final, DOWN, buff=0.12).align_to(final, LEFT)
        iguales = VGroup(*[
            mono("=", tam=16, color=VERDE).move_to(
                [original.bytes[i].get_x(), (original.get_bottom()[1] + final.get_top()[1]) / 2, 0])
            for i in range(len(MENSAJE))
        ])

        nuevo = texto_paso(
            "Comparación con el original",
            "Los 34 caracteres son iguales y están en el mismo orden.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeOut(chat), FadeOut(panel),
                  ReplacementTransform(recibido, final), run_time=0.8)
        self.play(FadeIn(original), FadeIn(rotulo_original), FadeIn(rotulo_final),
                  run_time=0.6)
        paso = nuevo
        self.play(LaggedStart(*[FadeIn(m) for m in iguales], lag_ratio=0.08), run_time=2.5)
        resultado = texto("34 de 34 iguales", tam=20, color=VERDE)
        resultado.next_to(rotulo_final, RIGHT, buff=0.5)
        self.play(FadeIn(resultado), run_time=0.5)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        usos = [
            (2, "FCS", "detectar errores en la trama (servidor y router)"),
            (2, "MAC destino", "aceptar la trama en cada tramo"),
            (2, "EtherType", "entregar el contenido a IPv4"),
            (3, "IP destino", "elegir la ruta en el router y aceptar el paquete"),
            (3, "TTL", "el router lo bajó de 64 a 63"),
            (3, "Protocolo", "entregar el segmento a TCP"),
            (4, "Checksum TCP", "verificar cada segmento"),
            (4, "Número de secuencia", "detectar el hueco y ordenar"),
            (4, "Puertos", "entregar los datos al chat"),
        ]
        filas = [[texto("Se agregó al enviar", tam=16, color=TEXTO_MEDIO),
                  texto("Se usó para", tam=16, color=TEXTO_MEDIO)]]
        for capa, campo_nombre, uso in usos:
            filas.append([texto(f"{campo_nombre} (capa {capa})", tam=17, color=COLOR_CAPA[capa]),
                          texto(uso, tam=17)])
        tabla_usos, _ = tabla_texto(filas, x_izquierda=X_ZONA_PRINCIPAL + 0.1,
                                    y_arriba=3.6, alto_fila=0.44, separacion=0.6)

        nuevo = texto_paso(
            "Cada dato de control se usó",
            "Todo lo que se agregó al bajar por la pila de PC A\n"
            "alguien lo leyó en el camino o al subir por la pila del servidor.",
        )
        self.play(FadeOut(VGroup(original, final, rotulo_original, rotulo_final,
                                 iguales, resultado)), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(tabla_usos), FadeIn(nuevo), *pila.activar(None), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]) + 8)
