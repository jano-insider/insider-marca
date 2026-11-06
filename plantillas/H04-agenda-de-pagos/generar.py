#!/usr/bin/env python3
"""H04 - Historia · Agenda de pagos (1080x1920).
Ej.: PLANIFICÁ CON TIEMPO / AVISO FINANCIERO: 'Hoy pagan estos instrumentos'."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, banda, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo_1", "titulo_2", "intro", "instrumentos", "pregunta", "cierre"}
TICKER = r"^[A-Z0-9]{2,8}$"

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo_1", 14, ayuda="Ej. 'PLANIFICÁ' o 'AVISO'.")
    f.texto("titulo_2", 14, ayuda="Ej. 'CON TIEMPO' o 'FINANCIERO'.")
    f.texto("intro", 70, ayuda="Ej. 'El lunes pagan estos instrumentos:'.")
    f.lista("instrumentos", 1, 12, 8, patron=TICKER, ayuda="Tickers en mayúsculas, ej. 'S30O6'.")
    f.texto("pregunta", 110, obligatorio=False)
    f.texto("cierre", 40, ayuda="Ej. 'Hablá con tu asesor'.")
    return f.errores

def armar(d, kit):
    # Hasta 6 tickers, la medida del original. Con más (fechas de pago de globales y bonares),
    # la letra de la banda y el aire entre bloques se achican en escalones para que entren hasta 12.
    n = len(d["instrumentos"])
    tam, gap, pad = (74, 60, 48) if n <= 6 else (62, 44, 36) if n <= 9 else (54, 34, 30)
    css = f"""
    .marco > * {{ flex-shrink:0; }}
    .marco {{ position:absolute; left:0; right:0; top:260px; bottom:260px;
             display:flex; flex-direction:column; justify-content:center; overflow:hidden; gap:{gap}px; }}
    .titulo {{ font-size:92px; line-height:1.02; text-transform:uppercase; text-align:center; }}
    .titulo .l1 {{ color:{VIOLETA}; white-space:nowrap; }}
    .titulo .l2 {{ color:{CORAL}; position:relative; display:inline-block; }}
    .titulo .l2::before {{ content:''; position:absolute; left:-90px; top:50%; width:60px; height:5px; background:{VIOLETA}; }}
    .titulo .l2::after  {{ content:''; position:absolute; left:-36px; top:calc(50% - 8px); width:20px; height:20px; border-radius:50%; background:{VIOLETA}; }}
    .alerta {{ display:inline-block; width:66px; height:56px; margin-left:14px; vertical-align:top; }}
    .intro {{ color:#1F1F1F; font-size:58px; text-align:center; padding:0 90px; line-height:1.2; }}
    .banda {{ background:{CORAL}; color:{BLANCO}; font-size:{tam}px; text-align:center; padding:{pad}px 60px; line-height:1.3; max-height:640px; overflow:hidden; }}
    .pregunta {{ color:#1F1F1F; font-size:48px; text-align:center; padding:0 110px; line-height:1.25; }}
    .cierre {{ color:{CORAL}; font-size:88px; text-align:center; text-transform:uppercase; line-height:1.05; padding:0 90px; }}
    """
    alerta = f'<span class="alerta">{svg_kit(kit, "alerta.svg")}</span>'
    # el guion queda pegado al ticker anterior (espacio duro): nunca empieza un renglón con "-"
    instr = "&nbsp;- ".join(t(x) for x in d["instrumentos"])
    preg = f'<div class="pregunta">{t(d["pregunta"])}</div>' if d.get("pregunta") else ""
    cuerpo = f"""{banda(kit, "hexagonos-banda-1.svg", -21, -769, 1101, 1048, 0.555)}
    <div class="marco ajusta" data-campo="contenido completo">
      <div class="titulo tit"><div class="l1">{t(d['titulo_1'])}{alerta}</div><div class="l2">{t(d['titulo_2'])}</div></div>
      <div class="intro">{t(d['intro'])}</div>
      <div class="banda tit ajusta" data-campo="instrumentos">{instr}</div>
      {preg}
      <div class="cierre ita">{t(d['cierre'])}</div>
    </div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920,
             ["hexagonos-banda-1.svg", "alerta.svg"])
