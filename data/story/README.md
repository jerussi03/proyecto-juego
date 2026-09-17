# Historia de The King of UTC

El botón MODO HISTORIA inicia la ruta con Chava. Confirmar o Enter avanza el diálogo, izquierda vuelve a la página anterior de la escena y Escape sale.

Contiene 58 tarjetas: prólogo, doce encuentros, transiciones y epílogo. Los retratos originales están en `portraits`. El nombre de Programación es Alejandro y su imagen es `alejandro_angular.jpeg`.

Actualmente solo Chan y Héctor tienen combates. Las otras diez etapas se cuentan como escenas narrativas, sin sustituir a los profesores por otros luchadores. La graduación es el desenlace narrado, no una recompensa por derrotar a un César aún inexistente como luchador. Para activar otro combate, añadir su personaje al select.def y su referencia en route.lua.

La introducción MP4 anterior queda archivada en video/utc_intro.mp4 y ya no se reproduce. Los diálogos empiezan únicamente al elegir MODO HISTORIA, nunca al arrancar ni en el modo de demostración. La introducción ilustrada comparte el lector y el estilo de los capítulos. intro.def conserva un storyboard nativo como respaldo, sin activación automática.

Los diálogos se editan en chapters.json. Leonardo y Víctor tienen escenas nuevas; la materia de Daniela y la asignatura de Víctor siguen sin especificar. Víctor aparece en una revisión del proyecto. La frase inicial usa «materias, trámites y título» porque los doce encuentros incluyen al director y al jefe final.

Para reconstruir las tarjetas: `python tools/build_story.py`. El script usa Pillow y las fuentes Consolas de Windows. La primera importación admite `--source DIRECTORIO`.

Las pruebas en tools/story_qa.lua recorren el lector en el motor real y simulan el resultado de los combates para comprobar la ruta, cancelación y fin. También ejecutan el callback real del menú para comprobar que Chava esté asignado antes de consultar su ruta. tools/story_fight_qa.lua carga y termina un combate real Chava contra Chan, con CPU y tiempo reducido, desde ese mismo callback.
