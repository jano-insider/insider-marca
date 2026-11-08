#!/usr/bin/env python3
"""C10 - Carrusel continuo (láminas de 1080x1350).

El carrusel se arma ENTERO, como una tira: las láminas coral seguidas forman un solo panel que
cruza de una lámina a la otra, y en cada cambio de color la plantilla pone sola la unión
(banda de color o triángulo blanco), copiando las medidas del original de Illustrator
(instagram_insider_sin_iconos.ai). Regla de marketing: donde hay banda de color, la lámina
siguiente es de color; donde hay triángulo blanco, la siguiente es blanca.

Ficha:
{
  "tema": "¿Gastas más de lo que quisieras?",   # subtítulo o tema: va chico arriba de cada lámina interna
  "laminas": [
    {"tipo": "portada",   "fondo": "blanco", "titulo": "¿Gastas **más** de lo que quisieras?"},
    {"tipo": "contenido", "fondo": "coral",  "antes": "...", "titulo": "...", "despues": "...", "alineacion": "izquierda"},
    {"tipo": "cierre",    "fondo": "blanco", "titulo": "¿Querés **saber más?**", "llamado": "Escribinos", "texto": "Somos tu asesor financiero."}
  ]
}
En el cierre, si hay "llamado", el "titulo" es opcional (ej. solo el recuadro "Escribinos" con su texto).
En los títulos, **así** va en coral sobre blanco (en violeta sobre coral).
Uniones (a criterio de marketing): por defecto se alternan como en los originales; en cada lámina coral
se pueden fijar con "union_izq" / "union_der": "banda-abajo", "banda-arriba", "borde-arriba", "borde-abajo" o "recta".
Los bordes de afuera de la primera y la última lámina van lisos, salvo que se indiquen igual (en una
lámina blanca, "banda-..." pone una banda coral en ese borde).
Elementos fijos (marketing): "Desliza" solo en la portada; botón de siguiente en todas menos la última;
íconos de redes solo en el cierre; marcador en la portada (invita a guardar el contenido).
Genera <nombre>-01.png, <nombre>-02.png, ... y <nombre>.pdf con todas las láminas.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import t, svg_kit, faltantes, JS_ENCOGER, CORAL, VIOLETA, BLANCO  # noqa: E402

W, H = 1080, 1350
NEGRO = "#1F1D1D"
BANDA = 246                       # cuánto se mete el coral en la lámina blanca vecina
CH_ARRIBA, CH_ABAJO = (226, 240), (240, 254)   # tamaño de los cortes en diagonal (ancho, alto)
UNIONES = {"banda-abajo", "banda-arriba", "borde-arriba", "borde-abajo", "recta"}
RECURSOS = ["logo-horizontal-color.svg", "logo-horizontal-blanco.svg"]


# ------------------------------------------------------------------ validación
def validar(d):
    e = []
    if not isinstance(d, dict):
        return ["La ficha tiene que ser un objeto JSON."]
    for k in d:
        if k not in {"tema", "laminas"}:
            e.append(f"Campo desconocido: '{k}'.")
    tc = d.get("tema")
    if not isinstance(tc, str) or not 0 < len(tc) <= 45:
        e.append("tema: el subtítulo o tema del carrusel, texto de hasta 45 caracteres.")
    lam = d.get("laminas")
    if not isinstance(lam, list) or not 2 <= len(lam) <= 10:
        return e + ["laminas: entre 2 y 10."]
    for i, l in enumerate(lam, 1):
        c = f"laminas[{i}]"
        if not isinstance(l, dict):
            e.append(f"{c}: tiene que ser un objeto."); continue
        permitidas = {"tipo", "fondo", "titulo", "antes", "despues", "alineacion", "llamado", "texto", "union_izq", "union_der"}
        for k in l:
            if k not in permitidas:
                e.append(f"{c}: campo desconocido '{k}'.")
        if l.get("tipo") not in {"portada", "contenido", "cierre"}:
            e.append(f"{c}.tipo: 'portada', 'contenido' o 'cierre'.")
        if l.get("fondo") not in {"blanco", "coral"}:
            e.append(f"{c}.fondo: 'blanco' o 'coral'.")
        # en el cierre, si hay llamado ("Escribinos" en su recuadro), el título es opcional
        tit_oblig = not (l.get("tipo") == "cierre" and l.get("llamado"))
        for campo, mx, oblig in (("titulo", 90, tit_oblig), ("antes", 140, False), ("despues", 140, False),
                                 ("llamado", 20, False), ("texto", 90, False)):
            v = l.get(campo)
            if v in (None, ""):
                if oblig:
                    e.append(f"{c}.{campo}: falta.")
            elif not isinstance(v, str) or len(v) > mx:
                e.append(f"{c}.{campo}: texto de hasta {mx} caracteres.")
        if l.get("alineacion", "izquierda") not in {"izquierda", "centro", "derecha"}:
            e.append(f"{c}.alineacion: 'izquierda', 'centro' o 'derecha'.")
        for u in ("union_izq", "union_der"):
            if u in l and l[u] not in UNIONES:
                e.append(f"{c}.{u}: uno de {sorted(UNIONES)}.")
    if lam and isinstance(lam[0], dict) and lam[0].get("tipo") != "portada":
        e.append("laminas[1]: la primera lámina es la portada.")
    if lam and isinstance(lam[-1], dict) and lam[-1].get("tipo") != "cierre":
        e.append(f"laminas[{len(lam)}]: la última lámina es el cierre.")
    return e


# ------------------------------------------------------------------ paneles de color
def tramos_coral(lam):
    """Grupos de láminas coral seguidas: [(inicio, fin), ...]."""
    tramos, i = [], 0
    while i < len(lam):
        if lam[i]["fondo"] == "coral":
            j = i
            while j + 1 < len(lam) and lam[j + 1]["fondo"] == "coral":
                j += 1
            tramos.append((i, j)); i = j + 1
        else:
            i += 1
    return tramos


def poligono(lam, k, i, j):
    """Contorno del panel coral de las láminas i..j, en coordenadas de la tira."""
    n = len(lam)
    x0, x1 = i * W, (j + 1) * W
    # uniones por defecto, alternando como en los carruseles originales
    izq_def = ("banda-abajo" if k % 2 == 0 else "borde-arriba") if i > 0 else "recta"
    der_def = ("borde-arriba" if k % 2 == 0 else "banda-abajo") if j < n - 1 else "recta"
    izq = lam[i].get("union_izq", izq_def if i > 0 else "recta")
    der = lam[j].get("union_der", der_def if j < n - 1 else "recta")
    ax, ay = CH_ARRIBA; bx, by = CH_ABAJO
    if izq.startswith("banda"):
        x0 -= BANDA
    if der.startswith("banda"):
        x1 += BANDA
    # lado izquierdo, de abajo hacia arriba
    if izq.endswith("abajo"):
        lado_i = [(x0 + bx, H), (x0, H - by), (x0, 0)]
    elif izq.endswith("arriba"):
        lado_i = [(x0, H), (x0, ay), (x0 + ax, 0)]
    else:
        lado_i = [(x0, H), (x0, 0)]
    # lado derecho, de arriba hacia abajo
    if der.endswith("arriba"):
        lado_d = [(x1 - ax, 0), (x1, ay), (x1, H)]
    elif der.endswith("abajo"):
        lado_d = [(x1, 0), (x1, H - by), (x1 - bx, H)]
    else:
        lado_d = [(x1, 0), (x1, H)]
    puntos = lado_i + lado_d
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos), izq, der


# ------------------------------------------------------------------ láminas
def play(x, y, fondo):
    c1, c2 = (BLANCO, CORAL) if fondo == "coral" else (CORAL, BLANCO)
    return (f'<svg class="abs" style="left:{x}px;top:{y}px;width:65px;height:65px" viewBox="0 0 65 65">'
            f'<circle cx="32.5" cy="32.5" r="32.5" fill="{c1}"/><path d="M24 17 L47 32.5 L24 48 Z" fill="{c2}"/></svg>')


def redes(fondo, derecha=87):
    c = BLANCO if fondo == "coral" else CORAL
    tr = f'fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"'
    return (f'<div class="abs" style="right:{derecha}px;top:1196px;display:flex;gap:26px">'
            f'<svg width="54" height="54" viewBox="0 0 32 32"><path d="M16 27 C6 20 3 15 3 10.5 A6.5 6.5 0 0 1 16 8 A6.5 6.5 0 0 1 29 10.5 C29 15 26 20 16 27 Z" {tr}/></svg>'
            f'<svg width="54" height="54" viewBox="0 0 32 32"><path d="M16 4 A12 11 0 1 1 9 24 L4 27 L6 21 A11 11 0 0 1 16 4 Z" {tr}/></svg>'
            f'<svg width="54" height="54" viewBox="0 0 32 32"><path d="M8 4 H24 V28 L16 21 L8 28 Z" {tr}/></svg>'
            f'<svg width="54" height="54" viewBox="0 0 32 32"><path d="M29 3 L13 19 M29 3 L19 29 L13 19 L3 13 Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/></svg>'
            '</div>')


def lamina(k, l, d, kit, uniones):
    coral = l["fondo"] == "coral"
    base, res = (BLANCO, VIOLETA) if coral else (VIOLETA, CORAL)
    cuerpo_col = BLANCO if coral else NEGRO
    x = k * W
    ol = BANDA if uniones.get("izq_banda") else 0      # si hay banda en un borde, el contenido se corre
    orr = BANDA if uniones.get("der_banda") else 0
    al = {"izquierda": "left", "centro": "center", "derecha": "right"}[l.get("alineacion", "izquierda")]
    partes = []
    if l["tipo"] == "portada":
        logo = "logo-horizontal-blanco.svg" if coral else "logo-horizontal-color.svg"
        partes.append(f'<div class="abs" style="left:{80 + ol}px;top:80px;width:240px;height:72px">{svg_kit(kit, logo)}</div>')
        marca = BLANCO if (coral or uniones.get("der", "").startswith("banda")) else CORAL
        mx = 933 if not orr or uniones.get("der") == "banda" else 933 - orr
        # portada coral con el corte blanco arriba a la derecha: el marcador se corre a la izquierda del corte
        if coral and uniones.get("der", "").endswith("arriba"):
            mx = W - CH_ARRIBA[0] - 68 - 40
        partes.append(f'<svg class="abs" style="left:{mx}px;top:88px;width:68px;height:78px" viewBox="0 0 68 78">'
                      f'<path d="M2 2 H66 V76 L34 56 L2 76 Z" fill="{marca}"/></svg>')
        partes.append(f'<div class="txt ajusta" data-campo="lámina {k+1}" style="left:{69 + ol}px;right:{360 if uniones.get("der","").startswith("banda") else 90}px;'
                      f'top:560px;height:620px;justify-content:flex-end">'
                      f'<div class="tit encoge" style="font-size:63px;line-height:1.08;color:{base}">{t(l["titulo"])}</div></div>')
        partes.append(f'<div class="abs desl" style="left:{85 + ol}px;top:1188px;border-color:{base};color:{cuerpo_col}">Desliza</div>')
        partes.append(play(290 + ol, 1192, l["fondo"]))
    else:
        # título del carrusel, chico arriba: a la derecha, o a la izquierda si arriba a la derecha hay un corte
        corte_der = uniones.get("der", "").endswith("arriba") and coral
        lado = f"left:{87 + ol}px;text-align:left" if corte_der else f"right:{82 + orr}px;text-align:right"
        partes.append(f'<div class="abs tit" style="{lado};top:88px;width:520px;font-size:19px;color:{base}">{t(d["tema"])}</div>')
        izq_m = 205 if not uniones.get("izq_banda") else 300
        der_m = 110 if not uniones.get("der_banda") else 320
        bloques = []
        if l.get("antes"):
            bloques.append(f'<div style="font-size:36px;line-height:1.2;color:{cuerpo_col};margin-bottom:30px">{t(l["antes"])}</div>')
        ancho_tit = "max-width:690px;" if l["tipo"] == "contenido" else ""
        margen_auto = {"left": "", "center": "margin-left:auto;margin-right:auto;", "right": "margin-left:auto;"}[al]
        if l.get("titulo"):
            bloques.append(f'<div class="tit encoge" style="{ancho_tit}{margen_auto}font-size:95px;line-height:1.02;color:{base}">{t(l["titulo"])}</div>')
        if l["tipo"] == "cierre" and l.get("llamado"):
            bloques.append(f'<div class="llam" style="margin-top:{28 if l.get("titulo") else 0}px;align-self:{ {"left":"flex-start","center":"center","right":"flex-end"}[al] }">'
                           f'<span class="tit">{t(l["llamado"])}</span></div>')
        if l.get("texto"):
            bloques.append(f'<div style="font-size:51px;line-height:1.2;color:{cuerpo_col};margin-top:24px">{t(l["texto"])}</div>')
        if l.get("despues"):
            bloques.append(f'<div style="font-size:36px;line-height:1.2;color:{cuerpo_col};margin-top:40px">{t(l["despues"])}</div>')
        partes.append(f'<div class="txt ajusta" data-campo="lámina {k+1}" style="left:{izq_m}px;right:{der_m}px;top:{300 if l["tipo"] == "contenido" else 220}px;height:{820 if l["tipo"] == "contenido" else 900}px;'
                      f'justify-content:{"flex-start" if l["tipo"] == "contenido" else "center"};text-align:{al}">{"".join(bloques)}</div>')
        partes.append(redes(l["fondo"], 87 + orr) if l["tipo"] == "cierre" else play(910 - orr, 1200, l["fondo"]))
    estilo_res = f".l{k} .res {{ color:{res}; }}"
    return f'<div class="lam l{k}" style="left:{x}px">{"".join(partes)}</div>', estilo_res


def banda_exterior(lado, union):
    """Banda coral en el borde de afuera de una primera o última lámina BLANCA."""
    ax, ay = CH_ARRIBA; bx, by = CH_ABAJO
    if lado == "izq":          # banda pegada al borde izquierdo de la lámina 1
        x = BANDA
        pts = [(0, 0), (x, 0), (x, H - by), (x - bx, H), (0, H)] if union.endswith("abajo") else \
              [(0, 0), (x - ax, 0), (x, ay), (x, H), (0, H)]
    else:                      # banda pegada al borde derecho de la última lámina
        x0 = lado - BANDA; x1 = lado
        pts = [(x0, 0), (x1, 0), (x1, H), (x0 + bx, H), (x0, H - by)] if union.endswith("abajo") else \
              [(x0 + ax, 0), (x1, 0), (x1, H), (x0, H), (x0, ay)]
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def armar(d, kit):
    lam = d["laminas"]; n = len(lam)
    polis, uniones = [], [dict() for _ in lam]
    # bordes de afuera en láminas blancas (solo si marketing lo indica en la ficha)
    if lam[0]["fondo"] == "blanco" and lam[0].get("union_izq", "recta").startswith("banda"):
        polis.append(f'<polygon points="{banda_exterior("izq", lam[0]["union_izq"])}" fill="{CORAL}"/>')
        uniones[0]["izq_banda"] = True
    if lam[-1]["fondo"] == "blanco" and lam[-1].get("union_der", "recta").startswith("banda"):
        polis.append(f'<polygon points="{banda_exterior(W * n, lam[-1]["union_der"])}" fill="{CORAL}"/>')
        uniones[-1]["der_banda"] = True; uniones[-1]["der"] = "banda"
    for k, (i, j) in enumerate(tramos_coral(lam)):
        pts, izq, der = poligono(lam, k, i, j)
        polis.append(f'<polygon points="{pts}" fill="{CORAL}"/>')
        if i > 0:
            uniones[i]["izq"] = izq
            if izq.startswith("banda"):
                uniones[i - 1]["der_banda"] = True; uniones[i - 1]["der"] = "banda"
        if j < n - 1:
            uniones[j]["der"] = der
            if der.startswith("banda"):
                uniones[j + 1]["izq_banda"] = True
    laminas, estilos = zip(*(lamina(k, l, d, kit, uniones[k]) for k, l in enumerate(lam)))
    css = f"""
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ margin:0; background:#fff; font-family:'Numans'; }}
    * {{ font-feature-settings:"calt" 0; }}   /* sin sustituciones de la fuente: "2X6" no se convierte en "2×6" */
    .pag {{ width:{W}px; height:{H}px; position:relative; overflow:hidden; page-break-after:always; }}
    .tira {{ position:absolute; top:0; width:{W*n}px; height:{H}px; }}
    .lam {{ position:absolute; top:0; width:{W}px; height:{H}px; }}
    .abs {{ position:absolute; }}
    .tit {{ font-family:'Insider Sans Expanded'; font-weight:700; }}
    .res {{ font-family:'Insider Sans Expanded'; font-weight:700; }}
    .txt {{ position:absolute; display:flex; flex-direction:column; overflow:hidden; }}
    .txt > * {{ flex-shrink:0; }}
    .desl {{ border:3px solid; border-radius:37px; width:274px; height:74px; padding-left:56px; display:flex; align-items:center; font-size:25px; }}
    .llam {{ position:relative; background:#F4F3F4; padding:2px 26px; margin:28px 10px 0; }}
    .llam span {{ font-size:95px; color:{VIOLETA}; }}
    .llam::before, .llam::after {{ content:''; position:absolute; top:-15px; bottom:-15px; width:11px; border-radius:6px; background:{CORAL}; }}
    .llam::before {{ left:-7px; }} .llam::after {{ right:-7px; }}
    div > svg {{ width:100%; height:100%; display:block; }}
    @page {{ size:{W}px {H}px; margin:0; }}
    {''.join(estilos)}
    """
    tira = (f'<svg class="abs" style="left:0;top:0;width:{W*n}px;height:{H}px" viewBox="0 0 {W*n} {H}">{"".join(polis)}</svg>'
            + "".join(laminas))
    paginas = "".join(f'<div class="pag"><div class="tira" style="left:{-k*W}px">{tira}</div></div>' for k in range(n))
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{paginas}</body></html>'


JS_AJUSTAR = """
() => {
  // Si el texto de una lámina no entra, se achica toda la letra de esa lámina en pasos de 4%,
  // hasta un mínimo del 62% (sigue siendo legible en Instagram). Se aplica igual en todas las copias.
  for (const caja of document.querySelectorAll('.ajusta')) {
    const conTexto = [...caja.querySelectorAll('*')].filter(e =>
      [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
    const base = conTexto.map(e => parseFloat(getComputedStyle(e).fontSize));
    let f = 1;
    while ((caja.scrollHeight > caja.clientHeight + 6 || caja.scrollWidth > caja.clientWidth + 2) && f > 0.62) {
      f -= 0.04;
      conTexto.forEach((e, i) => { e.style.fontSize = (base[i] * f) + 'px'; });
    }
  }
}
"""


def detalle_lamina(l):
    """Qué campos tiene la lámina y cuál es el más largo, para que el error diga qué acortar."""
    campos = [(c, len(str(l[c]).replace("**", ""))) for c in ("titulo", "antes", "texto", "despues", "llamado") if l.get(c)]
    largo = max(campos, key=lambda x: x[1])[0] if campos else "titulo"
    lista = ", ".join(f"{c} {n} caracteres" for c, n in campos)
    return f"tiene {lista}. Acortá primero '{largo}'"


JS_DESBORDE = """
() => [...document.querySelectorAll('.pag:first-child .ajusta')]
      .filter(el => el.scrollHeight > el.clientHeight + 6 || el.scrollWidth > el.clientWidth + 2)
      .map(el => el.dataset.campo)
"""


def main():
    ap = argparse.ArgumentParser(description="C10 - Carrusel continuo")
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
        html_txt = armar(datos, a.kit); n = len(datos["laminas"])
        with sync_playwright() as p:
            nav = p.chromium.launch()
            pag = nav.new_page(viewport={"width": W, "height": H})
            pag.set_content(html_txt); pag.evaluate("document.fonts.ready"); pag.wait_for_timeout(300)
            pag.evaluate(JS_ENCOGER)
            pag.evaluate(JS_AJUSTAR)
            malos = pag.evaluate(JS_DESBORDE)
            if malos:
                errores = []
                for m in malos:
                    k = int(m.split()[-1]) - 1
                    errores.append(f"La {m} no entra ni achicando la letra: {detalle_lamina(datos['laminas'][k])}.")
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
