# Chava — Ingeniería en Sistemas

Chava ya sustituye al antiguo «Alex» en la casilla **estudiante** del selector.
Su meta es vencer a los profesores para conseguir el título. Mantiene el rostro,
la polo verde, los pantalones oscuros, los tenis y la pose con control de las
referencias proporcionadas.

## Jugar

Abre `Ikemen_GO.exe` y selecciona **CHAVA**. No hace falta importar sprites.

Con la configuración actual del jugador 1:

| Tecla | Acción |
|---|---|
| Flechas | Moverse, agacharse y saltar |
| A | Puñetazo ligero |
| S | Mochilazo de pie / puñetazo fuerte agachado o en el aire |
| Z | Patada ligera |
| X | Patada fuerte; agachado hace barrida |
| D | Invocar al asistente de IA; cuesta 1000 de energía |
| Abajo, diagonal adelante, adelante + A y S | Entrada clásica del especial de IA |
| Dos veces adelante | Correr |
| Dos veces atrás | Salto corto hacia atrás |
| Atrás / diagonal abajo-atrás | Guardia alta / baja |
| Enter | Provocación |

Las letras de la lista de movimientos interna son **botones MUGEN**, no teclas:
`x=A`, `y=S`, `a=Z`, `b=X`, `z=D`. Si cambias la configuración del juego, las
teclas físicas pueden ser distintas.

Un ataque ligero que **conecta** puede continuar en uno fuerte durante su
recuperación. El golpe falla si el rival está fuera de alcance. La mochila solo
hace daño en el cuadro de contacto, no durante toda la animación.

La IA es un compañero holográfico del juego: aparece, dispara tres ráfagas de
código bloqueables y desaparece. No conecta con servicios externos. El personaje
debe reunir una barra de energía y no puede acumular varias invocaciones a la vez.

## Contenido

- Sprites nuevos de reposo, caminar, correr, agacharse, salto y aterrizaje.
- Puñetazos, mochila, patadas, barrida y ataques aéreos.
- Guardia alta, baja y aérea; daño, derribo, suelo, levantarse y recuperación.
- Entrada, provocación, victoria y asistente de IA con proyectiles e impacto.
- 104 acciones AIR y 175 entradas SFF, incluyendo retratos y alias de compatibilidad.
- PNG exportados con transparencia binaria y escala fija por lámina.
- Ejes de suelo estables y ejes de salto que conservan la altura del torso al recoger las piernas.
- Los sonidos de combate siguen siendo los de la base existente `kfm.snd`.
- Una paleta de traje. Los botones del selector usan esa misma paleta.

Los ataques fuertes y ligeros comparten algunas secuencias dibujadas, con distintos
tiempos, daño y recuperación. Las acciones de daño requeridas por el motor
también reutilizan poses apropiadas; 104 acciones no significa 104 dibujos únicos.
Los movimientos antiguos de Kung Fu Man que no pertenecen al concepto de Chava
ya no forman parte de sus controles.

## Revisar y editar

- `chava/preview/chava-showcase.gif`: reposo, mochila e invocación juntos.
- `chava/preview/0.gif`, `20.gif`, `100.gif`, `210.gif`, etc.: secuencias individuales.
- `chava/preview/all-sprites.png`: hoja de revisión de los dibujos exportados.
- `chava/source/`: cinco láminas originales, las dos referencias y `prompts.json`.
- `chava/frames/`: sprites PNG independientes.
- `chava/manifest.json`: origen, escala, ejes, tiempos y colisiones por cuadro.
- `chava/validation.json`: resultado de la verificación automatizada.
- `chava.air`, `chava.cns`, `chava.cmd`, `chava.sff`: archivos utilizados por el motor.

Arte creado con la herramienta integrada **ImageGen**. Los prompts completos se
conservan en `chava/source/prompts.json`. Las herramientas locales separan las
siluetas, eliminan el fondo, exportan los píxeles y empaquetan el personaje.

Desde la raíz del juego, con Node y el paquete `sharp` disponibles:

```powershell
node tools/build_chava.cjs
python tools/configure_chava.py
python tools/validate_chava.py
node tools/preview_chava.cjs
```

Los scripts de construcción regeneran los archivos `chava.*`. Si editas esos
archivos a mano, respalda tus ajustes o trasládalos al generador antes de reconstruir.
El validador usa Pillow y comprueba el SFF, las 282 referencias de cuadros AIR,
las poses requeridas, la transparencia, los contactos y la conservación de los originales.

Prueba opcional de los doce ataques y el especial, sin añadir otra casilla al selector:

```powershell
python tools/chava_qa.py
.\Ikemen_GO.exe -p1 estudiante/chava-qa.def -p2 kfm -s stages/patio.def -p2.life 10000 -p2.lifeMax 10000 -time 40
```

`chava-qa.def` y `chava-qa.cns` son exclusivamente de prueba: reposicionan al
personaje y rellenan su energía para recorrer los ataques. `estudiante.def`
no los carga.

## Verificación y límites

Se cargó el personaje en Ikemen GO v1.0.0-rc.4, se revisó su aspecto en el patio y
se ejecutó combate automático. El especial consumió energía y dañó al adversario.
Además se ejecutó la secuencia programada de ataques. Las comprobaciones estáticas
verifican que cada ataque tenga colisión activa en su cuarto cuadro y que esa
colisión coincida con píxeles del sprite.

Esta es una revisión jugable; la fluidez visual y el balance aún admiten ajustes
tras jugar con teclado o mando. No se ha hecho una prueba manual completa de todos
los comandos ni una prueba extensiva contra personajes externos. La comprobación
geométrica de las cajas no sustituye ese balance durante partidas.

Documentación técnica consultada: [controladores de estado de Elecbyte](https://elecbyte.com/mugendocs/sctrls.html).

## Volver a la versión anterior

La carpeta `backups/chava-pre-20260909/`, en la raíz del juego, conserva los archivos
anteriores, incluidos los cambios que ya había antes de esta revisión. Los
`estudiante.air`, `estudiante.sff`, `kfm.cns` y `kfm.cmd` antiguos siguen intactos.
Para reactivar esa versión basta con restaurar su `estudiante.def` desde la copia.
