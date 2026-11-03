# insider-marca

Kit de marca de **Insider Finance** para uso de sus agentes de IA internos.

Este repositorio es la fuente única de los recursos de marca que usan los agentes
(fuentes, logos, patrones, íconos y plantillas vacías). Los agentes descargan los
archivos directamente desde acá.

## Estructura

| Carpeta | Contenido |
|---|---|
| `fuentes/insider-sans/` | Insider Sans Expanded, todos los pesos (.ttf) + licencia OFL |
| `fuentes/numans/` | Numans Regular (.ttf) + licencia OFL |
| `fuentes/fredoka/` | Fredoka (.ttf) + licencia OFL, para los nombres de medios en las notas |
| `logos/` | 8 logos oficiales en SVG optimizado |
| `patrones/` | Patrones de hexágonos oficiales en SVG, fondo transparente |
| `iconos/` | 24 ilustraciones propias de la marca y el ícono de alerta, en SVG |
| `documentos/` | Recursos de la hoja membretada: banda lateral e íconos de contacto |
| `fondos/` | Fondos de plantillas sacados de los originales de marketing (incluyen fotos de Pablo Lazzati, propiedad de Insider Finance) |
| `plantillas/` | Código de las plantillas fijas del agente de Diseño: un programa por plantilla que rellena una ficha de datos |
| `logos-terceros/` | Logos de índices y empresas, nombrados por ticker (`indices/SPX.png`, `empresas/BBAR.png`) |

Logos disponibles:

- `logo-vertical-color.svg`: principal, sobre fondo blanco o claro
- `logo-horizontal-color.svg`: espacios anchos, fondo claro
- `isotipo-color.svg`: solo el símbolo, fondo claro
- `logo-vertical-blanco.svg`, `logo-horizontal-blanco.svg`, `isotipo-blanco.svg`: fondos Coral, oscuros o fotos
- `logo-vertical-negro.svg`, `isotipo-negro.svg`: monocromático (patrocinadores, impresión a una tinta)

Patrones disponibles:

- `hexagonos-patron-vertical.svg`: bloque de hexágonos entero, 1080x1350, solo si se pide un fondo de hexágonos destacado
- `hexagonos-esquinas-16x9.svg`: hexágonos en esquinas, 1920x1080, para presentaciones
- `hexagonos-esquina-sup-der.svg`: grupo de esquina superior derecha, para piezas nuevas sin modelo
- `hexagonos-esquina-inf-izq.svg`: grupo de esquina inferior izquierda, para piezas nuevas sin modelo
- `hexagonos-banda-1.svg`, `hexagonos-banda-2.svg`, `hexagonos-banda-3.svg`: banda de hexágonos de las historias y portadas, en sus tres variantes de color
- `hexagonos-indice.svg`: gráfico de 4 hexágonos encadenados del índice de las presentaciones
- `hexagonos-reel.svg`: capa de hexágonos blancos semitransparentes de las portadas de reels

Íconos:

- `iconografia-01.svg` a `iconografia-24.svg`: ilustraciones de la marca (personajes, monedas, banco, calendario, etc.). Se usan chicos, abajo a la derecha o arriba del título.
- `alerta.svg`: ícono de alerta de las historias de información.

## Plantillas

Cada carpeta de `plantillas/` tiene un `generar.py` y una ficha de ejemplo. Uso:

    python3 plantillas/<CODIGO>/generar.py ficha.json --kit <carpeta-del-kit> --salida <carpeta> --nombre <nombre>

La plantilla valida la ficha completa y, si algo falta o no entra, no genera la pieza y lista
los errores (todo o nada). `comun.py` tiene el código compartido.

## Uso desde los agentes

URL de descarga directa de cualquier archivo:

    https://raw.githubusercontent.com/jano-insider/insider-marca/main/<ruta-del-archivo>

Ejemplo:

    https://raw.githubusercontent.com/jano-insider/insider-marca/main/logos/logo-vertical-color.svg

## Licencias

**Fuentes.** Distribuidas bajo la SIL Open Font License 1.1. Cada carpeta incluye
su `OFL.txt`.

- *Insider Sans Expanded* es una versión renombrada de Zalando Sans
  (Copyright 2025 The Zalando Sans Project Authors), conforme a la cláusula de
  Reserved Font Name de la OFL.
- *Numans*: ver `fuentes/numans/OFL.txt`.
- *Fredoka* (Copyright 2016 The Fredoka Project Authors): ver `fuentes/fredoka/OFL.txt`.

**Logos, patrones, íconos, fondos y elementos de marca.** El nombre, logotipo, isotipo,
patrones, ilustraciones, fondos, fotografías y elementos de identidad de Insider Finance son propiedad de
Insider Finance SA. Todos los derechos reservados. Su publicación en este repositorio
**no** otorga licencia de uso a terceros.

**Logos de terceros.** Los logos de `logos-terceros/` son marcas de sus respectivos
titulares. Se incluyen solo para identificar instrumentos en piezas informativas de
mercado. No son propiedad de Insider Finance y este repositorio no otorga ningún
derecho sobre ellos.

## Reglas del repositorio

1. Solo recursos de marca **vacíos** y el código de las plantillas: nunca piezas
   terminadas, cifras, datos ni fotos de clientes, ni material confidencial.
2. Nunca secretos, claves ni credenciales (el repositorio es público).
3. Todo cambio se hace por commit, para que quede registro de qué cambió y cuándo.
