import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

NARANJA = COLOR_CAPA[2]
AMARILLO = COLOR_CAPA[3]
VERDE = COLOR_CAPA[4]

ALTO = 0.5
ANCHO_MAC = 2.35
ANCHO_ETHERTYPE = 1.2
ANCHO_IP = 0.75
ANCHO_TCP = 0.75
ANCHO_DATOS = 1.5
ANCHO_FCS = 1.15
X_INICIO = -3.6
X_PAQUETE = X_INICIO + 2 * ANCHO_MAC + ANCHO_ETHERTYPE
Y_FILAS = [0.95, 0.05, -0.85]

Y_EQUIPOS = 1.0
Y_BUS = 0.0
Y_PREGUNTA = -0.75
Y_RESPUESTA = -1.65
X_PC_A, X_OTRO, X_ROUTER = -2.4, 1.5, 5.3


def bloque(etiqueta, ancho, color, relleno=0.22):
    caja = Rectangle(width=ancho, height=ALTO, stroke_color=color,
                     stroke_width=1.5, fill_color=color, fill_opacity=relleno)
    return VGroup(caja, texto(etiqueta, tam=16).move_to(caja))


def equipo_lan(nombre, ip, x):
    caja = RoundedRectangle(width=2.0, height=0.95, corner_radius=0.08,
                            stroke_color=TEXTO_TENUE, stroke_width=1.5)
    caja.move_to([x, Y_EQUIPOS, 0])
    lineas = VGroup(texto(nombre, tam=18))
    if ip:
        lineas.add(mono(ip, tam=14, color=TEXTO_MEDIO))
    lineas.arrange(DOWN, buff=0.08).move_to(caja)
    bajada = Line(caja.get_bottom(), [x, Y_BUS, 0],
                  color=TEXTO_TENUE, stroke_width=1.5)
    return VGroup(caja, lineas, bajada)


def mensaje(lineas, color=NARANJA):
    contenido = VGroup(*[mono(l, tam=14) for l in lineas])
    contenido.arrange(DOWN, buff=0.08)
    caja = SurroundingRectangle(contenido, buff=0.14, color=color,
                                stroke_width=1.5, fill_color=color,
                                fill_opacity=0.18)
    return VGroup(caja, contenido)


class EscenaEnlace(Scene):
    def construct(self):
        pila = PilaCapas(activa=3)
        self.add(pila)
        panel = panel_capa(
            2,
            agrega="MAC destino, MAC origen, EtherType y FCS al final",
            para_que="llevar la trama al siguiente equipo dentro de la misma red",
        )
        self.play(*pila.activar(2), FadeIn(panel), run_time=0.8)

        paquetes = VGroup()
        for y in Y_FILAS:
            ip = bloque("IP", ANCHO_IP, AMARILLO)
            ip.move_to([X_PAQUETE, y, 0], aligned_edge=LEFT)
            tcp = bloque("TCP", ANCHO_TCP, VERDE).next_to(ip, RIGHT, buff=0)
            datos = bloque("datos", ANCHO_DATOS, BORDE_DATOS, relleno=0)
            datos[0].set_fill(CAJA_DATOS, opacity=1)
            datos[1].set_color(TEXTO_MEDIO)
            datos.next_to(tcp, RIGHT, buff=0)
            paquetes.add(VGroup(ip, tcp, datos))

        paso = texto_paso(
            "Llegan los tres paquetes",
            "La capa 2 pone un encabezado adelante y un cierre atrás.\n"
            "Lo de adentro (IP, TCP y datos) no se toca.",
        )
        self.play(FadeIn(paquetes), FadeIn(paso), run_time=0.8)
        self.wait(tiempo_lectura(paso[1]))

        def columna(valor, ancho, x_izq):
            return VGroup(*[
                campo(valor, ancho, NARANJA, tam=14)
                .move_to([x_izq, y, 0], aligned_edge=LEFT)
                for y in Y_FILAS
            ])

        def nombre_columna(nombre, col):
            return texto(nombre, tam=16, color=TEXTO_MEDIO).move_to(
                [col.get_x(), Y_FILAS[0] + ALTO / 2 + 0.12, 0], aligned_edge=DOWN)

        col_mac_dst = columna(MAC_ROUTER_A, ANCHO_MAC, X_INICIO)
        col_mac_src = columna(MAC_PC_A, ANCHO_MAC, X_INICIO + ANCHO_MAC)
        col_ethertype = columna(ETHERTYPE_IPV4, ANCHO_ETHERTYPE, X_INICIO + 2 * ANCHO_MAC)
        col_fcs = columna("CRC-32", ANCHO_FCS, paquetes[0].get_right()[0])
        nombres = VGroup(
            nombre_columna("MAC destino", col_mac_dst),
            nombre_columna("MAC origen", col_mac_src),
            nombre_columna("EtherType", col_ethertype),
            nombre_columna("FCS", col_fcs),
        )

        nuevo = texto_paso(
            "MAC de origen y de destino",
            f"Origen: {MAC_PC_A}, la tarjeta de red de PC A.\n"
            f"Destino: {MAC_ROUTER_A}, la del router. No la del servidor.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeIn(nombres[0]), FadeIn(nombres[1]),
                  FadeIn(col_mac_dst, shift=RIGHT * 0.2),
                  FadeIn(col_mac_src, shift=RIGHT * 0.2), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Por qué la MAC del router",
            "Una MAC solo sirve dentro de la red local. El servidor está en otra red,\n"
            "así que la trama va al router, que es el siguiente salto.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  estilo_columna(col_mac_src, atenuada=True), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "EtherType",
            f"{ETHERTYPE_IPV4} indica que adentro va un paquete IPv4.\n"
            "Así quien recibe sabe a qué protocolo de la capa 3 entregarlo.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  estilo_columna(col_mac_dst, atenuada=True),
                  FadeIn(nombres[2]), FadeIn(col_ethertype, shift=RIGHT * 0.2),
                  run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "FCS",
            "Son 4 bytes al final: un CRC-32 calculado sobre todo lo anterior.\n"
            "El receptor lo recalcula y, si no coincide, descarta la trama.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  estilo_columna(col_ethertype, atenuada=True),
                  FadeIn(nombres[3]), FadeIn(col_fcs, shift=LEFT * 0.2),
                  run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        encabezado = VGroup(col_mac_dst, col_mac_src, col_ethertype)
        llave_enc = Brace(encabezado, DOWN, buff=0.12, color=NARANJA)
        texto_enc = texto("Encabezado Ethernet", tam=18, color=NARANJA)
        texto_enc.next_to(llave_enc, DOWN, buff=0.08)
        llave_paq = Brace(paquetes, DOWN, buff=0.12, color=AMARILLO)
        texto_paq = texto("Paquete", tam=18, color=AMARILLO)
        texto_paq.next_to(llave_paq, DOWN, buff=0.08)
        llave_fcs = Brace(col_fcs, DOWN, buff=0.12, color=NARANJA)
        texto_fcs = texto("FCS", tam=18, color=NARANJA)
        texto_fcs.next_to(llave_fcs, DOWN, buff=0.08)

        nuevo = texto_paso(
            "Encabezado + paquete + FCS = trama",
            "El encabezado Ethernet mide 14 bytes y el FCS 4.\n"
            "Las tres tramas tienen las mismas MAC; cambia lo que llevan adentro.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  *[estilo_columna(c, atenuada=False)
                    for c in (col_mac_dst, col_mac_src, col_ethertype)],
                  GrowFromCenter(llave_enc), FadeIn(texto_enc),
                  GrowFromCenter(llave_paq), FadeIn(texto_paq),
                  GrowFromCenter(llave_fcs), FadeIn(texto_fcs), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        tramas = VGroup(encabezado, paquetes, col_fcs, nombres, llave_enc,
                        texto_enc, llave_paq, texto_paq, llave_fcs, texto_fcs)

        pc_a = equipo_lan("PC A", IP_PC_A, X_PC_A)
        otro = equipo_lan("Otro equipo", "", X_OTRO)
        router = equipo_lan("Router", IP_ROUTER_A, X_ROUTER)
        bus = Line([X_PC_A - 1.0, Y_BUS, 0], [X_ROUTER + 1.0, Y_BUS, 0],
                   color=TEXTO_TENUE, stroke_width=1.5)
        nombre_red = mono(RED_PC_A, tam=14, color=TEXTO_TENUE)
        nombre_red.next_to(bus, UP, buff=0.1).set_x((X_PC_A + X_OTRO) / 2)
        red_local = VGroup(bus, nombre_red, pc_a, otro, router)

        nuevo = texto_paso(
            "ARP: averiguar la MAC del router",
            f"PC A sabe la IP del router ({IP_ROUTER_A}) pero no su MAC.\n"
            "Si no la tiene guardada, pregunta.",
        )
        self.play(FadeOut(tramas), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(red_local), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        pregunta = mensaje(["¿Quién tiene", f"{IP_ROUTER_A}?"])
        pregunta.move_to([X_PC_A, Y_PREGUNTA, 0])
        copia = pregunta.copy()
        nuevo = texto_paso(
            "Pregunta a todos (broadcast)",
            f"La trama va a {MAC_BROADCAST}: la reciben todos\n"
            "los equipos de la red local. Solo responde el que tiene esa IP.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(pregunta), run_time=0.6)
        self.add(copia)
        paso = nuevo
        self.play(pregunta.animate.set_x(X_ROUTER),
                  copia.animate.set_x(X_OTRO), run_time=1.6)
        revisar_encuadre(self)
        self.play(FadeOut(copia), run_time=0.6)
        self.wait(max(tiempo_lectura(paso[1]) - 2.2, 1))

        respuesta = mensaje([f"{IP_ROUTER_A} está en", MAC_ROUTER_A])
        respuesta.move_to([X_ROUTER, Y_RESPUESTA, 0])
        respuesta.set_x(min(X_ROUTER, X_ZONA_DERECHA - respuesta.width / 2))
        nuevo = texto_paso(
            "Respuesta directa",
            "El router responde solo a PC A, con su MAC de origen.\n"
            "PC A la guarda un tiempo para no preguntar en cada trama.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeOut(pregunta),
                  FadeIn(respuesta), run_time=0.6)
        paso = nuevo
        self.play(respuesta.animate.set_x(X_PC_A), run_time=1.6)
        revisar_encuadre(self)
        self.wait(max(tiempo_lectura(paso[1]) - 1.6, 1))
