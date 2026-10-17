# Qué le pasa a un mensaje cuando viaja por la red

Video de unos 15 minutos sobre el modelo OSI, hecho con Manim Community.
En vez de recorrer las capas como una lista, sigue un solo mensaje
(`Nos vemos a las 5 en la biblioteca`) desde que sale de una PC hasta que
se vuelve a armar en un servidor de chat: qué encabezado agrega cada capa,
qué se verifica en el camino y cómo se recupera el mensaje cuando un
segmento llega tarde o se pierde.

Hecho por Sergio Verdugo.

Video: https://youtu.be/ER0ayaa9PpQ

## Requisitos

- Linux. El video se generó en Arch; `instalar.sh` contempla también
  Debian/Ubuntu y Fedora
- ffmpeg, cairo, pango y las fuentes DejaVu Sans y DejaVu Sans Mono
- Python 3.12 y Manim 0.22.0, que se instalan en un entorno virtual `.venv`

No hace falta LaTeX: todo el texto usa `Text`.

## Instalación

```bash
./instalar.sh
```

Instala los paquetes del sistema (pide sudo), descarga
[uv](https://github.com/astral-sh/uv) si no está y crea `.venv` con Manim.
En Fedora, ffmpeg viene de RPM Fusion, que tiene que estar habilitado antes.

## Generar el video

```bash
./generar.sh         # 1080p a 60 fps
./generar.sh baja    # 480p a 15 fps, mucho más rápido
```

Renderiza las escenas en orden, las une y les pone la marca de agua.
El resultado queda en `salida/osi_1080p60.mp4` (o `osi_480p15.mp4`), y al
lado queda también una copia sin marca. En calidad alta tarda unos 15 minutos.

Una escena suelta se puede renderizar así:

```bash
.venv/bin/manim -ql escenas/06_capa4_transporte.py EscenaTransporte
```

## Escenas

| Archivo | Contenido |
|---|---|
| `00_gancho.py` | El mensaje va de PC A al servidor; la red es una caja cerrada |
| `01_por_que_capas.py` | Los problemas que hay que resolver y por qué se separan en capas |
| `02_mapa_osi_tcpip.py` | Las 7 capas con su PDU y cómo las agrupa TCP/IP |
| `03_capa7_aplicacion.py` | El protocolo del chat y su encabezado |
| `04_capa6_presentacion.py` | Texto a bytes con UTF-8 |
| `05_capa5_sesion.py` | Apertura, intercambio y cierre del diálogo |
| `06_capa4_transporte.py` | Segmentación, puertos, número de secuencia, checksum, ACK |
| `07_capa3_red.py` | Encabezado IP, TTL y tabla de rutas |
| `08_capa2_enlace.py` | Encabezado Ethernet, FCS y ARP |
| `09_capa1_fisica.py` | Bits a señal |
| `10_switch_y_router.py` | Qué cambia y qué no al pasar por un switch y un router |
| `11_reconstruccion.py` | Subida por la pila del servidor, con un segmento perdido y otro demorado |
| `12_mismo_caso_udp.py` | El mismo caso con UDP |
| `13_resumen.py` | Tabla final con las 7 capas |

`comun.py` tiene lo que comparten todas: colores, fuentes, los datos del
ejemplo y los objetos que se repiten (la pila de capas, el panel de cada
capa, las filas de bytes, las tablas).

## Datos del ejemplo

Son ficticios y no cambian en todo el video. Están al principio de
`comun.py`.

| | |
|---|---|
| IP de PC A | 192.168.1.10 |
| IP del servidor | 203.0.113.20 |
| MAC de PC A | 3C:52:82:A1:10:0A |
| MAC del router (lado PC A / lado servidor) | 3C:52:82:B2:00:01 / 3C:52:82:B2:00:02 |
| MAC del servidor | 3C:52:82:C3:20:14 |
| Puertos | 50432 → 5000 |
| TTL inicial | 64 |

Los checksums TCP y UDP que aparecen en pantalla están calculados de verdad
a partir de estos datos (`checksum_tcp` y `checksum_udp` en `comun.py`).

## Simplificaciones

Todas se dicen en el video:

- Segmentos de 12 bytes en lugar de 1460, para que se vea la división.
- El número de secuencia empieza en 0; en TCP real es aleatorio.
- No hay NAT entre la red de PC A y la del servidor.
- El protocolo del chat es inventado.
- La señal de la capa 1 es un nivel alto para 1 y bajo para 0; Ethernet
  usa codificaciones más elaboradas.

## Ajustes

- El tiempo que cada texto queda en pantalla sale de `PALABRAS_POR_SEGUNDO`
  en `comun.py`. Como el video no tiene voz, es lo que marca el ritmo.
- Los colores de las capas están en `COLOR_CAPA`.
- La marca de agua cambia de esquina según los tramos de `TRAMOS` en
  `generar.sh`. Están elegidos para que no tape nada; si se modifican las
  escenas y cambian los tiempos, conviene revisarlos.

## Licencia

- El código (`comun.py`, `escenas/` y los scripts) está bajo licencia MIT: ver `LICENSE`.
- El video que se genera está bajo CC BY 4.0: ver `LICENSE-VIDEO.md`.
