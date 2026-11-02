# insider-marca

Kit de marca de **Insider Finance** para uso de sus agentes de IA internos.

Este repositorio es la fuente única de los recursos de marca que usan los agentes
(fuentes, logos, patrones y plantillas vacías). Los agentes descargan los archivos
directamente desde acá.

## Estructura

| Carpeta | Contenido |
|---|---|
| `fuentes/insider-sans/` | Insider Sans Expanded, todos los pesos (.ttf) + licencia OFL |
| `fuentes/numans/` | Numans Regular (.ttf) + licencia OFL |
| `logos/` | 8 logos oficiales en SVG optimizado |

Logos disponibles:

- `logo-vertical-color.svg`: principal, sobre fondo blanco o claro
- `logo-horizontal-color.svg`: espacios anchos, fondo claro
- `isotipo-color.svg`: solo el símbolo, fondo claro
- `logo-vertical-blanco.svg`, `logo-horizontal-blanco.svg`, `isotipo-blanco.svg`: fondos Coral, oscuros o fotos
- `logo-vertical-negro.svg`, `isotipo-negro.svg`: monocromático (patrocinadores, impresión a una tinta)

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

**Logos y elementos de marca.** El nombre, logotipo, isotipo y elementos de
identidad de Insider Finance son propiedad de Insider Finance SA. Todos los
derechos reservados. Su publicación en este repositorio **no** otorga licencia
de uso a terceros.

## Reglas del repositorio

1. Solo recursos de marca **vacíos**: nunca piezas terminadas, cifras, datos de
   clientes ni material confidencial.
2. Nunca secretos, claves ni credenciales (el repositorio es público).
3. Todo cambio se hace por commit, para que quede registro de qué cambió y cuándo.