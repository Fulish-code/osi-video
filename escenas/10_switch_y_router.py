import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

NARANJA = COLOR_CAPA[2]
AMARILLO = COLOR_CAPA[3]
VERDE = COLOR_CAPA[4]

Y_EQUIPOS = 0.8
Y_CARRIL = 1.75
X_PC_A, X_SWITCH, X_ROUTER, X_SERVIDOR = -2.8, -0.05, 2.8, 5.6
Y_DETALLE = -0.05


def equipo(nombre, alcance, x):
    caja = RoundedRectangle(width=1.6, height=0.75, corner_radius=0.08,
                            stroke_color=TEXTO_TENUE, stroke_width=1.5)
    caja.move_to([x, Y_EQUIPOS, 0])
    etiqueta = texto(nombre, tam=19).move_to(caja)
    grupo = VGroup(caja, etiqueta)
    if alcance:
        nota = texto(alcance, tam=15, color=TEXTO_TENUE)
        nota.next_to(caja, DOWN, buff=0.1)
        grupo.add(nota)
    return grupo


def trama_viaje():
    return tira([
        ("Eth", 0.5, NARANJA),
        (f"TTL {TTL_INICIAL}", 0.85, AMARILLO),
        ("TCP", 0.45, VERDE),
        ("datos", 0.65, None),
        ("FCS", 0.5, NARANJA),
    ], alto=0.36, tam=12)


def x_carril(x, objeto):
    mitad = objeto.width / 2
    return min(max(x, X_ZONA_PRINCIPAL + mitad), X_ZONA_DERECHA - mitad)


class EscenaViaje(Scene):
    def construct(self):
        pila = PilaCapas(activa=1)
        self.add(pila)
        panel = panel_libre(
            "El viaje por la red",
            ["Cada equipo abre la trama solo hasta la capa que necesita.",
             "La pila de la izquierda muestra hasta dónde llega cada uno."],
            TEXTO_TENUE,
        )

        pc_a = equipo("PC A", "", X_PC_A)
        switch = equipo("Switch", "capas 1 y 2", X_SWITCH)
        router = equipo("Router", "capas 1 a 3", X_ROUTER)
        servidor = equipo("Servidor", "", X_SERVIDOR)
        equipos = [pc_a, switch, router, servidor]
        enlaces = VGroup(*[
            Line(a[0].get_right(), b[0].get_left(), color=TEXTO_TENUE, stroke_width=1.5)
            for a, b in zip(equipos, equipos[1:])
        ])
        puerto_1 = mono(str(PUERTO_SWITCH_PC_A), tam=13, color=TEXTO_TENUE)
        puerto_1.next_to(switch[0].get_left(), UL, buff=0.06)
        puerto_2 = mono(str(PUERTO_SWITCH_ROUTER), tam=13, color=TEXTO_TENUE)
        puerto_2.next_to(switch[0].get_right(), UR, buff=0.06)
        mapa = VGroup(enlaces, *equipos, puerto_1, puerto_2)

        trama = trama_viaje()
        trama.move_to([x_carril(X_PC_A, trama), Y_CARRIL, 0])

        paso = texto_paso(
            "La trama sale de PC A",
            "Antes de llegar al servidor pasa por un switch y por el router.\n"
            "Ninguno de los dos necesita abrirla entera.",
        )
        self.play(*pila.activar(None), FadeIn(panel), FadeIn(mapa),
                  FadeIn(trama), FadeIn(paso), run_time=0.8)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        filas = [
            [texto("MAC", tam=16, color=TEXTO_MEDIO), texto("Puerto", tam=16, color=TEXTO_MEDIO)],
            [mono(MAC_PC_A, tam=17), mono(str(PUERTO_SWITCH_PC_A), tam=17)],
            [mono(MAC_ROUTER_A, tam=17), mono(str(PUERTO_SWITCH_ROUTER), tam=17)],
        ]
        tabla_mac, lineas_mac = tabla_texto(filas, x_izquierda=-1.6, y_arriba=Y_DETALLE)
        titulo_tabla = texto("Tabla de direcciones del switch", tam=16, color=TEXTO_TENUE)
        titulo_tabla.next_to(tabla_mac, RIGHT, buff=0.6).align_to(tabla_mac, UP)
        coincidencia = SurroundingRectangle(lineas_mac[2], buff=0.1,
                                            color=NARANJA, stroke_width=2)

        nuevo = texto_paso(
            "Switch: lee la MAC destino",
            f"Busca {MAC_ROUTER_A} en su tabla: está en el puerto {PUERTO_SWITCH_ROUTER}.\n"
            "Reenvía la trama por ese puerto sin cambiarle nada.",
        )
        self.play(trama.animate.set_x(x_carril(X_SWITCH, trama)), run_time=1.2)
        self.play(cambiar_texto(paso, nuevo), *pila.activar({1, 2}),
                  FadeIn(tabla_mac), FadeIn(titulo_tabla), run_time=0.8)
        paso = nuevo
        self.play(Create(coincidencia), run_time=0.5)
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Cómo arma esa tabla",
            "Anota la MAC de origen de cada trama y el puerto por donde llegó.\n"
            "No abre el paquete ni el segmento: llega solo hasta la capa 2.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        nuevo = texto_paso(
            "Router: llega hasta la capa 3",
            "Tiene que leer la IP de destino, así que saca el paquete de la trama.\n"
            "La trama que llegó no sigue: arma una nueva para el siguiente tramo.",
        )
        self.play(FadeOut(tabla_mac), FadeOut(titulo_tabla), FadeOut(coincidencia),
                  run_time=0.4)
        self.play(trama.animate.set_x(x_carril(X_ROUTER, trama)), run_time=1.2)
        self.play(cambiar_texto(paso, nuevo), *pila.activar({1, 2, 3}), run_time=0.8)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        items = VGroup(*[texto(t, tam=18) for t in [
            "1. Comprueba el FCS: coincide, la trama llegó sana.",
            "2. Quita el encabezado Ethernet y el FCS.",
            f"3. TTL {TTL_INICIAL} → {TTL_INICIAL - 1} y recalcula el checksum del encabezado IP.",
            f"4. Tabla de rutas: {RED_SERVIDOR} sale por la interfaz del lado del servidor.",
            f"5. Trama nueva: MAC origen {MAC_ROUTER_B}, MAC destino {MAC_SERVIDOR}.",
        ]])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        items.move_to([X_ZONA_PRINCIPAL + 0.1, Y_DETALLE, 0], aligned_edge=UL)

        eth_viejo, ip_trama, fcs_viejo = trama[0], trama[1], trama[4]
        ttl_nuevo = texto(f"TTL {TTL_INICIAL - 1}", tam=12, color=AMARILLO)
        ttl_nuevo.move_to(ip_trama[1])
        eth_nuevo = trama[0].copy()
        fcs_nuevo = trama[4].copy()
        for bloque in (eth_nuevo, fcs_nuevo):
            bloque[0].set_stroke(width=3)

        cambios = [
            [fcs_viejo[0].animate.set_stroke(width=3)],
            [FadeOut(eth_viejo, shift=UP * 0.3), FadeOut(fcs_viejo, shift=UP * 0.3)],
            [Transform(ip_trama[1], ttl_nuevo)],
            [],
            [FadeIn(eth_nuevo, shift=DOWN * 0.3), FadeIn(fcs_nuevo, shift=DOWN * 0.3)],
        ]
        for i, (item, cambio) in enumerate(zip(items, cambios)):
            anteriores = [items[j].animate.set_color(TEXTO_TENUE) for j in range(i)]
            self.play(FadeIn(item), *anteriores, *cambio, run_time=0.7)
            if i == 4:
                revisar_encuadre(self)
            self.wait(tiempo_lectura(item) * 0.8)

        nuevo = texto_paso(
            "Trama nueva",
            "La MAC del servidor la obtiene con ARP, igual que hizo PC A.\n"
            "El FCS se calcula de nuevo porque la trama es otra.",
        )
        self.play(cambiar_texto(paso, nuevo), run_time=0.6)
        paso = nuevo
        self.wait(tiempo_lectura(paso[1]))

        trama_nueva = VGroup(eth_nuevo, trama[1], trama[2], trama[3], fcs_nuevo)
        self.play(trama_nueva.animate.set_x(x_carril(X_SERVIDOR, trama_nueva)),
                  items.animate.set_color(TEXTO_TENUE), run_time=1.2)
        self.wait(0.5)

        def fila(nombre, antes, despues, cambia, color=NARANJA):
            tono = color if cambia else TEXTO
            return [
                texto(nombre, tam=17, color=TEXTO_MEDIO),
                mono(antes, tam=16, color=tono),
                mono(despues, tam=16, color=tono),
                texto("cambia" if cambia else "igual", tam=16,
                      color=color if cambia else TEXTO_TENUE),
            ]

        segmento = f"{PUERTO_ORIGEN} → {PUERTO_DESTINO}, seq 0"
        filas = [
            [texto("", tam=16),
             texto("PC A → router", tam=16, color=TEXTO_MEDIO),
             texto("router → servidor", tam=16, color=TEXTO_MEDIO),
             texto("", tam=16)],
            fila("MAC destino", MAC_ROUTER_A, MAC_SERVIDOR, True),
            fila("MAC origen", MAC_PC_A, MAC_ROUTER_B, True),
            fila("FCS", "CRC-32", "CRC-32 nuevo", True),
            fila("TTL", str(TTL_INICIAL), str(TTL_INICIAL - 1), True, AMARILLO),
            fila("IP origen", IP_PC_A, IP_PC_A, False),
            fila("IP destino", IP_SERVIDOR, IP_SERVIDOR, False),
            fila("Segmento", segmento, segmento, False),
        ]
        comparacion, _ = tabla_texto(filas, x_izquierda=X_ZONA_PRINCIPAL + 0.1,
                                     y_arriba=2.15, alto_fila=0.48, separacion=0.55)

        nuevo = texto_paso(
            "Qué cambió y qué no",
            "Cambia todo lo de la capa 2 y el TTL. Las IP y el segmento\n"
            "llegan tal como salieron de PC A.",
        )
        self.play(FadeOut(mapa), FadeOut(trama_nueva), FadeOut(items),
                  FadeOut(panel), FadeOut(paso), run_time=0.5)
        self.play(FadeIn(comparacion), FadeIn(nuevo), run_time=0.8)
        paso = nuevo
        revisar_encuadre(self)
        self.wait(tiempo_lectura(paso[1]) + 6)
