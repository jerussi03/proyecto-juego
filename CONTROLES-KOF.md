# Héctor y Chava: controles KOF

Reinicia Ikemen para cargar los cambios. A/B/C/D en esta guía son los botones de **KOF**, no las letras impresas en Xbox. Adelante y atrás siempre se interpretan respecto al rival.

| Acción | KOF / arcade | Xbox actual | Teclado P1 | Botón interno |
|---|---|---|---|---|
| Puño ligero | A | X | A | x |
| Patada ligera | B | A | Z | a |
| Puño fuerte | C | Y | S | y |
| Patada fuerte | D | B | X | b |
| Esquive | A+B | X+A o RT | A+Z o C | x+a o c |
| MAX | B+C | A+Y o RB | Z+S o D | a+y o z |
| Golpe de rechazo | C+D | Y+B | S+X | y+b |

Los botones de ataque del teclado y Xbox conservan sus asignaciones. Las direcciones del mando usan ahora la **palanca analógica izquierda**, con umbral 0.35 para facilitar diagonales. Sirve para caminar, saltar, agacharse y trazar los movimientos de los poderes. RT sigue siendo esquive y RB sigue siendo MAX.

Esta versión del motor admite una asignación por dirección. Para volver a la cruceta o a un arcade que envía direcciones digitales, cierra el juego y ejecuta desde la carpeta del juego:

```powershell
powershell -File tools/seleccionar-direcciones-mando.ps1 -Modo cruceta
```

Para volver a la palanca izquierda, usa `-Modo analogico`. Puedes añadir `-Jugador 2` para cambiar solo P2; sin ese argumento se cambian los cuatro mandos. Cada cambio guarda un respaldo en `backups/mandos-analogicos/`. También puedes reasignar las cuatro direcciones desde las opciones del juego.

Para un arcade, asigna los cuatro botones físicos a **x, a, y, b**, en ese orden, desde la configuración de controles. Todas las acciones pueden ejecutarse con cuatro botones; los auxiliares son opcionales. El orden físico de algunos mandos arcade necesita ese ajuste inicial.

## Movimiento y defensa

- Adelante dos veces: correr. Atrás dos veces: salto hacia atrás.
- Atrás: bloquear de pie. Abajo+atrás: bloquear abajo.
- A+B o RT: esquive hacia delante. Mantén atrás para esquivar hacia atrás.
- El esquive dura 24 cuadros: evita golpes y proyectiles entre los cuadros 2 y 15, admite agarres y termina con recuperación vulnerable.
- A+B mientras bloqueas un golpe: esquive de cancelación de guardia, cuesta 1000 de energía. Mantén atrás para salir hacia atrás.
- C+D: golpe de rechazo con derribo.

## MAX

B+C o RB activa MAX por 1000 de energía. Durante el contacto de un golpe normal cuesta 2000 y tiene recuperación más corta. No se puede reactivar mientras siga activo.

Su indicador dorado dura 600 cuadros de juego, aproximadamente 10 segundos sin contar pausas. Permite cancelar un especial que conecta o es bloqueado en otro especial distinto: cada cancelación consume 90 cuadros adicionales. También permite pasar de un especial que conecta a un super. Los supers siguen gastando energía.

MAX2 requiere MAX activo y 2000 de energía; consume ambos. La capacidad de cada personaje es de 5000. Es una adaptación inspirada en KOF 2002 con temática y balance propios, no una reproducción completa de todas sus mecánicas.

## Movimientos

Las flechas siguientes suponen que miras a la derecha; inviértelas al cambiar de lado. Pulsa el botón al terminar el recorrido. A o C significa cualquiera de los dos; ambos ejecutan la misma versión del especial. Los especiales admiten hasta 24 cuadros para completar el movimiento; los supers, 36, y MAX2, 40.

### Chava

| Poder | Comando KOF | Energía |
|---|---|---|
| Código compilado: proyectil | ↓ ↘ → + A o C | 0 |
| Código, alternativa en «U» | ← ↙ ↓ ↘ → + A o C | 0 |
| Gancho de compilación | → ↓ ↘ + A o C | 0 |
| Mochilazo de avance | ↓ ↙ ← + A o C | 0 |
| Barrida de semestre | ← ↙ ↓ ↘ → + B o D | 0 |
| Asistente IA, cinco disparos | ↓ ↘ → ↓ ↘ → + A o C | 1000 |
| Entrega final, combo de mochila | ↓ ↘ → ↘ ↓ ↙ ← + A o C | 1000 |
| MAX2: compilación final + IA | ↓ ↙ ← ↓ ↙ ← + A+C | 2000 + MAX |

Se conservan los golpes alternados de Chava y sus ataques de pie, agachado y en el aire. Los poderes nuevos reutilizan sus animaciones de mochila, gancho, barrida y efectos de código.

### Héctor

| Poder | Comando KOF | Energía |
|---|---|---|
| Paquete de red: proyectil | ↓ ↘ → + A o C | 0 |
| Gancho de protocolo | → ↓ ↘ + A o C | 0 |
| Latigazo RJ-45 de avance | ↓ ↙ ← + A o C | 0 |
| Barrida de capa física | ← ↙ ↓ ↘ → + B o D | 0 |
| Firewall: parry | ↓ ↙ ← + B o D | 0 |
| Error 403, tras parry exitoso | C | 0 |
| Handshake, agarre cerca | → ↘ ↓ ↙ ← + A | 0 |
| Sin conexión | ← ↙ ↓ ↘ → + A o C | 1000 |
| Drone Deploy | ↓ ↘ → ↓ ↘ → + A o C | 1000 |
| DDoS | ↓ ↘ → ↓ ↘ → + B o D | 1000 |
| Modo FPV | ↓ ↙ ← ↓ ↙ ← + B o D | 1000 |
| CTRL+ALT+SUPR | ↓ ↘ → ↘ ↓ ↙ ← + A o C | 1000 |
| Desconectado, rival con 120 de vida o menos | → ↘ ↓ ↙ ← + C | 1000 |
| MAX2: denegación de servicio | ↓ ↙ ← ↓ ↙ ← + A+C | 2000 + MAX |

Héctor tiene dibujos nuevos para puñetazos agachados ligero y fuerte, patada fuerte de pie y patada fuerte aérea. La barrida fuerte y el puño fuerte aéreo reutilizan sus secuencias existentes. Se agregó la acción de correr usando sus cuadros de carrera.

## Qué revisar jugando

1. Prueba los cuatro ataques de pie, agachado y saltando con ambos. Observa especialmente puñetazos agachados y patadas fuertes de Héctor.
2. Ejecuta cuartos de círculo, ganchos y medias lunas mirando a ambos lados. Comprueba que salga el poder y no un golpe normal. En Xbox, A de KOF es X del mando.
3. Compara el esquive A+B con RT, hacia delante y atrás: cruce del rival, distancia y recuperación vulnerable.
4. Compara MAX B+C con RB: coste, barra dorada, agotamiento, activación durante un golpe y cancelación entre especiales distintos.
5. Prueba supers y MAX2: consumo de energía, daño, bloqueo y desaparición de drones/IA al acabar el ataque o la ronda.
6. Comprueba las combinaciones simultáneas en tu mando y arcade; ajusta el mapeo si sus botones están en otro orden.

Los tiempos, alcance y daño quedan pendientes de tu evaluación jugando. Antes de que pidieras encargarte de la revisión, se había completado una carga y un combate de prueba, además de una revisión de referencias de sprites y estados. No se ha completado la validación de todos los controles físicos.

## Respaldo y mantenimiento

El respaldo previo está en `backups/kof-controls-20260913/`. Los `.cmd` contienen los comandos; `kof-extra.cns` de cada personaje contiene los poderes nuevos; `chars/kof-system.cns` comparte MAX y esquive. Las listas de movimientos del menú de pausa están actualizadas.

`tools/build_kof_controls.py` reconstruye esta revisión desde el respaldo. No lo ejecutes después de hacer nuevos cambios manuales sin adaptar primero el generador: sobrescribe los archivos de esta revisión. Las definiciones `kof-input-qa.def` son pruebas aisladas y no se incluyen en el selector normal.

Referencia: [sistema oficial de KOF 2002, SNK](https://www.snk-corp.co.jp/official/kof2002/english/e_kof2002_system.html).
