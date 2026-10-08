# Especiales y consistencia de animaciones UTC

**Guía actual:** [Identidades y repertorios completos](IDENTIDADES-PERSONAJES.md).
La revisión de identidad reemplazó los cinco especiales normales, los recursos
y los MAX2 que se describen en este documento anterior; añadió 60 cuadros nuevos.
Las tablas siguientes se conservan como registro de la revisión previa.

Los once maestros tienen movimientos relacionados con sus materias y aficiones. Héctor conserva drones y redes; los otros diez tienen ocho movimientos cada uno. Chava conserva su repertorio.

## Cambios de esta revisión

El escalado deja de ajustar cada pose o fila a una altura objetivo. Alejandro y los siete profesores de 72 poses usan una referencia de pie por hoja; las poses de salto, agachado y brazo levantado mantienen esa escala. Chan y Félix mantienen una escala constante y ahora usan una pose realmente agachada al agacharse. Los cuadros de cuerpo de los especiales también comparten escala. Los pivotes conservan el apoyo de los pies. Esto corrige el cambio de tamaño causado por el empaquetado; pueden quedar pequeñas diferencias de dibujo entre hojas generadas.

Los supers de doble cuarto de círculo y MAX2 ya no comparten un objeto que dispara proyectiles. Cada profesor realiza una acción física distinta:

| Maestro | Super principal | Acción |
|---|---|---|
| Chan | Circuito de Crossfit | Avanza cargando la pesa y conecta tres golpes de crossfit; el último levanta al rival. |
| Felix | Reinicio en Cadena | Se acerca y encadena cinco golpes cortos de reparación con un remate de reinicio. |
| Alejandro | Refactorizacion | Da dos pasos de refactorización con imágenes residuales y termina con un golpe ascendente. |
| Daniela | Victor, Echame la Mano | Víctor se levanta del escritorio, corre hasta el rival, encadena golpes y vuelve a sentarse. En MAX2 Daniela también avanza con un bolsazo. |
| Gameros | Combo de Gimnasio | Encadena puño, patada y gancho con sus propias poses de gimnasio. |
| Armando | Clavada Final | Salta, desciende con una clavada y remata contra el piso. |
| Vladimir | Conferencia Obligatoria | Se aproxima, agarra al rival, lo retiene durante la conferencia y lo suelta. |
| Jaime | Gambito Ciclista | Cruza con la bicicleta, gira y realiza una segunda pasada con remate. |
| Leonardo | Contraataque Movil | Espera un ataque y responde con un contraataque físico. Si el rival no ataca, termina sin causar daño. |
| Cesar | Empuje de Backend | Avanza apoyado en la silla con reducción temporal de daño y conecta un golpe pesado. |

MAX2 conserva el tema del super principal y aumenta su potencia; Daniela combina su bolsazo con la asistencia. Los proyectiles individuales permanecen en el especial de cuarto de círculo, con sus trayectorias propias.

### Segundo super: repertorio adicional

El segundo super (↓↘→↘↓↙← + puño) también tiene comportamiento propio, en lugar de la anterior secuencia compartida de avance y tres golpes:

| Maestro | Segundo super |
|---|---|
| Chan | Circuito de patadas alternadas con remate ascendente. |
| Félix | Mantenimiento con reducción temporal del daño recibido; recupera 35 de vida si conecta el remate. |
| Alejandro | Combo de compilación en el sitio; Importar Módulo añade un componente al final. |
| Daniela | Tres bolsazos con avance: combate ella mientras Víctor continúa trabajando. |
| Gameros | Cruza en moto, gira y vuelve para una segunda pasada. |
| Armando | Combinación deportiva; Calibrar IoT añade un rebote ofensivo. |
| Vladimir | Patrulla con un golpe que acerca al alumno y otro que lo devuelve al salón. |
| Jaime | Seis patadas de pedaleo y un remate, sin repetir el recorrido en bicicleta del primer super. |
| Leonardo | Avance rápido con patadas e imágenes residuales; alternativa ofensiva al contraataque del primer super. |
| César | Dos golpes pesados de ejecución lenta, sin repetir el avance con silla. |

Los golpes normales agachados ahora muestran las poses bajas existentes en lugar de las del gancho de pie. El antiaéreo conserva una acción separada con su gancho original. Estas acciones reutilizan arte existente; no se generaron nuevas hojas en esta revisión.

## Víctor y el escritorio

Víctor permanece sentado en el punto X=120 del escenario, detrás de los luchadores. Su posición no depende de Daniela ni del centro de la cámara. Puede quedar fuera de pantalla. El escritorio permanece en ese mismo punto durante la asistencia y Víctor regresa allí al terminar; se mantiene un único actor Víctor. No se puede volver a llamarlo hasta que se siente.

La secuencia usa 24 cuadros nuevos: levantarse, correr, golpear y escritorio vacío. Se generó con **ImageGen integrado**, usando el retrato del usuario y la hoja anterior del escritorio como referencias. Se extrajeron cuadros, se fijaron pivotes y se empaquetaron en SFF/AIR.

La espera alterna los cuadros originales de teclear, revisar el teléfono y atender una llamada. El ciclo incluye una sección larga de computadora antes de la llamada; no se limita a una imagen inmóvil.

Archivos finales:

- [Hoja generada](chars/daniela/art/victor-assist/sheet.png).
- [Vista de cuadros y pivotes](chars/daniela/art/victor-assist/preview.png).
- [Prompt exacto, referencias y método](chars/daniela/art/victor-assist/PROMPT.json).
- [Capturas dentro del juego](scratch/consistency-review/).

## Controles y costos

Los controles KOF y las asignaciones globales de teclado y mando se conservan: A KOF = X del mando, B = A, C = Y, D = B. Puño significa A/C; patada B/D. Las direcciones se invierten al mirar a la izquierda. Se conservan evasión, MAX, cancelaciones y las barras superiores VIDA y STACK/MAX.

Los cuatro especiales de ataque no gastan energía. Los dos supers gastan 1000. MAX2 requiere MAX activo, gasta 2000 y termina MAX. El apoyo tiene espera propia y puede interrumpirse; la curación no supera la vida máxima.

## Chan

| Movimiento | Combinación | Energía |
|---|---|---|
| Examen SQL | ↓↘→ + puño | 0 |
| Peso de Crossfit | →↓↘ + puño | 0 |
| Ruta de Senderismo | ↓↙← + puño | 0 |
| Indice Cluster | ←↙↓↘→ + patada | 0 |
| Documentacion Perfecta | ↓↙← + patada | 0 |
| Circuito de Crossfit | ↓↘→↓↘→ + puño | 1000 |
| Crossfit Total | ↓↘→↘↓↙← + puño | 1000 |
| DROP TABLE MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 3.33 segundos a 60 cuadros por segundo.

## Felix

| Movimiento | Combinación | Energía |
|---|---|---|
| Llave de Soporte | ↓↘→ + puño | 0 |
| Reinicio Forzado | →↓↘ + puño | 0 |
| Reparacion en Marcha | ↓↙← + puño | 0 |
| Cable a Tierra | ←↙↓↘→ + patada | 0 |
| Mantenimiento Preventivo | ↓↙← + patada | 150 |
| Reinicio en Cadena | ↓↘→↓↘→ + puño | 1000 |
| Reparacion General | ↓↘→↘↓↙← + puño | 1000 |
| Restaurar Sistema MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 6.00 segundos a 60 cuadros por segundo.

## Alejandro

| Movimiento | Combinación | Energía |
|---|---|---|
| Componente Angular | ↓↘→ + puño | 0 |
| Inyeccion de Dependencias | →↓↘ + puño | 0 |
| ng serve | ↓↙← + puño | 0 |
| Error de Compilacion | ←↙↓↘→ + patada | 0 |
| Importar Modulo | ↓↙← + patada | 0 |
| Refactorizacion | ↓↘→↓↘→ + puño | 1000 |
| Build de Produccion | ↓↘→↘↓↙← + puño | 1000 |
| Deploy MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 5.00 segundos a 60 cuadros por segundo.

## Daniela

| Movimiento | Combinación | Energía |
|---|---|---|
| Diagrama UML | ↓↘→ + puño | 0 |
| Revision de Negocio | →↓↘ + puño | 0 |
| Bolsazo de Requisitos | ↓↙← + puño | 0 |
| Cambio de Alcance | ←↙↓↘→ + patada | 0 |
| Documento Aprobado | ↓↙← + patada | 0 |
| Victor, Echame la Mano | ↓↘→↓↘→ + puño | 1000 |
| Entrega Documentada | ↓↘→↘↓↙← + puño | 1000 |
| Auditoria MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 3.50 segundos a 60 cuadros por segundo.

## Gameros

| Movimiento | Combinación | Energía |
|---|---|---|
| Gamepad Arcade | ↓↘→ + puño | 0 |
| Rep de Gimnasio | →↓↘ + puño | 0 |
| Rodada en Moto | ↓↙← + puño | 0 |
| Pedal a Fondo | ←↙↓↘→ + patada | 0 |
| Modo Gym | ↓↙← + patada | 0 |
| Combo de Gimnasio | ↓↘→↓↘→ + puño | 1000 |
| Full Throttle | ↓↘→↘↓↙← + puño | 1000 |
| Final Boss MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 4.00 segundos a 60 cuadros por segundo.

## Armando

| Movimiento | Combinación | Energía |
|---|---|---|
| Saque de Pingpong | ↓↘→ + puño | 0 |
| Clavada de Basquet | →↓↘ + puño | 0 |
| Impresion en Movimiento | ↓↙← + puño | 0 |
| Rebote Conectado | ←↙↓↘→ + patada | 0 |
| Calibrar IoT | ↓↙← + patada | 0 |
| Clavada Final | ↓↘→↓↘→ + puño | 1000 |
| Torneo de Basquet | ↓↘→↘↓↙← + puño | 1000 |
| Internet de los Golpes MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 5.00 segundos a 60 cuadros por segundo.

## Vladimir

| Movimiento | Combinación | Energía |
|---|---|---|
| Invitacion Obligatoria | ↓↘→ + puño | 0 |
| Pase al Frente | →↓↘ + puño | 0 |
| Nadie se Va | ↓↙← + puño | 0 |
| Honores al Sol | ←↙↓↘→ + patada | 0 |
| Pase de Lista | ↓↙← + patada | 0 |
| Conferencia Obligatoria | ↓↘→↓↘→ + puño | 1000 |
| Recorrido de Salones | ↓↘→↘↓↙← + puño | 1000 |
| Asistencia Total MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 4.00 segundos a 60 cuadros por segundo.

## Jaime

| Movimiento | Combinación | Energía |
|---|---|---|
| Salto del Caballo | ↓↘→ + puño | 0 |
| Potencia al Cuadrado | →↓↘ + puño | 0 |
| Sprint en Bicicleta | ↓↙← + puño | 0 |
| Derivada al Piso | ←↙↓↘→ + patada | 0 |
| Calculo Mental | ↓↙← + patada | 0 |
| Gambito Ciclista | ↓↘→↓↘→ + puño | 1000 |
| Tour de Integrales | ↓↘→↘↓↙← + puño | 1000 |
| Teorema Final MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 3.83 segundos a 60 cuadros por segundo.

## Leonardo

| Movimiento | Combinación | Energía |
|---|---|---|
| Notificacion Push | ↓↘→ + puño | 0 |
| Actualizar App | →↓↘ + puño | 0 |
| Swipe Elegante | ↓↙← + puño | 0 |
| Scroll Infinito | ←↙↓↘→ + patada | 0 |
| Modo Avion | ↓↙← + patada | 100 |
| Contraataque Movil | ↓↘→↓↘→ + puño | 1000 |
| Release Movil | ↓↘→↘↓↙← + puño | 1000 |
| Actualizacion MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 3.00 segundos a 60 cuadros por segundo.

## Cesar

| Movimiento | Combinación | Energía |
|---|---|---|
| Consulta PHP | ↓↘→ + puño | 0 |
| Baston del Backend | →↓↘ + puño | 0 |
| Silla de Apoyo | ↓↙← + puño | 0 |
| DELETE Sin WHERE | ←↙↓↘→ + patada | 0 |
| Pausa de Recuperacion | ↓↙← + patada | 200 |
| Empuje de Backend | ↓↘→↓↘→ + puño | 1000 |
| Revision Estricta | ↓↘→↘↓↙← + puño | 1000 |
| Examen Final MAX2 | ↓↙←↓↙← + A+C | 2000 + MAX |

Apoyo: espera 7.00 segundos a 60 cuadros por segundo.

## Arte y reconstrucción

Las diez hojas anteriores de especiales tienen 24 cuadros cada una. Sus fuentes y prompts exactos se conservan en `chars/<id>/art/specials/{sheet.png,PROMPT.json}` y sus vistas en `preview.png`. Los cuadros de dispositivos que dejaron de usarse se conservan como fuentes, sin invocar el antiguo emisor durante los supers. Las poses normales permanecen en `chars/<id>/art/`.

`python tools/build_teacher_specials.py` reconstruye especiales y la asistencia de Víctor. Acepta identificadores para reconstruir solo algunos. Los constructores de Chan, Félix, Alejandro y del reparto vuelven a aplicar los especiales automáticamente. `tools/teacher_super_variants.py` contiene las acciones físicas y `tools/victor-companion.cns` el actor persistente.

Las voces y algunos impactos siguen compartidos con el prototipo. Carrera y agarres de los profesores reutilizan poses; Chan y Félix todavía necesitan secuencias exclusivas de caída y victoria. Las bases KOF descargadas conservan sus repertorios originales.

## Validación

La revisión ejecutó **234 escenarios reales en Ikemen, sin fallos**: 230 del repertorio completo y cuatro adicionales para el ciclo de computadora/teléfono de Víctor y los segundos supers preparados de Félix, Alejandro y Armando. Incluye ocho comandos desde ambos lados, daño efectivo, costos, MAX2, curación, cargas, bloqueos por espera o energía, copias Angular, rebotes de pingpong, arco de ajedrez, agarre, contraataque y limpieza de helpers. Comprueba que los supers no invocan el antiguo emisor, que Víctor se levanta, golpea y vuelve a sentarse, y que su punto de reposo se mantiene fijo al mover la cámara. `python tools/test_teacher_specials.py` reproduce la batería; acepta identificadores de personajes. Informe: `scratch/teacher-specials-qa/validation.json`.

`python tools/test_kof_controls.py`: archivos SFF/AIR/CNS, sprites, referencias y las 50 definiciones de comandos de los doce luchadores. `python tools/test_utc_roster.py`: siete combates CPU completos. Las pruebas usan definiciones y configuraciones separadas que no están en el selector; verifican que `save/config.ini` permanece intacto.

La revisión visual usa poses extraídas de los SFF y capturas a velocidad normal del especial de Daniela en `scratch/consistency-review/`. El balance y la sensación de los combos todavía requieren una partida con tu mando.
