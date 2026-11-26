#!/usr/bin/env python3
"""Prueba de regresión del kit de marca (insider-marca).

Genera todas las plantillas con sus fichas de ejemplo usando el kit de DOS commits (el que está en producción y el
nuevo) y compara las piezas píxel por píxel. Así se ve qué cambió de verdad, incluido lo que cambió sin querer.

Uso:  python3 regresion.py <commit_viejo> <commit_nuevo> [carpeta_de_fichas_extra]

- Las fichas que piden una foto adjunta (/mnt/session/uploads/...) usan una foto de prueba generada acá.
- La carpeta de fichas extra (opcional) tiene subcarpetas con el nombre de la plantilla (ej. N01-nota-video-audio/)
  y adentro fichas .json: sirve para probar variantes que el ejemplo no cubre.
- Resultado por pieza: IGUAL, DISTINTA (con la zona que cambió), NUEVA (no existe en el commit viejo) o FALLA.
"""
import json, os, re, subprocess, sys, shutil, urllib.request, concurrent.futures as cf
from pathlib import Path
from PIL import Image, ImageChops

REPO = "https://raw.githubusercontent.com/jano-insider/insider-marca/"
BASE = Path(os.environ.get("REGRESION_DIR", "/tmp/regresion"))


def bajar_kit(commit):
    """Baja el kit de un commit con la misma lógica que la preparación del agente."""
    raiz = BASE / commit[:7]
    if (raiz / "listo").exists():
        return raiz
    marca, fuentes = raiz / "marca", Path.home() / ".fonts"
    marca.mkdir(parents=True, exist_ok=True); fuentes.mkdir(exist_ok=True)
    lista = urllib.request.urlopen(REPO + commit + "/kit.txt").read().decode().split("\n")
    lista = [x for x in lista if re.match(r"^[A-Za-z0-9_/.-]+$", x) and ".." not in x]

    def uno(f):
        if f.startswith("fuentes/"):
            d = fuentes / Path(f).name
        elif f.startswith("plantillas/"):
            d = raiz / f
        elif f.startswith("logos-terceros/"):
            d = marca / f
        else:
            d = marca / Path(f).name
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(urllib.request.urlopen(REPO + commit + "/" + f).read())

    with cf.ThreadPoolExecutor(8) as ex:
        list(ex.map(uno, lista))
    subprocess.run(["fc-cache", "-f"], capture_output=True)
    (raiz / "listo").write_text("ok")
    return raiz


def foto_prueba():
    p = BASE / "foto-prueba.jpg"
    if not p.exists():
        BASE.mkdir(parents=True, exist_ok=True)
        im = Image.linear_gradient("L").resize((1600, 1000)).convert("RGB")
        im.save(p, quality=90)
    return str(p)


def preparar_ficha(origen, destino):
    datos = json.loads(Path(origen).read_text(encoding="utf-8"))
    foto = foto_prueba()

    def cambiar(x):
        if isinstance(x, str) and x.startswith("/mnt/session/uploads/"):
            return foto
        if isinstance(x, list):
            return [cambiar(y) for y in x]
        if isinstance(x, dict):
            return {k: cambiar(v) for k, v in x.items()}
        return x

    destino.write_text(json.dumps(cambiar(datos), ensure_ascii=False), encoding="utf-8")


def generar(raiz, plantilla, ficha, salida, nombre):
    gen = raiz / "plantillas" / plantilla / "generar.py"
    if not gen.exists():
        return "no existe"
    salida.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(gen), str(ficha), "--kit", str(raiz / "marca"),
                        "--salida", str(salida), "--nombre", nombre], capture_output=True, text=True)
    return "ok" if r.returncode == 0 else (r.stdout + r.stderr).strip().splitlines()[-1][:160]


def comparar(a, b):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return f"DISTINTA (tamaño {ia.size} → {ib.size})"
    caja = ImageChops.difference(ia, ib).getbbox()
    return "IGUAL" if caja is None else f"DISTINTA en x {caja[0]}-{caja[2]}, y {caja[1]}-{caja[3]}"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    viejo, nuevo = sys.argv[1], sys.argv[2]
    extra = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    kv, kn = bajar_kit(viejo), bajar_kit(nuevo)
    casos = []
    for d in sorted((kn / "plantillas").iterdir()):
        if not d.is_dir():
            continue
        fichas = sorted(d.glob("ejemplo*.json"))
        if extra and (extra / d.name).is_dir():
            fichas += sorted((extra / d.name).glob("*.json"))
        for f in fichas:
            casos.append((d.name, f))
    trabajo = BASE / "fichas"; trabajo.mkdir(parents=True, exist_ok=True)
    resultados = []
    for plantilla, f in casos:
        nombre = re.sub(r"[^a-z0-9-]", "-", f"{plantilla[:3]}-{f.stem}".lower())[:60]
        ficha = trabajo / f"{nombre}.json"; preparar_ficha(f, ficha)
        sv, sn = BASE / "salida" / viejo[:7], BASE / "salida" / nuevo[:7]
        rv = generar(kv, plantilla, ficha, sv, nombre)
        rn = generar(kn, plantilla, ficha, sn, nombre)
        if rn != "ok":
            resultados.append((nombre, f"FALLA en el nuevo: {rn}")); continue
        if rv == "no existe":
            resultados.append((nombre, "NUEVA")); continue
        if rv != "ok":
            resultados.append((nombre, f"NUEVA (en el viejo falla: {rv})")); continue
        pngs = sorted(sn.glob(f"{nombre}*.png"))
        if not pngs:   # documentos (D01-D03): se comparan las páginas del PDF
            for s in (sv, sn):
                pdf = s / f"{nombre}.pdf"
                if pdf.exists():
                    subprocess.run(["pdftoppm", "-r", "40", "-png", str(pdf), str(s / f"{nombre}-pag")], capture_output=True)
            pngs = sorted(sn.glob(f"{nombre}-pag*.png"))
            if not pngs:
                resultados.append((nombre, "FALLA: no generó PNG ni PDF")); continue
        for p in pngs:
            q = sv / p.name
            resultados.append((p.stem, comparar(q, p) if q.exists() else "NUEVA (lámina de más)"))
    ancho = max(len(n) for n, _ in resultados)
    for n, r in resultados:
        print(f"{n:<{ancho}}  {r}")
    distintas = [n for n, r in resultados if not r.startswith("IGUAL")]
    print(f"\n{len(resultados)} piezas · {len(resultados) - len(distintas)} iguales · {len(distintas)} con cambios")


if __name__ == "__main__":
    main()
