#!/usr/bin/env python3
"""Y01 - Miniatura de YouTube (1280x720), en 4 variantes copiadas de Canva (miniaturas 2026):
  - "pablo":    fondo coral con hexágonos y Pablo; título opcional en blanco (se agrega cuando se usa).
  - "programa": título grande violeta + subtítulo blanco sobre barra coral, con Pablo (ej. "TIC TAC / DEL MERCADO").
  - "nota":     "Nota con ..." + título violeta + texto blanco en recuadro coral, con Pablo y flechas.
  - "video":    captura del video de fondo (--foto) con banda coral y título blanco abajo.
Los textos van en Insider Sans Expanded ExtraBold (en Canva figura como "Heavy"), en mayúsculas.
"""
import base64, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, ejecutar, CORAL, VIOLETA, BLANCO  # noqa: E402

FONDOS = {"pablo": "youtube-pablo.png", "programa": "youtube-programa.png", "nota": "youtube-nota.png"}
CAMPOS = {"variante", "titulo", "subtitulo", "invitado", "texto", "foto"}
HEAVY = "font-family:'Insider Sans Expanded ExtraBold';"

def validar(d):
    f = Ficha(d, CAMPOS)
    f.opcion("variante", set(FONDOS) | {"video"})
    v = d.get("variante")
    if v == "pablo":
        f.texto("titulo", 40, obligatorio=False)
    if v == "programa":
        f.texto("titulo", 16); f.texto("subtitulo", 26)
    if v == "nota":
        f.texto("invitado", 40, ayuda="Ej. 'Nota con Pablo Wende'."); f.texto("titulo", 26); f.texto("texto", 60)
    if v == "video":
        f.texto("titulo", 90)
        foto = d.get("foto")
        if not isinstance(foto, str) or not Path(foto).is_file():
            f.errores.append("foto: ruta a la captura del video (PNG o JPG) que adjuntó la persona.")
        else:
            cab = Path(foto).read_bytes()[:4]
            if not (cab.startswith(b"\x89PNG") or cab.startswith(b"\xff\xd8")):
                f.errores.append("foto: tiene que ser una imagen PNG o JPG real.")
    return f.errores

def uri(ruta):
    datos = Path(ruta).read_bytes()
    tipo = "png" if datos.startswith(b"\x89PNG") else "jpeg"
    return f"data:image/{tipo};base64," + base64.b64encode(datos).decode()

def caja(x, y, w, h, texto, tam, color, clase="", extra=""):
    return (f'<div class="abs {clase}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;'
            f'align-items:center;justify-content:center;text-align:center;font-size:{tam}px;color:{color};'
            f'line-height:1.1;text-transform:uppercase;{extra}">{t(texto)}</div>')

def armar(d, kit):
    v = d["variante"]
    if v == "video":
        cuerpo = (f'<img class="abs" src="{uri(d["foto"])}" style="left:0;top:0;width:1280px;height:720px;object-fit:cover">'
                  f'<div class="abs" style="left:0;top:602px;width:1280px;height:118px;background:{CORAL}"></div>'
                  + caja(0, 610, 1280, 104, d["titulo"], 40, BLANCO, "encoge ajusta", HEAVY + "padding:0 30px;"))
    else:
        cuerpo = f'<img class="abs" src="{uri(Path(kit, FONDOS[v]))}" style="left:0;top:0;width:1280px;height:720px">'
        if v == "pablo" and d.get("titulo"):
            cuerpo += caja(60, 200, 700, 320, d["titulo"], 80, BLANCO, "encoge ajusta", HEAVY + "justify-content:flex-start;text-align:left;")
        if v == "programa":
            cuerpo += caja(72, 241, 683, 140, d["titulo"], 110, VIOLETA, "encoge", HEAVY + "white-space:nowrap;")
            cuerpo += caja(94, 371, 600, 63, d["subtitulo"], 40, BLANCO, "encoge", HEAVY + "white-space:nowrap;")
        if v == "nota":
            cuerpo += caja(463, 197, 784, 37, d["invitado"], 27, VIOLETA, "", "text-transform:none;")
            cuerpo += caja(463, 262, 784, 80, d["titulo"], 57, VIOLETA, "encoge", HEAVY + "white-space:nowrap;")
            cuerpo += caja(502, 343, 717, 118, d["texto"], 40, BLANCO, "encoge ajusta", HEAVY + "padding:0 20px;")
    return pagina(1280, 720, "", cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1280, 720, list(FONDOS.values()))
