#!/usr/bin/env python3
"""S02 - Posteo · Evento "Desbloquea tus finanzas" (1080x1350). Copiado del Illustrator de marketing.
Título en dos líneas, subtítulo, fecha, hora, lugar, texto y orador (foto, nombre y cargo; por defecto Pablo).
El teléfono de contacto es fijo. Es un modelo de base: cada evento se termina de diseñar con marketing."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, multilinea, pagina, ejecutar, fondo_kit, foto_uri, es_imagen, caja, VIOLETA, BLANCO
from pathlib import Path as _P

CAMPOS = {"titulo_1", "titulo_2", "subtitulo", "dia", "mes", "hora", "lugar", "texto", "orador", "cargo", "foto"}
TELEFONO = "+54 9 11 7237-4932"   # fijo (marketing)
GRIS = "#3C3C3C"; BLACK = "font-family:'Insider Sans Expanded Black';"; EXTRA = "font-family:'Insider Sans Expanded ExtraBold';"

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo_1", 14); f.texto("titulo_2", 16); f.texto("subtitulo", 36)
    f.texto("dia", 12, ayuda="Ej. 'Viernes 28'."); f.texto("mes", 12, ayuda="Ej. 'de Enero'.")
    f.texto("hora", 7, ayuda="Ej. '19hrs'."); f.texto("lugar", 70, ayuda="Dos líneas con \\n: 'Salón...\\nCalle 123 ciudad'.")
    f.texto("texto", 50); f.texto("orador", 18, obligatorio=False); f.texto("cargo", 30, obligatorio=False)
    if "foto" in d and not es_imagen(d["foto"]):
        f.errores.append("foto: ruta a la foto recortada del orador (PNG con fondo transparente).")
    return f.errores

def armar(d, kit):
    c = fondo_kit(kit, "fondo-evento.png", 1080, 1350)
    c += caja(100, 226, 880, 90, f'<div class="tit encoge" style="width:100%;font-size:78px;color:{VIOLETA};white-space:nowrap">{t(d["titulo_1"])}</div>')
    c += caja(100, 310, 880, 90, f'<div class="tit encoge" style="width:100%;font-size:78px;color:{BLANCO};white-space:nowrap">{t(d["titulo_2"])}</div>')
    c += caja(100, 404, 880, 55, f'<div style="font-size:43px;color:{BLANCO}">{t(d["subtitulo"])}</div>')
    c += caja(286, 508, 230, 90, f'<div style="{BLACK}font-size:34px;color:{VIOLETA};line-height:1.05">{t(d["dia"])}</div>'
              f'<div style="font-size:34px;color:{GRIS};line-height:1.05">{t(d["mes"])}</div>', alinear="center")
    c += caja(655, 518, 130, 50, f'<div style="{BLACK}font-size:34px;color:{VIOLETA}">{t(d["hora"])}</div>', alinear="left")
    c += caja(287, 622, 400, 70, f'<div style="font-size:25px;line-height:1.2;color:{GRIS}">{multilinea(d["lugar"])}</div>', alinear="left")
    c += caja(199, 795, 400, 100, f'<div style="font-size:35px;line-height:1.2;color:{BLANCO}">{t(d["texto"])}</div>', alinear="left")
    foto = foto_uri(d["foto"]) if d.get("foto") else foto_uri(str(_P(kit, "pablo-de-pie.png")))
    c += (f'<img class="abs" src="{foto}" style="left:437px;top:493px;width:737px;height:1106px;object-fit:contain;'
          f'object-position:50% 0;filter:drop-shadow(10px 10px 18px rgba(0,0,0,.30))">')
    c += f'<img class="abs" src="{foto_uri(str(_P(kit, "evento-cartel.png")))}" style="left:188px;top:950px;width:560px;height:132px">'
    c += f'<img class="abs" src="{foto_uri(str(_P(kit, "evento-pie.png")))}" style="left:0;top:1145px;width:1080px;height:205px">'
    c += caja(307, 980, 430, 50, f'<div class="tit" style="font-size:41px;color:{VIOLETA};white-space:nowrap">{t(d.get("orador", "PABLO LAZZATI"))}</div>', alinear="left")
    c += caja(310, 1026, 430, 30, f'<div style="font-size:22px;color:{VIOLETA}">{t(d.get("cargo", "CEO de Insider Finance"))}</div>', alinear="left")
    c += caja(84, 1202, 280, 100, f'<div style="{EXTRA}font-size:36px;line-height:1.15;color:{BLANCO}">RESERVA<br>TU LUGAR</div>', alinear="left")
    c += caja(381, 1210, 400, 70, f'<div style="font-size:25px;line-height:1.2;color:{BLANCO}">CONTACTOS<br>{TELEFONO}</div>', alinear="left")
    return pagina(1080, 1350, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["fondo-evento.png", "pablo-de-pie.png", "evento-cartel.png", "evento-pie.png"])
