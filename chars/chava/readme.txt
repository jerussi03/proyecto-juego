=================================
 ALEX — EL ALUMNO PROMEDIO
=================================

Personaje jugable para IKEMEN GO.

Alex es un estudiante de Desarrollo de Software: relajado, gamer e
improvisador. Pelea usando su tarea, mochila, laptop y una IA holográfica.

INSTALACIÓN
===========

El personaje ya está registrado en data/select.def como `estudiante` y se
selecciona en el roster con el nombre ALEX — EL ALUMNO PROMEDIO.

CONTROLES
=========

Las letras son acciones abstractas de IKEMEN, no teclas físicas. Puedes
asignarlas a teclado, gamepad o arcade stick desde la configuración del juego.

  X                   Entregar Tarea con 10
  Y                   Mochilazo con Libros
  Abajo + X/Y         Barrida con Laptop (versiones rápida/pesada)
  Salto + X/Y         Mochilazo Aéreo
  Abajo, Atrás + X/Y  Invocación de IA (requiere 1 barra de poder)

COMBOS SENCILLOS
================

  Entregar Tarea con 10 -> Mochilazo con Libros -> Invocación de IA
  Mochilazo Aéreo -> Entregar Tarea con 10 -> Mochilazo con Libros

BALANCE
=======

La tarea es rápida y sirve para confirmar golpes. La mochila tiene más alcance
y daño, pero recupera más lento. La laptop golpea bajo. La Invocación de IA
emite tres pulsos, lanza al rival con el último y tiene recuperación larga si
se bloquea o falla.

ARCHIVOS PRINCIPALES
====================

  estudiante.def  Identidad y enlaces del personaje
  kfm.cmd         Entradas y rutas a estados
  kfm.cns         Física, daño, HitDefs y estado 3100 de la IA
  estudiante.air  Animaciones y cajas de colisión
  estudiante.sff  Sprites
  build_alex_sprites.py  Generador de poses transparentes y consistentes
