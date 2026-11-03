#!/usr/bin/env python3
"""C03 - Carrusel · Cierre con llamado a la acción (1080x1350)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo", "puntos", "cta"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo", 90, obligatorio=False)
    f.lista("puntos", 1, 5, 45, obligatorio=False)
    f.texto("cta", 24, ayuda="Ej. '¡Escribinos!'.")
    if not d.get("titulo") and not d.get("puntos"):
        f.errores.append("Hace falta 'titulo' o 'puntos' (al menos uno).")
    return f.errores

def armar(d, kit):
    css = f"""
    .logo {{ position:absolute; right:80px; top:70px; width:190px; height:200px; }}
    .redes {{ position:absolute; right:90px; bottom:90px; display:flex; gap:26px; }}
    .redes svg {{ width:54px; height:54px; }}
    .marco {{ position:absolute; left:120px; right:120px; top:240px; bottom:200px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:60px; }}
    .marco > * {{ flex-shrink:0; }}
    .titulo {{ color:{VIOLETA}; font-size:66px; line-height:1.2; }}
    ul {{ list-style:none; color:{CORAL}; font-size:62px; line-height:1.25; }}
    li {{ padding-left:44px; position:relative; margin-top:10px; }}
    li::before {{ content:'•'; position:absolute; left:0; }}
    .cta {{ color:{VIOLETA}; font-size:96px; }}
    """
    tit = f'<div class="titulo tit">{t(d["titulo"])}</div>' if d.get("titulo") else ""
    pts = ("<ul class='tit'>" + "".join(f"<li>{t(p)}</li>" for p in d["puntos"]) + "</ul>") if d.get("puntos") else ""
    c = CORAL
    trazo = f'fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"'
    redes = ('<div class="redes">'
             f'<svg viewBox="0 0 32 32"><path d="M16 27 C6 20 3 15 3 10.5 A6.5 6.5 0 0 1 16 8 A6.5 6.5 0 0 1 29 10.5 C29 15 26 20 16 27 Z" {trazo}/></svg>'
             f'<svg viewBox="0 0 32 32"><path d="M16 4 A12 11 0 1 1 9 24 L4 27 L6 21 A11 11 0 0 1 16 4 Z" {trazo}/></svg>'
             f'<svg viewBox="0 0 32 32"><path d="M8 4 H24 V28 L16 21 L8 28 Z" {trazo}/></svg>'
             f'<svg viewBox="0 0 32 32"><path d="M29 3 L13 19 M29 3 L19 29 L13 19 L3 13 Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/></svg>'
             '</div>')
    cuerpo = f"""{svg_kit(kit,'logo-vertical-color.svg','logo')}
    <div class="marco ajusta" data-campo="titulo/puntos/cta">{tit}{pts}<div class="cta ita">{t(d['cta'])}</div></div>{redes}"""
    return pagina(1080, 1350, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["logo-vertical-color.svg"])
