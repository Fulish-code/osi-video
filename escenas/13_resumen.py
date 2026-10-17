import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from comun import *

RESUMEN = [
    (7, "encabezado del protocolo", "entrega el mensaje al programa"),
    (6, "UTF-8; cifrado si lo hay", "pasa de bytes a texto"),
    (5, "control del diálogo (rara vez aparte)", "que la sesión siga abierta"),
    (4, "puertos, secuencia, checksum", "checksum, orden, huecos, ACK"),
    (3, "IP origen y destino, TTL, protocolo", "IP destino, checksum IP"),
    (2, "MAC destino y origen, EtherType, FCS", "FCS y MAC destino"),
    (1, "nada: bits a señal", "señal a bits"),
]

ALTO_FILA = 0.72
X_IZQUIERDA = -6.6
Y_ARRIBA = 3.0


class EscenaResumen(Scene):
    def construct(self):
        titulo = texto("Resumen", tam=30)
        titulo.move_to([X_IZQUIERDA, 3.55, 0], aligned_edge=LEFT)

        filas = [[texto("Capa", tam=17, color=TEXTO_MEDIO),
                  texto("PDU", tam=17, color=TEXTO_MEDIO),
                  texto("Agrega al enviar", tam=17, color=TEXTO_MEDIO),
                  texto("Verifica al recibir", tam=17, color=TEXTO_MEDIO)]]
        for n, agrega, verifica in RESUMEN:
            filas.append([
                texto(f"{n}  {NOMBRE_CAPA[n]}", tam=19),
                texto(PDU_CAPA[n], tam=18, color=TEXTO_MEDIO),
                texto(agrega, tam=17),
                texto(verifica, tam=17),
            ])
        tabla, lineas = tabla_texto(filas, x_izquierda=X_IZQUIERDA + 0.3,
                                    y_arriba=Y_ARRIBA, alto_fila=ALTO_FILA,
                                    separacion=0.45)
        franjas = VGroup()
        for i, (n, _, _) in enumerate(RESUMEN, start=1):
            franja = Rectangle(width=0.14, height=ALTO_FILA * 0.7, stroke_width=0,
                               fill_color=COLOR_CAPA[n], fill_opacity=1)
            franja.move_to([X_IZQUIERDA + 0.07, lineas[i].get_y(), 0])
            franjas.add(franja)

        self.play(FadeIn(titulo), FadeIn(tabla[0]), run_time=0.6)
        resto = [m for m in tabla[1:]]
        self.play(LaggedStart(*[FadeIn(m) for m in resto], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(f) for f in franjas], lag_ratio=0.2),
                  run_time=2.0)
        revisar_encuadre(self)
        self.wait(40)
