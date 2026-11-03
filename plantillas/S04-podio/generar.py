#!/usr/bin/env python3
"""S04 - Posteo · Podio de acciones argentinas (1080x1350). Copiado del Illustrator de marketing.
Las 3 acciones del período: la 1.ª va en el centro (columna alta), la 2.ª a la izquierda y la 3.ª a la derecha."""
import re, sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, ejecutar, fondo_kit, caja, VIOLETA, BLANCO

CAMPOS = {"periodo", "podio", "nota"}
COLUMNAS = [(409, 667, 620), (142, 400, 790), (676, 934, 845)]   # 1.º, 2.º, 3.º: (x0, x1, alto donde empieza la columna)

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("periodo", 16, ayuda="Ej. 'OCTUBRE 2026'.")
    p = d.get("podio")
    if not isinstance(p, list) or len(p) != 3:
        f.errores.append("podio: exactamente 3 acciones, en orden (1.º, 2.º, 3.º).")
    else:
        for i, a in enumerate(p, 1):
            if not isinstance(a, dict) or set(a) != {"ticker", "variacion"}:
                f.errores.append(f"podio[{i}]: lleva 'ticker' y 'variacion'."); continue
            if not re.match(r"^[A-Z0-9]{2,6}$", str(a["ticker"])):
                f.errores.append(f"podio[{i}].ticker: en mayúsculas, ej. 'GGAL'.")
            if not re.match(r"^[+-]?\d{1,4}(,\d{1,2})?%$", str(a["variacion"])):
                f.errores.append(f"podio[{i}].variacion: ej. '12,5%'.")
    f.texto("nota", 40, obligatorio=False)
    return f.errores

def armar(d, kit):
    c = fondo_kit(kit, "fondo-podio.png", 1080, 1350)
    c += caja(100, 196, 880, 120, f'<div class="tit" style="font-size:101px;color:{VIOLETA}">PODIO</div>')
    c += caja(100, 294, 880, 50, '<div style="font-size:36px;color:#1D1D1B">de acciones argentinas</div>')
    c += caja(440, 362, 200, 40, f'<div class="tit encoge" style="width:100%;font-size:26px;color:#1D1D1B;white-space:nowrap">{t(d["periodo"])}</div>', vertical="center")
    for (x0, x1, y), a in zip(COLUMNAS, d["podio"]):
        c += caja(x0, y, x1 - x0, 80, f'<div class="tit encoge" style="width:100%;font-size:46px;color:{BLANCO};white-space:nowrap">{t(a["ticker"])}</div>', vertical="center")
        c += caja(x0, 1034, x1 - x0, 45, f'<div class="tit" style="font-size:27px;color:#1D1D1B">{t(a["variacion"])}</div>')
    c += caja(100, 1120, 880, 50, f'<div style="font-size:36px;color:{VIOLETA}">{t(d.get("nota", "Datos tomados en pesos"))}</div>')
    c += caja(150, 1250, 470, 55, f'<div style="font-size:36px;color:{BLANCO}">hablá con tu asesor</div>', alinear="left")
    c += caja(639, 1242, 300, 70, f'<div style="font-size:23px;line-height:1.25;color:{BLANCO}">para elegir la mejor<br>opción de inversión</div>', alinear="left")
    return pagina(1080, 1350, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["fondo-podio.png"])
