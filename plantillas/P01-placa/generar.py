#!/usr/bin/env python3
"""P01 - Placa simple (historia 1080x1920 o posteo 1080x1350).
Título + texto opcional + llamado a la acción. Para piezas puntuales (ej. FAL).
En el título y el texto, **así** resalta una parte."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"formato", "fondo", "titulo", "texto", "cta"}
MEDIDAS = {"historia": (1080, 1920), "posteo": (1080, 1350)}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.opcion("formato", set(MEDIDAS))
    f.opcion("fondo", {"blanco", "coral"})
    f.texto("titulo", 90)
    f.texto("texto", 240, obligatorio=False)
    f.texto("cta", 30, obligatorio=False, ayuda="Ej. 'ESCRIBINOS'.")
    return f.errores

def armar(d, kit):
    ancho, alto = MEDIDAS[d["formato"]]
    coral = d["fondo"] == "coral"
    fg = BLANCO if coral else VIOLETA
    res_css = (f"background:{VIOLETA}; color:{BLANCO}; padding:0 14px; -webkit-box-decoration-break:clone; box-decoration-break:clone;"
               if coral else f"color:{CORAL};")
    margen = 260 if d["formato"] == "historia" else 150
    css = f"""
    .marco {{ position:absolute; left:90px; right:90px; top:{margen}px; bottom:{margen}px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:60px; color:{fg}; }}
    .marco > * {{ flex-shrink:0; }}
    .titulo {{ font-size:92px; line-height:1.18; text-transform:uppercase; }}
    .titulo .res {{ {res_css} }}
    .texto .res {{ font-weight:700; }}
    .texto {{ font-size:58px; line-height:1.3; }}
    .cta {{ align-self:flex-start; background:{BLANCO if coral else CORAL}; color:{CORAL if coral else BLANCO};
           font-size:54px; padding:16px 44px; border-radius:60px; text-transform:uppercase; }}
    .esquina {{ position:absolute; right:0; top:0; width:0; height:0; border-style:solid;
               border-width:0 230px 230px 0; border-color:transparent {BLANCO if coral else CORAL} transparent transparent; }}
    .logo {{ position:absolute; left:50%; transform:translateX(-50%); bottom:{margen - 120}px; width:240px; height:72px; }}
    """
    texto = f'<div class="texto">{t(d["texto"])}</div>' if d.get("texto") else ""
    cta = f'<div class="cta ita">{t(d["cta"])}</div>' if d.get("cta") else ""
    logo = svg_kit(kit, "logo-horizontal-blanco.svg" if coral else "logo-horizontal-color.svg", "logo")
    cuerpo = f"""<div class="esquina"></div>
    <div class="marco ajusta" data-campo="titulo/texto/cta">
      <div class="titulo tit encoge">{t(d['titulo'])}</div>{texto}{cta}
    </div>{logo}"""
    return pagina(ancho, alto, css, cuerpo, fondo=CORAL if coral else BLANCO)

if __name__ == "__main__":
    import json
    datos = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")) if len(sys.argv) > 1 else {}
    ancho, alto = MEDIDAS.get(datos.get("formato"), (1080, 1920))
    ejecutar(__doc__, validar, armar, ancho, alto,
             ["logo-horizontal-color.svg", "logo-horizontal-blanco.svg"])
