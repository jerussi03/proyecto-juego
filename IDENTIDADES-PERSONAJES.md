# Repertorios e identidades de los profesores

Esta revisión reemplaza los cinco especiales compartidos de los diez profesores
que usaban la base de Chava. Cada uno tiene sus propios ataques, movilidad,
recursos y MAX2. Chava y Héctor conservan sus repertorios originales.
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

En cada fila, las cinco acciones corresponden a los cinco primeros controles de la tabla.

| Profesor | Especial 1 | Especial 2 | Especial 3 | Especial 4 | Apoyo |
|---|---|---|---|---|---|
| Chan | Corrección SQL de contacto corto | Levanta y presiona una pesa | Salto de senderismo con patada | Tres golpes bajos que gastan correcciones | Prepara una corrección |
| Félix | Avance con golpe de soporte | Espera un ataque y responde con un golpe físico | Reparación baja que recupera 12 de vida si conecta | Cable bajo con retroceso y mucho tiempo de aturdimiento | Cura 40 más 10 por diagnóstico consumido; cuesta 150 |
| Alejandro | Componente directo; módulo preparado añade una copia | Paso corto y golpe ascendente | Cruza al rival, gira y golpea | Planta una trampa de piso y retrocede | Importa un módulo durante cuatro segundos |
| Daniela | Tres golpes UML que acumulan requisitos | Revisa el ataque y contraataca | Bolsazo con avance | Agarra y cambia de posición al rival | Aprueba un documento: requisito y 180 de energía |
| Gameros | Tres golpes de boxeo, potenciados por racha | Patada ascendente con salto | Avance físico en moto | Dos golpes bajos de pedaleo | Activa gimnasio por cinco segundos |
| Armando | Saque de pingpong que rebota | Salta y remata contra el suelo | Planta un sensor de proximidad impreso | Patada doble con remate mejorado por calibración | Calibra IoT durante cuatro segundos |
| Vladimir | Agarre de invitación obligatoria | Golpe que acerca y eleva al alumno | Se planta en la puerta, reduce daño y rechaza al rival | Pisotón de zona que consume asistencias | Pase de lista: asistencia y 180 de energía |
| Jaime | Salto de caballo con patada en arco | Golpe ascendente potenciado por cálculos consumidos | Avanza en bicicleta | Derivada baja y retroceso | Prepara un cálculo |
| Leonardo | Dos patadas; batería añade una tercera | Patada aérea que evade ataques bajos al arrancar | Cruza al rival con un paso rápido y gira | Espera un golpe y responde | Modo avión: retroceso, evasión temporal y dos de batería; cuesta 100 |
| César | Golpe de bastón lento, con alcance propio | Golpe ascendente pesado | Avanza con silla y reduce daño recibido | Agarre DELETE que consume Rigor | Pastillas: cura 65 tras 40 cuadros, protección temporal; cuesta 200 |

Los contraataques de Félix, Daniela y Leonardo fallan sin causar daño si nadie
los ataca. Las trampas de Alejandro y Armando permanecen en el suelo, pueden
romperse con ataques y caducan; cada uno puede tener una sola activa.
Solo Alejandro y Armando usan un proyectil como primer especial.

Alejandro puede volver a importar después de 1.5 segundos y Armando volver a
calibrar después de dos segundos: pueden acumular preparación antes de que
caduque. Cada calibración añade un rebote de piso al saque de pingpong; los
saques calibrados también regresan al tocar un borde lateral de pantalla.

## Recursos y forma de jugar

| Profesor | Recurso | Cómo se obtiene y para qué sirve |
|---|---|---|
| Chan | Correcciones | SQL o puño fuerte confirmado; también al documentar. Los golpes bajos y MAX2 las consumen para aumentar el daño. |
| Félix | Diagnósticos | Llave, Cable o contraataque confirmado. Se consumen para mejorar la curación de mantenimiento o MAX2. |
| Alejandro | Módulos | Importar Módulo. Permiten una copia de Angular y mejoran el despliegue; caducan con la preparación. |
| Daniela | Requisitos | Cadena UML, revisión acertada o documento aprobado. Víctor los consume para potenciar sus golpes durante la asistencia. |
| Gameros | Racha | Ataques confirmados. Se pierde al recibir un golpe; potencia boxeo y moto. Gimnasio aumenta el daño temporalmente. |
| Armando | Calibraciones | Calibrar IoT. Mejoran el remate, los rebotes y el MAX2; caducan con la preparación. |
| Vladimir | Asistencias | Agarre confirmado o pase de lista. Se consumen en Honores y potencian la penalización del MAX2. |
| Jaime | Cálculos | Cálculo Mental. Mejoran el salto y se consumen en Potencia o Teorema Final. |
| Leonardo | Batería | Evasión en modo avión o contraataque. Push gasta una unidad para añadir una patada; MAX2 consume la batería para el remate. |
| César | Rigor | Recibir un golpe. DELETE y el examen MAX2 lo consumen para castigar más fuerte. |

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

Se añadieron **60 cuadros originales**, seis por profesor: pesa, bloqueo de
Félix, importación de módulo, revisión de documentos, calentamiento de gimnasio,
calibración IoT, agarre de Vladimir, salto de caballo, patadas de Leonardo y bastón
de César. Se generaron con **ImageGen integrado**, se extrajeron como sprites y
se empaquetaron en los SFF. Una escala fija por personaje evita reajustar su
tamaño según el ancho del arma o la altura de cada pose.

- Hojas nuevas: `data/teacher-identity-art/master-a.png` y `master-b.png`.
- Prompts exactos y referencia: `data/teacher-identity-art/PROMPTS.json`.
- Vista de los 60 cuadros: `data/teacher-identity-art/preview.png`.
- Cuadros individuales: `chars/<personaje>/art/identity-v2/`.
- Lógica y secuencias propias: `tools/teacher_identity.py`.
- Constructor: `python tools/build_teacher_specials.py`.
- Pruebas de comandos, daño, recursos y comportamiento: `python tools/test_teacher_specials.py`.
- Validación de sprites, estados y comandos: `python tools/test_kof_controls.py`.
- Respaldo anterior: `backups/teacher-identity-v2/`.
- Capturas dentro del motor a velocidad normal: `scratch/identity-preview/<personaje>/`.

Las secuencias también reutilizan poses normales y especiales existentes para
combos y transiciones. No se sustituyeron todas las poses ni las voces.
La validación automática verifica ejecución y mecánicas; el balance fino y la
sensación con mando necesitan partidas de juego.

Validación final de esta revisión: **311 escenarios de comandos y mecánicas,
sin fallos**, validación estática de los doce luchadores UTC y siete combates
CPU completos. Se capturaron las diez nuevas secuencias a velocidad normal.
Informe de comportamiento: `scratch/teacher-specials-qa/validation.json`.
