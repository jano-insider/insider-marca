#!/usr/bin/env python3
"""D02 - Documento · Hoja membretada (Word A4 + PDF).

Uso:
    python3 generar.py datos.json --kit /tmp/marca --salida /mnt/session/outputs --nombre carta-cliente

Ficha:
    {"titulo": "...", "parrafos": ["...", "..."], "cierre": "..."}   (cierre opcional)
En los párrafos, **así** pone una parte en negrita.

Necesita en --kit: logo-horizontal-color.svg, banda-hexagonos-lateral.png e
icono-telefono/instagram/linkedin/web.png. Genera <nombre>.docx y <nombre>.pdf.
El PDF lleva las fuentes incrustadas; el Word necesita las fuentes del kit
instaladas en la PC donde se abra.
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, faltantes  # noqa: E402

from docx import Document  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402

VIOLETA = RGBColor(0x57, 0x3D, 0x8B)
TEXTO = RGBColor(0x1F, 0x1F, 0x1F)
GRIS = RGBColor(0x4D, 0x4D, 0x4D)
TITULO, CUERPO = "Insider Sans Expanded", "Numans"
CONTACTO = [("icono-telefono.png", "54 9 11 7237-4932"), ("icono-instagram.png", "@insider.arg"),
            ("icono-linkedin.png", "Insider Finance"), ("icono-web.png", "www.insiderfinance.com.ar")]
RECURSOS = ["logo-horizontal-color.svg", "banda-hexagonos-lateral.png"] + [c[0] for c in CONTACTO]


def validar(d):
    f = Ficha(d, {"titulo", "parrafos", "cierre"})
    f.texto("titulo", 100)
    f.lista("parrafos", 1, 30, 1500)
    f.texto("cierre", 200, obligatorio=False)
    return f.errores


def fuente(run, nombre, tam, color, negrita=False, italica=False):
    run.font.name = nombre
    run.font.size = Pt(tam)
    run.font.color.rgb = color
    run.font.bold = negrita
    run.font.italic = italica
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), nombre)


def logo_png(kit, destino):
    """Renderiza el logo oficial (SVG) a PNG de alta resolución para el Word."""
    from playwright.sync_api import sync_playwright
    svg = Path(kit, "logo-horizontal-color.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1200, "height": 400})
        pag.set_content('<html><body style="margin:0;background:transparent">'
                        f'<div id="l" style="width:1200px">{svg}</div>'
                        '<style>#l svg{width:1200px;height:auto;display:block}</style></body></html>')
        pag.wait_for_timeout(300)
        pag.locator("#l").screenshot(path=destino, omit_background=True)
        nav.close()


def anclar_detras(run, x_cm, y_cm):
    """Convierte la imagen del run en flotante, detrás del texto, en posición fija de página."""
    inline = run._element.find(".//" + qn("wp:inline"))
    ext = inline.find(qn("wp:extent"))
    cx, cy = ext.get("cx"), ext.get("cy")
    emu = lambda cm: str(int(cm * 360000))
    from docx.oxml import parse_xml
    anchor = parse_xml(
        '<wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="0" behindDoc="1" '
        'locked="1" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        f'<wp:positionH relativeFrom="page"><wp:posOffset>{emu(x_cm)}</wp:posOffset></wp:positionH>'
        f'<wp:positionV relativeFrom="page"><wp:posOffset>{emu(y_cm)}</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
        '</wp:anchor>')
    for tag in ("wp:docPr", "wp:cNvGraphicFramePr"):
        nodo = inline.find(qn(tag))
        if nodo is not None:
            anchor.append(copy.deepcopy(nodo))
    anchor.append(copy.deepcopy(inline.find(qn("a:graphic"))))
    inline.getparent().replace(inline, anchor)


def parrafo_con_negritas(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.3
    for i, trozo in enumerate(re.split(r"\*\*(.+?)\*\*", texto)):
        if trozo:
            if i % 2 == 1:   # resaltado: Insider Sans Bold, como en las piezas
                fuente(p.add_run(trozo), TITULO, 10.5, TEXTO, negrita=True)
            else:
                fuente(p.add_run(trozo), CUERPO, 11, TEXTO)


def armar(d, kit, destino_docx):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(4.2), Cm(4.0)
    sec.left_margin, sec.right_margin = Cm(3.4), Cm(2.4)
    sec.header_distance, sec.footer_distance = Cm(1.2), Cm(1.0)

    # Encabezado: logo centrado + banda de hexágonos detrás, al borde izquierdo
    with tempfile.TemporaryDirectory() as tmp:
        png = str(Path(tmp, "logo.png"))
        logo_png(kit, png)
        enc = sec.header.paragraphs[0]
        enc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        enc.add_run().add_picture(png, width=Cm(5.2))
    banda = sec.header.add_paragraph().add_run()
    banda.add_picture(str(Path(kit, "banda-hexagonos-lateral.png")), height=Cm(25))
    anclar_detras(banda, -1.3, 4.4)

    # Pie: datos de contacto, 2 x 2
    pie = sec.footer
    tabla = pie.add_table(rows=2, cols=2, width=Cm(15.2))
    tabla.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, (icono, texto) in enumerate(CONTACTO):
        celda = tabla.cell(i // 2, i % 2)
        p = celda.paragraphs[0]
        p.add_run().add_picture(str(Path(kit, icono)), height=Cm(0.45))
        fuente(p.add_run("   " + texto), CUERPO, 9, GRIS)

    # Cuerpo
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.paragraph_format.space_after = Pt(18)
    fuente(t.add_run(d["titulo"]), TITULO, 20, VIOLETA, negrita=True)
    for texto in d["parrafos"]:
        parrafo_con_negritas(doc, texto)
    if d.get("cierre"):
        c = doc.add_paragraph()
        c.paragraph_format.space_before = Pt(14)
        fuente(c.add_run(d["cierre"]), TITULO, 11, VIOLETA, negrita=True, italica=True)
    doc.save(destino_docx)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="D02 - Hoja membretada")
    ap.add_argument("datos")
    ap.add_argument("--kit", required=True)
    ap.add_argument("--salida", required=True)
    ap.add_argument("--nombre", required=True)
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
        print("NO SE GENERÓ EL DOCUMENTO. Errores:")
        for x in errores:
            print(" -", x)
        sys.exit(1)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    docx_path = salida / f"{a.nombre}.docx"
    armar(datos, a.kit, str(docx_path))
    r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(salida), str(docx_path)],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not (salida / f"{a.nombre}.pdf").exists():
        sys.exit(f"ERROR: se generó el Word pero falló el PDF: {r.stderr[-300:]}")
    print(f"OK: {docx_path} y {salida / (a.nombre + '.pdf')}")


if __name__ == "__main__":
    main()
