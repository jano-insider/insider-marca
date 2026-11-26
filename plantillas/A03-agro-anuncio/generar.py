#!/usr/bin/env python3
"""A03 - Insider AgroFinance · Historia · Anuncio (1080x1920).
Dirección de marketing (Chari, 26/11/2026): foto de campo con filtro coral, una palabra grande que segmente
(AGRO, SOJA, GRANOS...) para que la pieza le llegue al productor y no a quien busca un préstamo, lo financiero
más chico abajo, y los hexágonos de Insider para la personalidad. Sin fondo violeta pleno.
Palabra grande + etiqueta opcional + título (**así** va en violeta) + 1 a 3 ítems con tilde + llamado.
El llamado es "Consultá para recibir asesoramiento" si no se indica otro; nunca un número de teléfono ni "tu asesor".
Solo piezas de mercado o educativas: nunca datos de un cliente.

Ficha:
{
  "palabra": "SOJA",
  "etiqueta": "Granos y coberturas",                     # opcional
  "titulo": "Decisiones financieras **para tu campaña**",
  "items": ["Comercialización de granos y coberturas.", "Con asesores idóneos matriculados."],   # opcional
  "cta": "Consultá para recibir asesoramiento",               # opcional
  "foto": "/mnt/session/uploads/campo.jpg"                # foto de campo adjunta (JPG o PNG)
}"""
import re, sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, foto_uri, es_imagen, CORAL, VIOLETA, BLANCO

CAMPOS = {"palabra", "etiqueta", "titulo", "items", "cta", "foto"}
LOGO = "agro-logo-vertical-blanco.png"
PIE = "Un área de Insider Finance · Agente Productor CNV Mat. 1581"
LLAMADO = "Consultá para recibir asesoramiento"
C = "238,117,99"
FILTRO = (f"linear-gradient(to bottom, rgba({C},0.55) 0%, rgba({C},0.08) 18%, rgba({C},0.30) 36%, "
          f"rgba({C},0.86) 52%, rgba({C},0.95) 100%)")


def validar(d):
    f = Ficha(d, CAMPOS)
    f.texto("palabra", 10, patron=r"^[A-ZÁÉÍÓÚÑÜ ]+$", ayuda="Una palabra corta en mayúsculas que diga 'campo': AGRO, SOJA, GRANOS, COSECHA.")
    f.texto("etiqueta", 45, obligatorio=False, ayuda="Ej. 'GRANOS Y COBERTURAS'.")
    f.texto("titulo", 80, ayuda="Usá **así** para la parte en violeta.")
    f.lista("items", 1, 3, 60, obligatorio=False)
    f.texto("cta", 40, obligatorio=False)
    cta = d.get("cta") or ""
    if re.search(r"\d{6,}|\d[\d\s\-]{8,}\d", cta) or re.search(r"\basesor(a|es|as)?\b", cta.lower()):
        f.errores.append("cta: sin números de teléfono ni \"tu asesor\". Usá \"Consultá para recibir asesoramiento\".")
    if not es_imagen(d.get("foto")):
        f.errores.append("foto: falta la foto de campo adjunta (ruta a un JPG o PNG en /mnt/session/uploads/).")
    return f.errores


def armar(d, kit):
    css = f"""
    .marco {{ position:absolute; left:100px; right:100px; top:640px; bottom:250px; overflow:hidden;
             display:flex; flex-direction:column; justify-content:flex-end; gap:34px; }}
    .marco > * {{ flex-shrink:0; }}
    .palabra {{ font-family:'Insider Sans Expanded Black'; color:{BLANCO}; font-size:230px; line-height:0.95; white-space:nowrap; }}
    .etq {{ color:{BLANCO}; font-size:32px; letter-spacing:3px; text-transform:uppercase; }}
    .titulo {{ color:{BLANCO}; font-size:78px; line-height:1.08; }}
    .titulo .res {{ color:{VIOLETA}; }}
    .item {{ display:flex; align-items:center; gap:24px; margin-bottom:20px; font-size:40px; color:{BLANCO}; }}
    .item svg {{ width:48px; height:48px; flex-shrink:0; }}
    .cta {{ align-self:flex-start; background:{BLANCO}; color:{CORAL}; border-radius:44px; padding:22px 40px; font-size:32px; white-space:nowrap; }}
    .blanco svg {{ filter:brightness(0) invert(1); -webkit-mask-image:linear-gradient(to right, transparent 0%, #000 45%); mask-image:linear-gradient(to right, transparent 0%, #000 45%); }}   /* hexágonos en blanco sobre la foto (pedido de marketing) */
    .pie {{ position:absolute; left:100px; right:100px; top:1745px; font-size:26px; color:{BLANCO}; text-align:center; }}
    """
    tilde = (f'<svg viewBox="0 0 50 50"><circle cx="25" cy="25" r="24" fill="{BLANCO}"/>'
             f'<path d="M14 26 L22 34 L37 17" fill="none" stroke="{CORAL}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    foto = (f'<img class="abs" src="{foto_uri(d["foto"])}" style="left:0;top:0;width:1080px;height:1920px;object-fit:cover">'
            f'<div class="abs" style="left:0;top:0;width:1080px;height:1920px;background:{FILTRO}"></div>')
    logo = f'<img class="abs" src="{foto_uri(Path(kit) / LOGO)}" style="left:100px;top:110px;width:200px" alt="Insider AgroFinance">'
    etq = f'<div class="etq tit">{t(d["etiqueta"])}</div>' if d.get("etiqueta") else ""
    items = "".join(f'<div class="item">{tilde}<span>{t(x)}</span></div>' for x in d.get("items", []))
    items = f"<div>{items}</div>" if items else ""
    cta = f'<div class="cta tit">{t(d.get("cta") or LLAMADO)}</div>'
    cuerpo = f"""{foto}<div class="esq-sd blanco">{svg_kit(kit, "hexagonos-esquina-sup-der.svg")}</div>{logo}
    <div class="marco ajusta" data-campo="palabra/titulo/items/cta"><div class="palabra encoge-alto" data-max="260">{t(d["palabra"])}</div>{etq}
    <div class="titulo tit encoge">{t(d['titulo'])}</div>{items}{cta}</div><div class="pie">{PIE}</div>"""
    return pagina(1080, 1920, css, cuerpo)


if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1080, 1920, ["hexagonos-esquina-sup-der.svg", LOGO])
