#!/usr/bin/env python3
"""H03 - Historia · Información / actualización (1080x1920).
Ej.: INFORMACIÓN OPERATORIA (feriados, horarios), ACTUALIZACIÓN FONDO FAL."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, banda, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo_1", "titulo_2", "destacado", "puntos", "cierre"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo_1", 14, ayuda="Primera línea del título, ej. 'INFORMACIÓN'.")
    f.texto("titulo_2", 14, ayuda="Segunda línea, ej. 'OPERATORIA'.")
    f.texto("destacado", 90, ayuda="Frase principal de la tarjeta.")
    f.lista("puntos", 1, 5, 140)
    f.texto("cierre", 60, ayuda="Ej. 'Comunicate para consultar con tu asesor.'")
    return f.errores

def armar(d, kit):
    css = f"""
    .marco > * {{ flex-shrink:0; }}
    .marco {{ position:absolute; left:70px; right:70px; top:260px; bottom:260px;
             display:flex; flex-direction:column; justify-content:center; overflow:hidden; gap:56px; }}
    .titulo {{ font-size:90px; line-height:1.02; text-transform:uppercase; }}
    .titulo .l1 {{ color:{VIOLETA}; white-space:nowrap; }}
    .titulo .l2 {{ color:{CORAL}; position:relative; }}
    .titulo .l2::before {{ content:''; position:absolute; left:-70px; top:50%; width:52px; height:5px; background:{VIOLETA}; }}
    .titulo .l2::after  {{ content:''; position:absolute; left:-24px; top:calc(50% - 8px); width:20px; height:20px; border-radius:50%; background:{VIOLETA}; }}
    .alerta {{ display:inline-block; width:66px; height:56px; margin-left:14px; vertical-align:top; }}
    .tarjeta {{ background:rgba(238,117,99,0.78); border-radius:36px; padding:46px 44px; color:{BLANCO}; max-height:960px; overflow:hidden; }}
    .tarjeta .dest {{ font-size:70px; line-height:1.15; margin-bottom:28px; }}
    .tarjeta ul {{ list-style:none; font-size:48px; line-height:1.3; }}
    .tarjeta li {{ margin-top:14px; padding-left:34px; position:relative; }}
    .tarjeta li::before {{ content:'•'; position:absolute; left:0; }}
    .cierre {{ color:{CORAL}; font-size:58px; text-align:center; text-transform:uppercase; line-height:1.15; }}
    """
    alerta = f'<span class="alerta">{svg_kit(kit, "alerta.svg")}</span>'
    puntos = "".join(f"<li>{t(p)}</li>" for p in d["puntos"])
    cuerpo = f"""{banda(kit, "hexagonos-banda-1.svg", -21, -769, 1101, 1048, 0.555)}
    <div class="marco ajusta" data-campo="contenido completo">
      <div class="titulo tit"><div class="l1">{t(d['titulo_1'])}{alerta}</div><div class="l2">{t(d['titulo_2'])}</div></div>
      <div class="tarjeta ajusta" data-campo="destacado/puntos"><div class="dest tit">{t(d['destacado'])}</div><ul>{puntos}</ul></div>
      <div class="cierre ita">{t(d['cierre'])}</div>
    </div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920,
             ["hexagonos-banda-1.svg", "alerta.svg"])
