"""
Módulo común de las plantillas de Insider Finance.

Cada plantilla (H02, H03, ...) arma su diseño en HTML/CSS y usa este módulo para:
  - validar la ficha de datos (todo o nada),
  - verificar que estén las fuentes y los recursos del kit,
  - incrustar logos y hexágonos oficiales (sin redibujarlos),
  - renderizar con Chromium: PNG final + PDF vectorial (editable en Illustrator).

Ningún texto de la ficha se inserta sin escapar: lo que escriba el modelo
nunca puede convertirse en código dentro de la pieza.
"""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

CORAL, VIOLETA, BLANCO = "#EE7563", "#573D8B", "#FFFFFF"
FUENTES = ("Insider Sans Expanded", "Numans")


# ------------------------------------------------------------- validación
class Ficha:
    """Junta todos los errores de una ficha antes de decidir."""

    def __init__(self, datos, permitidas):
        self.d = datos if isinstance(datos, dict) else {}
        self.errores = [] if isinstance(datos, dict) else ["La ficha tiene que ser un objeto JSON."]
        for k in self.d:
            if k not in permitidas:
                self.errores.append(f"Campo desconocido: '{k}'.")

    def texto(self, clave, maximo, obligatorio=True, patron=None, ayuda=""):
        v = self.d.get(clave)
        if v is None or v == "":
            if obligatorio:
                self.errores.append(f"{clave}: falta. {ayuda}".strip())
            return
        if not isinstance(v, str):
            self.errores.append(f"{clave}: tiene que ser texto.")
        elif len(v) > maximo:
            self.errores.append(f"{clave}: máximo {maximo} caracteres (tiene {len(v)}).")
        elif patron and not re.match(patron, v):
            self.errores.append(f"{clave}: formato inválido. {ayuda}".strip())

    def lista(self, clave, minimo, maximo, largo_item, obligatorio=True, patron=None, ayuda=""):
        v = self.d.get(clave)
        if v is None:
            if obligatorio:
                self.errores.append(f"{clave}: falta.")
            return
        if not isinstance(v, list) or not minimo <= len(v) <= maximo:
            self.errores.append(f"{clave}: entre {minimo} y {maximo} elementos.")
            return
        for i, x in enumerate(v, 1):
            if not isinstance(x, str) or not 0 < len(x) <= largo_item:
                self.errores.append(f"{clave}[{i}]: texto de hasta {largo_item} caracteres.")
            elif patron and not re.match(patron, x):
                self.errores.append(f"{clave}[{i}]: formato inválido. {ayuda}".strip())

    def opcion(self, clave, opciones, obligatorio=True):
        v = self.d.get(clave)
        if v is None and not obligatorio:
            return
        if v not in opciones:
            self.errores.append(f"{clave}: tiene que ser uno de {sorted(opciones)}.")


# ------------------------------------------------------------- texto seguro
def t(s):
    """Escapa texto para HTML. Permite **resaltado** como único formato."""
    s = html.escape(str(s), quote=True)
    return re.sub(r"\*\*(.+?)\*\*", r'<b class="res">\1</b>', s)


def multilinea(s):
    return "<br>".join(t(x) for x in str(s).split("\n"))


# ------------------------------------------------------------- kit de marca
def svg_kit(kit, archivo, clase=""):
    """Devuelve el SVG oficial para incrustar inline (vectorial en el PDF)."""
    ruta = Path(kit) / archivo
    svg = ruta.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    raiz = re.search(r"<svg\b[^>]*>", svg).group(0)
    nueva = re.sub(r'\s(width|height)="[^"]*"', "", raiz)
    nueva = nueva.replace("<svg", f'<svg class="{clase}" preserveAspectRatio="xMidYMid meet"', 1)
    return svg.replace(raiz, nueva, 1)


def sin_sustituciones(obj):
    """Para PowerPoint y Word: mete un espacio pelo (U+200A, el más fino que existe) entre un número y una
    X seguida de número ("T2X6" -> "T2\u200aX6"), para que la fuente no lo convierta en "2×6" y cambie
    un ticker. Un separador invisible no alcanza: el motor de texto lo ignora. Los números quedan igual."""
    if isinstance(obj, str):
        return re.sub(r"(\d)([xX])(?=\d)", "\\1\u200a\\2", obj)
    if isinstance(obj, list):
        return [sin_sustituciones(x) for x in obj]
    if isinstance(obj, dict):
        return {k: sin_sustituciones(v) for k, v in obj.items()}
    return obj


def fondo_kit(kit, archivo, ancho, alto):
    """Fondo de la pieza sacado del original (PNG del kit), a página completa."""
    import base64
    datos = Path(kit, archivo).read_bytes()
    return (f'<img class="abs" src="data:image/png;base64,{base64.b64encode(datos).decode()}" '
            f'style="left:0;top:0;width:{ancho}px;height:{alto}px">')


def foto_uri(ruta):
    """Foto que adjuntó quien pide la pieza, incrustada (PNG o JPG)."""
    import base64
    datos = Path(ruta).read_bytes()
    tipo = "png" if datos.startswith(b"\x89PNG") else "jpeg"
    return f"data:image/{tipo};base64," + base64.b64encode(datos).decode()


def es_imagen(ruta):
    return isinstance(ruta, str) and Path(ruta).is_file() and Path(ruta).read_bytes()[:3] in (b"\x89PN", b"\xff\xd8\xff")


def caja(x, y, w, h, contenido, alinear="center", vertical="flex-start", extra="", campo=None):
    """Bloque de texto en la posición exacta del original."""
    aj = f' ajusta" data-campo="{campo}' if campo else ""
    return (f'<div class="abs{aj}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;flex-direction:column;'
            f'justify-content:{vertical};align-items:{ {"center": "center", "left": "flex-start", "right": "flex-end"}[alinear] };'
            f'text-align:{alinear};overflow:hidden;{extra}">{contenido}</div>')


def banda(kit, archivo, x, y, ancho, alto, opacidad):
    """Banda de hexágonos tal como está en el original de Canva: posición, tamaño
    (estirada igual que en Canva) y transparencia exactas."""
    svg = svg_kit(kit, archivo).replace('preserveAspectRatio="xMidYMid meet"', 'preserveAspectRatio="none"', 1)
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{ancho}px;height:{alto}px;'
            f'opacity:{opacidad}">{svg}</div>')


def faltantes(kit, archivos):
    e = []
    salida = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
    for f in FUENTES:
        if f not in salida:
            e.append(f"Falta la fuente '{f}'. Corré la preparación del kit.")
    if "Bold Italic" not in salida:
        e.append("Falta Insider Sans Expanded Bold Italic. Corré la preparación del kit.")
    for a in archivos:
        if not (Path(kit) / a).exists():
            e.append(f"Falta {kit}/{a}. Bajalo del kit de marca.")
    return e


# ------------------------------------------------------------- HTML base
def pagina(ancho, alto, css, cuerpo, fondo=BLANCO):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@page {{ size: {ancho}px {alto}px; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {ancho}px; height: {alto}px; }}
body {{ position: relative; overflow: hidden; background: {fondo};
       font-family: 'Numans'; color: {VIOLETA}; -webkit-print-color-adjust: exact; print-color-adjust: exact;
       font-variant-ligatures: no-contextual; font-feature-settings: "calt" 0; }}
/* sin sustituciones automáticas de la fuente: "T2X6" no puede convertirse en "T2×6" (cambiaría el ticker) */
* {{ font-feature-settings: "calt" 0; }}
.tit {{ font-family: 'Insider Sans Expanded'; font-weight: 700; }}
.ita {{ font-family: 'Insider Sans Expanded'; font-weight: 700; font-style: italic; }}
.res {{ font-family: 'Insider Sans Expanded'; font-weight: 700; }}
.abs {{ position: absolute; }}
div > svg {{ width: 100%; height: 100%; display: block; }}
.esq-sd {{ position: absolute; right: 0; top: 0; width: 560px; height: 140px; }}
.esq-ii {{ position: absolute; left: 0; bottom: 0; width: 560px; height: 140px; }}
{css}
</style></head><body>{cuerpo}</body></html>"""


def esquinas(kit):
    return (svg_kit(kit, "hexagonos-esquina-sup-der.svg", "esq-sd")
            + svg_kit(kit, "hexagonos-esquina-inf-izq.svg", "esq-ii"))


# ------------------------------------------------------------- render
JS_ENCOGER = """
() => {
  // Títulos con palabras muy largas: se achican de a 2 px (hasta 60%) para que ninguna palabra se salga.
  for (const el of document.querySelectorAll('.encoge')) {
    const base = parseFloat(getComputedStyle(el).fontSize);
    let tam = base;
    while (el.scrollWidth > el.clientWidth + 1 && tam > base * 0.6) {
      tam -= 2; el.style.fontSize = tam + 'px';
    }
  }
  // Títulos con alto máximo (data-max en px): se achican hasta entrar (mínimo 45%).
  for (const el of document.querySelectorAll('.encoge-alto')) {
    const base = parseFloat(getComputedStyle(el).fontSize), max = parseFloat(el.dataset.max);
    let tam = base;
    while ((el.scrollHeight > max || el.scrollWidth > el.clientWidth + 1) && tam > base * 0.45) {
      tam -= 2; el.style.fontSize = tam + 'px';
    }
  }
}
"""

JS_CONTROL = """
() => {
  // Devuelve los elementos marcados .ajusta que se desbordan de su caja.
  const malos = [];
  for (const el of document.querySelectorAll('.ajusta')) {
    if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) malos.push(el.dataset.campo || el.className);
  }
  return malos;
}
"""


def render(html_txt, ancho, alto, salida, nombre):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": ancho, "height": alto})
        pag.set_content(html_txt)
        pag.evaluate("document.fonts.ready")
        pag.wait_for_timeout(200)
        pag.evaluate(JS_ENCOGER)
        desbordes = pag.evaluate(JS_CONTROL)
        if desbordes:
            nav.close()
            return [f"El texto de '{c}' no entra en su espacio. Acortalo." for c in desbordes]
        pag.screenshot(path=str(salida / f"{nombre}.png"))
        pag.pdf(path=str(salida / f"{nombre}.pdf"), width=f"{ancho}px", height=f"{alto}px",
                print_background=True, page_ranges="1")
        nav.close()
    return []


def ejecutar(descripcion, validar, armar, ancho, alto, recursos):
    """Punto de entrada común: lee la ficha, valida, arma y renderiza."""
    ap = argparse.ArgumentParser(description=descripcion)
    ap.add_argument("datos")
    ap.add_argument("--kit", required=True, help="carpeta con los SVG del kit (logos y patrones)")
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
    errores += validar(datos)
    errores += faltantes(a.kit, recursos)
    if not errores:
        salida = Path(a.salida)
        salida.mkdir(parents=True, exist_ok=True)
        errores = render(armar(datos, a.kit), ancho, alto, salida, a.nombre)
    if errores:
        print("NO SE GENERÓ LA PIEZA. Errores:")
        for x in errores:
            print(" -", x)
        sys.exit(1)
    print(f"OK: {a.salida}/{a.nombre}.png y {a.salida}/{a.nombre}.pdf")


# ------------------------------------------------------------- logos de terceros
REPO = "https://raw.githubusercontent.com/jano-insider/insider-marca/main"
RE_CLAVE = re.compile(r"^[A-Z0-9]{1,10}$")


def logo_tercero(tipo, clave, kit):
    """Logo de un índice o empresa (PNG) como data URI, o None si no está.

    Busca primero en <kit>/terceros/<tipo>/<clave>.png; si no está, lo baja del
    repositorio y lo guarda ahí. Si no existe, devuelve None y la plantilla
    usa el ticker en texto: un logo faltante nunca frena una pieza.
    """
    import base64
    import urllib.request
    if tipo not in ("indices", "empresas") or not RE_CLAVE.match(clave):
        return None                       # nada armado con texto libre llega a una URL
    local = Path(kit) / "terceros" / tipo / f"{clave}.png"
    if not local.exists():
        try:
            with urllib.request.urlopen(f"{REPO}/logos-terceros/{tipo}/{clave}.png", timeout=10) as r:
                datos = r.read(2_000_000)
        except Exception:
            return None
        if not datos.startswith(b"\x89PNG"):
            return None                   # solo se aceptan PNG reales
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(datos)
    datos = local.read_bytes()
    if not datos.startswith(b"\x89PNG"):
        return None
    return "data:image/png;base64," + base64.b64encode(datos).decode()
