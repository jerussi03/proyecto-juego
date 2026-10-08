# Repertorios e identidades de los profesores

Esta revisión da a los doce luchadores doce ataques normales propios y cadenas
confirmadas diferentes. Los diez profesores que usaban la base de Chava tienen,
además, especiales, movilidad, recursos y MAX2 diferenciados. Chava y Héctor
conservan su arte y sus especiales originales; sus normales también se revisan.
Los controles comunes de KOF, defensa, evasión y MAX se conservan.

La referencia temática es el TXT de profesores del usuario. Alejandro figura
como pendiente allí: se conserva su tema Angular del proyecto. Félix conserva
el tema de soporte que ya tenía en el juego.

## Controles

| Entrada | Acción |
|---|---|
| ↓↘→ + puño | Especial 1 |
| →↓↘ + puño | Especial 2 |
| ↓↙← + puño | Especial 3 |
| ←↙↓↘→ + patada | Especial 4 |
| ↓↙← + patada | Preparación, recuperación o evasión propia |
| ↓↘→↓↘→ + puño | Super principal, 1000 de energía |
| ↓↘→↘↓↙← + puño | Segundo super, 1000 de energía |
| ↓↙←↓↙← + A+C KOF | MAX2, 2000 y MAX activo |

Los pequeños iconos debajo de VIDA representan el recurso propio (máximo tres).
También hay instrucciones de identidad en la lista de movimientos de cada profesor.

## Repertorio normal

Cada personaje tiene cuatro golpes de pie, cuatro agachados y cuatro aéreos.
Las diferencias incluyen avance, retirada, deslizamiento, lanzamiento, impactos
dobles, descenso y modificación de la trayectoria del salto. Las cadenas propias
exigen acertar el golpe anterior; un ataque bloqueado o fallido debe recuperarse.
Chava conserva además sus repeticiones alternadas del mismo botón.

La guía [GOLPES-PROPIOS.md](GOLPES-PROPIOS.md) contiene los doce repertorios,
sus controles y las continuaciones de cada personaje. Por ejemplo, Gameros tiene
la cadena de pie A → B → C → D; Daniela A → B → C; Héctor tres pulsaciones
confirmadas de A; César une su mano baja con el bastón de pie. No todos comparten
la misma continuación. Los parámetros están en
[data/teacher-normal-kits.json](data/teacher-normal-kits.json).

## Especiales y apoyo

En cada fila, las cinco acciones corresponden a los cinco primeros controles de la tabla.

| Profesor | Especial 1 | Especial 2 | Especial 3 | Especial 4 | Apoyo |
|---|---|---|---|---|---|
| Chan | Corrección SQL de contacto corto; confirmada permite continuar con KOF B si tiene correcciones | Levanta y presiona una pesa | Salto de senderismo con patada | Tres golpes bajos que gastan correcciones | Prepara una corrección |
| Félix | Avance con golpe de soporte | Espera un ataque y responde con golpe bajo y curación al acertar | Reparación baja que recupera 12 más 4 de vida por diagnóstico si conecta | Cable bajo con retroceso y mucho tiempo de aturdimiento | Cura 40 más 10 por diagnóstico consumido; cuesta 150 |
| Alejandro | Componente directo; módulo preparado añade una copia | Paso corto y golpe ascendente | Cruza al rival, gira y golpea | Planta una trampa de piso y retrocede | Importa un módulo durante cuatro segundos |
| Daniela | Tres golpes UML que acumulan requisitos | Intercepta un golpe cuerpo a cuerpo y responde con una llave | Bolsazo con avance | Agarre de comando que retiene y suelta al rival | Aprueba un documento: requisito y 180 de energía |
| Gameros | Tres golpes de boxeo, potenciados por racha; con Gym y racha de dos permite continuar con KOF B | Patada ascendente con salto | Avance físico en moto | Dos golpes bajos de pedaleo | Activa gimnasio por cinco segundos |
| Armando | Saque de pingpong que rebota | Salta y remata contra el suelo | Planta un sensor que espera proximidad o señal remota y eleva al rival | Patada doble con remate mejorado por calibración | Calibra IoT durante cuatro segundos y activa el sensor instalado |
| Vladimir | Agarre de invitación obligatoria | Golpe que acerca y eleva al alumno | Se planta en la puerta, reduce daño y rechaza al rival | Pisotón de Honores: consume asistencias, atrae y retira energía al conectar | Pase de lista: asistencia y 180 de energía |
| Jaime | Salto de caballo; adelante o atrás corrige la trayectoria gastando un cálculo | Golpe ascendente potenciado por cálculos consumidos | Avanza en bicicleta | Derivada baja y retroceso | Prepara un cálculo |
| Leonardo | Dos patadas; batería añade una tercera | Patada aérea que evade ataques bajos al arrancar | Corre para cruzar al rival y gira al finalizar | Retrocede y regresa con una patada al interceptar un ataque | Modo avión: retroceso, evasión temporal y dos de batería; cuesta 100 |
| César | Golpe de bastón lento, con alcance propio | Golpe ascendente pesado | Avanza con silla; un punto de Rigor refuerza la protección | Agarre DELETE que consume Rigor | Pastillas: cura 65 tras 40 cuadros, protección temporal; cuesta 200 |

Los contraataques de Félix, Daniela y Leonardo fallan sin causar daño si nadie
los ataca. La revisión de Daniela intercepta golpes cuerpo a cuerpo: un
proyectil distante no convierte a su dueño en víctima de un agarre. Félix
responde con un golpe bajo que recupera 8 más 4 de vida por diagnóstico
disponible al confirmar; Leonardo se retira y vuelve con una patada mediante
desplazamiento continuo.

Las trampas de Alejandro y Armando permanecen en el suelo, pueden romperse
con ataques y caducan; cada uno puede tener una sola activa. La de Angular
golpea bajo al contacto. El sensor IoT espera a que el rival se acerque o a
que Armando termine la señal de Calibrar; entonces entra en su ráfaga y lanza.
Solo Alejandro y Armando usan un proyectil como primer especial.

Alejandro puede volver a importar después de 1.5 segundos y Armando volver a
calibrar después de dos segundos: pueden acumular preparación antes de que
caduque. Cada calibración añade un rebote de piso al saque de pingpong; los
saques calibrados también regresan al tocar un borde lateral de pantalla.

Las continuaciones de SQL y Combo Arcade usan KOF B (`a` interno). Chan
necesita confirmar SQL y disponer de una corrección; continúa hacia Índice
Cluster, que gasta su recurso. Gameros necesita confirmar Arcade con Gym
activo y al menos dos puntos de racha; entonces puede pasar a Pedal.

Jaime puede mantener adelante o atrás durante la parte aérea de Caballo para
elegir una nueva diagonal. La elección consume exactamente un cálculo y solo
puede hacerse una vez por salto. César gasta como máximo un punto de Rigor
al iniciar Silla: su protección usa `DefenceMulSet=.35`; sin ese punto usa
`.55`. Honores de Vladimir consume las asistencias y, al conectar, retira
50 de energía del rival por cada asistencia gastada.

## Recursos y forma de jugar

| Profesor | Recurso | Cómo se obtiene y para qué sirve |
|---|---|---|
| Chan | Correcciones | SQL o puño fuerte confirmado; también al documentar. Los golpes bajos y MAX2 las consumen para aumentar el daño. |
| Félix | Diagnósticos | Llave, Cable o contraataque confirmado. Se consumen para mejorar la curación de mantenimiento o MAX2. |
| Alejandro | Módulos | Importar Módulo. Permiten una copia de Angular y mejoran el despliegue; caducan con la preparación. |
| Daniela | Requisitos | Cadena UML, revisión acertada o documento aprobado. Víctor los consume para potenciar sus golpes durante la asistencia. |
| Gameros | Racha | Ataques confirmados. Se pierde al recibir un golpe; potencia boxeo y moto. Gimnasio aumenta el daño temporalmente. |
| Armando | Calibraciones | Calibrar IoT. Mejoran el remate, los rebotes y el MAX2; la calibración también activa a distancia el sensor. Caducan con la preparación. |
| Vladimir | Asistencias | Agarre confirmado o pase de lista. Se consumen en Honores y potencian la penalización del MAX2. |
| Jaime | Cálculos | Cálculo Mental. Un punto permite corregir Caballo hacia delante o atrás; Potencia consume el stock para elevar más y Teorema Final lo usa en su remate. |
| Leonardo | Batería | Evasión en modo avión o contraataque. Push gasta una unidad para añadir una patada; MAX2 consume la batería para el remate. |
| César | Rigor | Recibir un golpe. Silla consume un punto para reforzar su protección; DELETE y el examen MAX2 lo consumen para castigar más fuerte. |

La movilidad y los golpes básicos también difieren: Leonardo y Gameros son más
rápidos y ligeros; César es más lento y pesado; Chan, Jaime y Armando tienen
saltos distintos. El desplazamiento de la CPU usa la velocidad de su personaje.

## Supers y MAX2

| Profesor | Super principal | Segundo super | MAX2 |
|---|---|---|---|
| Chan | Avanza con pesa y tres golpes | Serie de patadas de crossfit | Tres impactos de pesa con remate, consume correcciones |
| Félix | Cadena corta de reparación | Golpes protegidos y recuperación al conectar | Reparación general: protección y curación al conectar el remate |
| Alejandro | Dos pasos de refactor y gancho | Compilación en el sitio con componente preparado | Despliegue: avance instantáneo, componentes y remate según módulos |
| Daniela | Llama a Víctor para que se levante, golpee y vuelva | Daniela avanza con tres bolsazos | Auditoría conjunta: Daniela golpea mientras Víctor asiste, gastan requisitos |
| Gameros | Combinación de gimnasio | Pasada y regreso en moto | Final Boss: activa ocho segundos de gimnasio, llena racha y encadena patadas |
| Armando | Clavada con salto y remate | Combinación deportiva con rebote preparado | Salto, impacto contra el suelo y segundo remate con calibraciones |
| Vladimir | Agarra, retiene y suelta durante la conferencia | Patrulla con acercamiento y rechazo | Agarre obligatorio, retención y penalización de energía según asistencias |
| Jaime | Pasada en bicicleta y remate | Serie de seis patadas de pedaleo | Dos saltos de caballo y remate según cálculos |
| Leonardo | Contraataque reactivo | Avance ofensivo con patadas | Ráfaga de patadas, remate con batería y retirada |
| César | Avance protegido con silla | Dos golpes lentos y pesados | Apoyo con silla, golpe pesado y castigo según Rigor |

## Víctor

El escritorio permanece en X=120 del escenario. Víctor alterna computadora y
teléfono, puede quedar fuera de pantalla y no sigue a Daniela. Al llamarlo se
levanta, corre, golpea, vuelve al escritorio y se sienta. No puede volver a
llamarse hasta terminar. El escritorio vacío permanece en su punto durante la asistencia.

## Arte, construcción y pruebas

La revisión actual añade **240 cuadros originales** para diez profesores:
seis fases de golpe fuerte de pie, puño agachado, ataque aéreo de mano y patada
aérea por personaje. Chava y Héctor conservan su arte propio. Estos cuadros
se suman a los **60 cuadros de identidad de la revisión anterior**, seis por
profesor: pesa, bloqueo de
Félix, importación de módulo, revisión de documentos, calentamiento de gimnasio,
calibración IoT, agarre de Vladimir, salto de caballo, patadas de Leonardo y bastón
de César. Se generaron con **ImageGen integrado**, se extrajeron como sprites y
se empaquetaron en los SFF. Una escala fija por personaje evita reajustar su
tamaño según el ancho del arma o la altura de cada pose.

- Hojas nuevas: `data/teacher-identity-art/master-a.png` y `master-b.png`.
- Prompts exactos y referencia: `data/teacher-identity-art/PROMPTS.json`.
- Vista de los 60 cuadros: `data/teacher-identity-art/preview.png`.
- Cuadros individuales: `chars/<personaje>/art/identity-v2/`.
- Hojas nuevas de normales: `chars/<personaje>/art/normal-v3/sheet.png`.
- Prompts exactos y referencias de los normales: `data/teacher-normal-art/PROMPTS.json`.
- Registro de ejes y metadatos por personaje: `chars/<personaje>/art/normal-v3/`.
- Vista local regenerable: `chars/<personaje>/art/normal-v3/preview.png`; los PNG individuales y esta vista se omiten del repositorio.
- Lógica y secuencias propias: `tools/teacher_identity.py`.
- Normales y cadenas: `tools/teacher_normals.py` y `data/teacher-normal-kits.json`.
- Registro de cuerpos completos y sincronización de contactos: `tools/teacher_animation.py`.
- Constructor: `python tools/build_teacher_specials.py`.
- Pruebas de comandos, daño, recursos y comportamiento: `python tools/test_teacher_specials.py`.
- Validación de sprites, estados y comandos: `python tools/test_kof_controls.py`.
- Validación de normales, proporciones, contactos y cadenas: `python tools/test_teacher_normals.py`.
- Respaldo anterior: `backups/teacher-identity-v2/`.
- Capturas dentro del motor a velocidad normal: `scratch/identity-preview/<personaje>/`.

Las secuencias también reutilizan poses normales y especiales existentes para
combos y transiciones. Se recuperaron cuerpos completos de las hojas anteriores
cuando la importación había seleccionado sombras sueltas. Una calibración por
hoja y un origen virtual por fila aérea conservan las proporciones al cambiar
de postura. No se sustituyeron todas las poses ni las voces.
La validación automática verifica ejecución y mecánicas; el balance fino y la
sensación con mando necesitan partidas de juego.

**Validación final: 960 escenarios de normales y 349 de especiales, sin fallos.**
Incluye ambos lados, contactos, bloqueos, fallos a distancia, cadenas, recursos,
contraataques y agarres. Los doce luchadores pasan la inspección de sprites,
estados y comandos; siete combates CPU terminaron correctamente con los controles
y la configuración global intactos. Se revisaron 40 capturas nuevas a velocidad
normal, cuatro por profesor. Los saltos especiales corregidos registraron un
máximo de Y=0: no atravesaron el suelo.

La prueba de Daniela mantiene a Víctor exactamente en X=120, recorre 66.5 píxeles
de cámara entre ambos lados y permite que quede fuera de pantalla. También
comprueba computadora, teléfono, asistencia física y regreso al escritorio.

Los informes se generan en `scratch/teacher-specials-qa/validation.json`,
`scratch/teacher-normals-qa/` y `scratch/utc-roster-validation.json`.
Las 40 capturas están en `scratch/identity-preview/normals/<personaje>/`;
los resultados, capturas y módulos de prueba quedan fuera del repositorio.

El material versionado de `normal-v3` conserva la hoja fuente `sheet.png` y sus
JSON de registro, movimientos y secuencias. El constructor regenera los cuadros
individuales y las vistas desde esa hoja; no se publican esas copias redundantes.
