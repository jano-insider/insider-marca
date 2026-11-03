#!/usr/bin/env python3
"""S03 - Posteo · Cita (1080x1350). Copiado del Illustrator de marketing.
Frase y autor en el recuadro coral; la foto recortada de quien la dijo es opcional (--foto, PNG con fondo transparente)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, ejecutar, fondo_kit, foto_uri, es_imagen, caja, BLANCO

CAMPOS = {"frase", "autor", "foto"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("frase", 130); f.texto("autor", 30)
    if "foto" in d and not es_imagen(d["foto"]):
        f.errores.append("foto: ruta a la foto recortada de quien dijo la frase (PNG), o sacá el campo para que vaya sin foto.")
    return f.errores

def armar(d, kit):
    c = fondo_kit(kit, "fondo-cita.png", 1080, 1350)
    c += caja(135, 420, 590, 280, f'<div style="font-size:44px;line-height:1.2;color:{BLANCO}">{t(d["frase"])}</div>',
              vertical="center", campo="frase")
    c += caja(135, 718, 590, 45, f'<div style="font-family:\'Insider Sans Expanded Medium\';font-size:30px;color:{BLANCO}">- {t(d["autor"])}</div>')
    if d.get("foto"):
        c += (f'<img class="abs" src="{foto_uri(d["foto"])}" style="left:100px;top:760px;width:760px;height:590px;'
              f'object-fit:contain;object-position:50% 100%;filter:drop-shadow(8px 8px 14px rgba(0,0,0,.35))">')
    return pagina(1080, 1350, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["fondo-cita.png"])
