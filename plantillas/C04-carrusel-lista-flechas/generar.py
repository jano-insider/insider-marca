#!/usr/bin/env python3
"""C04 - Carrusel · Lista con flechas (1080x1350, fondo coral).
Título (**así** va en violeta) + 2 a 7 ítems con flecha desde el borde."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo", "items", "ilustracion"}
ILUSTRACIONES = {f"iconografia-{i:02d}" for i in range(1, 25)}


def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo", 160, ayuda="Usá **así** para la parte en violeta.")
    f.lista("items", 2, 7, 90)
    f.opcion("ilustracion", ILUSTRACIONES | {"ninguna"}, obligatorio=False)
    return f.errores

def armar(d, kit):
    css = f"""
    .marco {{ position:absolute; left:0; right:260px; top:70px; bottom:70px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:34px; }}
    .marco > * {{ flex-shrink:0; }}
    .titulo {{ margin-left:150px; color:{BLANCO}; font-size:50px; line-height:1.15; margin-bottom:18px; }}
    .titulo .res {{ color:{VIOLETA}; text-transform:uppercase; }}
    .item {{ position:relative; padding-left:150px; color:{BLANCO}; font-size:38px; line-height:1.25; }}
    .ilu {{ position:absolute; left:829px; top:1040px; width:151px; height:214px; }}
    .item svg {{ position:absolute; left:0; top:12px; width:142px; height:22px; }}
    """
    flecha = (f'<svg viewBox="0 0 142 22"><line x1="0" y1="11" x2="128" y2="11" stroke="{VIOLETA}" stroke-width="4"/>'
              f'<path d="M124 3 L140 11 L124 19 Z" fill="{VIOLETA}"/></svg>')
    items = "".join(f'<div class="item">{flecha}{t(x)}</div>' for x in d["items"])
    nombre = d.get("ilustracion", "iconografia-22")
    ilu = f'<div class="ilu">{svg_kit(kit, nombre + ".svg")}</div>' if nombre != "ninguna" else ""
    cuerpo = f"""{ilu}<div class="marco ajusta" data-campo="titulo/items"><div class="titulo tit">{t(d['titulo'])}</div>{items}</div>"""
    return pagina(1080, 1350, css, cuerpo, fondo=CORAL)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["iconografia-22.svg"])
