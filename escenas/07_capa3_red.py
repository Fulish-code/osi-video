import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

AMARILLO = COLOR_CAPA[3]
VERDE = COLOR_CAPA[4]

ALTO = 0.5
CAMPOS_IP = [
    ("IP origen", 2.1),
    ("IP destino", 2.1),
    ("TTL", 0.9),
    ("Protocolo", 1.4),
]
ANCHO_TCP = 1.1
ANCHO_CELDA = 0.22
X_INICIO = -3.6
X_SEGMENTO = X_INICIO + sum(a for _, a in CAMPOS_IP)
Y_FILAS = [0.95, 0.05, -0.85]

Y_MAPA = 0.5
Y_CARRIL = 1.38
X_PC_A, X_ROUTER, X_SERVIDOR = -2.9, 1.45, 5.75


def dispositivo(nombre, ip, x):
    caja = RoundedRectangle(width=1.7, height=0.8, corner_radius=0.08,
                            stroke_color=TEXTO_TENUE, stroke_width=1.5)
    caja.move_to([x, Y_MAPA, 0])
    etiqueta = texto(nombre, tam=20).move_to(caja)
    direccion = mono(ip, tam=15, color=TEXTO_MEDIO)
    direccion.next_to(caja, DOWN, buff=0.12)
    return VGroup(caja, etiqueta, direccion)


def paquete_compacto(ttl):
    ip = Rectangle(width=1.05, height=0.34, stroke_color=AMARILLO,
                   stroke_width=1.5, fill_color=AMARILLO, fill_opacity=0.22)
    tcp = Rectangle(width=0.35, height=0.34, stroke_color=VERDE,
                    stroke_width=1.5, fill_color=VERDE, fill_opacity=0.22)
    datos = Rectangle(width=0.6, height=0.34, stroke_color=BORDE_DATOS,
                      stroke_width=1, fill_color=CAJA_DATOS, fill_opacity=1)
    tcp.next_to(ip, RIGHT, buff=0)
    datos.next_to(tcp, RIGHT, buff=0)
    etiqueta_ttl = mono(f"TTL {ttl}", tam=15).move_to(ip)
    return VGroup(ip, tcp, datos, etiqueta_ttl)


class EscenaRed(Scene):
    def construct(self):
        pila = PilaCapas(activa=4)
        self.add(pila)
        panel = panel_capa(
            3,
            agrega="IP origen, IP destino, TTL y protocolo",
            para_que="llevar el paquete de un equipo a otro, aunque estén en otra red",
        )
        self.play(*pila.activar(3), FadeIn(panel), run_time=0.8)

        segmentos = VGroup()
        for (inicio, contenido), y in zip(SEGMENTOS, Y_FILAS):
            tcp = campo("TCP", ANCHO_TCP, VERDE, tam=18)
            tcp.move_to([X_SEGMENTO, y, 0], aligned_edge=LEFT)
            datos = FilaBytes(contenido, ancho_celda=ANCHO_CELDA,
                              alto_celda=ALTO, tam=16)
            datos.next_to(tcp, RIGHT, buff=0)
            segmentos.add(VGroup(tcp, datos))

        paso = texto_paso(
            "Llegan los tres segmentos",
            "La capa 3 toma cada segmento tal como viene de la capa 4\n"
            "y le agrega su propio encabezado adelante.",
        )
        self.play(FadeIn(segmentos), FadeIn(paso), run_time=0.8)
        self.wait(tiempo_lectura(paso[1]))

        x = X_INICIO
        centros_x = []
        for _, ancho in CAMPOS_IP:
            centros_x.append(x + ancho / 2)
            x += ancho
        nombres = VGroup(*[
            texto(nombre, tam=16, color=TEXTO_MEDIO)
            .move_to([cx, Y_FILAS[0] + ALTO / 2 + 0.12, 0], aligned_edge=DOWN)
            for (nombre, _), cx in zip(CAMPOS_IP, centros_x)
        ])
        valores = [IP_PC_A, IP_SERVIDOR, str(TTL_INICIAL), str(PROTOCOLO_TCP)]
        columnas = [
            VGroup(*[campo(valor, ancho, AMARILLO, tam=18).move_to([cx, y, 0])
                     for y in Y_FILAS])
            for valor, (_, ancho), cx in zip(valores, CAMPOS_IP, centros_x)
        ]

        nuevo = texto_paso(
            "IP de origen y de destino",
            f"{IP_PC_A} es PC A. {IP_SERVIDOR} es el servidor.\n"
            "Identifican a los equipos de los extremos, no a los programas.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  FadeIn(nombres[0]), FadeIn(nombres[1]),
                  FadeIn(columnas[0], shift=RIGHT * 0.2),
                  FadeIn(columnas[1], shift=RIGHT * 0.2), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Protocolo",
            f"Dice qué va adentro del paquete. {PROTOCOLO_TCP} es TCP (UDP sería 17).\n"
            "Con eso el servidor sabe a qué protocolo de la capa 4 entregarlo.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  estilo_columna(columnas[0], atenuada=True),
                  estilo_columna(columnas[1], atenuada=True),
                  FadeIn(nombres[3]), FadeIn(columnas[3], shift=RIGHT * 0.2),
                  run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "TTL",
            f"Empieza en {TTL_INICIAL} y baja en cada router.\n"
            "Qué pasa con él en el camino se ve en el mapa.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  estilo_columna(columnas[3], atenuada=True),
                  FadeIn(nombres[2]), FadeIn(columnas[2], shift=RIGHT * 0.2),
                  run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        encabezados = VGroup(*columnas)
        llave_ip = Brace(encabezados, DOWN, buff=0.12, color=AMARILLO)
        texto_ip = texto("Encabezado IP", tam=18, color=AMARILLO)
        texto_ip.next_to(llave_ip, DOWN, buff=0.08)
        llave_seg = Brace(segmentos, DOWN, buff=0.12, color=VERDE)
        texto_seg = texto("Segmento", tam=18, color=VERDE)
        texto_seg.next_to(llave_seg, DOWN, buff=0.08)

        nuevo = texto_paso(
            "Encabezado IP + segmento = paquete",
            "El encabezado IPv4 real mide 20 bytes como mínimo y tiene más\n"
            "campos (largo, checksum y otros). Aquí solo los que se usan.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  *[estilo_columna(col, atenuada=False) for col in columnas],
                  GrowFromCenter(llave_ip), FadeIn(texto_ip),
                  GrowFromCenter(llave_seg), FadeIn(texto_seg), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        paquetes = VGroup(encabezados, segmentos, nombres,
                          llave_ip, texto_ip, llave_seg, texto_seg)

        pc_a = dispositivo("PC A", IP_PC_A, X_PC_A)
        router = dispositivo("Router", f"{IP_ROUTER_A} (lado PC A)", X_ROUTER)
        servidor = dispositivo("Servidor", IP_SERVIDOR, X_SERVIDOR)

        enlaces = VGroup()
        for izq, der, red in [(pc_a, router, RED_PC_A), (router, servidor, RED_SERVIDOR)]:
            linea = Line(izq[0].get_right(), der[0].get_left(),
                         color=TEXTO_TENUE, stroke_width=1.5)
            nombre_red = mono(red, tam=15, color=TEXTO_TENUE)
            nombre_red.next_to(linea, UP, buff=0.12)
            enlaces.add(VGroup(linea, nombre_red))
        mapa = VGroup(enlaces, pc_a, router, servidor)

        nuevo = texto_paso(
            "PC A, router y servidor",
            "PC A y el servidor están en redes distintas.\n"
            "El router tiene una interfaz en cada una y las conecta.",
        )
        self.play(FadeOut(paquetes), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(mapa), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Simplificación: sin NAT",
            "Aquí el router une las dos redes directo. En una red de casa\n"
            "el router cambiaría la IP de origen (eso se llama NAT).",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        paquete = paquete_compacto(TTL_INICIAL)
        paquete.move_to([X_PC_A, Y_CARRIL, 0])
        nuevo = texto_paso(
            "PC A se lo entrega al router",
            f"{IP_SERVIDOR} no está en la red de PC A ({RED_PC_A}).\n"
            "Por eso va al router. Se sigue un paquete; los tres hacen lo mismo.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(paquete), run_time=0.6)
        paso = nuevo
        self.play(paquete.animate.set_x(X_ROUTER), run_time=1.5)
        self.wait(tiempo_lectura(paso[1]) - 1.5)

        ttl_nuevo = mono(f"TTL {TTL_INICIAL - 1}", tam=15, color=AMARILLO)
        ttl_nuevo.move_to(paquete[3])
        nuevo = texto_paso(
            f"TTL: {TTL_INICIAL} → {TTL_INICIAL - 1}",
            "Cada router le resta 1. Si llega a 0, el router descarta el paquete.\n"
            "Así un paquete no da vueltas para siempre si hay un error en las rutas.",
        )
        self.play(cambiar_texto(paso, nuevo),
                  Transform(paquete[3], ttl_nuevo), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        filas = [
            [texto("Red destino", tam=17, color=TEXTO_MEDIO),
             texto("Salida", tam=17, color=TEXTO_MEDIO)],
            [mono(RED_PC_A, tam=18), texto("interfaz del lado de PC A", tam=18)],
            [mono(RED_SERVIDOR, tam=18), texto("interfaz del lado del servidor", tam=18)],
        ]
        tabla, lineas = tabla_texto(filas, x_izquierda=-0.6, y_arriba=-0.4)
        titulo_tabla = texto("Tabla de rutas del router", tam=17, color=TEXTO_MEDIO)
        coincidencia = SurroundingRectangle(lineas[2], buff=0.1,
                                            color=AMARILLO, stroke_width=2)

        nuevo = texto_paso(
            "Tabla de rutas",
            f"El router busca qué red contiene a {IP_SERVIDOR}: {RED_SERVIDOR}.\n"
            "Está conectada directo, así que el siguiente salto es el servidor.",
        )
        self.play(cambiar_texto(paso, nuevo), FadeIn(tabla), run_time=0.8)
        paso = nuevo
        self.play(Create(coincidencia), run_time=0.6)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "En redes más grandes",
            "La tabla tiene muchas más rutas y el siguiente salto\n"
            "suele ser otro router. Cada uno repite lo mismo.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.play(paquete.animate.set_x(X_SERVIDOR), run_time=1.5)
        self.wait(tiempo_lectura(paso[1]) - 1.5)

        filas = [
            [texto("", tam=17),
             texto("Sale de PC A", tam=17, color=TEXTO_MEDIO),
             texto("Llega al servidor", tam=17, color=TEXTO_MEDIO)],
            [texto("IP origen", tam=18, color=TEXTO_MEDIO), mono(IP_PC_A, tam=18), mono(IP_PC_A, tam=18)],
            [texto("IP destino", tam=18, color=TEXTO_MEDIO), mono(IP_SERVIDOR, tam=18), mono(IP_SERVIDOR, tam=18)],
            [texto("TTL", tam=18, color=TEXTO_MEDIO),
             mono(str(TTL_INICIAL), tam=18, color=AMARILLO),
             mono(str(TTL_INICIAL - 1), tam=18, color=AMARILLO)],
        ]
        comparacion, _ = tabla_texto(filas, x_izquierda=-1.4, y_arriba=-0.4,
                                     alto_fila=0.45, separacion=0.7)

        nuevo = texto_paso(
            "Qué cambió y qué no",
            "Las dos IP llegan igual: identifican a los extremos del viaje.\n"
            "El TTL bajó en 1 porque el paquete pasó por un router.",
        )
        self.play(FadeOut(tabla), FadeOut(coincidencia), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(comparacion), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))
