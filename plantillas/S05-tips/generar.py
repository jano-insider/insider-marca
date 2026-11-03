#!/usr/bin/env python3
"""S05 - Posteo · Tips (1080x1350). Copiado del Illustrator de marketing.
TIPS + subtítulo en dos líneas, 3 tips con título y texto, y la invitación a guardar el post."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, multilinea, pagina, ejecutar, fondo_kit, caja, VIOLETA, BLANCO

CAMPOS = {"subtitulo", "tips"}
GRIS = "#3C3C3C"

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("subtitulo", 36, ayuda="Dos líneas con \\n: 'El Tridente del\\nÉxito Financiero'.")
    tp = d.get("tips")
    if not isinstance(tp, list) or len(tp) != 3:
        f.errores.append("tips: exactamente 3.")
    else:
        for i, x in enumerate(tp, 1):
            if not isinstance(x, dict) or set(x) != {"titulo", "texto"}:
                f.errores.append(f"tips[{i}]: lleva 'titulo' y 'texto'."); continue
            if not 0 < len(x["titulo"]) <= 30 or not 0 < len(x["texto"]) <= 110:
                f.errores.append(f"tips[{i}]: título hasta 30 caracteres y texto hasta 110.")
    return f.errores

def armar(d, kit):
    c = fondo_kit(kit, "fondo-tips.png", 1080, 1350)
    c += caja(141, 93, 330, 34, f'<div style="font-size:22px;color:{VIOLETA}">www.insiderfinance.com.ar</div>', alinear="left", vertical="center")
    c += caja(191, 312, 330, 120, f'<div class="tit" style="font-size:101px;color:{VIOLETA}">TIPS</div>', alinear="left")
    c += caja(527, 322, 400, 100, f'<div style="font-family:\'Insider Sans Expanded Black\';font-size:36px;line-height:1.2;color:{BLANCO}">{multilinea(d["subtitulo"])}</div>', alinear="left")
    for i, x in enumerate(d["tips"]):
        c += caja(301, 588 + i * 150, 600, 140,
                  f'<div style="font-size:27px;line-height:1.15;color:{GRIS}"><span style="font-family:\'Insider Sans Expanded Medium\'">{t(x["titulo"])}</span> {t(x["texto"])}</div>',
                  alinear="left", campo=f"tips[{i+1}]")
    c += caja(210, 1216, 560, 75, '<div style="font-size:28px;line-height:1.2;color:#1D1D1B">Recomendamos guardar este post<br>ya que contiene valiosa información</div>', alinear="left")
    return pagina(1080, 1350, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["fondo-tips.png"])
