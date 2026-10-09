# Animaciones UTC integradas

La revisión actual de repertorios está en [IDENTIDADES-PERSONAJES.md](IDENTIDADES-PERSONAJES.md):
cinco especiales propios por profesor, recursos, movilidad diferenciada, MAX2 distintos
y **240 cuadros nuevos de normales**, además de los **60 cuadros de identidad de la
revisión anterior**. Los doce luchadores tienen doce normales y cadenas confirmadas
propias; su guía es [GOLPES-PROPIOS.md](GOLPES-PROPIOS.md). Los recuentos de hojas
siguientes describen el material original, antes de estas incorporaciones.

El reparto UTC completo está disponible: Chava y once profesores jugables.
Chan y Félix tienen 48 poses cada uno. Alejandro y los siete profesores nuevos
tienen 72 poses cada uno. Víctor acompaña a Daniela en un punto fijo del escenario y añade 24 cuadros nuevos
para levantarse, correr, golpear como asistencia y volver a su escritorio. No tiene controles propios. El selector ahora tiene 4 filas por 6 columnas. Sus
secuencias de espera, caminar, puño, gancho, patada, barrida, salto, guardia y
reacción al golpe conservan los estados y controles KOF del proyecto. Los ataques
ahora tienen desplazamientos, contactos, recuperaciones y continuaciones propios.
La pantalla del juego muestra sus retratos propios.

## Normales nuevos y registro corporal

Diez profesores reciben veinticuatro cuadros nuevos cada uno: seis fases de golpe
fuerte de pie, puño agachado, ataque aéreo de mano y patada aérea. Chava y Héctor
conservan sus dibujos originales. Cada personaje tiene cuatro normales de pie,
cuatro agachados y cuatro aéreos; [GOLPES-PROPIOS.md](GOLPES-PROPIOS.md) explica sus
cadenas y su función. Incluyen el triple Ping de Héctor, los contactos dobles de
Gameros, el lanzamiento de Armando, las diagonales de Jaime, las patadas de
Leonardo y el bastón lento de César.

Las hojas fuente están en `chars/<personaje>/art/normal-v3/sheet.png`. Los prompts
exactos y sus referencias se conservan en `data/teacher-normal-art/PROMPTS.json`.
Cada carpeta `normal-v3` conserva la hoja fuente y sus JSON de registro,
movimientos y secuencias; la vista `preview.png` y los PNG individuales son
derivados locales regenerables que se omiten del repositorio. Las sesenta poses
de identidad previas conservan sus fuentes y prompts en `data/teacher-identity-art/`.

La extracción registra cuerpos completos, incluso cuando una mano o un pie cruza
la cuadrícula de la hoja. También recupera las patadas y barridas originales que
habían sido importadas como fragmentos de sombra. La escala se calibra una vez
por hoja. Las filas aéreas usan un origen virtual propio para que la colocación
de la figura en la lámina no añada otro salto al cambiar de animación. Agacharse
y recoger las piernas cambian la silueta conservando las proporciones del cuerpo.

El cuadro de contacto se elige por la extensión visible de la extremidad. Las
cajas usan los ejes reales de los sprites; los ataques de dos contactos tienen
eventos de impacto separados. `tools/teacher_normals.py` define los normales y
sus cadenas, `data/teacher-normal-kits.json` conserva el catálogo de parámetros y
`tools/teacher_animation.py` registra las hojas y sincroniza los especiales.

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

La primera revisión de especiales añadió ocho movimientos temáticos por profesor,
con 24 cuadros adicionales de efectos y poses para cada uno de los diez maestros.
Incluyen los rebotes de pingpong de Armando, la moto de Gameros, el ajedrez y la
bicicleta de Jaime, la silla de César, UML, SQL, Angular, soporte y apps móviles.
Las voces y algunos sonidos de impacto siguen compartidos. Chan y Félix ya tienen
caída hacia atrás, impacto, pose en el suelo, levantada, guardia y KO propios.
Las ocho secuencias legacy de caída/levantada también se recalibraron juntas para
conservar la escala hasta ponerse de pie. La guía histórica de esa revisión, con prompts y referencias, está en
[ESPECIALES-MAESTROS.md](ESPECIALES-MAESTROS.md). La lógica vigente y las diferencias
entre los repertorios se documentan en
[IDENTIDADES-PERSONAJES.md](IDENTIDADES-PERSONAJES.md).

## Comprobación de la revisión actual

La revisión registra atlas de seis fases para caminar, correr, agacharse y saltar
en diez maestros, con postura y ropa basadas en los JPEG originales. Chan y Félix
tienen esas cuatro familias además de atlas propios de reacciones; César conserva
el bastón durante sus ciclos. La pose de salto usa un origen aéreo estable; las
figuras agachadas conservan su escala. Las posiciones de los pies se alinearon por
sus ejes de dibujo. Los prompts, hojas transparentes y métricas se guardan en
`chars/<personaje>/art/*-v4/`; las vistas previas y la captura de QA quedan en
`scratch/`.

La comprobación del motor actual se completó en una copia aislada del juego: los
doce luchadores ejecutaron caminar en ambos sentidos, correr, agacharse y volver
a erguirse, saltar y aterrizar, tres tipos de guardia, caída por golpe, impacto,
permanencia en el suelo, levantada con control y KO. Los 120 escenarios pasaron.
El combate real de las ocho secuencias especiales se comprobó en los diez
profesores. `tools/test_teacher_motion.py` revisa además el contenido AIR/SFF y
dibujó tiras de revisión a escala de juego. Estas pruebas verifican los archivos
y el motor de Windows; el APK se comprueba por separado en un emulador Android.

`tools/test_teacher_normals.py --run` comprobó golpes, contactos, guardia y cadenas
en los doce personajes: 960 escenarios, sin fallos. Las mecánicas especiales se
ejercitaron en el motor para los diez profesores; los sprites, estados y comandos
se validaron con `tools/test_kof_controls.py`. El detalle de movimiento está en
`scratch/teacher-motion-runtime/results.json`; los informes e imágenes no se
incluyen en el juego publicado.

Los scripts de integración `tools/test_utc_roster.py`, `tools/utc_selector_qa.lua`
y `tools/utc_companion_qa.lua` permiten revisar combates, selector y acompañante.
El capítulo 11 continúa siendo el ensayo del proyecto de Chava antes de César.

## Revisión de proporciones y supers

Se corrigió el escalado por pose/fila y la postura de agachado de Chan y Félix.
Los supers usan combos, agarres, saltos, contraataques y la asistencia física de Víctor.
Víctor y su escritorio tienen una posición fija en el escenario, independiente de la cámara.
La hoja nueva y su prompt exacto están en `chars/daniela/art/victor-assist/`.
La guía vigente de acciones, recursos y validación es `IDENTIDADES-PERSONAJES.md`.

La revisión mecánica añade continuaciones con requisitos propios: Chan confirma
SQL y pulsa KOF B con correcciones; Gameros confirma Arcade y pulsa KOF B solo con
Gym activo y racha de dos. Jaime puede elegir adelante o atrás durante Caballo
gastando un cálculo. Félix contraataca por abajo y cura al confirmar; Daniela
intercepta un brazo con una llave; Leonardo se retira y regresa con una patada
mediante movimiento continuo. Calibrar IoT activa el sensor instalado de Armando,
Silla gasta un punto de Rigor para reforzar la protección de César, y Honores
consume asistencias para retirar energía del rival cuando conecta.
