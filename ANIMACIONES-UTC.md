# Animaciones UTC integradas

El reparto UTC completo está disponible: Chava y once profesores jugables.
Chan y Félix tienen 48 poses cada uno. Alejandro y los siete profesores nuevos
tienen 72 poses cada uno. Víctor acompaña a Daniela en un punto fijo del escenario y añade 24 cuadros nuevos
para levantarse, correr, golpear como asistencia y volver a su escritorio. No tiene controles propios. El selector ahora tiene 4 filas por 6 columnas. Sus
secuencias de espera, caminar, puño, gancho, patada, barrida, salto, guardia y
reacción al golpe conservan las duraciones y colisiones del sistema KOF de
Chava. La pantalla del juego muestra sus retratos propios.

| Personaje | Archivos del juego | Hojas fuente | Capítulo |
|---|---|---|---|
| Chan | `chars/chan_kof/chan_kof.def` | `chars/chan_kof/art/chan-idle-walk-punch-uppercut.png`, `chan-kick-sweep-jump-guard.png` | 1 |
| Félix | `chars/felix/felix.def` | `chars/felix/art/felix-idle-walk-punch-uppercut.png`, `felix-kick-sweep-jump-guard.png` | 2 |
| Alejandro | `chars/alejandro/alejandro.def` | `chars/alejandro/art/alejandro-idle-walk-punch-uppercut.png`, `alejandro-kick-sweep-jump-guard.png`, `alejandro-intro-fall-getup-win.png` | 3 |
| Daniela | `chars/daniela/daniela.def` | `chars/daniela/art/{basics,combat,reactions}.png` | 4 |
| Héctor Hugo | `chars/hector/hector.def` | Se conservan sus animaciones existentes | 5 |
| Gameros | `chars/gameros/gameros.def` | `chars/gameros/art/{basics,combat,reactions}.png` | 6 |
| Armando | `chars/armando/armando.def` | `chars/armando/art/{basics,combat,reactions}.png` | 7 |
| Vladimir | `chars/vladimir/vladimir.def` | `chars/vladimir/art/{basics,combat,reactions}.png` | 8 |
| Jaime, Matemáticas | `chars/jaime/jaime.def` | `chars/jaime/art/{basics,combat,reactions}.png` | 9 |
| Leonardo | `chars/leonardo/leonardo.def` | `chars/leonardo/art/{basics,combat,reactions}.png` | 10 |
| César Giovani | `chars/cesar/cesar.def` | `chars/cesar/art/{basics,combat,reactions}.png` | 12 |
| Víctor (acompañante) | Integrado en Daniela | `chars/daniela/art/victor-desk.png` | Presentación y combate de Daniela |

Las hojas se crearon con ImageGen a partir de
`chan_basededatos.jpeg`, `felix_soporte.jpeg` y `alejandro_angular.jpeg`, respectivamente. Se usó el
mismo prompt estructural para cada personaje, con sus rasgos y ropa propios:

> Pixel art para juego de lucha 2D, vista lateral hacia la derecha, 6 columnas
> por 4 filas, personaje completo en cada celda, escala consistente, fondo
> realmente transparente. Hoja 1: espera, caminar, puño y gancho (seis cuadros
> por acción). Hoja 2: patada, barrida, salto, guardia y daño (seis cuadros por
> fila). Conservar cara, pelo, ropa y proporciones de la imagen de referencia.

Alejandro añade una tercera hoja: saludo de entrada, caída hacia atrás hasta
quedar acostado, levantarse y victoria con los brazos cruzados. El conjunto de
prompts y las rutas están en `chars/alejandro/art/PROMPTS.md`; la vista de las
72 poses con sus pivotes está en `scratch/alejandro-poses-preview.png`.

Las 21 hojas nuevas y la hoja de Víctor se generaron con la herramienta integrada
ImageGen, usando las referencias originales del usuario. Los prompts exactos
están en `chars/<personaje>/art/PROMPTS.json`; el prompt de Víctor está en
`chars/daniela/art/VICTOR-PROMPT.json`. Cada profesor nuevo tiene una vista
de sus 72 poses en `chars/<personaje>/art/preview.png`. `data/utc-roster.json`
registra identidad, referencia de retrato, materia y nombres de movimientos.

Los constructores `tools/build_chan_kof.py`, `tools/build_felix.py`,
`tools/build_alejandro.py` y `tools/build_utc_roster.py` recortan
las poses y preparan los sprites. El Chan anterior permanece en `chars/chan`
como referencia y respaldo, pero la selección y la historia usan `chan_kof`.

Los diez maestros que compartían los especiales de Chava ahora tienen ocho
movimientos temáticos cada uno, con 24 cuadros adicionales de efectos y poses.
Incluyen los rebotes de pingpong de Armando, la moto de Gameros, el ajedrez y la
bicicleta de Jaime, la silla de César, UML, SQL, Angular, soporte y apps móviles.
Las voces y algunos sonidos de impacto siguen compartidos. Chan y Félix todavía
necesitan animaciones propias de caída y victoria; agarres y carrera reutilizan
poses. La guía completa, prompts, referencias y pruebas está en
[ESPECIALES-MAESTROS.md](ESPECIALES-MAESTROS.md).

Las partidas de prueba automáticas están en `scratch/chan-kof-match.log` y
`scratch/felix-match.log` y `scratch/alejandro-match.log`. La prueba de la ruta confirmó los once combates y
las 60 tarjetas de diálogo, incluyendo la presentación de Víctor con Daniela.
El capítulo 11 es un ensayo del proyecto de Chava antes de César, sin otro jefe.
La prueba de integración cargó y terminó el combate real de Chava contra Chan
desde el menú de historia sin salir por error.

`tools/test_utc_roster.py` completó siete combates reales, uno por profesor
nuevo, y verificó los comandos originales y la configuración global. Resultados
en `scratch/utc-roster-validation.json`. El test estático validó los doce
luchadores UTC. `tools/utc_selector_qa.lua` comprobó el selector ampliado y
`tools/utc_companion_qa.lua` confirmó exactamente un Víctor en la pelea.
Las capturas están en `scratch/utc-selector-preview/` y
`scratch/utc-daniela-preview/`. Los módulos de prueba usan configuraciones
separadas en `scratch/`; no se cargan en una partida normal.

## Revisión de proporciones y supers

Se corrigió el escalado por pose/fila y la postura de agachado de Chan y Félix.
Los supers ahora usan combos, agarres, saltos, contraataques y la asistencia física de Víctor.
Víctor y su escritorio tienen una posición fija en el escenario, independiente de la cámara.
La hoja nueva y su prompt exacto están en `chars/daniela/art/victor-assist/`.
Detalle de acciones y 230 escenarios de prueba en `ESPECIALES-MAESTROS.md`.
