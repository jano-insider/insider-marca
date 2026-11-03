#!/usr/bin/env python3
"""H10 - Historia · Lista de servicios con títulos (1080x1920).
Ej.: 'EN INSIDER FINANCE OFRECEMOS:' + 2 a 4 servicios con título y descripción."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"encabezado", "servicios", "nota", "cta", "ilustracion"}
ILUSTRACIONES = {f"iconografia-{i:02d}" for i in range(1, 25)}


def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("encabezado", 40, ayuda="Ej. 'En Insider Finance ofrecemos:'.")
    s = d.get("servicios")
    if not isinstance(s, list) or not 2 <= len(s) <= 4:
        f.errores.append("servicios: entre 2 y 4.")
    else:
        for i, x in enumerate(s, 1):
            if not isinstance(x, dict) or set(x) != {"titulo", "texto"}:
                f.errores.append(f"servicios[{i}]: lleva 'titulo' y 'texto'."); continue
            if not 0 < len(str(x["titulo"])) <= 30:
                f.errores.append(f"servicios[{i}].titulo: hasta 30 caracteres.")
            if not 0 < len(str(x["texto"])) <= 130:
                f.errores.append(f"servicios[{i}].texto: hasta 130 caracteres.")
    f.texto("nota", 90, obligatorio=False)
    f.texto("cta", 25, obligatorio=False, ayuda="Ej. '¡Escribinos!'.")
    f.opcion("ilustracion", ILUSTRACIONES | {"ninguna"}, obligatorio=False)
    return f.errores

def armar(d, kit):
    css = f"""
    .marco {{ position:absolute; left:0; right:90px; top:220px; bottom:300px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:flex-start; gap:46px; }}
    .marco > * {{ flex-shrink:0; }}
    .enc {{ margin-left:110px; margin-right:250px; border:4px solid {CORAL}; border-radius:24px; padding:16px 34px;
           color:{CORAL}; font-size:52px; text-transform:uppercase; }}
    .serv {{ position:relative; padding-left:150px; }}
    .serv::before {{ content:''; position:absolute; left:0; top:28px; width:120px; height:5px; background:{VIOLETA}; }}
    .serv::after {{ content:''; position:absolute; left:112px; top:21px; width:20px; height:20px; border-radius:50%; background:{VIOLETA}; }}
    .serv h3 {{ color:{CORAL}; font-size:56px; text-transform:uppercase; line-height:1.1; }}
    .serv p {{ color:{VIOLETA}; font-size:48px; line-height:1.25; margin-top:8px; }}
    .nota {{ margin-left:110px; color:{VIOLETA}; font-size:34px; }}
    .cta {{ margin-left:110px; color:{CORAL}; font-size:56px; text-transform:uppercase; }}
    .logo {{ position:absolute; right:90px; bottom:260px; width:220px; height:66px; }}
    .encw {{ position:relative; align-self:flex-start; }}
    .ilu {{ position:absolute; left:783px; top:250px; width:216px; height:196px; }}
    """
    serv = "".join(f'<div class="serv"><h3 class="tit">{t(x["titulo"])}</h3><p>{t(x["texto"])}</p></div>' for x in d["servicios"])
    nota = f'<div class="nota">{t(d["nota"])}</div>' if d.get("nota") else ""
    cta = f'<div class="cta tit">{t(d["cta"])}</div>' if d.get("cta") else ""
    nombre = d.get("ilustracion", "iconografia-10")
    ilu = f'<div class="ilu">{svg_kit(kit, nombre + ".svg")}</div>' if nombre != "ninguna" else ""
    cuerpo = f"""<div class="marco ajusta" data-campo="servicios"><div class="encw"><div class="enc tit">{t(d['encabezado'])}</div></div>{serv}{nota}{cta}</div>
    {ilu}{svg_kit(kit,'logo-horizontal-color.svg','logo')}"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["logo-horizontal-color.svg", "iconografia-10.svg"])
