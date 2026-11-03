#!/usr/bin/env python3
"""S01 - Posteo · Testimonio "Insider views" (1080x1350). Copiado del Illustrator de marketing.
Foto del cliente en círculo (--foto, la adjunta quien pide), testimonio y nombre con la inicial del apellido.
Los hexágonos de abajo van siempre como en el original (marketing: no se modifican)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, ejecutar, fondo_kit, foto_uri, es_imagen, caja, VIOLETA

CAMPOS = {"foto", "testimonio", "nombre"}
AMARILLO, VACIO, BARRA = "#F7B731", "#3C2A68", "#573D8C"

def validar(d):
    f = Ficha(d, CAMPOS)
    if not es_imagen(d.get("foto")):
        f.errores.append("foto: ruta a la foto de quien da el testimonio (PNG o JPG).")
    f.texto("testimonio", 170)
    f.texto("nombre", 30, patron=r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+( [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)* [A-ZÁÉÍÓÚÑ]\.$",
            ayuda="Nombre y solo la inicial del apellido, ej. 'Armando A.'.")
    return f.errores

def hexa(cx, cy, color):
    import math
    pts = " ".join(f"{cx + 22 * math.sin(math.radians(a)):.1f},{cy - 25 * math.cos(math.radians(a)):.1f}" for a in range(0, 360, 60))
    return f'<polygon points="{pts}" fill="none" stroke="{color}" stroke-width="6" stroke-linejoin="round"/>'

def armar(d, kit):
    c = fondo_kit(kit, "fondo-testimonio.png", 1080, 1350)
    c += (f'<div class="abs" style="left:423px;top:337px;width:227px;height:227px;border-radius:50%;overflow:hidden">'
          f'<img src="{foto_uri(d["foto"])}" style="width:100%;height:100%;object-fit:cover;object-position:50% 25%"></div>')
    c += caja(170, 612, 740, 195, f'<div style="font-size:36px;line-height:1.21;color:#1D1D1B">{t(d["testimonio"])}</div>',
              vertical="center", campo="testimonio")
    c += caja(170, 812, 740, 50, f'<div style="font-size:36px;color:{VIOLETA}">{t(d["nombre"])}</div>')
    c += caja(300, 1252, 480, 50, f'<div style="font-size:36px;color:#FFFFFF">Insider<span style="color:{AMARILLO}">views</span></div>')
    return pagina(1080, 1350, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1350, ["fondo-testimonio.png"])
