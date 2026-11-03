#!/usr/bin/env python3
"""H05 - Historia · Aviso financiero de cobro (1080x1920, fondo coral).
Ej.: 'Si invertiste en: VSCRO (Vista Energy). Hoy es día de cobro de intereses.'"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"instrumento", "detalle", "texto", "cierre"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("instrumento", 20, patron=r"^[A-Z0-9]{2,8}( o [A-Z0-9]{2,8})?$",
            ayuda="Ticker en mayúsculas, o dos con ' o ' (ej. 'S30N6 o AN29').")
    f.texto("detalle", 60, obligatorio=False)
    f.texto("texto", 120, ayuda="Ej. 'Hoy es día de cobro de intereses.'")
    f.texto("cierre", 170, ayuda="Ej. 'Hablá con tu asesor para rebalancear el capital...'")
    return f.errores

def armar(d, kit):
    css = f"""
    .titulo {{ position:absolute; left:110px; top:300px; color:{BLANCO}; font-size:96px; line-height:1.05; text-transform:uppercase; }}
    .linea {{ position:absolute; left:116px; top:640px; width:5px; height:820px; background:{BLANCO}; }}
    .punto {{ position:absolute; left:107px; top:1450px; width:24px; height:24px; border-radius:50%; background:{BLANCO}; }}
    .cuerpo {{ position:absolute; left:170px; right:90px; top:600px; height:900px; overflow:hidden;
              display:flex; flex-direction:column; justify-content:space-between; color:{BLANCO}; }}
    .si {{ color:{VIOLETA}; font-size:68px; }}
    .instr {{ font-size:86px; line-height:1.1; }}
    .detalle {{ font-size:64px; line-height:1.15; margin-top:10px; }}
    .texto {{ font-size:54px; line-height:1.25; }}
    .logo {{ position:absolute; right:90px; bottom:270px; width:230px; height:70px; }}
    """
    det = f'<div class="detalle tit">{t(d["detalle"])}</div>' if d.get("detalle") else ""
    cuerpo = f"""
    <div class="titulo tit">Aviso<br>financiero</div>
    <div class="linea"></div><div class="punto"></div>
    <div class="cuerpo ajusta" data-campo="instrumento/detalle/texto/cierre">
      <div class="si tit">Si invertiste en:</div>
      <div><div class="instr tit encoge">{t(d['instrumento'])}</div>{det}</div>
      <div class="texto tit">{t(d['texto'])}<br>{t(d['cierre'])}</div>
    </div>
    {svg_kit(kit, 'logo-horizontal-blanco.svg', 'logo')}"""
    return pagina(1080, 1920, css, cuerpo, fondo=CORAL)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["logo-horizontal-blanco.svg"])
