#!/usr/bin/env python3
"""C01 - Carrusel · Portada (1080x1350). Título grande + subtítulo."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, banda, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo", "subtitulo"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo", 60)
    f.texto("subtitulo", 70, obligatorio=False)
    return f.errores

def armar(d, kit):
    css = f"""
    .esq-sd {{ width:540px; height:135px; }} .esq-ii {{ width:540px; height:135px; }}
    .logo {{ position:absolute; left:50%; transform:translateX(-50%); top:200px; width:210px; height:220px; }}
    .marco {{ position:absolute; left:100px; right:100px; top:470px; bottom:200px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:30px; }}
    .titulo {{ color:{VIOLETA}; font-size:90px; line-height:1.12; letter-spacing:6px; text-transform:uppercase; }}
    .sub {{ color:{CORAL}; font-size:70px; line-height:1.12; }}
    """
    sub = f'<div class="sub ita">{t(d["subtitulo"])}</div>' if d.get("subtitulo") else ""
    cuerpo = f"""{banda(kit, 'hexagonos-banda-1.svg', 0, -806, 1080, 1028, 0.555)}{banda(kit, 'hexagonos-banda-1.svg', 0, 1095, 1080, 1028, 0.555)}
    {svg_kit(kit,'logo-vertical-color.svg','logo')}
    <div class="marco ajusta" data-campo="titulo/subtitulo"><div class="titulo tit encoge">{t(d['titulo'])}</div>{sub}</div>"""
    return pagina(1080, 1350, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350,
             ["hexagonos-banda-1.svg", "logo-vertical-color.svg"])
