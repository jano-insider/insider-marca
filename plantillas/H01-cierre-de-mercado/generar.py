#!/usr/bin/env python3
"""
Plantilla H01 - Cierre de mercado (historia de Instagram 1080x1920).

Uso:
    python3 generar.py datos.json --kit /tmp/marca --salida /mnt/session/outputs --nombre cierre-dolares-02-11

Lee una ficha de datos (JSON), la valida completa y, solo si todo está bien,
genera <nombre>.svg (editable) y <nombre>.png (final). Si algo está mal,
no genera nada y lista todos los errores (todo o nada).

Requisitos: fuentes del kit instaladas (Insider Sans Expanded y Numans) y
el archivo isotipo-color.svg en la carpeta --kit.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import logo_tercero

ANCHO, ALTO = 1080, 1920
CORAL, VIOLETA, BLANCO = "#EE7563", "#573D8B", "#FFFFFF"
TITULO = "Insider Sans Expanded"   # se usa con peso 700 (Bold), igual que las piezas publicadas
CUERPO = "Numans"

DIAS = "Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo"
RE_FECHA = re.compile(rf"^({DIAS}) \d{{2}}/\d{{2}}$")
RE_HORA = re.compile(r"^\d{2}:\d{2}$")
RE_NOMBRE = re.compile(r"^[A-ZÁÉÍÓÚÑ0-9&.\- ]{1,14}$")
RE_VALOR = re.compile(r"^\d{1,3}(\.\d{3})*(,\d{1,2})?( ARS| USD)?$")
RE_VARIACION = re.compile(r"^\d{1,3}(\.\d{3})*,\d{2}%$")
RE_RIESGO = re.compile(r"^\d{1,3}(\.\d{3})*$")
TENDENCIAS = {"sube", "baja", "igual"}
SECCIONES = {"Dólares", "Índices"}
# Índices fijos y su logo (logos-terceros/indices/<clave>.png). Sin logo, se escribe el nombre.
INDICES = {"S&P 500": "SPX", "NASDAQ": "NASDAQ", "DOW JONES": "DJI", "MSCI": "MSCI", "MERVAL": "MERVAL"}
# Versión Índices: siempre estos cuatro, en este orden (definido por marketing). Solo cambian los valores.
ORDEN_INDICES = ["S&P 500", "NASDAQ", "DOW JONES", "MSCI", "MERVAL"]   # marketing: el Merval va siempre con los índices
ORDEN_DOLARES = ["OFICIAL", "MEP", "CABLE", "BLUE"]
TOLERANCIA = 0.05   # puntos porcentuales de diferencia admitidos al recalcular la variación


# ---------------------------------------------------------------- validación
def numero(txt):
    """'1.566 ARS' -> 1566.0 ; '53,08 USD' -> 53.08 ; '0,32' -> 0.32. None si no es número."""
    m = re.match(r"^\s*([\d.]+(?:,\d+)?)", str(txt or ""))
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except ValueError:
        return None

def validar(d):
    """Devuelve la lista de errores. Lista vacía = ficha válida."""
    e = []
    if not isinstance(d, dict):
        return ["La ficha tiene que ser un objeto JSON."]
    permitidas = {"fecha", "hora", "seccion", "filas", "riesgo_pais", "leyenda"}
    for k in d:
        if k not in permitidas:
            e.append(f"Campo desconocido: '{k}'.")
    if "leyenda" in d and (not isinstance(d["leyenda"], str) or not 0 < len(d["leyenda"]) <= 60):
        e.append("leyenda: texto de hasta 60 caracteres.")
    if not RE_FECHA.match(str(d.get("fecha", ""))):
        e.append("fecha: tiene que ser 'Día dd/mm', por ejemplo 'Lunes 02/11'.")
    if not RE_HORA.match(str(d.get("hora", ""))):
        e.append("hora: tiene que ser 'hh:mm', por ejemplo '18:05'.")
    if d.get("seccion") not in SECCIONES:
        e.append("seccion: tiene que ser 'Dólares' o 'Índices'.")

    def fila_ok(f, donde, re_valor):
        if not isinstance(f, dict):
            e.append(f"{donde}: tiene que ser un objeto.")
            return
        claves = {"valor", "variacion", "tendencia", "valor_anterior"} | ({"nombre"} if donde.startswith("filas") else set())
        for k in f:
            if k not in claves:
                e.append(f"{donde}: campo desconocido '{k}'.")
        if "nombre" in claves and not RE_NOMBRE.match(str(f.get("nombre", ""))):
            e.append(f"{donde}.nombre: mayúsculas, hasta 14 caracteres (ej. 'OFICIAL', 'S&P 500').")
        if not re_valor.match(str(f.get("valor", ""))):
            e.append(f"{donde}.valor: formato inválido ('{f.get('valor')}').")
        var = str(f.get("variacion", ""))
        if not RE_VARIACION.match(var):
            e.append(f"{donde}.variacion: formato 'n,nn%' sin signo (ej. '0,32%').")
        t = f.get("tendencia")
        if t not in TENDENCIAS:
            e.append(f"{donde}.tendencia: 'sube', 'baja' o 'igual'.")
        elif RE_VARIACION.match(var):
            cero = var == "0,00%"
            if cero and t != "igual":
                e.append(f"{donde}: variación 0,00% tiene que tener tendencia 'igual'.")
            if not cero and t == "igual":
                e.append(f"{donde}: tendencia 'igual' solo con variación 0,00%.")
        # Control de Rosario: si viene el valor del día anterior, la variación y la flecha tienen que cerrar
        if "valor_anterior" in f:
            hoy, ayer = numero(f.get("valor")), numero(f.get("valor_anterior"))
            if hoy is None or ayer is None or ayer == 0:
                e.append(f"{donde}.valor_anterior: formato inválido ('{f.get('valor_anterior')}').")
            elif RE_VARIACION.match(var) and t in TENDENCIAS:
                real = (hoy - ayer) / ayer * 100
                informada = numero(var.rstrip("%"))
                if abs(abs(real) - informada) > TOLERANCIA:
                    e.append(f"{donde}: la variación informada ({var}) no coincide con la calculada "
                             f"({abs(real):.2f}%) entre {f.get('valor_anterior')} y {f.get('valor')}.")
                esperada = "igual" if round(real, 2) == 0 else ("sube" if real > 0 else "baja")
                if t != esperada:
                    e.append(f"{donde}: la flecha dice '{t}' pero el valor {('subió' if real > 0 else 'bajó') if esperada != 'igual' else 'no cambió'} respecto del día anterior.")

    filas = d.get("filas")
    if d.get("seccion") == "Índices" and isinstance(filas, list):
        nombres = [f.get("nombre") if isinstance(f, dict) else None for f in filas]
        if nombres != ORDEN_INDICES:
            e.append(f"filas: en Índices van siempre {ORDEN_INDICES}, en ese orden.")
    if d.get("seccion") == "Dólares" and isinstance(filas, list):
        nombres = [f.get("nombre") if isinstance(f, dict) else None for f in filas]
        if nombres != ORDEN_DOLARES:
            e.append(f"filas: en Dólares van siempre {ORDEN_DOLARES}, en ese orden.")
    if not isinstance(filas, list) or not 1 <= len(filas) <= 5:
        e.append("filas: entre 1 y 5 filas.")
    else:
        for i, f in enumerate(filas, 1):
            fila_ok(f, f"filas[{i}]", RE_VALOR)
    if d.get("seccion") == "Índices":
        if "riesgo_pais" not in d:
            e.append("riesgo_pais: es obligatorio en la versión Índices.")
    if "riesgo_pais" in d:
        fila_ok(d["riesgo_pais"], "riesgo_pais", RE_RIESGO)
    return e


def fuentes_instaladas():
    salida = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
    return all(f in salida for f in ("Insider Sans Expanded", "Numans"))


# ---------------------------------------------------------------- dibujo
def flecha(cx, cy, tendencia, color, tam=67):
    """Ícono de tendencia centrado en (cx, cy)."""
    if tendencia == "igual":
        w, h = tam * 1.25, tam * 0.24
        return (f'<rect x="{cx - w/2:.1f}" y="{cy - h*1.35:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{color}"/>'
                f'<rect x="{cx - w/2:.1f}" y="{cy + h*0.35:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{color}"/>')
    s = tam / 2
    puntos = [(0, -s), (s, -0.05 * s), (0.42 * s, -0.05 * s), (0.42 * s, s),
              (-0.42 * s, s), (-0.42 * s, -0.05 * s), (-s, -0.05 * s)]
    if tendencia == "baja":
        puntos = [(x, -y) for x, y in puntos]
    p = " ".join(f"{cx + x:.1f},{cy + y:.1f}" for x, y in puntos)
    return f'<polygon points="{p}" fill="{color}"/>'


def bandera_argentina(x, y, w=68, h=42):
    f = h / 3
    return (f'<g><rect x="{x}" y="{y}" width="{w}" height="{f:.1f}" fill="#74ACDF"/>'
            f'<rect x="{x}" y="{y + f:.1f}" width="{w}" height="{f:.1f}" fill="#FFFFFF"/>'
            f'<rect x="{x}" y="{y + 2*f:.1f}" width="{w}" height="{f:.1f}" fill="#74ACDF"/>'
            f'<circle cx="{x + w/2}" cy="{y + h/2}" r="{f*0.38:.1f}" fill="#F6B40E"/></g>')


def isotipo(kit):
    svg = (Path(kit) / "isotipo-color.svg").read_text(encoding="utf-8")
    raiz = re.search(r"<svg\b[^>]*>", svg).group(0)
    nueva = re.sub(r'\s(width|height)="[^"]*"', "", raiz)
    nueva = nueva.replace("<svg", '<svg x="447" y="1585" width="186" height="195"', 1)
    return svg.replace(raiz, nueva, 1)


def armar_svg(d, kit):
    t = lambda s: escape(str(s))
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{ALTO}" viewBox="0 0 {ANCHO} {ALTO}">',
        '<!-- Insider Finance · Plantilla H01 Cierre de mercado -->',
        f'<rect width="{ANCHO}" height="{ALTO}" fill="{BLANCO}"/>',
        f'<rect x="0" y="0" width="{ANCHO}" height="213" fill="{CORAL}"/>',
        f'<rect x="0" y="1836" width="{ANCHO}" height="84" fill="{CORAL}"/>',
        f'<text x="540" y="330" text-anchor="middle" font-family="{TITULO}" font-weight="700" font-size="63.6" fill="{CORAL}">CIERRE DE MERCADO</text>',
        # píldora de fecha: el ancho lo ajusta el render al largo del texto
        f'<rect id="pildora" x="132" y="355" width="347" height="77" rx="38.5" fill="{VIOLETA}"/>',
        f'<text id="fecha" x="305.5" y="393.5" text-anchor="middle" dominant-baseline="central" font-family="{CUERPO}" font-size="57.7" fill="{BLANCO}">{t(d["fecha"])}</text>',
        f'<text id="hora" x="305.5" y="478" text-anchor="middle" dominant-baseline="central" font-family="{CUERPO}" font-size="42.7" fill="{VIOLETA}">hora: {t(d["hora"])} hs</text>',
        f'<text x="540" y="636" text-anchor="middle" dominant-baseline="central" font-family="{CUERPO}" font-size="83" fill="{VIOLETA}">{t(d["seccion"])}</text>',
        f'<rect x="409" y="690" width="262" height="4" rx="2" fill="{CORAL}"/>',
    ]
    n = len(d["filas"])
    paso = 128 if n <= 4 else 108            # con el Merval son 5 filas: se compactan para que entre todo
    y = 884
    for i, f in enumerate(d["filas"]):
        logo = logo_tercero("indices", INDICES[f["nombre"]], kit) if d["seccion"] == "Índices" else None
        if logo:
            etiqueta = (f'<image href="{logo}" x="72" y="{y - 32}" width="235" height="64" '
                        f'preserveAspectRatio="xMinYMid meet"/>')
        else:
            etiqueta = (f'<text class="etiqueta" x="72" y="{y}" dominant-baseline="central" font-family="{TITULO}" '
                        f'font-weight="700" font-size="35" fill="{VIOLETA}">{t(f["nombre"])}</text>')
        partes += [
            etiqueta,
            f'<text x="330" y="{y}" dominant-baseline="central" font-family="{CUERPO}" font-size="42.7" fill="{VIOLETA}">{t(f["valor"])}</text>',
            f'<text x="880" y="{y}" text-anchor="end" dominant-baseline="central" font-family="{CUERPO}" font-size="42.7" fill="{VIOLETA}">{t(f["variacion"])}</text>',
            flecha(971, y, f["tendencia"], CORAL),
        ]
        y += paso
    sep = y - paso + 112
    partes.append(f'<rect x="132" y="{sep}" width="809" height="3" rx="1.5" fill="{CORAL}"/>')
    if "riesgo_pais" in d:
        r = d["riesgo_pais"]
        by = sep + 44
        cy = by + 38.5
        partes += [
            f'<rect x="52" y="{by}" width="958" height="77" rx="8" fill="{VIOLETA}"/>',
            bandera_argentina(74, by + 17.5),
            f'<text x="160" y="{cy}" dominant-baseline="central" font-family="{TITULO}" font-weight="700" font-size="28" fill="{BLANCO}">Riesgo País</text>',
            f'<text x="430" y="{cy}" dominant-baseline="central" font-family="{CUERPO}" font-size="39" fill="{BLANCO}">{t(r["valor"])}</text>',
            f'<text x="880" y="{cy}" text-anchor="end" dominant-baseline="central" font-family="{CUERPO}" font-size="39" fill="{BLANCO}">{t(r["variacion"])}</text>',
            f'<circle cx="963" cy="{cy}" r="31" fill="{BLANCO}"/>',
            flecha(963, cy, r["tendencia"], VIOLETA, tam=38),
        ]
    partes.append(isotipo(kit))
    # Leyenda legal (marketing: va siempre en las placas diarias de dólar e índices)
    leyenda = d.get("leyenda", f"*Valores al cierre del {d['fecha']}, hora {d['hora']} hs.")
    partes.append(f'<text x="540" y="1818" text-anchor="middle" font-family="{CUERPO}" font-size="29" fill="{CORAL}">{t(leyenda)}</text>')
    partes.append("</svg>")
    return "\n".join(partes)


# ---------------------------------------------------------------- render
AJUSTES_JS = """
() => {
  // píldora de fecha: ancho = texto + 64 px de margen, centrada en el texto
  const f = document.getElementById('fecha').getBBox();
  const p = document.getElementById('pildora');
  const w = f.width + 64;
  p.setAttribute('x', (305.5 - w / 2).toFixed(1));
  p.setAttribute('width', w.toFixed(1));
  // etiquetas: si una es muy larga, se achica para no pisar el valor
  for (const el of document.querySelectorAll('.etiqueta')) {
    let size = 35;
    while (el.getBBox().width > 235 && size > 22) {
      size -= 1; el.setAttribute('font-size', size);
    }
  }
  return new XMLSerializer().serializeToString(document.documentElement);
}
"""


def render(svg, salida, nombre):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": ANCHO, "height": ALTO})
        pag.set_content(svg)
        pag.wait_for_timeout(300)
        svg_final = pag.evaluate(AJUSTES_JS)
        pag.screenshot(path=str(salida / f"{nombre}.png"))
        nav.close()
    (salida / f"{nombre}.svg").write_text(svg_final, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Plantilla H01 - Cierre de mercado")
    ap.add_argument("datos")
    ap.add_argument("--kit", required=True, help="carpeta con isotipo-color.svg")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--nombre", required=True)
    a = ap.parse_args()

    if not re.match(r"^[a-z0-9\-]{1,60}$", a.nombre):
        sys.exit("ERROR: --nombre solo minúsculas, números y guiones (máx. 60).")
    try:
        datos = json.loads(Path(a.datos).read_text(encoding="utf-8"))
    except Exception as ex:
        sys.exit(f"ERROR: no se pudo leer la ficha JSON: {ex}")
    errores = validar(datos)
    if not fuentes_instaladas():
        errores.append("Faltan las fuentes del kit (Insider Sans Expanded / Numans). Corré la preparación.")
    if not (Path(a.kit) / "isotipo-color.svg").exists():
        errores.append(f"Falta {a.kit}/isotipo-color.svg. Bajalo del kit de marca.")
    if errores:
        print("NO SE GENERÓ LA PIEZA. Errores en la ficha:")
        for x in errores:
            print(" -", x)
        sys.exit(1)

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    render(armar_svg(datos, a.kit), salida, a.nombre)
    print(f"OK: {salida / (a.nombre + '.png')} y {salida / (a.nombre + '.svg')}")


if __name__ == "__main__":
    main()
