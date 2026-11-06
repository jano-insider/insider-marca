#!/usr/bin/env python3
"""D03 - Documento · Presentación (PowerPoint 16:9 + PDF).

Copia el diseño de la Presentación institucional y de la propuesta de consultoría.
La ficha trae una lista de diapositivas de estos tipos:
  - "portada":   frase debajo del logo (ej. "Sé protagonista de tus finanzas")
  - "texto":     título (arriba a la derecha) y párrafos justificados
  - "indice":    título grande (**así** va en violeta) y exactamente 4 ítems numerados
  - "tarjetas":  título, subtítulo y 2 a 4 tarjetas de texto
  - "pildoras":  título, subtítulo, texto, frase de introducción y 2 a 6 píldoras
  - "lista":     título, subtítulo y 1 a 4 párrafos con hexágono
  - "contacto":  cierre CONTACTANOS (sin campos)
En los textos, **así** pone una parte en negrita itálica violeta, como en el original.
Genera <nombre>.pptx y <nombre>.pdf.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import faltantes, sin_sustituciones  # noqa: E402

from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Pt  # noqa: E402

CORAL, VIOLETA = RGBColor(0xEE, 0x75, 0x63), RGBColor(0x57, 0x3D, 0x8B)
BLANCO, OSCURO, NEGRO = RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1D, 0x1C, 0x1B), RGBColor(0, 0, 0)
GRIS_TARJETA, GRIS_FRASE = RGBColor(0xF3, 0xF3, 0xF3), RGBColor(0x44, 0x42, 0x49)
SEMI, BLACK, CUERPO = "Insider Sans Expanded SemiBold", "Insider Sans Expanded Black", "Numans"
RESALTE = "Insider Sans Expanded"          # en Bold Italic (el original usa Montserrat, fuera del manual)
CONTACTO = [("icono-telefono.png", "54 9 11 7237-4932"), ("icono-instagram.png", "@insider.arg"),
            ("icono-web.png", "www.insiderfinance.com.ar"), ("icono-linkedin.png", "Insider Finance")]
RECURSOS = ["logo-horizontal-color.svg", "hexagonos-esquinas-16x9.svg", "hexagonos-indice.svg"] + [c[0] for c in CONTACTO]
TIPOS = {"portada", "texto", "indice", "tarjetas", "pildoras", "lista", "contacto"}

# Coordenadas en px del original (1920x1080); se dibuja en una diapositiva 16:9 estándar.
ESC = 1280 / 1920
px = lambda v: Emu(int(v * ESC * 9525))
pt = lambda v: Pt(v * 0.5)                 # tamaños del PDF original (página de 1920 pt)


# ------------------------------------------------------------------ validación
def validar(d):
    e = []
    def txt(v, campo, maximo, obligatorio=True):
        if v in (None, ""):
            if obligatorio:
                e.append(f"{campo}: falta.")
        elif not isinstance(v, str) or len(v) > maximo:
            e.append(f"{campo}: texto de hasta {maximo} caracteres.")
    def lista(v, campo, mn, mx, largo):
        if not isinstance(v, list) or not mn <= len(v) <= mx or not all(isinstance(x, str) and 0 < len(x) <= largo for x in v):
            e.append(f"{campo}: entre {mn} y {mx} textos de hasta {largo} caracteres.")

    if not isinstance(d, dict) or set(d) - {"diapositivas"}:
        return ["La ficha lleva solo 'diapositivas'."]
    dias = d.get("diapositivas")
    if not isinstance(dias, list) or not 1 <= len(dias) <= 20:
        return ["diapositivas: entre 1 y 20."]
    for i, s in enumerate(dias, 1):
        c = f"diapositivas[{i}]"
        if not isinstance(s, dict) or s.get("tipo") not in TIPOS:
            e.append(f"{c}.tipo: uno de {sorted(TIPOS)}."); continue
        tp = s["tipo"]
        if tp == "portada":
            txt(s.get("frase"), f"{c}.frase", 45)
        if tp in ("texto", "tarjetas", "pildoras", "lista"):
            txt(s.get("titulo"), f"{c}.titulo", 40)
        if tp == "texto":
            lista(s.get("parrafos"), f"{c}.parrafos", 1, 4, 420)
        if tp in ("tarjetas", "pildoras", "lista"):
            txt(s.get("subtitulo"), f"{c}.subtitulo", 50)
        if tp == "indice":
            txt(s.get("titulo"), f"{c}.titulo", 40)
            lista(s.get("items"), f"{c}.items", 4, 4, 50)
        if tp == "tarjetas":
            lista(s.get("tarjetas"), f"{c}.tarjetas", 2, 4, 200)
        if tp == "pildoras":
            txt(s.get("texto"), f"{c}.texto", 260, obligatorio=False)
            txt(s.get("intro"), f"{c}.intro", 60, obligatorio=False)
            lista(s.get("pildoras"), f"{c}.pildoras", 2, 6, 40)
        if tp == "lista":
            lista(s.get("parrafos"), f"{c}.parrafos", 1, 4, 220)
    return e


# ------------------------------------------------------------------ dibujo
def caja(slide, forma, x, y, w, h, relleno=None, linea=None, grosor=0):
    sh = slide.shapes.add_shape(forma, px(x), px(y), px(w), px(h))
    if relleno is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = relleno
    if linea is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = linea; sh.line.width = Pt(grosor)
    sh.shadow.inherit = False
    return sh


def texto(slide, x, y, w, h, parrafos, fam=CUERPO, tam=34, color=OSCURO, alinear=PP_ALIGN.LEFT,
          ancla=MSO_ANCHOR.TOP, espaciado=0, interlineado=1.15, sep=18):
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = ancla
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, par in enumerate(parrafos if isinstance(parrafos, list) else [parrafos]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinear; p.line_spacing = interlineado
        if i:
            p.space_before = pt(sep)
        for j, trozo in enumerate(re.split(r"\*\*(.+?)\*\*", par)):
            if not trozo:
                continue
            r = p.add_run(); r.text = trozo
            f = r.font; f.size = pt(tam)
            if j % 2 == 1:                     # resaltado
                f.name, f.bold, f.italic, f.color.rgb = RESALTE, True, True, VIOLETA
            else:
                f.name, f.color.rgb = fam, color
            if espaciado:
                r._r.get_or_add_rPr().set("spc", str(espaciado))
    return tb


def svg_a_png(kit, archivo, ancho, destino, fondo_blanco=False):
    from playwright.sync_api import sync_playwright
    svg = re.sub(r"<\?xml[^>]*\?>", "", Path(kit, archivo).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": ancho, "height": 400})
        fondo = "#fff" if fondo_blanco else "transparent"
        pag.set_content(f'<html><body style="margin:0;background:{fondo}"><div id="l" style="width:{ancho}px">'
                        f'{svg}</div><style>#l svg{{width:{ancho}px;height:auto;display:block}}</style></body></html>')
        pag.wait_for_timeout(300)
        pag.locator("#l").screenshot(path=destino, omit_background=not fondo_blanco)
        nav.close()


def cabecera(slide, s, logo):
    slide.shapes.add_picture(logo, px(129), px(92), width=px(222))
    texto(slide, 900, 92, 900, 60, s["titulo"], fam=SEMI, tam=36, color=VIOLETA, alinear=PP_ALIGN.RIGHT)


def subtitulo(slide, s):
    texto(slide, 155, 240, 1650, 60, s["subtitulo"], fam=SEMI, tam=36, color=OSCURO)


def hexagono(slide, cx, cy, ancho, color=CORAL, grosor=6):   # viñetas chicas (tarjetas, lista)
    caja(slide, MSO_SHAPE.HEXAGON, cx - ancho / 2, cy - ancho * 0.45, ancho, ancho * 0.9, linea=color, grosor=grosor * ESC * 0.75)


def d_portada(slide, s, r):
    slide.shapes.add_picture(r["esquinas"], 0, 0, width=px(1920))
    slide.shapes.add_picture(r["logo_grande"], px(470), px(250), width=px(980))
    for y in (690, 790):
        caja(slide, MSO_SHAPE.RECTANGLE, 431, y, 1108, 2, relleno=GRIS_FRASE)
    texto(slide, 431, 700, 1108, 80, s["frase"], tam=48, color=GRIS_FRASE, alinear=PP_ALIGN.CENTER,
          ancla=MSO_ANCHOR.MIDDLE, espaciado=260)


def d_texto(slide, s, r):
    cabecera(slide, s, r["logo"])
    texto(slide, 129, 280, 1670, 700, s["parrafos"], tam=34, alinear=PP_ALIGN.JUSTIFY, interlineado=1.25, sep=34)


def d_indice(slide, s, r):
    """Copia exacta del original: gráfico de 4 hexágonos con degradado, números y textos
    en las mismas coordenadas que la Presentación institucional."""
    slide.shapes.add_picture(r["logo"], px(129), px(92), width=px(222))
    texto(slide, 143, 410, 760, 320, s["titulo"].upper(), fam=BLACK, tam=83, color=NEGRO, interlineado=1.0, sep=0)
    for p in slide.shapes[-1].text_frame.paragraphs:   # el resaltado del índice va en Black violeta
        for run in p.runs:
            if run.font.italic:
                run.font.name, run.font.italic, run.font.bold = BLACK, False, False
    slide.shapes.add_picture(r["indice"], px(848), px(242), width=px(342))
    # Centro de cada hexágono, medido sobre el gráfico (px del original 1920x1080)
    centros = [(966, 376), (1072, 552), (966, 728), (1072, 904)]
    textos = [(1145, 330), (1229, 517), (1141, 707), (1210, 877)]
    for i, item in enumerate(s["items"]):
        cx, cy = centros[i]
        texto(slide, cx - 110, cy - 90, 220, 180, str(i + 1), fam=BLACK, tam=116, color=VIOLETA,
              alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE, interlineado=1.0)
        tx, ty = textos[i]
        texto(slide, tx, ty, 1840 - tx, 100, item, tam=34, color=OSCURO)


def d_tarjetas(slide, s, r):
    cabecera(slide, s, r["logo"]); subtitulo(slide, s)
    n = len(s["tarjetas"]); gap = 46
    w = (1700 - gap * (n - 1)) / n
    for i, tx in enumerate(s["tarjetas"]):
        x = 110 + i * (w + gap)
        tarjeta = caja(slide, MSO_SHAPE.SNIP_2_DIAG_RECTANGLE, x, 380, w, 520, relleno=GRIS_TARJETA)
        tarjeta.adjustments[0] = 0.0; tarjeta.adjustments[1] = 0.16
        texto(slide, x + 34, 430, w - 68, 430, tx, tam=28, color=OSCURO, interlineado=1.1)
        hexagono(slide, x + w / 2, 900, 90, grosor=7)


def d_pildoras(slide, s, r):
    cabecera(slide, s, r["logo"]); subtitulo(slide, s)
    y = 330
    if s.get("texto"):
        texto(slide, 129, y, 1670, 140, s["texto"], tam=34, alinear=PP_ALIGN.JUSTIFY, interlineado=1.25)
        y += 160
    if s.get("intro"):
        texto(slide, 129, y, 1670, 60, s["intro"], tam=34)
        y += 110
    for i, pl in enumerate(s["pildoras"]):
        col, fila = i % 2, i // 2
        x, yy = 130 + col * 820, y + 80 + fila * 125
        caja(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, yy, 780, 92, relleno=CORAL).adjustments[0] = 0.5
        texto(slide, x, yy, 780, 92, pl, tam=34, color=BLANCO, alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)


def d_lista(slide, s, r):
    cabecera(slide, s, r["logo"]); subtitulo(slide, s)
    n = len(s["parrafos"]); paso = 155
    for i, par in enumerate(s["parrafos"]):
        y = 370 + i * paso
        hexagono(slide, 235, y + 55, 90, grosor=7)
        texto(slide, 364, y, 1435, 130, par, tam=34, alinear=PP_ALIGN.JUSTIFY, interlineado=1.25, ancla=MSO_ANCHOR.MIDDLE)


def d_contacto(slide, s, r):
    slide.shapes.add_picture(r["esquinas"], 0, 0, width=px(1920))
    slide.shapes.add_picture(r["logo"], px(129), px(92), width=px(222))
    texto(slide, 200, 340, 1520, 160, "CONTACTANOS", fam=BLACK, tam=116, color=NEGRO, alinear=PP_ALIGN.CENTER)
    for i, (icono, dato) in enumerate(CONTACTO):
        col, fila = i % 2, i // 2
        x, y = 330 + col * 820, 560 + fila * 100
        slide.shapes.add_picture(str(Path(r["kit"], icono)), px(x), px(y + 8), height=px(54))
        texto(slide, x + 80, y, 700, 70, dato, tam=40, color=GRIS_FRASE, ancla=MSO_ANCHOR.MIDDLE)


def armar(d, kit, destino):
    prs = Presentation()
    prs.slide_width, prs.slide_height = px(1920), px(1080)
    vacio = prs.slide_layouts[6]
    with tempfile.TemporaryDirectory() as tmp:
        r = {"kit": kit, "logo": str(Path(tmp, "l.png")), "logo_grande": str(Path(tmp, "lg.png")), "esquinas": str(Path(tmp, "e.png"))}
        svg_a_png(kit, "logo-horizontal-color.svg", 800, r["logo"])
        svg_a_png(kit, "logo-horizontal-color.svg", 1600, r["logo_grande"])
        svg_a_png(kit, "hexagonos-esquinas-16x9.svg", 1920, r["esquinas"])
        r["indice"] = str(Path(tmp, "i.png"))
        svg_a_png(kit, "hexagonos-indice.svg", 1026, r["indice"], fondo_blanco=True)   # sin transparencias: LibreOffice las dibuja grises
        fns = {"portada": d_portada, "texto": d_texto, "indice": d_indice, "tarjetas": d_tarjetas,
               "pildoras": d_pildoras, "lista": d_lista, "contacto": d_contacto}
        for s in d["diapositivas"]:
            fns[s["tipo"]](prs.slides.add_slide(vacio), s, r)
        prs.save(destino)


def main():
    ap = argparse.ArgumentParser(description="D03 - Presentación")
    ap.add_argument("datos"); ap.add_argument("--kit", required=True)
    ap.add_argument("--salida", required=True); ap.add_argument("--nombre", required=True)
    a = ap.parse_args()
    errores = []
    if not re.match(r"^[a-z0-9\-]{1,60}$", a.nombre):
        errores.append("--nombre: solo minúsculas, números y guiones (máx. 60).")
    try:
        datos = json.loads(Path(a.datos).read_text(encoding="utf-8"))
    except Exception as ex:
        sys.exit(f"ERROR: no se pudo leer la ficha JSON: {ex}")
    errores += validar(datos) + faltantes(a.kit, RECURSOS)
    if errores:
        print("NO SE GENERÓ LA PRESENTACIÓN. Errores:")
        for x in errores:
            print(" -", x)
        sys.exit(1)
    salida = Path(a.salida); salida.mkdir(parents=True, exist_ok=True)
    pptx = salida / f"{a.nombre}.pptx"
    armar(sin_sustituciones(datos), a.kit, str(pptx))   # "T2X6" no se convierte en "T2×6"
    rr = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(salida), str(pptx)],
                        capture_output=True, text=True, timeout=240)
    if rr.returncode != 0 or not (salida / f"{a.nombre}.pdf").exists():
        sys.exit(f"ERROR: se generó el PowerPoint pero falló el PDF: {rr.stderr[-300:]}")
    print(f"OK: {pptx} y {salida / (a.nombre + '.pdf')}")


if __name__ == "__main__":
    main()
