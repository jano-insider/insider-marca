#!/usr/bin/env python3
"""H07 - Historia · Pregunta + lista en tarjeta (1080x1920).
Ej.: '¿Por qué elegimos como administradora para tu Fondo FAL?' + beneficios."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"pregunta", "puntos", "cierre"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("pregunta", 90)
    f.lista("puntos", 2, 6, 60)
    f.texto("cierre", 80, obligatorio=False)
    return f.errores

def armar(d, kit):
    css = f"""
    .logo {{ position:absolute; left:50%; transform:translateX(-50%); top:250px; width:260px; height:80px; }}
    .marco {{ position:absolute; left:90px; right:90px; top:400px; bottom:330px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:44px; }}
    .marco > * {{ flex-shrink:0; }}
    .tarjeta {{ border:4px solid {CORAL}; border-radius:40px; overflow:hidden; }}
    .preg {{ background:{CORAL}; color:{BLANCO}; font-size:54px; line-height:1.18; text-align:center; padding:44px 50px; }}
    ul {{ list-style:none; padding:36px 56px 44px; font-size:46px; line-height:1.3; color:{VIOLETA}; }}
    li {{ padding-left:40px; position:relative; margin-top:22px; }}
    li::before {{ content:'•'; position:absolute; left:0; color:{CORAL}; }}
    .cierre {{ color:{CORAL}; font-size:42px; line-height:1.2; }}
    .web {{ position:absolute; left:50%; transform:translateX(-50%); bottom:260px; border:3px solid {VIOLETA};
           border-radius:40px; padding:10px 34px; font-size:30px; color:{VIOLETA}; }}
    """
    pts = "".join(f"<li>{t(p)}</li>" for p in d["puntos"])
    cierre = f'<div class="cierre tit">{t(d["cierre"])}</div>' if d.get("cierre") else ""
    cuerpo = f"""{svg_kit(kit,'logo-horizontal-color.svg','logo')}
    <div class="marco ajusta" data-campo="pregunta/puntos/cierre">
      <div class="tarjeta"><div class="preg tit">{t(d['pregunta'])}</div><ul>{pts}</ul></div>{cierre}
    </div>
    <div class="web">www.insiderfinance.com.ar</div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["logo-horizontal-color.svg"])
