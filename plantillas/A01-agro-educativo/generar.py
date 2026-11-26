#!/usr/bin/env python3
"""A01 - Insider AgroFinance · Carrusel educativo (láminas de 1080x1350).
Dirección de marketing (Chari, 26/11/2026): foto de campo con filtro coral o blanco, lo agro grande y lo
financiero más chico, elementos de Insider (hexágonos, coral) para la personalidad. Sin fondo violeta pleno.
  portada: foto adjunta con filtro coral, el tema grande y una bajada opcional más chica, "Deslizá →";
  1 a 4 láminas blancas (título y texto);
  cierre: la misma foto con filtro blanco, título y el llamado fijo "Consultá para recibir asesoramiento" (sin número).
Logo de AgroFinance (blanco en la portada, color en el resto) y pie institucional en todas.
Si lleva cifras, "valores_al" agrega en todas las láminas: "Valores al <corte>. No constituyen recomendación de inversión."
Solo piezas de mercado o educativas: nunca datos de un cliente.

Ficha:
{
  "tema": "¿Vender o guardar la soja?",
  "bajada": "Dos caminos para decidir con números claros",          # opcional
  "foto": "/mnt/session/uploads/campo.jpg",                          # foto de campo adjunta (JPG o PNG)
  "laminas": [{"titulo": "Opción 1 — **Vender** y colocar el dinero a tasa", "texto": "..."}],
  "cierre": {"titulo": "Lo decidís vos, con números claros"},
  "valores_al": "25/11/2026, 17:00"                                  # opcional
}
En títulos de las láminas blancas y del cierre, **así** va en coral.
Genera <nombre>-01.png, <nombre>-02.png, ... y <nombre>.pdf con todas las láminas."""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, svg_kit, foto_uri, es_imagen, faltantes, JS_ENCOGER, CORAL, VIOLETA, BLANCO

W, H = 1080, 1350
GRIS = "#3C3C3C"
PIE = "Un área de Insider Finance · Agente Productor CNV Mat. 1581"
LLAMADO = "Consultá para recibir asesoramiento"
LOGO_COLOR, LOGO_BLANCO = "agro-logo-horizontal-color.png", "agro-logo-vertical-blanco.png"
LOGO_CIERRE = "agro-logo-vertical-color.png"
RECURSOS = [LOGO_COLOR, LOGO_BLANCO, LOGO_CIERRE, "hexagonos-esquina-sup-der.svg"]
C = "238,117,99"   # coral en RGB, para los filtros sobre la foto
FILTRO_CORAL = (f"linear-gradient(to bottom, rgba({C},0.55) 0%, rgba({C},0.10) 26%, rgba({C},0.35) 45%, "
                f"rgba({C},0.88) 68%, rgba({C},0.95) 100%)")
FILTRO_BLANCO = "linear-gradient(to bottom, rgba(255,255,255,0.80) 0%, rgba(255,255,255,0.93) 40%, rgba(255,255,255,0.96) 100%)"


def validar(d):
    f = Ficha(d, {"tema", "bajada", "foto", "laminas", "cierre", "valores_al"})
    f.texto("tema", 70, ayuda="La pregunta o tema de la portada, con lo agro adelante.")
    f.texto("bajada", 90, obligatorio=False, ayuda="Una línea más chica debajo del tema.")
    f.texto("valores_al", 40, obligatorio=False, ayuda="Fecha y hora de corte de las cifras, ej. '25/11/2026, 17:00'.")
    if not es_imagen(d.get("foto")):
        f.errores.append("foto: falta la foto de campo adjunta (ruta a un JPG o PNG en /mnt/session/uploads/).")
    la = d.get("laminas")
    if not isinstance(la, list) or not 1 <= len(la) <= 4:
        f.errores.append("laminas: entre 1 y 4 láminas interiores.")
    else:
        for i, x in enumerate(la, 1):
            if not isinstance(x, dict) or set(x) != {"titulo", "texto"}:
                f.errores.append(f"laminas[{i}]: lleva 'titulo' y 'texto'."); continue
            if not 0 < len(x["titulo"]) <= 60: f.errores.append(f"laminas[{i}].titulo: hasta 60 caracteres.")
            if not 0 < len(x["texto"]) <= 260: f.errores.append(f"laminas[{i}].texto: hasta 260 caracteres.")
    c = d.get("cierre")
    if not isinstance(c, dict) or set(c) != {"titulo"}:
        f.errores.append("cierre: lleva solo 'titulo' (el llamado es fijo: \"Consultá para recibir asesoramiento\").")
    elif not 0 < len(c["titulo"]) <= 60:
        f.errores.append("cierre.titulo: hasta 60 caracteres.")
    return f.errores


def armar(d, kit):
    logo_c = foto_uri(Path(kit) / LOGO_COLOR); logo_b = foto_uri(Path(kit) / LOGO_BLANCO)
    logo_v = foto_uri(Path(kit) / LOGO_CIERRE); foto = foto_uri(d["foto"])
    hexa = svg_kit(kit, "hexagonos-esquina-sup-der.svg")
    n = len(d["laminas"]) + 2
    leyenda = (f"Valores al {t(d['valores_al'])}. No constituyen recomendación de inversión." if d.get("valores_al") else "")

    def pie(color):
        ley = f'<div class="ley">{leyenda}</div>' if leyenda else ""
        return f'<div class="pie" style="color:{color}">{ley}<div>{PIE}</div></div>'

    def nro(k, color):
        return f'<div class="nro" style="color:{color}">{k}/{n}</div>'

    def fondo_foto(filtro):
        return (f'<img class="abs" src="{foto}" style="left:0;top:0;width:{W}px;height:{H}px;object-fit:cover">'
                f'<div class="abs" style="left:0;top:0;width:{W}px;height:{H}px;background:{filtro}"></div>')

    sin_coral = lambda s: s.replace('class="res"', 'class="res" style="color:inherit"')
    bajada = (f'<div style="font-size:40px;line-height:1.3;color:{BLANCO}">{t(d["bajada"])}</div>'
              if d.get("bajada") else "")
    pags = []
    # portada: foto con filtro coral
    pags.append(f'''<div class="pag">{fondo_foto(FILTRO_CORAL)}
      <div class="abs esq blanco">{hexa}</div>
      <img class="abs" src="{logo_b}" style="left:90px;top:90px;width:190px">
      <div class="txt ajusta" data-campo="lámina 1" style="left:90px;top:420px;width:900px;height:540px;justify-content:flex-end;gap:30px">
        <div class="tit-black encoge" style="font-size:92px;line-height:1.08;color:{BLANCO}">{sin_coral(t(d["tema"]))}</div>{bajada}</div>
      <div class="desl" style="left:90px;top:1000px">Deslizá →</div>
      {pie(BLANCO)}</div>''')
    # interiores
    for k, x in enumerate(d["laminas"], 2):
        pags.append(f'''<div class="pag" style="background:{BLANCO}">
      <div class="abs esq">{hexa}</div>
      <img class="abs" src="{logo_c}" style="left:90px;top:92px;width:330px">
      <div class="abs" style="left:90px;top:170px;width:120px;height:8px;border-radius:4px;background:{CORAL}"></div>
      <div class="txt ajusta" data-campo="lámina {k}" style="left:90px;top:300px;width:900px;height:820px;justify-content:center;gap:44px">
        <div class="tit encoge" style="font-size:66px;line-height:1.12;color:{VIOLETA}">{t(x["titulo"])}</div>
        <div style="font-size:38px;line-height:1.4;color:{GRIS}">{t(x["texto"])}</div></div>
      {nro(k, VIOLETA)}{pie(VIOLETA)}</div>''')
    # cierre: la misma foto con filtro blanco
    pags.append(f'''<div class="pag">{fondo_foto(FILTRO_BLANCO)}
      <div class="abs esq">{hexa}</div>
      <img class="abs" src="{logo_v}" style="left:445px;top:150px;width:190px">
      <div class="txt ajusta" data-campo="lámina {n}" style="left:90px;top:460px;width:900px;height:520px;justify-content:center;align-items:center;text-align:center;gap:52px">
        <div class="tit encoge" style="font-size:74px;line-height:1.12;color:{VIOLETA}">{t(d["cierre"]["titulo"])}</div>
        <div class="llam tit">{LLAMADO}</div></div>
      <div class="abs" style="left:90px;top:1030px;width:900px;text-align:center;font-size:28px;color:{VIOLETA}">www.insiderfinance.com.ar</div>
      {nro(n, VIOLETA)}{pie(VIOLETA)}</div>''')
    css = f"""
    * {{ box-sizing:border-box; margin:0; padding:0; font-feature-settings:"calt" 0; }}
    body {{ margin:0; background:#fff; font-family:'Numans'; }}
    .pag {{ width:{W}px; height:{H}px; position:relative; overflow:hidden; page-break-after:always; background:{BLANCO}; }}
    .abs {{ position:absolute; }}
    .tit, .res {{ font-family:'Insider Sans Expanded'; font-weight:700; }}
    .tit-black {{ font-family:'Insider Sans Expanded Black'; }}
    .res {{ color:{CORAL}; }}
    .txt {{ position:absolute; display:flex; flex-direction:column; overflow:hidden; }}
    .txt > * {{ flex-shrink:0; }}
    .esq {{ right:0; top:0; width:560px; height:140px; }}
    .desl {{ position:absolute; border:3px solid {BLANCO}; border-radius:37px; height:74px; padding:0 40px; display:flex; align-items:center; font-size:30px; color:{BLANCO}; }}
    .llam {{ background:{CORAL}; color:{BLANCO}; border-radius:44px; padding:22px 48px; font-size:38px; }}
    .nro {{ position:absolute; right:90px; top:1160px; font-size:28px; }}
    .pie {{ position:absolute; left:90px; right:90px; bottom:70px; font-size:24px; line-height:1.4; }}
    .ley {{ font-size:22px; opacity:0.9; }}
    div > svg {{ width:100%; height:100%; display:block; }}
    .blanco svg {{ filter:brightness(0) invert(1); }}   /* hexágonos en blanco sobre la foto (pedido de marketing) */
    @page {{ size:{W}px {H}px; margin:0; }}
    """
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(pags)}</body></html>', n


JS_DESBORDE = """
() => [...document.querySelectorAll('.ajusta')]
      .filter(el => el.scrollHeight > el.clientHeight + 8 || el.scrollWidth > el.clientWidth + 2)
      .map(el => el.dataset.campo)
"""


def main():
    ap = argparse.ArgumentParser(description="A01 - AgroFinance · Carrusel educativo")
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
    if not errores:
        from playwright.sync_api import sync_playwright
        salida = Path(a.salida); salida.mkdir(parents=True, exist_ok=True)
        html_txt, n = armar(datos, a.kit)
        with sync_playwright() as p:
            nav = p.chromium.launch()
            pag = nav.new_page(viewport={"width": W, "height": H})
            pag.set_content(html_txt); pag.evaluate("document.fonts.ready"); pag.wait_for_timeout(300)
            pag.evaluate(JS_ENCOGER)
            malos = pag.evaluate(JS_DESBORDE)
            if malos:
                errores = [f"El texto de la {m} no entra en su espacio. Acortalo." for m in malos]
            else:
                for k in range(n):
                    pag.screenshot(path=str(salida / f"{a.nombre}-{k+1:02d}.png"),
                                   clip={"x": 0, "y": k * H, "width": W, "height": H}, full_page=True)
                pag.pdf(path=str(salida / f"{a.nombre}.pdf"), width=f"{W}px", height=f"{H}px", print_background=True)
            nav.close()
    if errores:
        print("NO SE GENERÓ EL CARRUSEL. Errores:")
        for x in errores:
            print(" -", x)
        sys.exit(1)
    print(f"OK: {n} láminas ({a.nombre}-01.png a {a.nombre}-{n:02d}.png) y {a.nombre}.pdf")


if __name__ == "__main__":
    main()
