#!/usr/bin/env python3
"""N02 - Historia · Nota en un diario o medio escrito (1440x2560), copiada de "historias y posts para
mostrar notas de diarios 2026". El recorte de la nota (--recorte, lo adjunta quien pide) va dentro de un
recuadro crema, con margen alrededor (pedido de marketing).
Variantes:
  - "clasica":  medio, "ENTREVISTA A ..." en recuadro, recorte grande y llamado abajo.
  - "compacta": lo mismo en tamaño más chico, con más aire alrededor.
  - "coral":    fondo coral, medio en blanco, NOTA grande, recorte y entrevista abajo.
  - "titular":  medio, un titular en violeta, recorte y entrevista abajo.
Ficha: {"variante": "clasica", "medio": "Diario El Cronista", "entrevista": "Entrevista a Pablo Lazzati",
        "recorte": "/mnt/session/uploads/adjunto-1.jpg", "llamado": "...", "titular": "..."}
"llamado" va en clasica y compacta (opcional); "titular" es obligatorio en la variante titular.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comun import Ficha, t, pagina, svg_kit, ejecutar, fondo_kit, foto_uri, es_imagen, caja, CORAL, VIOLETA, BLANCO  # noqa: E402

VARIANTES = {"clasica", "compacta", "coral", "titular"}
CAMPOS = {"variante", "medio", "entrevista", "recorte", "llamado", "titular"}
NEGRO, CREMA = "#1D1D1B", "#FAF6F0"
EXTRA = "font-family:'Insider Sans Expanded ExtraBold';"
LLAMADO = "Hablá con tu asesor para invertir de acuerdo a tu perfil."
# Recuadro del recorte (x, y, ancho, alto) en cada variante, medido en el original
RECUADRO = {"clasica": (29, 991, 1383, 1057), "compacta": (144, 1026, 1174, 892),
            "coral": (58, 1004, 1306, 757), "titular": (32, 899, 1374, 1044)}
MARGEN = 60   # aire entre el borde del recuadro y el recorte
# Ícono propio de marketing (celular con portal de noticias), en el lugar del ícono del original: (x, y, alto)
ICONO = {"clasica": (729, 233, 300), "compacta": (726, 495, 210), "coral": (726, 470, 210), "titular": (729, 455, 160)}

def validar(d):
    f = Ficha(d, CAMPOS)
    f.opcion("variante", VARIANTES)
    f.texto("medio", 30, ayuda="Ej. 'Diario El Cronista'.")
    f.texto("entrevista", 40, ayuda="Ej. 'Entrevista a Pablo Lazzati'.")
    if not es_imagen(d.get("recorte")):
        f.errores.append("recorte: ruta a la imagen del recorte de la nota (PNG o JPG) que adjuntó quien pide la pieza.")
    if d.get("variante") == "titular":
        f.texto("titular", 90)
    elif "titular" in d:
        f.errores.append("titular: solo va en la variante 'titular'.")
    if d.get("variante") in ("clasica", "compacta"):
        f.texto("llamado", 90, obligatorio=False)
    elif "llamado" in d:
        f.errores.append("llamado: solo va en las variantes 'clasica' y 'compacta'.")
    return f.errores

def armar(d, kit):
    v = d["variante"]
    c = fondo_kit(kit, f"diario-{v}.png", 1440, 2560)
    cx, iy, ih = ICONO[v]; iw = round(ih * 195 / 316)
    c += f'<div class="abs" style="left:{cx - iw // 2}px;top:{iy}px;width:{iw}px;height:{ih}px">{svg_kit(kit, "noticias-celular.svg")}</div>'
    x, y, w, h = RECUADRO[v]
    c += (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CREMA};padding:{MARGEN}px;'
          f'box-sizing:border-box"><img src="{foto_uri(d["recorte"])}" style="width:100%;height:100%;object-fit:contain"></div>')
    up = "text-transform:uppercase;"
    if v == "clasica":
        c += caja(200, 596, 1040, 92, f'<div class="encoge" style="{EXTRA}font-size:57px;color:{CORAL};white-space:nowrap;width:100%">{t(d["medio"])}</div>', vertical="center")
        c += caja(387, 733, 677, 202, f'<div style="font-size:57px;line-height:1.15;color:{NEGRO};{up}max-width:500px">{t(d["entrevista"])}</div>', vertical="center")
        c += caja(150, 2110, 1140, 250, f'<div style="{EXTRA}font-size:53px;line-height:1.25;color:{VIOLETA};{up}">{t(d.get("llamado", LLAMADO))}</div>', vertical="center", campo="llamado")
    if v == "compacta":
        c += caja(300, 748, 840, 66, f'<div class="encoge" style="{EXTRA}font-size:40px;color:{CORAL};white-space:nowrap;width:100%">{t(d["medio"])}</div>', vertical="center")
        c += caja(486, 845, 476, 142, f'<div style="font-size:40px;line-height:1.15;color:{NEGRO};{up}max-width:350px">{t(d["entrevista"])}</div>', vertical="center")
        c += caja(126, 1970, 1189, 180, f'<div style="{EXTRA}font-size:37px;line-height:1.3;color:{VIOLETA};{up}">{t(d.get("llamado", LLAMADO))}</div>', vertical="center", campo="llamado")
    if v == "coral":
        c += caja(300, 736, 840, 66, f'<div class="encoge" style="{EXTRA}font-size:40px;color:{BLANCO};white-space:nowrap;width:100%">{t(d["medio"])}</div>', vertical="center")
        c += caja(200, 800, 1040, 190, f'<div class="tit" style="font-size:151px;line-height:1;color:{VIOLETA}">NOTA</div>', vertical="center")
        c += caja(495, 1834, 454, 142, f'<div style="font-size:40px;line-height:1.15;color:{BLANCO};{up}max-width:350px">{t(d["entrevista"])}</div>', vertical="center")
    if v == "titular":
        c += caja(300, 638, 840, 74, f'<div class="encoge" style="{EXTRA}font-size:46px;color:{CORAL};white-space:nowrap;width:100%">{t(d["medio"])}</div>', vertical="center")
        c += caja(110, 722, 1220, 160, f'<div style="{EXTRA}font-size:41px;line-height:1.25;color:{VIOLETA};{up}">{t(d["titular"])}</div>', vertical="center", campo="titular")
        c += caja(470, 1975, 500, 120, f'<div style="font-size:43px;line-height:1.15;color:{NEGRO};{up}max-width:380px">{t(d["entrevista"])}</div>', vertical="center")
    return pagina(1440, 2560, "", c)

if __name__ == "__main__":
    ejecutar(__doc__, validar, armar, 1440, 2560, [f"diario-{v}.png" for v in sorted(VARIANTES)] + ["noticias-celular.svg"])
