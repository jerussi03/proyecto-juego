# Alejandro: hojas de animación

Método: herramienta integrada ImageGen; fondo transparente. Referencia de
identidad: `alejandro_angular.jpeg`, proporcionada por el autor del juego.

Especificación común del conjunto de prompts:

> Sprites originales de pixel art para un juego de lucha 2D. Usar la imagen
> adjunta como referencia de identidad: Alejandro, cabello negro peinado hacia
> atrás, barba corta, camisa abierta de cuadros rojos y negros, camiseta gris,
> lentes colgados del cuello, pantalón verde olivo y tenis negros con blanco.
> Conservar cara, ropa y proporciones. Vista lateral hacia la derecha. Hoja
> de 1536 × 1024 con seis columnas y cuatro filas; un personaje completo por
> celda y seis poses consecutivas por fila. Fondo realmente transparente.
> Mantener espacio alrededor de manos, pies y cabeza. Sin texto, números,
> cuadrícula visible, efectos ni otros personajes.

Acciones de cada prompt/hoja:

1. `alejandro-idle-walk-punch-uppercut.png`: fila 1, respiración en guardia;
   fila 2, caminar; fila 3, preparación, extensión y recuperación del puño;
   fila 4, agacharse y ejecutar un gancho ascendente.
2. `alejandro-kick-sweep-jump-guard.png`: fila 1, patada frontal completa;
   fila 2, barrida baja y recuperación; fila 3, agacharse, despegar, salto,
   descenso y aterrizaje; fila 4, tres poses de guardia y tres reacciones
   al recibir un golpe.
3. `alejandro-intro-fall-getup-win.png`: fila 1, entrada saludando y
   señalando con las manos hasta adoptar guardia; fila 2, perder el equilibrio,
   caer hacia atrás y terminar acostado boca arriba; fila 3, levantarse desde
   el suelo hasta guardia; fila 4, celebrar señalando, mano detrás de la cabeza
   y terminar de brazos cruzados.

El constructor `tools/build_alejandro.py` separa las 72 siluetas y ajusta sus
pivotes para incorporarlas a `chars/alejandro/alejandro.sff`. Conserva tiempos,
colisiones y controles de la base UTC actual; estas hojas no son sprites
extraídos de KOF ni una conversión completa de sus movimientos.
