#!/usr/bin/env python3
"""H08 - Historia · Anuncio destacado (1080x1920).
Etiqueta chica + título grande en dos colores (**así** va en coral) + ítems con tilde + llamado.
Ej.: 'Ya se habilitó la apertura de las cuentas FAL'."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, banda, ejecutar, CORAL, VIOLETA, BLANCO

CAMPOS = {"etiqueta", "titulo", "items", "cta"}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("etiqueta", 45, obligatorio=False, ayuda="Ej. 'FONDO DE ASISTENCIA LABORAL'.")
    f.texto("titulo", 80, ayuda="Usá **así** para la parte en coral.")
    f.lista("items", 1, 3, 60, obligatorio=False)
    f.texto("cta", 70, obligatorio=False)
    return f.errores

def armar(d, kit):
    css = f"""
    .marco {{ position:absolute; left:110px; right:110px; top:300px; bottom:300px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:center; gap:48px; }}
    .marco > * {{ flex-shrink:0; }}
    .etq {{ color:{VIOLETA}; font-size:34px; letter-spacing:3px; text-transform:uppercase; }}
    .titulo {{ color:{VIOLETA}; font-size:122px; line-height:1.05; }}
    .titulo .res {{ color:{CORAL}; }}
    .item {{ display:flex; align-items:center; gap:24px; font-size:44px; color:{VIOLETA}; }}
    .item svg {{ width:50px; height:50px; flex-shrink:0; }}
    .cta {{ color:{VIOLETA}; font-size:50px; line-height:1.2; text-transform:uppercase; }}
    """
    tilde = (f'<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="24" fill="{CORAL}"/>'
             f'<path d="M14 26 L22 34 L37 17" fill="none" stroke="{BLANCO}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    etq = f'<div class="etq tit">{t(d["etiqueta"])}</div>' if d.get("etiqueta") else ""
    items = "".join(f'<div class="item">{tilde}<span>{t(x)}</span></div>' for x in d.get("items", []))
    cta = f'<div class="cta tit">{t(d["cta"])}</div>' if d.get("cta") else ""
    cuerpo = f"""{banda(kit, "hexagonos-banda-2.svg", -18, -683, 1116, 1062, 0.405)}{banda(kit, "hexagonos-banda-3.svg", -26, 1665, 1106, 1053, 0.405)}
    <div class="marco ajusta" data-campo="titulo/items/cta">{etq}<div class="titulo tit encoge">{t(d['titulo'])}</div>
    <div>{items}</div>{cta}</div>"""
    return pagina(1080, 1920, css, cuerpo)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920,
             ["hexagonos-banda-2.svg", "hexagonos-banda-3.svg"])
