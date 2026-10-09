# The King of UTc para Android

Descarga [TheKingOfUTc-Android-v1.0.1.apk](https://github.com/jerussi03/proyecto-juego/releases/download/android-v1.0.1/TheKingOfUTc-Android-v1.0.1.apk)
e instálalo en el teléfono. Si Android lo solicita, habilita la instalación desde
el navegador o administrador de archivos utilizado. Abre **The King of UTc** y
espera a que termine de preparar los recursos en el primer inicio.

Requisitos: **Android 14 / API 34 o posterior, ARM64 y OpenGL ES 3.2**. La
compilación oficial del motor usada aquí enlaza `aarch64-linux-android34`.
Se recomienda disponer de 1 GB libre para descargar, instalar y extraer el juego.
No necesita copiar carpetas, conexión a Internet ni permisos de acceso a tus
archivos. Los ajustes y partidas quedan en el almacenamiento privado de la app.

Esta actualización conserva la firma de la versión 1.0.0 y se instala encima de
ella. Android anterior a 14 o un sistema de 32 bits no cumplen los requisitos
del motor incluido. Para investigar un rechazo de instalación, conserva el
mensaje exacto y consulta el modelo y la versión de Android del teléfono. Con
Android SDK y depuración USB autorizada, este comando lee la compatibilidad sin
instalar ni borrar datos:

```powershell
python tools/build_android.py --check-device
```

Comprueba API, ABI y OpenGL ES anunciado; no sustituye la instalación real.

Incluye los 12 personajes UTC con sus golpes y mecánicas personalizadas,
9 escenarios, modo historia y práctica. Las bases KOF opcionales del paquete de
escritorio no se incluyen en Android.

| Control táctil | Acción |
| --- | --- |
| Cruceta | Caminar, agacharse, saltar y diagonales |
| A | Puño ligero (`x`) |
| B | Patada ligera (`a`) |
| C | Puño fuerte (`y`) |
| D | Patada fuerte (`b`) |
| AB | Esquiva |
| BC | Activar MAX |
| CD | Golpe fuerte simultáneo |
| START | Confirmar / inicio |
| ATRÁS / PAUSA | Volver / menú de pausa |

La cruceta y los golpes se pueden mantener simultáneamente. Las secuencias y
requisitos de cada personaje están en [CONTROLES-KOF.md](CONTROLES-KOF.md),
[GOLPES-PROPIOS.md](GOLPES-PROPIOS.md) e
[IDENTIDADES-PERSONAJES.md](IDENTIDADES-PERSONAJES.md).

Los mandos de Android usan la misma distribución de cuatro golpes en todos los
jugadores. Así, conectar un mando antes del control táctil mantiene la asignación
de los botones al iniciar una partida.

## Validación de esta versión

Se verificaron la compilación, la firma, la alineación de bibliotecas a 16 KB,
los hashes de los 199 recursos del juego y sus 248 referencias. El menú y los
12 combates de contenido pasaron en una copia aislada con el mismo motor para
Windows. La ejecución Android se probó en un emulador Android 16, incluida la
instalación, extracción, selección de personajes y práctica con controles táctiles.

El emulador x86 utiliza traducción ARM64 y necesitó habilitar en ANGLE
`exposeNonConformantExtensionsAndVersions` para anunciar OpenGL ES 3.2. Esta prueba
no certifica compatibilidad con todos los teléfonos. Falta comprobar la versión
en un teléfono ARM64 físico y escuchar el audio; el emulador se ejecutó sin sonido.
Por ese motivo, la publicación Android se identifica como versión de prueba.

La versión 1.0.1 conserva el certificado de la 1.0.0 para instalarse como
actualización. Su APK se volvió a compilar con los 199 recursos del juego y se
verificaron firma, alineación de 16 KB, manifiesto y diez bibliotecas ARM64. La
prueba reciente de movimiento recorrió los doce personajes en el motor de
escritorio. No se ejecutó el APK 1.0.1 en un teléfono físico; el Android, ABI,
controlador gráfico o espacio del dispositivo pueden explicar un rechazo
concreto de instalación.

## Volver a compilar

En Windows, instala Python 3.11+, JDK 17 o 21 y Android SDK con plataforma 36 y
Build Tools 36.1.0. Define `ANDROID_HOME` y pon Java/Python en `PATH`.
El wrapper descarga Gradle 8.13 y usa Android Gradle Plugin 8.13.0. No se necesita
NDK para reconstruir esta app con las bibliotecas publicadas.

```powershell
python tools/build_android.py
```

El constructor verifica cada biblioteca contra [engine.lock.json](android/engine.lock.json),
genera los recursos desde una lista permitida, compila y firma el APK. El resultado
queda en `dist/TheKingOfUTc-Android-v1.0.1.apk`, junto con `SHA256SUMS.txt` y los
metadatos de compilación. Las bibliotecas permanecen fijadas a la Release 1.0.0.
También puedes proporcionar un APK previamente descargado que contenga esas
bibliotecas exactas:

```powershell
python tools/build_android.py --engine-apk ruta/al/APK.apk
python tools/package_android_assets.py --validate-only
```

Los recursos generados quedan en `scratch/`; Gradle y sus resultados quedan
excluidos de Git. La clave privada y su contraseña se guardan en
`android/.signing/`, también excluido. Conserva esa carpeta fuera del repositorio
para poder distribuir actualizaciones con la misma firma. Nunca la publiques.

## Motor y licencias

Se usan las bibliotecas ARM64 del Android nightly oficial del 7 de octubre de 2026,
commit [`86ac412b`](https://github.com/ikemen-engine/Ikemen-GO/tree/86ac412b156b524e2ec9aa47de4528acf47f175b),
con SHA-256 y procedencia fijados en `android/engine.lock.json`. El contenedor
adapta [Jesuszilla/ikemen-droid](https://github.com/Jesuszilla/ikemen-droid/tree/dbc5cfb49b1fed1d4a732ff48b439dd684d54145).
Las modificaciones están en `android/`, incluida la extracción con verificación
SHA-256 y los controles táctiles.

Los avisos están en [ENGINE-LICENSES.txt](android/ENGINE-LICENSES.txt),
[LICENSE-SDL.txt](android/LICENSE-SDL.txt) y
[THIRD-PARTY-NOTICES.md](android/THIRD-PARTY-NOTICES.md). La Release incluye
`src_ffmpeg.tar.gz`, el código correspondiente a FFmpeg distribuido por el motor.
Sus opciones de compilación están en
[`build/build.sh`](https://github.com/ikemen-engine/Ikemen-GO/blob/86ac412b156b524e2ec9aa47de4528acf47f175b/build/build.sh).
