import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

VERDE = COLOR_CAPA[4]

ANCHO_CELDA = 0.3
ALTO = 0.5
CAMPOS = [
    ("Puerto\norigen", 1.55),
    ("Puerto\ndestino", 1.55),
    ("Número de\nsecuencia", 1.4),
    ("Checksum", 1.55),
]
X_ENCABEZADO = -3.6
X_DATOS = X_ENCABEZADO + sum(a for _, a in CAMPOS) + 0.3
Y_FILAS = [0.95, 0.05, -0.85]


class EscenaTransporte(Scene):
    def construct(self):
        pila = PilaCapas(activa=5)
        self.add(pila)
        panel = panel_capa(
            4,
            agrega="puertos, número de secuencia y checksum",
            para_que="datos completos, en orden y al programa correcto",
        )
        self.play(*pila.activar(4), FadeIn(panel), run_time=0.8)

        fila = FilaBytes(MENSAJE, ancho_celda=ANCHO_CELDA, alto_celda=ALTO)
        centro_x = (X_ZONA_PRINCIPAL + X_ZONA_DERECHA) / 2
        fila.move_to([centro_x, 0.3, 0])
        llave_total = Brace(fila, DOWN, buff=0.12, color=TEXTO_TENUE)
        etiqueta_total = texto("34 bytes", tam=20, color=TEXTO_MEDIO)
        etiqueta_total.next_to(llave_total, DOWN, buff=0.1)

        paso = texto_paso(
            "Los 34 bytes del mensaje",
            "Llegan así desde las capas de arriba. Cada caja es un byte.\n"
            "Los espacios también cuentan; se marcan con un punto tenue.",
        )
        self.play(FadeIn(fila), FadeIn(paso), run_time=0.8)
        self.play(GrowFromCenter(llave_total), FadeIn(etiqueta_total), run_time=0.6)
        self.wait(tiempo_lectura(paso[1]))

        etiqueta_max = Paragraph("Máx. didáctico", "12 bytes", font=FUENTE, font_size=17,
                                 color=TEXTO_MEDIO, alignment="center", line_spacing=0.8)
        marco_max = SurroundingRectangle(etiqueta_max, buff=0.12,
                                         color=TEXTO_TENUE, stroke_width=1)
        aviso_max = VGroup(marco_max, etiqueta_max)
        aviso_max.move_to([X_ZONA_DERECHA, Y_PANEL, 0], aligned_edge=UR)

        nuevo = texto_paso(
            "Tamaño máximo didáctico: 12 bytes",
            "En la práctica el máximo suele ser de 1460 bytes por segmento.\n"
            "Aquí usamos 12 para que se vea la división.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(aviso_max), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        trozos = [VGroup(*fila.bytes[i:i + TAM_MAX_SEGMENTO])
                  for i, _ in SEGMENTOS]

        cortes = VGroup(*[
            DashedLine(UP * 0.45, DOWN * 0.45, color=VERDE, stroke_width=2)
            .move_to(fila.bytes[i].get_left())
            for i, _ in SEGMENTOS[1:]
        ])
        nuevo = texto_paso(
            "Se corta cada 12 bytes",
            "12 + 12 + 10 = 34.\nEl último trozo es más corto porque ya no queda más mensaje.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeOut(llave_total), FadeOut(etiqueta_total),
                  Create(cortes), run_time=0.8)
        paso = nuevo

        self.play(FadeOut(cortes),
                  trozos[0].animate.shift(LEFT * 0.12),
                  trozos[2].animate.shift(RIGHT * 0.12), run_time=0.6)

        llaves = VGroup()
        for trozo, (inicio, contenido) in zip(trozos, SEGMENTOS):
            llave = Brace(trozo, DOWN, buff=0.12, color=TEXTO_TENUE)
            etiqueta = texto(f"{len(contenido)} bytes", tam=20, color=TEXTO_MEDIO)
            etiqueta.next_to(llave, DOWN, buff=0.1)
            posicion = texto(f"byte {inicio}", tam=16, color=TEXTO_TENUE)
            posicion.next_to(trozo[0], UP, buff=0.12).align_to(trozo[0], LEFT)
            llaves.add(VGroup(llave, etiqueta, posicion))
        self.play(LaggedStart(*[FadeIn(l) for l in llaves], lag_ratio=0.3),
                  run_time=1.0)
        self.wait(tiempo_lectura(paso[1]))

        self.play(FadeOut(llaves), run_time=0.4)
        self.play(*[
            trozo.animate.move_to([X_DATOS, y, 0], aligned_edge=LEFT)
            for trozo, y in zip(trozos, Y_FILAS)
        ], run_time=1.0)

        x = X_ENCABEZADO
        posiciones_x = []
        for _, ancho in CAMPOS:
            posiciones_x.append(x + ancho / 2)
            x += ancho
        nombres = VGroup()
        for (nombre, _), cx in zip(CAMPOS, posiciones_x):
            n = Paragraph(*nombre.split("\n"), font=FUENTE, font_size=16,
                          color=TEXTO_MEDIO, alignment="center", line_spacing=0.8)
            n.move_to([cx, Y_FILAS[0] + ALTO / 2 + 0.12, 0], aligned_edge=DOWN)
            nombres.add(n)
        nombre_datos = texto("Datos", tam=16, color=TEXTO_MEDIO)
        nombre_datos.move_to([X_DATOS, nombres[0].get_bottom()[1], 0],
                             aligned_edge=DL)

        valores = [
            [str(PUERTO_ORIGEN)] * 3,
            [str(PUERTO_DESTINO)] * 3,
            [str(inicio) for inicio, _ in SEGMENTOS],
            [f"0x{checksum_tcp(i, c):04X}" for i, c in SEGMENTOS],
        ]
        columnas = []
        for c, ((_, ancho), cx) in enumerate(zip(CAMPOS, posiciones_x)):
            col = VGroup(*[
                campo(valores[c][f], ancho, VERDE).move_to([cx, y, 0])
                for f, y in enumerate(Y_FILAS)
            ])
            columnas.append(col)

        nuevo = texto_paso(
            "Puertos",
            f"{PUERTO_ORIGEN}: el chat en PC A, puerto efímero que asigna el sistema.\n"
            f"{PUERTO_DESTINO}: el servicio de chat. Indican a qué programa van los datos.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(nombre_datos),
                  FadeIn(nombres[0]), FadeIn(nombres[1]),
                  FadeIn(columnas[0], shift=RIGHT * 0.2),
                  FadeIn(columnas[1], shift=RIGHT * 0.2), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Número de secuencia",
            "Es la posición del primer byte del segmento dentro del mensaje.\n"
            "Con él, el receptor los pone en orden aunque lleguen mezclados.",
        )
        primeros = VGroup(*[
            SurroundingRectangle(t[0], buff=0, color=VERDE, stroke_width=3)
            for t in trozos
        ])
        self.play(cambiar_texto(paso, nuevo),
                  FadeIn(nombres[2]), FadeIn(columnas[2], shift=RIGHT * 0.2),
                  estilo_columna(columnas[0], atenuada=True),
                  estilo_columna(columnas[1], atenuada=True),
                  FadeIn(primeros), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Simplificación",
            "En TCP real el primer número de secuencia es aleatorio.\n"
            "Aquí empieza en 0 para que coincida con la posición del byte.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Checksum",
            "Se calcula con el encabezado y los datos. El receptor lo recalcula\n"
            "y, si no coincide, descarta el segmento porque se corrompió.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeIn(nombres[3]), FadeIn(columnas[3], shift=RIGHT * 0.2),
                  estilo_columna(columnas[2], atenuada=True),
                  FadeOut(primeros), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        encabezados = VGroup(*columnas)
        llave_enc = Brace(encabezados, DOWN, buff=0.12, color=VERDE)
        texto_enc = texto("Encabezado TCP", tam=18, color=VERDE)
        texto_enc.next_to(llave_enc, DOWN, buff=0.08)
        llave_datos = Brace(VGroup(*trozos), DOWN, buff=0.12, color=TEXTO_TENUE)
        texto_datos = texto("Datos", tam=18, color=TEXTO_MEDIO)
        texto_datos.next_to(llave_datos, DOWN, buff=0.08)

        nuevo = texto_paso(
            "Encabezado + datos = segmento",
            "El encabezado TCP real mide 20 bytes como mínimo y tiene más campos\n"
            "(número de ACK, flags, ventana). Aquí solo los que usa este video.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  *[estilo_columna(col, atenuada=False) for col in columnas],
                  GrowFromCenter(llave_enc), FadeIn(texto_enc),
                  GrowFromCenter(llave_datos), FadeIn(texto_datos), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        segmentos = VGroup(encabezados, *trozos, nombres, nombre_datos,
                           llave_enc, texto_enc, llave_datos, texto_datos)

        filas_tabla = [
            ("Orden", "Reordena por número de secuencia", "En el orden en que llega"),
            ("Pérdidas", "Detecta lo que falta y lo reenvía", "No lo detecta ni lo reenvía"),
            ("Conexión", "La abre antes de enviar datos", "Envía directamente"),
            ("Encabezado", "20 bytes como mínimo", "8 bytes"),
        ]
        celdas = [
            [texto(tema, tam=18, color=TEXTO_MEDIO), texto(tcp, tam=18), texto(udp, tam=18)]
            for tema, tcp, udp in filas_tabla
        ]
        separacion = 0.45
        x_col = [X_ZONA_PRINCIPAL + 0.1]
        for c in range(2):
            x_col.append(x_col[c] + max(f[c].width for f in celdas) + separacion)
        y_tabla = 1.75
        tabla = VGroup()
        tabla.add(texto("TCP", tam=24, color=VERDE).move_to([x_col[1], y_tabla, 0], aligned_edge=LEFT))
        tabla.add(texto("UDP", tam=24, color=VERDE).move_to([x_col[2], y_tabla, 0], aligned_edge=LEFT))
        for i, fila_celdas in enumerate(celdas):
            y = y_tabla - 0.75 * (i + 1)
            for celda, x in zip(fila_celdas, x_col):
                tabla.add(celda.move_to([x, y, 0], aligned_edge=LEFT))
            linea = Line([x_col[0], y + 0.375, 0], [X_ZONA_DERECHA, y + 0.375, 0],
                         color=BORDE_DATOS, stroke_width=1)
            tabla.add(linea)

        nuevo = texto_paso(
            "TCP y UDP",
            "Los dos trabajan en la capa 4 y usan puertos. Este chat usa TCP.\n"
            "En UDP la unidad de datos se suele llamar datagrama.",
        )
        self.play(FadeOut(segmentos), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(tabla), FadeIn(nuevo), run_time=0.6)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]) + 8)

        def equipo(nombre, x):
            caja = RoundedRectangle(width=1.5, height=3.0, corner_radius=0.08,
                                    stroke_color=TEXTO_TENUE, stroke_width=1.5)
            caja.move_to([x, -0.15, 0])
            etiqueta = texto(nombre, tam=20, color=TEXTO_MEDIO)
            etiqueta.next_to(caja, UP, buff=0.12)
            return VGroup(caja, etiqueta)

        pc_a = equipo("PC A", X_ZONA_PRINCIPAL + 0.75)
        servidor = equipo("Servidor", X_ZONA_DERECHA - 0.75)

        compactos = VGroup()
        x_bloque = pc_a[0].get_right()[0] + 0.25
        for (inicio, contenido), y in zip(SEGMENTOS, [0.75, 0.0, -0.75]):
            enc = Rectangle(width=0.5, height=0.36, stroke_color=VERDE,
                            stroke_width=1.5, fill_color=VERDE, fill_opacity=0.22)
            enc.move_to([x_bloque, y, 0], aligned_edge=LEFT)
            dat = Rectangle(width=0.06 * len(contenido), height=0.36,
                            stroke_color=BORDE_DATOS, stroke_width=1,
                            fill_color=CAJA_DATOS, fill_opacity=1)
            dat.next_to(enc, RIGHT, buff=0)
            etiqueta = mono(f"seq {inicio}", tam=15, color=TEXTO_MEDIO)
            etiqueta.next_to(enc, UP, buff=0.06).align_to(enc, LEFT)
            compactos.add(VGroup(etiqueta, enc, dat))

        nuevo = texto_paso(
            "Los tres segmentos salen hacia el servidor",
            "Cada uno viaja por separado.\nLo que pasa en el camino se ve en las capas siguientes.",
        )
        self.play(FadeOut(tabla), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(pc_a), FadeIn(servidor), FadeIn(compactos), FadeIn(nuevo),
                  run_time=0.6)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(1.0)

        distancia = servidor[0].get_left()[0] - 0.25 - compactos.get_right()[0]
        self.play(LaggedStart(*[
            c.animate.shift(RIGHT * distancia) for c in compactos
        ], lag_ratio=0.25), run_time=2.0, rate_func=smooth)
        self.wait(tiempo_lectura(paso[1]) - 2)

        caja_ack = Rectangle(width=1.6, height=0.42, stroke_color=VERDE,
                             stroke_width=1.5, fill_color=VERDE, fill_opacity=0.22)
        texto_ack = mono("ACK 34", tam=18).move_to(caja_ack)
        puertos_ack = mono(f"{PUERTO_DESTINO} → {PUERTO_ORIGEN}", tam=15,
                           color=TEXTO_MEDIO)
        puertos_ack.next_to(caja_ack, DOWN, buff=0.1)
        ack = VGroup(caja_ack, texto_ack, puertos_ack)
        ack.next_to(servidor[0], LEFT, buff=0.25).set_y(-1.2)

        nuevo = texto_paso(
            "ACK",
            "El servidor responde con el siguiente byte que espera: 34.\n"
            "Quiere decir que recibió del byte 0 al 33 sin huecos.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(ack), run_time=0.6)
        paso = nuevo
        destino_x = pc_a[0].get_right()[0] + 0.25 + ack.width / 2
        self.play(ack.animate.set_x(destino_x), run_time=1.6, rate_func=smooth)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "El flag ACK",
            "Es un bit del encabezado TCP. Indica que el número de ACK es válido.\n"
            "Se puede confirmar cada segmento o varios juntos. Aquí va uno solo.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))
