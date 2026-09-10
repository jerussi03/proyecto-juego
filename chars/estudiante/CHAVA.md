# Chava — variantes de combate

Abre `Ikemen_GO.exe` y selecciona **CHAVA** (estudiante). Reinicia el juego si ya estaba abierto.

## Controles

| Tecla actual P1 | Acción |
|---|---|
| A | Puñetazo ligero: alterna derecho e izquierdo |
| S | Mochila de pie: alterna subida y bajada |
| Abajo + A / S | Puñetazos alternados / gancho |
| A / S en el aire | Puñetazos alternados / martillo descendente |
| Z / X | Patada ligera / patada alta fuerte |
| Abajo + Z / X | Patada baja / barrida |
| Z / X en el aire | Patada horizontal / patada de hacha |
| D | Invocar IA, cuesta 1000 de energía |
| Flechas | Moverse, agacharse y saltar |

Pulsa nuevamente el mismo botón durante el puñetazo ligero o la mochila para guardar una repetición que sale en recuperación. Cada nueva ejecución alterna la variante. Mantener el botón no dispara una cadena automática. Un ligero que conecta también puede continuar en uno fuerte.

La lista interna usa botones MUGEN: x=A, y=S, a=Z, b=X, z=D. Las teclas físicas dependen de tu configuración.

## Cambios y conservación de tu trabajo

Se trabajó desde tus archivos manuales, conservando el gancho, la barrida, el martillo aéreo y la patada de hacha. Se restauraron dibujos diferentes para los ataques aéreos ligeros y se añadió una patada alta de pie. Se corrigieron los cuadros activos del jab agachado y de las patadas bajas.

La IA conserva tus cinco disparos, daño 32 y daño bloqueado 4, tiempos, posición y restricciones. Los controles, retratos y escenario se conservaron. El ayudante es ficticio y no conecta con servicios externos.

El cuerpo se exportó un 12 % más pequeño: reposo de 120 a 106 píxeles. Se ajustaron ejes, colisiones y dimensiones físicas. Se limpiaron dos capas de borde claro expuesto y se hizo binaria la transparencia del cuerpo. Los PNG de efectos de IA y retratos se conservaron exactamente.

El paquete contiene 229 entradas SFF, 108 acciones AIR y 318 referencias de cuadros. Conserva los sonidos kfm.snd. Algunas poses de reacción se reutilizan.

## Revisión y mantenimiento

- chava/revision2/preview/chava-variants.gif: comparación animada.
- chava/revision2/preview/variants.png: todos los cuadros de los ataques.
- chava/revision2/source/: láminas ImageGen y prompts completos en prompts.json.
- chava/revision2/manifest.json: dimensiones y ejes actuales.
- chava/revision2/validation.json: comprobaciones del paquete final.
- chava/frames/: PNG actuales.
- chava.air, chava.cns, chava.cmd, chava.sff: archivos del motor.
- estudiante.air y estudiante.sff: copias sincronizadas.

Los manifiestos y vistas de chava/preview/ anteriores a esta revisión son históricos.

Desde la raíz del juego, con Node, sharp, Python y Pillow disponibles:

```powershell
node tools/revise_chava.cjs
python tools/validate_chava_revision.py
node tools/preview_chava_revision.cjs
```

La reconstrucción parte de backups/chava-manual-20260910/, que conserva tus cambios previos a esta revisión. Si vuelves a editar manualmente, respalda los archivos y actualiza el generador antes de reconstruir. Los generadores antiguos están bloqueados para evitar sobrescribir esta versión.

Prueba opcional fuera del selector normal:

```powershell
python tools/chava_qa.py
.\Ikemen_GO.exe -debug -p1 estudiante/chava-qa.def -p2 kfm -s stages/patio.def -p2.life 10000 -p2.lifeMax 10000 -time 40
```

Recorre 17 ataques, incluidos cuatro pares alternados, y comprueba la animación elegida. La definición normal no carga chava-qa.*. La validación estática comprueba referencias, transparencia, contacto con píxeles del sprite, variantes distintas y conservación exacta del código y secuencias de IA. Se comprobó la carga y los ataques en Ikemen. El balance y las cadenas con teclado o mando necesitan evaluación jugando.

## Restaurar tu versión manual

Con el juego cerrado, restaura los archivos del personaje desde backups/chava-manual-20260910/. Esa copia contiene tu versión inmediatamente anterior a estas variantes.
