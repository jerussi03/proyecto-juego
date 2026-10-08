# Bases KOF para el proyecto UTC

Actualizado: 8 de octubre de 2026.

## Lo que ya está instalado

En Entrenamiento y Versus están disponibles Kyo, Iori, K’, Terry EX,
Ryo EX y Nameless, de Ikaruga. Conservan sus nombres, voces y animaciones
originales. Son bases jugables de **KOF 2002 UM**, no conversiones visuales
terminadas de los profesores ni una reproducción exacta de KOF 2002 original.
La campaña sigue usando los luchadores UTC existentes.

Se conservan las asignaciones de teclado y mando de `CONTROLES-KOF.md`:

| Acción | Botones internos | Atajo existente |
|---|---|---|
| A: puño débil | x | Xbox X / teclado A |
| B: patada débil | a | Xbox A / teclado Z |
| C: puño fuerte | y | Xbox Y / teclado S |
| D: patada fuerte | b | Xbox B / teclado X |
| Evasión / recuperación | x+a | c: RT / teclado C |
| MAX | a+y | z: RB / teclado D |
| Golpe CD | y+b | C+D |

Los comandos de especiales, agarres, cancelaciones, saltos y supers proceden
de cada base. Los manuales originales están en `chars/base-*/txt/ReadMe(ENG).txt`.
En esos manuales, los atajos originales z=CD y c=MAX ya no corresponden:
se sustituyeron por los de esta tabla. No se cambiaron las asignaciones
globales de teclado, mando ni el umbral del stick.

## Adaptación propuesta a los profesores

Todos los profesores jugables tienen animaciones UTC y entradas de control KOF.
Héctor conserva sus poderes de drones y redes; los otros diez ahora tienen ocho
especiales temáticos cada uno, con lógica y arte originales. Las bases descargadas
siguen siendo referencias: no se ha trasladado su lógica a estos profesores.
Las referencias de movimientos de la tabla siguen siendo propuestas de diseño;
la presencia de un profesor en el selector no implica haber importado esa lógica.
La referencia de personalidad es `personajes.txt`; donde faltan detalles se usa
la historia proporcionada por el autor del juego.

| Personaje UTC | Referencia descargada | Aplicación a su personalidad |
|---|---|---|
| Chan | Luchadora UTC nueva; Ryo EX como referencia de diseño futuro | Tiene 48 poses propias, controles KOF y pelea en el primer capítulo. Añade 24 cuadros para exámenes SQL, crossfit y documentación; falta voz propia. |
| Félix | Luchador UTC nuevo; Terry EX como referencia de diseño futuro | Tiene 48 poses propias, controles KOF y pelea en el segundo capítulo. Añade llave, combo de reparación y mantenimiento; falta voz propia. |
| Alejandro | Luchador UTC nuevo; Kyo como referencia futura de lógica | Tiene 72 poses propias, entrada, caída, recuperación y victoria. Pelea en el capítulo 3 con los controles actuales; componentes Angular, ng serve y preparación de módulos integrados. Falta voz propia; personalidad adicional pendiente en el documento. |
| Daniela | Iori como referencia futura | 72 poses propias con su bolsa; capítulo 4. Víctor permanece en un punto fijo del fondo y se levanta para golpear durante el super. Especiales UML, bolsazo y documentación integrados. |
| Héctor Hugo | K’ como referencia adicional | Control de distancia y conexiones de red. Su luchador existente permanece intacto. |
| Gameros | Iori como referencia futura | 72 poses propias, capítulo 6; 24 cuadros adicionales con moto, gamepad, arcade/gym y bicicleta. |
| Armando | Terry EX como referencia futura | 72 poses propias, capítulo 7; presentación de anfitrión y celebración deportiva. Pingpong con rebotes, salto con clavada y guiños IoT integrados. |
| Vladimir | Ryo EX como referencia futura | 72 poses propias, capítulo 8; entrada revisando asistencia. Invitaciones que atraen, puerta, sol y conferencia integrados. |
| Jaime, Matemáticas | Ryo EX como referencia futura | 72 poses propias, capítulo 9; caballo de ajedrez en arco, bicicleta, tablero y cálculo mental integrados. |
| Leonardo | K’ como referencia futura | 72 poses propias, capítulo 10; entrada y victoria ajustándose la ropa elegante. Notificaciones, swipe, contraataque físico y modo avión integrados. |
| César Giovani | Nameless como referencia futura | 72 poses propias con bastón; jefe del capítulo 12. Proyectil PHP, empuje con silla y pausa de recuperación integrados. |
| Víctor | Ninguna: acompañante | Acompañante fijo de Daniela; 24 cuadros nuevos de asistencia física y regreso al escritorio, sin controles propios. |

Las poses básicas, saltos, guardia, ataques, daño, caída, recuperación, entrada
y victoria de los siete profesores nuevos ya están integradas. Carrera y agarres
reutilizan cuadros del conjunto actual. Quedan voces propias y más poses para acciones normales. Los especiales
ya tienen efectos y parámetros diferentes; guía en [ESPECIALES-MAESTROS.md](ESPECIALES-MAESTROS.md). La revisión separada de Víctor se sustituyó por
un ensayo del proyecto de Chava; Víctor aparece con Daniela.

## Procedencia y conservación

- Autor: Ikaruga; gráficos y personajes originales acreditados a SNK en los manuales.
- Descargas: http://ikrgmugen.web.fc2.com/kof02um.html
- Archivos originales intactos: `downloads/kof-bases/`.
- Importación: `tools/import_kof_bases.py`.
- Rutas y SHA-256: `data/kof-bases.json`.
- Los ReadMe japoneses incluyen los permisos por componente. En particular,
  Kyo permite adaptar CNS/SND pero no su SFF: usar su lógica con ilustraciones
  UTC nuevas, sin editar ni reutilizar sus sprites para las conversiones.
- No se han publicado ni redistribuido los paquetes.

## Comprobaciones realizadas

- Kyo contra Iori: un combate automático completo en el motor actual.
- Terry EX contra Ryo EX: un combate automático completo.
- K’ contra Nameless: un combate automático completo.
- Registros: `scratch/kof-base-match-1.log`, `-2.log`, `-3.log`.
- Comprobaciones de sprites, estados y comandos de Chava/Héctor: correctas.
- Prueba del menú de historia, sus 60 tarjetas y salidas: correcta; esa prueba
  sustituye los combates por llamadas simuladas.
- Falta una prueba manual de sensaciones y combos con el mando del usuario.

## Actualización del motor

Descargada la versión oficial 1.0.0 estable:
https://github.com/ikemen-engine/Ikemen-GO/releases/tag/v1.0.0

Paquete: `downloads/ikemen-v1.0.0/Ikemen_GO-v1.0.0-windows.zip`.
SHA-256 verificado contra SHA256SUMS oficial:
`9338eaeb68599ceb13b0867819a091ea3f92eba58077e800b4540b7a1f9c3731`.

**No se reemplazó TheKingOfUTc.exe.** La fusión automática de los scripts de
la distribución con los scripts personalizados tiene conflictos. Una prueba
aislada de la versión estable produjo un registro de combate, pero el proceso
no terminó correctamente y se cerró. No se considera validada para sustituir
el motor actual. Los archivos de comparación y fusión son material de trabajo
dentro de `downloads/ikemen-v1.0.0/`, no scripts activos del juego.
