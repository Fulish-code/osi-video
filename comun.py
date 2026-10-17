import struct

from manim import *

FUENTE = "DejaVu Sans"
FUENTE_MONO = "DejaVu Sans Mono"

FONDO = "#1E1F22"
TEXTO = "#E4E4E4"
TEXTO_MEDIO = "#B4B7BD"
TEXTO_TENUE = "#6E727A"
CAJA_DATOS = "#34373C"
BORDE_DATOS = "#4C5058"

COLOR_CAPA = {
    7: "#5B84B1",
    6: "#8E7CC3",
    5: "#4E9FA0",
    4: "#6BA368",
    3: "#CDB45A",
    2: "#CC8650",
    1: "#BC5F58",
}

NOMBRE_CAPA = {
    7: "Aplicación",
    6: "Presentación",
    5: "Sesión",
    4: "Transporte",
    3: "Red",
    2: "Enlace",
    1: "Física",
}

PDU_CAPA = {7: "datos", 6: "datos", 5: "datos", 4: "segmento",
            3: "paquete", 2: "trama", 1: "bits"}

config.background_color = FONDO

MENSAJE = "Nos vemos a las 5 en la biblioteca"

IP_PC_A = "192.168.1.10"
MAC_PC_A = "3C:52:82:A1:10:0A"
IP_ROUTER_A = "192.168.1.1"
MAC_ROUTER_A = "3C:52:82:B2:00:01"
MAC_ROUTER_B = "3C:52:82:B2:00:02"
IP_SERVIDOR = "203.0.113.20"
MAC_SERVIDOR = "3C:52:82:C3:20:14"

PUERTO_ORIGEN = 50432
PUERTO_DESTINO = 5000
TTL_INICIAL = 64
PROTOCOLO_TCP = 6
RED_PC_A = "192.168.1.0/24"
RED_SERVIDOR = "203.0.113.0/24"
CHAT_TIPO = "MSG"
CHAT_LARGO = len(MENSAJE)
ETHERTYPE_IPV4 = "0x0800"
MAC_BROADCAST = "FF:FF:FF:FF:FF:FF"
PUERTO_SWITCH_PC_A = 1
PUERTO_SWITCH_ROUTER = 2

TAM_MAX_SEGMENTO = 12
ACK_PC_A = 0
VENTANA = 64240
FLAGS_PSH_ACK = 0x18

SEGMENTOS = [
    (inicio, MENSAJE[inicio:inicio + TAM_MAX_SEGMENTO])
    for inicio in range(0, len(MENSAJE), TAM_MAX_SEGMENTO)
]


def checksum_tcp(secuencia, datos):

    datos = datos.encode("utf-8")
    encabezado = struct.pack(
        "!HHIIHHHH",
        PUERTO_ORIGEN, PUERTO_DESTINO,
        secuencia, ACK_PC_A,
        (5 << 12) | FLAGS_PSH_ACK,
        VENTANA,
        0,
        0,
    )
    pseudo = (
        bytes(int(x) for x in IP_PC_A.split("."))
        + bytes(int(x) for x in IP_SERVIDOR.split("."))
        + struct.pack("!BBH", 0, 6, len(encabezado) + len(datos))
    )
    todo = pseudo + encabezado + datos
    if len(todo) % 2:
        todo += b"\0"
    suma = sum(struct.unpack(f"!{len(todo) // 2}H", todo))
    while suma >> 16:
        suma = (suma & 0xFFFF) + (suma >> 16)
    return (~suma) & 0xFFFF


def checksum_udp(datos):
    datos = datos.encode("utf-8")
    largo = 8 + len(datos)
    encabezado = struct.pack("!HHHH", PUERTO_ORIGEN, PUERTO_DESTINO, largo, 0)
    pseudo = (
        bytes(int(x) for x in IP_PC_A.split("."))
        + bytes(int(x) for x in IP_SERVIDOR.split("."))
        + struct.pack("!BBH", 0, 17, largo)
    )
    todo = pseudo + encabezado + datos
    if len(todo) % 2:
        todo += b"\0"
    suma = sum(struct.unpack(f"!{len(todo) // 2}H", todo))
    while suma >> 16:
        suma = (suma & 0xFFFF) + (suma >> 16)
    return (~suma) & 0xFFFF


X_ZONA_PRINCIPAL = -3.9
X_ZONA_DERECHA = 6.8
Y_PANEL = 3.65
Y_TEXTO_PASO = -2.55


def texto(contenido, tam=24, color=TEXTO, **kwargs):
    return Text(contenido, font=FUENTE, font_size=tam, color=color, **kwargs)


def mono(contenido, tam=22, color=TEXTO, **kwargs):
    return Text(contenido, font=FUENTE_MONO, font_size=tam, color=color, **kwargs)


PALABRAS_POR_SEGUNDO = 2.8


def tiempo_lectura(*textos):
    textos = [getattr(t, "original_text", t) for t in textos]
    palabras = sum(len(t.split()) for t in textos)
    return max(3, palabras / PALABRAS_POR_SEGUNDO)


class PilaCapas(VGroup):

    ANCHO = 2.6
    ALTO_FILA = 0.66
    SEPARACION = 0.12

    def __init__(self, activa=None):
        super().__init__()
        self.filas = {}
        for n in range(7, 0, -1):
            caja = Rectangle(width=self.ANCHO, height=self.ALTO_FILA,
                             stroke_width=1.5)
            franja = Rectangle(width=0.14, height=self.ALTO_FILA,
                               stroke_width=0, fill_opacity=1)
            franja.align_to(caja, LEFT)
            numero = mono(str(n), tam=22)
            numero.next_to(franja, RIGHT, buff=0.2)
            nombre = texto(NOMBRE_CAPA[n], tam=21)
            nombre.next_to(numero, RIGHT, buff=0.2)
            fila = VGroup(caja, franja, numero, nombre)
            self.filas[n] = fila
            self.add(fila)
        self.arrange(DOWN, buff=self.SEPARACION)
        self.to_edge(LEFT, buff=0.3)
        activas = self._conjunto(activa)
        for n, fila in self.filas.items():
            self._estilo(fila, n, activa=(n in activas))

    @staticmethod
    def _conjunto(activa):
        if activa is None:
            return set()
        if isinstance(activa, int):
            return {activa}
        return set(activa)

    @staticmethod
    def _estilo(fila, n, activa):
        caja, franja, numero, nombre = fila
        color = COLOR_CAPA[n]
        if activa:
            caja.set_stroke(color, opacity=1)
            caja.set_fill(color, opacity=0.28)
            franja.set_fill(color, opacity=1)
            numero.set_color(TEXTO)
            nombre.set_color(TEXTO)
        else:
            caja.set_stroke(color, opacity=0.3)
            caja.set_fill(color, opacity=0.06)
            franja.set_fill(color, opacity=0.35)
            numero.set_color(TEXTO_TENUE)
            nombre.set_color(TEXTO_TENUE)

    def activar(self, activa):
        activas = self._conjunto(activa)
        animaciones = []
        for n, fila in self.filas.items():
            fila.generate_target()
            self._estilo(fila.target, n, activa=(n in activas))
            animaciones.append(MoveToTarget(fila))
        return animaciones


def panel_capa(n, agrega, para_que):
    return panel_libre(
        f"Capa {n} · {NOMBRE_CAPA[n]}",
        [f"PDU: {PDU_CAPA[n]}", f"Agrega: {agrega}", f"Para qué: {para_que}"],
        COLOR_CAPA[n],
    )


def panel_libre(titulo, lineas, color):
    filas = VGroup(texto(titulo, tam=30))
    for linea in lineas:
        filas.add(texto(linea, tam=19, color=TEXTO_MEDIO))
    filas.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    barra = Line(filas.get_corner(UL), filas.get_corner(DL),
                 color=color, stroke_width=4)
    barra.shift(LEFT * 0.2)
    panel = VGroup(barra, filas)
    panel.move_to([X_ZONA_PRINCIPAL + 0.2, Y_PANEL, 0], aligned_edge=UL)
    if panel.get_right()[0] > X_ZONA_DERECHA:
        print(f"[encuadre] panel demasiado ancho: {titulo!r}")
    panel.zona_fija = f"panel {titulo!r}"
    return panel


def texto_paso(titulo, descripcion="", x_izquierda=X_ZONA_PRINCIPAL):
    t = texto(titulo, tam=28)
    grupo = VGroup(t)
    if descripcion:
        d = texto(descripcion, tam=21, color=TEXTO_MEDIO, line_spacing=0.9)
        grupo.add(d)
    grupo.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    grupo.move_to([x_izquierda, Y_TEXTO_PASO, 0], aligned_edge=UL)
    if grupo.get_right()[0] > X_ZONA_DERECHA:
        print(f"[encuadre] texto demasiado ancho: {titulo!r}")
    grupo.zona_fija = f"texto {titulo!r}"
    return grupo


ESPACIO_VISIBLE = "·"


class FilaBytes(VGroup):

    def __init__(self, contenido, ancho_celda=0.3, alto_celda=0.5, tam=22,
                 hexadecimal=False):
        super().__init__()
        if hexadecimal:
            glifos = VGroup(*[
                mono(f"{ord(c):02X}", tam=tam,
                     color=TEXTO_TENUE if c == " " else TEXTO)
                for c in contenido
            ])
        else:
            visible = contenido.replace(" ", ESPACIO_VISIBLE)
            glifos = mono(visible, tam=tam)
            assert len(glifos) == len(contenido), "un glifo por carácter"
            glifos.move_to(ORIGIN)

        self.bytes = VGroup()
        for i, (caracter, glifo) in enumerate(zip(contenido, glifos)):
            celda = Rectangle(width=ancho_celda, height=alto_celda,
                              stroke_color=BORDE_DATOS, stroke_width=1,
                              fill_color=CAJA_DATOS, fill_opacity=1)
            celda.move_to(RIGHT * i * ancho_celda)
            if hexadecimal:
                glifo.move_to(celda)
            else:
                glifo.set_x(celda.get_x())
            if caracter == " ":
                glifo.set_color(TEXTO_TENUE)
            self.bytes.add(VGroup(celda, glifo))
        self.add(self.bytes)
        self.move_to(ORIGIN)


def revisar_encuadre(escena, margen=0.15):
    ancho = config.frame_width / 2 - margen
    alto = config.frame_height / 2 - margen
    hay_pila = any(isinstance(m, PilaCapas) for m in escena.mobjects)
    for m in escena.mobjects:
        for fijo in escena.mobjects:
            if fijo is m or not hasattr(fijo, "zona_fija") or hasattr(m, "zona_fija") \
                    or isinstance(m, PilaCapas):
                continue
            se_cruzan = (m.get_left()[0] < fijo.get_right()[0] and m.get_right()[0] > fijo.get_left()[0]
                         and m.get_bottom()[1] < fijo.get_top()[1] and m.get_top()[1] > fijo.get_bottom()[1])
            if se_cruzan and m.width > 0 and m.height > 0:
                print(f"[encuadre] se cruza con {fijo.zona_fija}: {type(m).__name__} "
                      f"y=({m.get_bottom()[1]:.2f}, {m.get_top()[1]:.2f})")
        if hay_pila and not isinstance(m, PilaCapas) \
                and m.get_left()[0] < X_ZONA_PRINCIPAL - 0.1:
            print(f"[encuadre] invade la pila: {type(m).__name__} "
                  f"x=({m.get_left()[0]:.2f}, {m.get_right()[0]:.2f})")
        if m.get_left()[0] < -ancho or m.get_right()[0] > ancho \
                or m.get_bottom()[1] < -alto or m.get_top()[1] > alto:
            print(f"[encuadre] fuera de plano: {type(m).__name__} "
                  f"x=({m.get_left()[0]:.2f}, {m.get_right()[0]:.2f}) "
                  f"y=({m.get_bottom()[1]:.2f}, {m.get_top()[1]:.2f})")


def cambiar_texto(viejo, nuevo):
    return Succession(FadeOut(viejo), FadeIn(nuevo))


def campo(valor, ancho, color, tam=22, alto=0.5):
    caja = Rectangle(width=ancho, height=alto, stroke_color=color,
                     stroke_width=1.5, fill_color=color, fill_opacity=0.22)
    valor = mono(valor, tam=tam).move_to(caja)
    return VGroup(caja, valor)


def estilo_columna(columna, atenuada):
    columna.generate_target()
    for caja, valor in columna.target:
        caja.set_stroke(opacity=0.35 if atenuada else 1)
        caja.set_fill(opacity=0.08 if atenuada else 0.22)
        valor.set_opacity(0.35 if atenuada else 1)
    return MoveToTarget(columna)


def tabla_texto(filas, x_izquierda, y_arriba, alto_fila=0.5, separacion=0.45,
                x_derecha=None):

    columnas = len(filas[0])
    x_col = [x_izquierda]
    for c in range(columnas - 1):
        x_col.append(x_col[c] + max(f[c].width for f in filas) + separacion)
    if x_derecha is None:
        x_derecha = x_col[-1] + max(f[-1].width for f in filas)

    tabla = VGroup()
    lineas = []
    for i, fila in enumerate(filas):
        y = y_arriba - alto_fila * (i + 0.5)
        for objeto, x in zip(fila, x_col):
            objeto.move_to([x, y, 0], aligned_edge=LEFT)
        grupo = VGroup(*fila)
        lineas.append(grupo)
        tabla.add(grupo)
        if i > 0:
            tabla.add(Line([x_izquierda, y + alto_fila / 2, 0],
                           [x_derecha, y + alto_fila / 2, 0],
                           color=BORDE_DATOS, stroke_width=1))
    return tabla, lineas


def tira(bloques, alto=0.5, tam=16):
    grupo = VGroup()
    for etiqueta, ancho, color in bloques:
        if color is None:
            caja = Rectangle(width=ancho, height=alto, stroke_color=BORDE_DATOS,
                             stroke_width=1, fill_color=CAJA_DATOS, fill_opacity=1)
            letra = texto(etiqueta, tam=tam, color=TEXTO_MEDIO)
        else:
            caja = Rectangle(width=ancho, height=alto, stroke_color=color,
                             stroke_width=1.5, fill_color=color, fill_opacity=0.22)
            letra = texto(etiqueta, tam=tam)
        grupo.add(VGroup(caja, letra.move_to(caja)))
    grupo.arrange(RIGHT, buff=0)
    return grupo


def trama_compacta(alto=0.5, tam=16, escala=1.0):
    return tira([
        ("Ethernet", 1.6 * escala, COLOR_CAPA[2]),
        ("IP", 0.8 * escala, COLOR_CAPA[3]),
        ("TCP", 0.8 * escala, COLOR_CAPA[4]),
        ("datos", 1.4 * escala, None),
        ("FCS", 0.8 * escala, COLOR_CAPA[2]),
    ], alto=alto, tam=tam)
