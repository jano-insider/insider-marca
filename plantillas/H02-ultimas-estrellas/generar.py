#!/usr/bin/env python3
"""H02 - Historia · Últimas "estrellas" (1080x1920).
Acciones y/o CEDEARs destacados con precio y variación."""
import re, sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, logo_tercero, CORAL, VIOLETA, BLANCO

CAMPOS = {"fecha_valores", "acciones", "cedears"}
RE_PRECIO = r"^\$\d{1,3}(\.\d{3})*(,\d{1,2})?$"
RE_VAR = r"^\d{1,3}(\.\d{3})*,\d{1,2}%$"
VERDE = "#1DB954"   # flecha de suba: así se publica hoy (fuera de paleta; a confirmar por marketing)

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("fecha_valores", 10, patron=r"^\d{2}/\d{2}/\d{4}$", ayuda="dd/mm/aaaa.")
    grupos = [g for g in ("acciones", "cedears") if d.get(g)]
    if not grupos:
        f.errores.append("Hace falta 'acciones' o 'cedears' (al menos un grupo).")
    for g in grupos:
        filas = d[g]
        if not isinstance(filas, list) or not 1 <= len(filas) <= 3:
            f.errores.append(f"{g}: entre 1 y 3 filas."); continue
        for i, x in enumerate(filas, 1):
            donde = f"{g}[{i}]"
            if not isinstance(x, dict) or set(x) != {"nombre", "precio", "variacion", "tendencia"}:
                f.errores.append(f"{donde}: lleva exactamente nombre, precio, variacion y tendencia."); continue
            if not re.match(r"^[A-Z0-9]{1,8}$", str(x["nombre"])):
                f.errores.append(f"{donde}.nombre: ticker en mayúsculas (ej. 'ALUA', 'SAP').")
            if not re.match(RE_PRECIO, str(x["precio"])):
                f.errores.append(f"{donde}.precio: formato '$847,50'.")
            if not re.match(RE_VAR, str(x["variacion"])):
                f.errores.append(f"{donde}.variacion: formato '1,3%' sin signo.")
            if x["tendencia"] not in {"sube", "baja"}:
                f.errores.append(f"{donde}.tendencia: 'sube' o 'baja'.")
    return f.errores

def flecha(tend):
    color = VERDE if tend == "sube" else CORAL
    pts = "4,52 26,30 38,42 64,14" if tend == "sube" else "4,14 26,36 38,24 64,52"
    punta = "48,12 66,12 66,30" if tend == "sube" else "48,54 66,54 66,36"
    return (f'<svg class="fl" viewBox="0 0 70 66"><polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/><polyline points="{punta}" fill="none" '
            f'stroke="{color}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/></svg>')

def armar(d, kit):
    css = f"""
    .barra-sup {{ position:absolute; left:0; top:0; width:100%; height:160px; background:{CORAL}; }}
    .barra-inf {{ position:absolute; left:0; bottom:0; width:100%; height:70px; background:{CORAL}; }}
    .marco {{ position:absolute; left:80px; right:80px; top:230px; bottom:420px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:46px; }}
    .marco > * {{ flex-shrink:0; }}
    .titulo {{ color:{CORAL}; font-size:52px; text-align:center; white-space:nowrap; }}
    .grupo h2 {{ color:{CORAL}; font-size:54px; text-align:center; margin-bottom:22px; }}
    .tarjeta {{ border:4px solid {CORAL}; border-radius:28px; padding:18px 38px; }}
    .fila {{ display:grid; grid-template-columns: 230px 1fr 170px 80px; align-items:center; height:118px; }}
    .nom {{ color:{VIOLETA}; font-size:44px; height:80px; display:flex; align-items:center; }}
    .nom img {{ max-width:180px; max-height:76px; object-fit:contain; }}
    .pre, .var {{ color:{VIOLETA}; font-size:46px; }}
    .var {{ text-align:right; padding-right:16px; }}
    .fl {{ width:70px; height:66px; }}
    .iso {{ position:absolute; left:447px; top:1520px; width:186px; height:195px; }}
    .nota {{ position:absolute; left:0; right:0; top:1745px; text-align:center; color:{CORAL}; font-size:34px; }}
    """
    def grupo(clave, titulo):
        if not d.get(clave):
            return ""
        def nombre(x):
            logo = logo_tercero("empresas", x["nombre"], kit)
            return f'<img src="{logo}" alt="{t(x["nombre"])}">' if logo else t(x["nombre"])
        filas = "".join(
            f'<div class="fila"><div class="nom tit">{nombre(x)}</div><div class="pre">{t(x["precio"])}</div>'
            f'<div class="var">{t(x["variacion"])}</div>{flecha(x["tendencia"])}</div>' for x in d[clave])
        return f'<div class="grupo"><h2 class="tit">{titulo}</h2><div class="tarjeta">{filas}</div></div>'
    cuerpo = f"""<div class="barra-sup"></div><div class="barra-inf"></div>
    <div class="marco ajusta" data-campo="acciones/cedears">
      <div class="titulo tit">LAS ÚLTIMAS “ESTRELLAS”</div>
      {grupo('acciones', 'ACCIONES')}{grupo('cedears', 'CEDEARS')}
    </div>
    {svg_kit(kit, 'isotipo-color.svg', 'iso')}
    <div class="nota">*Valores al {t(d['fecha_valores'])}</div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["isotipo-color.svg"])
