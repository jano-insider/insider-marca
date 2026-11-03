#!/usr/bin/env python3
"""H09 - Historia · Pregunta en píldoras con personaje (1080x1920).
Ej.: 'Termina la semana.' / 'Quedan pocos días para elegir…' / '¿El plazo fijo conviene hoy?'
Título coral (un salto de línea con \\n), personaje, 1 a 3 píldoras violetas y cierre (**así** va en violeta)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, multilinea, pagina, svg_kit, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"titulo", "pildoras", "cierre", "ilustracion"}
ILUSTRACIONES = {f"iconografia-{i:02d}" for i in range(1, 25)}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("titulo", 70)
    f.lista("pildoras", 1, 3, 36, ayuda="Cada píldora es una línea corta.")
    f.texto("cierre", 120)
    f.opcion("ilustracion", ILUSTRACIONES, obligatorio=False)
    return f.errores

def armar(d, kit):
    # Medidas tomadas del original de Canva (historias de oct/nov 2026)
    css = f"""
    .esquina {{ position:absolute; right:0; top:0; width:0; height:0; border-style:solid;
               border-width:0 308px 330px 0; border-color:transparent {CORAL} transparent transparent; }}
    .marco {{ position:absolute; left:108px; right:98px; top:360px; bottom:280px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:flex-start; }}
    .marco > * {{ flex-shrink:0; }}
    .titulo {{ color:{CORAL}; font-size:140px; line-height:1.08; }}
    .ilu {{ width:168px; height:195px; margin:70px 0 0 15px; }}
    .pildoras {{ margin-top:-12px; display:flex; flex-direction:column; gap:22px; }}
    .pil {{ background:{VIOLETA}; color:{BLANCO}; height:83px; border-radius:6px; display:flex; align-items:center; padding:0 18px;
           justify-content:flex-start; font-family:'Insider Sans Expanded Light'; font-style:italic; font-size:44px; white-space:nowrap; overflow:hidden; }}
    .cierre {{ color:{CORAL}; font-size:66px; line-height:1.15; margin-top:90px; }}
    .cierre .res {{ color:{VIOLETA}; }}
    """
    pil = "".join(f'<div class="pil encoge">{t(p)}</div>' for p in d["pildoras"])
    nombre = d.get("ilustracion", "iconografia-05")
    cuerpo = f"""<div class="esquina"></div>
    <div class="marco ajusta" data-campo="titulo/pildoras/cierre">
      <div class="titulo tit encoge-alto" data-max="330" style="font-size:{140 if len(d['titulo']) <= 25 else 80}px">{multilinea(d['titulo'])}</div>
      <div class="ilu">{svg_kit(kit, nombre + '.svg')}</div>
      <div class="pildoras">{pil}</div>
      <div class="cierre tit">{t(d['cierre'])}</div>
    </div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["iconografia-05.svg"])
