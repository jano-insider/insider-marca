#!/usr/bin/env python3
"""C02 - Carrusel · Lámina interna (1080x1350). Texto con **resaltado**, fondo blanco o coral."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"fondo", "texto", "nota", "siguiente"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.opcion("fondo", {"blanco", "coral"})
    f.texto("texto", 260)
    f.texto("nota", 160, obligatorio=False)
    if "siguiente" in d and not isinstance(d["siguiente"], bool):
        f.errores.append("siguiente: true o false.")
    return f.errores

def armar(d, kit):
    coral = d["fondo"] == "coral"
    fg = BLANCO if coral else VIOLETA
    css = f"""
    .linea {{ position:absolute; left:96px; top:330px; width:5px; height:640px; background:{BLANCO if coral else '#B9B2C8'}; }}
    .punto {{ position:absolute; left:87px; top:962px; width:24px; height:24px; border-radius:50%; background:{BLANCO if coral else CORAL}; }}
    .marco {{ position:absolute; left:150px; right:110px; top:300px; height:720px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:40px; color:{fg}; }}
    .texto {{ font-size:74px; line-height:1.22; }}
    .texto .res {{ font-style:italic; color:{fg}; }}
    .nota {{ font-size:36px; line-height:1.3; color:{BLANCO if coral else CORAL}; }}
    .logo {{ position:absolute; right:80px; top:70px; width:190px; height:200px; }}
    .sig {{ position:absolute; right:80px; bottom:80px; width:96px; height:96px; }}
    """
    nota = f'<div class="nota">{t(d["nota"])}</div>' if d.get("nota") else ""
    c1, c2 = (BLANCO, CORAL) if coral else (CORAL, BLANCO)
    sig = (f'<svg class="sig" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="{c1}"/>'
           f'<path d="M26 20 L46 32 L26 44 Z" fill="{c2}"/></svg>') if d.get("siguiente", True) else ""
    logo = svg_kit(kit, "logo-vertical-blanco.svg" if coral else "logo-vertical-color.svg", "logo")
    cuerpo = f"""{logo}<div class="linea"></div><div class="punto"></div>
    <div class="marco ajusta" data-campo="texto/nota"><div class="texto">{t(d['texto'])}</div>{nota}</div>{sig}"""
    return pagina(1080, 1350, css, cuerpo, fondo=CORAL if coral else BLANCO)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["logo-vertical-color.svg", "logo-vertical-blanco.svg"])
