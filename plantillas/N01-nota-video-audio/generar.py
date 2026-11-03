#!/usr/bin/env python3
"""N01 - Historia · Nota en video o audio (1440x2560), copiada de "plantillas Notas de video o audio 2026".

Variantes:
  - "una-foto":       Pablo en círculo, NUEVA NOTA, medio, tema, entrevista y banda coral abajo (ej. radio).
  - "dos-fotos":      Pablo y el invitado en círculos, título, nombre del invitado, tema y "ENTREVISTA A ...".
  - "coral":          fondo coral, Pablo en círculo, nombre del medio en etiqueta, titular, bajada y entrevista.
  - "programa-video": ícono de video, NOTA, programa en recuadro gris, descripción y entrevista.
  - "programa-audio": ícono de audio, NOTA coral, programa, descripción, entrevista y banda coral abajo.
  - "canal-video":    fondo degradado con el recuadro para el video, NOTA y el nombre del canal.
  - "canal-fotos":    NOTA y canal, con las fotos de Pablo y del invitado en tarjetas con sus nombres.
Las fotos del invitado (--foto) las adjunta quien pide la pieza. En titular y tema, **así** va en violeta.
"""
import base64, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, ejecutar, CORAL, VIOLETA, BLANCO  # noqa: E402

FONDO = {v: f"nota-{v}.png" for v in ("una-foto", "dos-fotos", "coral", "programa-video", "programa-audio", "canal-video", "canal-fotos")}
NECESITA_FOTO = {"dos-fotos", "canal-fotos"}
CAMPOS = {"variante", "titulo", "invitado", "tema", "entrevista", "medio", "color_medio", "titular", "bajada",
          "programa", "descripcion", "canal", "nombre_pablo", "nombre_invitado", "foto", "foto_pablo"}
NEGRO = "#1D1D1B"

def es_imagen(ruta):
    return isinstance(ruta, str) and Path(ruta).is_file() and Path(ruta).read_bytes()[:4][:3] in (b"\x89PN", b"\xff\xd8\xff")

def validar(d):
    f = Ficha(d, CAMPOS)
    f.opcion("variante", set(FONDO))
    v = d.get("variante")
    if v == "una-foto":
        f.opcion("titulo", {"NUEVA NOTA", "NOTA"}); f.texto("medio", 24); f.texto("tema", 40); f.texto("entrevista", 40)
    if v in ("dos-fotos", "coral"):
        f.opcion("titulo", {"NUEVA NOTA", "NOTA"})
        f.texto("entrevista", 40, ayuda="Ej. 'ENTREVISTA A PABLO LAZATTI'.")
    if v == "dos-fotos":
        f.texto("invitado", 30); f.texto("tema", 60)
    if v == "coral":
        f.texto("medio", 18, ayuda="Ej. 'AHORAPLAY.AR' o 'AFTER MARKET'.")
        f.texto("color_medio", 7, obligatorio=False, patron=r"^#[0-9A-Fa-f]{6}$", ayuda="Color del nombre del medio, ej. '#62A7C5'.")
        f.texto("titular", 90); f.texto("bajada", 50, obligatorio=False)
    if v in ("programa-video", "programa-audio"):
        f.texto("programa", 24); f.texto("descripcion", 150); f.texto("entrevista", 40, obligatorio=False)
    if v in ("canal-video", "canal-fotos"):
        f.texto("canal", 18, ayuda="Ej. 'CANAL E'.")
    if v == "canal-fotos":
        f.texto("nombre_pablo", 24, obligatorio=False); f.texto("nombre_invitado", 24)
    if v in NECESITA_FOTO and not es_imagen(d.get("foto")):
        f.errores.append("foto: ruta a la foto del invitado (PNG o JPG) que adjuntó quien pide la pieza.")
    if v == "canal-fotos" and not es_imagen(d.get("foto_pablo")):
        f.errores.append("foto_pablo: ruta a la foto de Pablo para la tarjeta (PNG o JPG).")
    return f.errores

def uri(ruta):
    datos = Path(ruta).read_bytes()
    return f"data:image/{'png' if datos.startswith(b'\\x89PNG') else 'jpeg'};base64," + base64.b64encode(datos).decode()

def caja(x, y, w, h, html_txt, extra=""):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:center;text-align:center;{extra}">{html_txt}</div>')

def circulo(x, y, d, src, fondo=CORAL):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{d}px;height:{d}px;border-radius:50%;overflow:hidden;background:{fondo}">'
            f'<img src="{src}" style="width:100%;height:100%;object-fit:cover;object-position:50% 20%"></div>')

def armar(d, kit):
    v = d["variante"]
    c = f'<img class="abs" src="{uri(Path(kit, FONDO[v]))}" style="left:0;top:0;width:1440px;height:2560px">'
    entrevista = lambda y, color: caja(400, y, 645, 202, f'<div style="font-size:64px;line-height:1.1;color:{color};text-transform:uppercase">{t(d["entrevista"])}</div>')
    if v == "una-foto":   # medidas del Illustrator (1080x1920) llevadas a 1440x2560
        c += caja(150, 850, 1140, 340, f'<div class="tit" style="font-size:167px;line-height:0.95;color:{VIOLETA}">{t(d["titulo"])}</div>')
        c += caja(150, 1195, 1140, 90, f'<div style="font-size:67px;color:{NEGRO};text-transform:uppercase">{t(d["medio"])}</div>')
        c += caja(150, 1430, 1140, 220, f'<div class="tit" style="font-size:81px;line-height:1.15;color:{VIOLETA};text-transform:uppercase">{t(d["tema"])}</div>',
                  "overflow:hidden").replace('class="abs"', 'class="abs ajusta" data-campo="tema"', 1)
        c += caja(400, 1648, 645, 200, f'<div style="font-size:57px;line-height:1.15;color:{NEGRO};text-transform:uppercase;max-width:480px">{t(d["entrevista"])}</div>')
    if v == "dos-fotos":
        c += circulo(263, 427, 399, uri(Path(kit, "nota-pablo-circulo-coral.png")))
        c += circulo(725, 427, 399, uri(d["foto"]))
        c += caja(150, 865, 1140, 740,
                  f'<div class="tit encoge" style="font-size:167px;line-height:1.02;color:{VIOLETA};width:100%">{t(d["titulo"])}</div>'
                  f'<div style="font-size:67px;color:{NEGRO};margin-top:30px;text-transform:uppercase">{t(d["invitado"])}</div>'
                  f'<div class="tit" style="font-size:81px;line-height:1.1;color:{VIOLETA};margin-top:20px;text-transform:uppercase">{t(d["tema"])}</div>',
                  "justify-content:flex-start;overflow:hidden").replace('class="abs"', 'class="abs ajusta" data-campo="titulo/invitado/tema"', 1)
        c += entrevista(1628, "#000")
    if v == "coral":
        c += circulo(496, 474, 399, uri(Path(kit, "nota-pablo-circulo-blanco.png")), BLANCO)
        c += caja(150, 920, 1140, 340, f'<div class="tit" style="font-size:167px;line-height:1.02;color:{BLANCO}">{t(d["titulo"])}</div>')
        col = d.get("color_medio", "#62A7C5")
        c += (f'<div class="abs" style="left:372px;top:1276px;width:734px;height:178px;display:flex;align-items:center;justify-content:center">'
              f'<div style="background:{BLANCO};border:6px solid {col};border-radius:24px;padding:4px 50px;font-family:\'Fredoka\';'
              f'font-size:72px;color:{col};white-space:nowrap">{t(d["medio"])}</div></div>')
        c += caja(59, 1520, 1326, 360, f'<div class="tit" style="font-size:81px;line-height:1.12;color:{BLANCO};text-transform:uppercase">{t(d["titular"])}</div>',
                  "overflow:hidden").replace('class="abs"', 'class="abs ajusta" data-campo="titular"', 1)
        if d.get("bajada"):
            c += caja(150, 1880, 1140, 90, f'<div style="font-size:57px;color:{BLANCO}">{t(d["bajada"])}</div>')
        c += caja(423, 2041, 645, 202, f'<div style="font-size:64px;line-height:1.1;color:{BLANCO};text-transform:uppercase">{t(d["entrevista"])}</div>')
    if v in ("programa-video", "programa-audio"):
        video = v == "programa-video"
        y0, color_nota = (584, VIOLETA) if video else (246, CORAL)
        c += caja(100, y0, 1240, 260, f'<div class="tit" style="font-size:215px;line-height:1;color:{color_nota}">NOTA</div>',
                  "justify-content:flex-start")
        c += caja(100, y0 + 330 if video else y0 + 340, 1240, 120,
                  f'<div style="background:#EFEFEF;padding:6px 40px;font-size:{67 if video else 82}px;color:{NEGRO};text-transform:uppercase">{t(d["programa"])}</div>')
        c += caja(200, y0 + 500, 1040, 460 if video else 400,
                  f'<div style="font-size:67px;line-height:1.3;color:{NEGRO}">{t(d["descripcion"])}</div>', "overflow:hidden"
                  ).replace('class="abs"', 'class="abs ajusta" data-campo="descripcion"', 1)
        if d.get("entrevista"):
            c += caja(400, 2048 if video else 1472, 645, 202, f'<div style="font-size:57px;line-height:1.15;color:{NEGRO};text-transform:uppercase;max-width:480px">{t(d["entrevista"])}</div>')
    if v in ("canal-video", "canal-fotos"):
        color = BLANCO if v == "canal-video" else VIOLETA
        c += caja(200, 405, 1040, 400,
                  f'<div class="tit" style="font-size:215px;line-height:1;color:{color}">NOTA</div>'
                  f'<div style="font-size:67px;color:{color};margin-top:24px;text-transform:uppercase">{t(d["canal"])}</div>', "justify-content:flex-start")
    if v == "canal-fotos":
        for (x, y, w, h), src in (((122, 990, 588, 629), uri(d["foto_pablo"])), ((717, 980, 601, 639), uri(d["foto"]))):
            c += f'<img class="abs" src="{src}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;object-fit:cover;object-position:50% 20%">'
        c += caja(200, 1690, 440, 240, f'<div style="font-size:67px;line-height:1.1;color:#020203;text-transform:uppercase">{t(d.get("nombre_pablo", "PABLO LAZZATI"))}</div>')
        c += caja(800, 1690, 440, 240, f'<div style="font-size:67px;line-height:1.1;color:#020203;text-transform:uppercase">{t(d["nombre_invitado"])}</div>')
    return pagina(1440, 2560, ".res { color:%s; }" % VIOLETA, c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1440, 2560, list(FONDO.values()) + ["nota-pablo-circulo-coral.png", "nota-pablo-circulo-blanco.png"])
