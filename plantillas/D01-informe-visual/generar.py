#!/usr/bin/env python3
"""D01 - Documento · Informe Visual semanal (PowerPoint 16:9 + PDF).

Uso:
    python3 generar.py datos.json --kit /tmp/marca --salida /mnt/session/outputs --nombre informe-visual-27-10

La ficha trae la fecha y una lista de diapositivas de tres tipos:
  - "datos":      sección, título, bajada, 1 a 3 indicadores, un gráfico, recuadro "La cadena", fuente, notas
Gráficos: "barras_h", "columnas", "lineas" o "curva" (línea suavizada, ej. curva de rendimientos);
"decimales" (0, 1 o 2) para las etiquetas; en líneas y curvas, null deja un punto sin dato.
  - "estrategia": sección, título, indicador opcional, gráfico, 3 perfiles y hasta 3 acciones
  - "agenda":     sección, título, bajada y hasta 8 eventos (internacional / argentina)
Al final se agrega siempre el disclaimer legal. Los gráficos son nativos de
PowerPoint (editables). En los textos, **así** pone una parte en negrita.
Genera <nombre>.pptx y <nombre>.pdf (con las fuentes incrustadas).
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
from pptx.chart.data import CategoryChartData  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Pt  # noqa: E402

CORAL, VIOLETA, ROSA = RGBColor(0xEE, 0x75, 0x63), RGBColor(0x57, 0x3D, 0x8B), RGBColor(0xE4, 0x59, 0x77)
BLANCO, TEXTO, GRIS = RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1F, 0x1F, 0x1F), RGBColor(0x6B, 0x6B, 0x6B)
LAVANDA, CORAL_SUAVE = RGBColor(0xF3, 0xF0, 0xF8), RGBColor(0xFD, 0xEC, 0xE9)
TITULO, CUERPO = "Insider Sans Expanded", "Numans"
PERFIL_COLOR = {"CONSERVADOR": VIOLETA, "MODERADO": CORAL, "AGRESIVO": ROSA}
TIPOS_GRAFICO = {"barras_h": XL_CHART_TYPE.BAR_CLUSTERED, "columnas": XL_CHART_TYPE.COLUMN_CLUSTERED,
                 "lineas": XL_CHART_TYPE.LINE_MARKERS, "curva": XL_CHART_TYPE.LINE_MARKERS}
LINEALES = {"lineas", "curva"}       # "curva" = línea suavizada (ej. curva de rendimientos por vencimiento)
DISCLAIMER = ("El contenido de esta presentación, como la web de Insider Finance, así también sus redes sociales "
              "son canales educativos con el objetivo de educar al público sobre inversiones en el mercado de "
              "capitales y educación financiera. Toda la información provista y sus respectivos contenidos, en "
              "dichos canales, se presenta a título meramente informativo y no constituye una recomendación de "
              "inversión, ni invitación, oferta, solicitud u obligación para llevar a cabo operación o transacción "
              "alguna. Dicha información tampoco es un reflejo de posiciones propias, de los accionistas, "
              "directores, sucursales o de terceros.")
RECURSOS = ["logo-horizontal-color.svg", "hexagonos-esquinas-16x9.svg"]
px = lambda v: Emu(int(v * 9525))


# ------------------------------------------------------------------ validación
def validar(d):
    e = []
    def txt(v, campo, maximo, obligatorio=True):
        if v in (None, ""):
            if obligatorio:
                e.append(f"{campo}: falta.")
            return
        if not isinstance(v, str) or len(v) > maximo:
            e.append(f"{campo}: texto de hasta {maximo} caracteres.")

    def grafico(g, campo):
        if not isinstance(g, dict):
            e.append(f"{campo}: falta el gráfico."); return
        if g.get("tipo") not in TIPOS_GRAFICO:
            e.append(f"{campo}.tipo: uno de {list(TIPOS_GRAFICO)}.")
        txt(g.get("titulo"), f"{campo}.titulo", 90)
        cats = g.get("categorias")
        if not isinstance(cats, list) or not 2 <= len(cats) <= 14 or not all(isinstance(c, str) and 0 < len(c) <= 40 for c in cats):
            e.append(f"{campo}.categorias: entre 2 y 14 textos cortos.")
            return
        series = g.get("series")
        if not isinstance(series, list) or not 1 <= len(series) <= 3:
            e.append(f"{campo}.series: entre 1 y 3 series."); return
        for j, s in enumerate(series, 1):
            vals = s.get("valores") if isinstance(s, dict) else None
            txt(s.get("nombre") if isinstance(s, dict) else None, f"{campo}.series[{j}].nombre", 40)
            sueltos_ok = g.get("tipo") in LINEALES          # en líneas se admite null = punto sin dato
            if not isinstance(vals, list) or len(vals) != len(cats) or not all(
                    isinstance(v, (int, float)) or (v is None and sueltos_ok) for v in vals):
                e.append(f"{campo}.series[{j}].valores: un número por categoría ({len(cats)})"
                         + ("; null para un punto sin dato." if sueltos_ok else "."))
        dec = g.get("decimales", 1)
        if dec not in (0, 1, 2):
            e.append(f"{campo}.decimales: 0, 1 o 2.")

    if not isinstance(d, dict):
        return ["La ficha tiene que ser un objeto JSON."]
    for k in d:
        if k not in {"fecha", "diapositivas"}:
            e.append(f"Campo desconocido: '{k}'.")
    txt(d.get("fecha"), "fecha", 80)
    dias = d.get("diapositivas")
    if not isinstance(dias, list) or not 1 <= len(dias) <= 12:
        return e + ["diapositivas: entre 1 y 12."]
    for i, s in enumerate(dias, 1):
        c = f"diapositivas[{i}]"
        if not isinstance(s, dict) or s.get("tipo") not in {"datos", "estrategia", "agenda"}:
            e.append(f"{c}.tipo: 'datos', 'estrategia' o 'agenda'."); continue
        txt(s.get("seccion"), f"{c}.seccion", 80)
        txt(s.get("titulo"), f"{c}.titulo", 70)
        txt(s.get("bajada"), f"{c}.bajada", 170, obligatorio=False)
        txt(s.get("fuente"), f"{c}.fuente", 220, obligatorio=False)
        txt(s.get("notas"), f"{c}.notas", 4000, obligatorio=False)
        kpis = s.get("indicadores", [])
        maximo_kpis = 3 if s["tipo"] == "datos" else 1
        if not isinstance(kpis, list) or len(kpis) > maximo_kpis or (s["tipo"] == "datos" and not kpis):
            e.append(f"{c}.indicadores: {'1 a 3' if s['tipo'] == 'datos' else 'hasta 1'}.")
        else:
            for j, k in enumerate(kpis, 1):
                k = k if isinstance(k, dict) else {}
                txt(k.get("etiqueta"), f"{c}.indicadores[{j}].etiqueta", 40)
                txt(k.get("valor"), f"{c}.indicadores[{j}].valor", 16)
                txt(k.get("detalle"), f"{c}.indicadores[{j}].detalle", 110, obligatorio=False)
        if s["tipo"] in ("datos", "estrategia"):
            grafico(s.get("grafico"), f"{c}.grafico")
        if s["tipo"] == "datos":
            cad = s.get("cadena")
            if not isinstance(cad, dict):
                e.append(f"{c}.cadena: falta el recuadro.")
            else:
                txt(cad.get("titulo"), f"{c}.cadena.titulo", 30)
                pts = cad.get("puntos")
                if not isinstance(pts, list) or not 1 <= len(pts) <= 5 or not all(isinstance(p, str) and len(p) <= 160 for p in pts):
                    e.append(f"{c}.cadena.puntos: 1 a 5 textos de hasta 160 caracteres.")
        if s["tipo"] == "estrategia":
            per = s.get("perfiles")
            if not isinstance(per, list) or len(per) != 3:
                e.append(f"{c}.perfiles: exactamente 3 (conservador, moderado, agresivo).")
            else:
                for j, p in enumerate(per, 1):
                    p = p if isinstance(p, dict) else {}
                    if p.get("perfil") not in PERFIL_COLOR:
                        e.append(f"{c}.perfiles[{j}].perfil: {list(PERFIL_COLOR)}.")
                    txt(p.get("texto"), f"{c}.perfiles[{j}].texto", 260)
            acc = s.get("acciones", [])
            if not isinstance(acc, list) or len(acc) > 3 or not all(isinstance(a, str) and len(a) <= 120 for a in acc):
                e.append(f"{c}.acciones: hasta 3 textos de hasta 120 caracteres.")
        if s["tipo"] == "agenda":
            ev = s.get("eventos")
            if not isinstance(ev, list) or not 1 <= len(ev) <= 8:
                e.append(f"{c}.eventos: entre 1 y 8.")
            else:
                for j, x in enumerate(ev, 1):
                    x = x if isinstance(x, dict) else {}
                    txt(x.get("fecha"), f"{c}.eventos[{j}].fecha", 12)
                    txt(x.get("titulo"), f"{c}.eventos[{j}].titulo", 45)
                    txt(x.get("detalle"), f"{c}.eventos[{j}].detalle", 120, obligatorio=False)
                    if x.get("ambito") not in {"internacional", "argentina"}:
                        e.append(f"{c}.eventos[{j}].ambito: 'internacional' o 'argentina'.")
    return e


# ------------------------------------------------------------------ dibujo
def caja(slide, x, y, w, h, color=None, redondeo=True):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if redondeo else MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(h))
    if redondeo:
        sh.adjustments[0] = 0.08
    sh.line.fill.background()
    if color is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.shadow.inherit = False
    return sh


def texto(slide, x, y, w, h, contenido, fam=CUERPO, tam=11, color=TEXTO, negrita=False, italica=False,
          alinear=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP):
    """Caja de texto. 'contenido' es texto o lista de párrafos; **así** = negrita."""
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancla
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    parrafos = contenido if isinstance(contenido, list) else [contenido]
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinear
        if i:
            p.space_before = Pt(5)
        for j, trozo in enumerate(re.split(r"\*\*(.+?)\*\*", par)):
            if not trozo:
                continue
            r = p.add_run(); r.text = trozo
            f = r.font
            f.size = Pt(tam); f.color.rgb = color; f.italic = italica
            res = j % 2 == 1
            f.name = TITULO if (res or fam == TITULO) else fam
            f.bold = negrita or res or fam == TITULO
    return tb


def svg_a_png(kit, archivo, ancho, destino):
    from playwright.sync_api import sync_playwright
    svg = re.sub(r"<\?xml[^>]*\?>", "", Path(kit, archivo).read_text(encoding="utf-8"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": ancho, "height": 400})
        pag.set_content(f'<html><body style="margin:0;background:transparent"><div id="l" style="width:{ancho}px">'
                        f'{svg}</div><style>#l svg{{width:{ancho}px;height:auto;display:block}}</style></body></html>')
        pag.wait_for_timeout(300)
        pag.locator("#l").screenshot(path=destino, omit_background=True)
        nav.close()


def encabezado(slide, d, s, n, total, logo):
    slide.shapes.add_picture(logo, px(48), px(26), width=px(150))
    texto(slide, 700, 36, 532, 20, d["fecha"], tam=10, color=GRIS, alinear=PP_ALIGN.RIGHT)
    banda = caja(slide, 48, 96, 1184, 32, CORAL, redondeo=False)
    texto(slide, 62, 96, 1160, 32, s["seccion"].upper(), fam=TITULO, tam=11, color=BLANCO, ancla=MSO_ANCHOR.MIDDLE)
    texto(slide, 48, 140, 1184, 44, s["titulo"], fam=TITULO, tam=26, color=VIOLETA, ancla=MSO_ANCHOR.MIDDLE)
    if s.get("bajada"):
        texto(slide, 48, 190, 1184, 34, s["bajada"], tam=12.5, color=VIOLETA, italica=True)
    texto(slide, 48, 684, 800, 20, "Insider Finance  |  Research Semanal  |  DOCUMENTO DE USO INTERNO", tam=8, color=GRIS)
    texto(slide, 1100, 684, 132, 20, f"{n} / {total}", tam=9, color=GRIS, alinear=PP_ALIGN.RIGHT)
    if s.get("notas"):
        slide.notes_slide.notes_text_frame.text = s["notas"]


def indicadores(slide, kpis, x0, y, ancho_total, n_cols=3):
    w = (ancho_total - 24 * (n_cols - 1)) / n_cols
    for i, k in enumerate(kpis):
        x = x0 + i * (w + 24)
        caja(slide, x, y, w, 112, LAVANDA)
        texto(slide, x + 16, y + 10, w - 32, 18, k["etiqueta"].upper(), fam=TITULO, tam=9, color=CORAL)
        texto(slide, x + 16, y + 30, w - 32, 38, k["valor"], fam=TITULO, tam=21, color=VIOLETA, ancla=MSO_ANCHOR.MIDDLE)
        if k.get("detalle"):
            texto(slide, x + 16, y + 72, w - 32, 36, k["detalle"], tam=9.5, color=GRIS)


def grafico(slide, g, x, y, w, h):
    datos = CategoryChartData()
    datos.categories = g["categorias"]
    for s in g["series"]:
        datos.add_series(s["nombre"], s["valores"])
    gf = slide.shapes.add_chart(TIPOS_GRAFICO[g["tipo"]], px(x), px(y), px(w), px(h), datos)
    ch = gf.chart
    ch.has_title = True
    ch.chart_title.text_frame.text = g["titulo"]
    tp = ch.chart_title.text_frame.paragraphs[0]
    for r in tp.runs:
        r.font.size = Pt(11); r.font.name = TITULO; r.font.bold = True; r.font.color.rgb = VIOLETA
    ch.has_legend = len(g["series"]) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(9); ch.legend.font.name = CUERPO
    ch.font.size = Pt(9); ch.font.name = CUERPO; ch.font.color.rgb = TEXTO
    colores = [CORAL, VIOLETA, ROSA]
    plot = ch.plots[0]
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(9); dl.font.name = TITULO; dl.font.bold = True
    dl.number_format = {0: '0', 1: '0.0', 2: '0.00'}[g.get("decimales", 1)]; dl.number_format_is_linked = False
    if g["tipo"] in LINEALES:
        dl.position = XL_LABEL_POSITION.ABOVE
    else:
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        plot.gap_width = 60
    for i, serie in enumerate(plot.series):
        color = colores[i % 3]
        if g["tipo"] in LINEALES:
            serie.format.line.color.rgb = color; serie.format.line.width = Pt(2.5)
            serie.marker.format.fill.solid(); serie.marker.format.fill.fore_color.rgb = color
            serie.marker.format.line.color.rgb = color
            serie.smooth = g["tipo"] == "curva"
        else:
            serie.format.fill.solid(); serie.format.fill.fore_color.rgb = color
            if len(g["series"]) == 1:      # una sola serie: negativos en violeta
                for j, v in enumerate(g["series"][0]["valores"]):
                    if v < 0:
                        pt = serie.points[j]
                        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = VIOLETA
    va = ch.value_axis
    if g["tipo"] in LINEALES:
        # como en el original: el eje no arranca en 0, así se ve la forma de la curva
        import math
        todos = [v for se in g["series"] for v in se["valores"] if v is not None]
        bajo, alto = min(todos), max(todos)
        margen = max((alto - bajo) * 0.4, abs(alto) * 0.02, 0.5)
        va.minimum_scale = math.floor(bajo - margen)
        va.maximum_scale = math.ceil(alto + margen * 0.6)
        # etiquetas: la serie más alta (en promedio) arriba de sus puntos, las demás abajo, para que no se pisen
        prom = [sum(v for v in se["valores"] if v is not None) / max(1, sum(v is not None for v in se["valores"]))
                for se in g["series"]]
        mas_alta = prom.index(max(prom))
        for i, serie in enumerate(plot.series):
            serie.data_labels.position = XL_LABEL_POSITION.ABOVE if i == mas_alta else XL_LABEL_POSITION.BELOW
            serie.data_labels.font.size = Pt(9); serie.data_labels.font.name = TITULO; serie.data_labels.font.bold = True
            serie.data_labels.number_format = dl.number_format; serie.data_labels.number_format_is_linked = False
            serie.data_labels.show_value = True
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xE6, 0xE6, 0xE6)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(8)
    ch.category_axis.tick_labels.font.size = Pt(9)
    ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW   # etiquetas afuera, aunque haya negativos
    if g["tipo"] == "barras_h":
        ch.category_axis.reverse_order = True                           # la primera categoría arriba
    ch.category_axis.format.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)


def diapo_datos(slide, s):
    indicadores(slide, s["indicadores"], 48, 236, 1184)
    tiene_bajada_corta = True
    grafico(slide, s["grafico"], 48, 368, 662, 262)
    if s.get("fuente"):
        texto(slide, 58, 636, 650, 36, "Fuente: " + s["fuente"], tam=8, color=GRIS)
    cad = s["cadena"]
    caja(slide, 734, 368, 498, 300, CORAL_SUAVE)
    texto(slide, 754, 382, 458, 24, cad["titulo"], fam=TITULO, tam=13, color=CORAL)
    texto(slide, 754, 416, 458, 240, ["• " + p for p in cad["puntos"]], tam=11.5, color=TEXTO)


def diapo_estrategia(slide, s):
    y_graf = 236
    if s.get("indicadores"):
        indicadores(slide, s["indicadores"], 48, 236, 538, n_cols=1)
        y_graf = 360
    grafico(slide, s["grafico"], 48, y_graf, 538, 584 - y_graf)
    for i, p in enumerate(s["perfiles"]):
        y = 236 + i * 118
        caja(slide, 610, y, 622, 104, LAVANDA)
        pill = caja(slide, 624, y + 15, 150, 74, PERFIL_COLOR[p["perfil"]])
        texto(slide, 624, y + 15, 150, 74, p["perfil"], fam=TITULO, tam=10.5, color=BLANCO,
              alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
        texto(slide, 790, y + 8, 428, 90, p["texto"], tam=10.5, color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)
    for i, a in enumerate(s.get("acciones", [])):
        x = 48 + i * 403
        caja(slide, x, 600, 379, 70, CORAL_SUAVE)
        texto(slide, x + 16, 604, 347, 62, a, tam=10.5, color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)
    if s.get("fuente"):
        texto(slide, 48, 586, 538, 12, "Fuente: " + s["fuente"], tam=7, color=GRIS)


def diapo_agenda(slide, s):
    texto(slide, 900, 196, 332, 24, "**■** Internacional     **■** Argentina", tam=9.5, color=GRIS, alinear=PP_ALIGN.RIGHT)
    # colorear los cuadraditos de la leyenda
    p = slide.shapes[-1].text_frame.paragraphs[0]
    p.runs[0].font.color.rgb = CORAL; p.runs[2].font.color.rgb = VIOLETA
    for i, ev in enumerate(s["eventos"]):
        col, fila = divmod(i, 4)
        x, y = 48 + col * 604, 236 + fila * 108
        caja(slide, x, y, 580, 94, LAVANDA)
        color = CORAL if ev["ambito"] == "internacional" else VIOLETA
        caja(slide, x + 14, y + 18, 112, 58, color)
        texto(slide, x + 14, y + 18, 112, 58, ev["fecha"], fam=TITULO, tam=10, color=BLANCO,
              alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
        cuerpo = [f"**{ev['titulo']}**"] + ([ev["detalle"]] if ev.get("detalle") else [])
        texto(slide, x + 142, y + 8, 424, 80, cuerpo, tam=11, color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)


def diapo_disclaimer(slide, n, total, logo, esquinas, d):
    slide.shapes.add_picture(esquinas, 0, 0, width=px(1280))
    slide.shapes.add_picture(logo, px(48), px(26), width=px(150))
    texto(slide, 700, 36, 532, 20, d["fecha"], tam=10, color=GRIS, alinear=PP_ALIGN.RIGHT)
    texto(slide, 140, 200, 1000, 50, "Disclaimer", fam=TITULO, tam=30, color=VIOLETA)
    caja(slide, 140, 270, 1000, 250, LAVANDA)
    texto(slide, 170, 290, 940, 210, DISCLAIMER, tam=13, color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)
    texto(slide, 140, 540, 1000, 24, "www.insiderfinance.com.ar", fam=TITULO, tam=12, color=CORAL, alinear=PP_ALIGN.CENTER)
    texto(slide, 1100, 684, 132, 20, f"{n} / {total}", tam=9, color=GRIS, alinear=PP_ALIGN.RIGHT)


def armar(d, kit, destino):
    prs = Presentation()
    prs.slide_width, prs.slide_height = px(1280), px(720)
    vacio = prs.slide_layouts[6]
    total = len(d["diapositivas"]) + 1
    with tempfile.TemporaryDirectory() as tmp:
        logo, esq = str(Path(tmp, "logo.png")), str(Path(tmp, "esquinas.png"))
        svg_a_png(kit, "logo-horizontal-color.svg", 900, logo)
        svg_a_png(kit, "hexagonos-esquinas-16x9.svg", 1920, esq)
        for n, s in enumerate(d["diapositivas"], 1):
            slide = prs.slides.add_slide(vacio)
            encabezado(slide, d, s, n, total, logo)
            {"datos": diapo_datos, "estrategia": diapo_estrategia, "agenda": diapo_agenda}[s["tipo"]](slide, s)
        diapo_disclaimer(prs.slides.add_slide(vacio), total, total, logo, esq, d)
        prs.save(destino)


def main():
    ap = argparse.ArgumentParser(description="D01 - Informe Visual")
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
        print("NO SE GENERÓ EL INFORME. Errores:")
        for x in errores:
            print(" -", x)
        sys.exit(1)
    salida = Path(a.salida); salida.mkdir(parents=True, exist_ok=True)
    pptx = salida / f"{a.nombre}.pptx"
    armar(sin_sustituciones(datos), a.kit, str(pptx))   # "T2X6" no se convierte en "T2×6"
    r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(salida), str(pptx)],
                       capture_output=True, text=True, timeout=240)
    if r.returncode != 0 or not (salida / f"{a.nombre}.pdf").exists():
        sys.exit(f"ERROR: se generó el PowerPoint pero falló el PDF: {r.stderr[-300:]}")
    print(f"OK: {pptx} y {salida / (a.nombre + '.pdf')}")


if __name__ == "__main__":
    main()
