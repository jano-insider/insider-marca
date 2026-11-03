#!/usr/bin/env python3
"""R01 - Portada de reel o de video (1080x1920), copiada de las portadas de Canva y del Illustrator.
"estilo": "reel" (hexágonos blancos suaves, por defecto) o "video" (hexágonos grandes y botón PLAY del Illustrator).

Foto de la persona a pantalla completa (--foto, la adjunta quien pide la pieza), la capa de hexágonos
blancos semitransparentes de los originales y el título en líneas: cada línea va en violeta, o en blanco
sobre barra coral ("barra": true). Opcional, la etiqueta PLAY arriba del título.
En una línea con barra, **así** va en violeta (como "CLAVE ANTES **DE**").
"""
import base64, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO  # noqa: E402


def fondo_uri(kit, archivo):
    return "data:image/png;base64," + base64.b64encode(Path(kit, archivo).read_bytes()).decode()

CAMPOS = {"foto", "lineas", "play", "foco", "estilo"}

def validar(d):
    f = Ficha(d, CAMPOS)
    foto = d.get("foto")
    if not isinstance(foto, str) or not Path(foto).is_file():
        f.errores.append("foto: ruta a la foto de la persona (PNG o JPG) que adjuntó quien pide la pieza.")
    else:
        cab = Path(foto).read_bytes()[:4]
        if not (cab.startswith(b"\x89PNG") or cab.startswith(b"\xff\xd8")):
            f.errores.append("foto: tiene que ser una imagen PNG o JPG real.")
    ls = d.get("lineas")
    if not isinstance(ls, list) or not 1 <= len(ls) <= 5:
        f.errores.append("lineas: entre 1 y 5.")
    else:
        for i, l in enumerate(ls, 1):
            if not isinstance(l, dict) or not set(l) <= {"texto", "barra"} or "texto" not in l:
                f.errores.append(f"lineas[{i}]: lleva 'texto' y opcionalmente 'barra' (true/false)."); continue
            if not isinstance(l["texto"], str) or not 0 < len(l["texto"]) <= 28:
                f.errores.append(f"lineas[{i}].texto: hasta 28 caracteres (una línea).")
            if "barra" in l and not isinstance(l["barra"], bool):
                f.errores.append(f"lineas[{i}].barra: true o false.")
    if "play" in d and not isinstance(d["play"], bool):
        f.errores.append("play: true o false.")
    f.opcion("foco", {"centro", "izquierda", "derecha"}, obligatorio=False)
    f.opcion("estilo", {"reel", "video"}, obligatorio=False)
    return f.errores

def armar(d, kit):
    datos = Path(d["foto"]).read_bytes()
    foto = f"data:image/{'png' if datos.startswith(b'\\x89PNG') else 'jpeg'};base64," + base64.b64encode(datos).decode()
    foco = {"centro": "50%", "izquierda": "25%", "derecha": "75%"}[d.get("foco", "centro")]
    n = len(d["lineas"])
    video = d.get("estilo") == "video"
    largo = max(len(l['texto'].replace('*', '')) for l in d['lineas'])
    alto_linea, tam = (98, 81) if largo <= 14 else (92, 73)   # medidas de los originales (81 px u 73 px)
    y0 = 1640 - n * alto_linea                   # el bloque termina siempre a la misma altura
    alto, x0 = 1920, 102
    if video:                                     # estilo "video": medidas del Illustrator
        x0, alto_linea, tam = 142, 68, 73
        y0 = 1537 - n * alto_linea
    css = f"""
    .foto {{ position:absolute; inset:0; width:1080px; height:{alto}px; object-fit:cover; object-position:{foco} 30%; }}
    .hex {{ position:absolute; left:0; top:0; width:1080px; height:{alto}px; }}
    .bloque {{ position:absolute; left:{x0}px; right:60px; top:{y0}px; display:flex; flex-direction:column; align-items:flex-start; }}
    .lin {{ height:{alto_linea}px; display:flex; align-items:center; font-size:{tam}px; line-height:1; text-transform:uppercase;
            white-space:nowrap; max-width:918px; overflow:hidden; }}
    .lin.sin {{ color:{VIOLETA}; padding-left:16px; }}
    .lin.con span {{ background:{CORAL}; color:{BLANCO}; padding:4px 16px 0; height:{alto_linea - 8}px; line-height:{alto_linea - 8}px; display:block; }}
    .lin.con .res {{ color:{VIOLETA}; }}
    .play {{ position:absolute; left:160px; top:{y0 - 125}px; display:flex; align-items:center; }}
    .play .pill {{ margin-left:-30px; border:3px solid {CORAL}; border-radius:40px; padding:6px 26px 6px 44px; font-size:22px; color:#1D1D1B; background:rgba(255,255,255,.35); }}
    """
    lineas = "".join(f'<div class="lin tit encoge {"con" if l.get("barra") else "sin"}"><span>{t(l["texto"])}</span></div>'
                     for l in d["lineas"])
    play = (f'<div class="play"><svg width="72" height="72" viewBox="0 0 72 72" style="position:relative;z-index:1">'
            f'<circle cx="36" cy="36" r="36" fill="{CORAL}"/><path d="M28 22 L50 36 L28 50 Z" fill="{BLANCO}"/></svg>'
            f'<div class="pill tit">PLAY</div></div>') if d.get("play") else ""
    if video:   # la capa del estilo "video" ya trae los hexágonos y el botón PLAY
        capa = (f'<img class="hex" src="{fondo_uri(kit, "capa-video-reel.png")}">'
                '<div class="abs tit" style="left:254px;top:1219px;font-size:22px;color:#1D1D1B">PLAY</div>')
        play = ""
    else:
        capa = f'<div class="hex">{svg_kit(kit, "hexagonos-reel.svg")}</div>'
    cuerpo = f'<img class="foto" src="{foto}">{capa}{play}<div class="bloque">{lineas}</div>'
    return pagina(1080, alto, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["hexagonos-reel.svg", "capa-video-reel.png"])
