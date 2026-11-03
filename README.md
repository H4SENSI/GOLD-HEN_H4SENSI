# GoldHEN Multi

Launcher web para PS4, mantenido por H4SENSI.

**Abrir el host:** https://h4sensi.github.io/GOLD-HEN_H4SENSI/

El launcher detecta el firmware de la consola y comprueba que estén disponibles los archivos de la ruta correspondiente antes de habilitar el inicio.

## Firmware probado

En una PS4 con firmware **13.52** se registraron **9 ejecuciones correctas de 10 pruebas** (90%). El resultado corresponde a esa configuración.

## Uso

1. Abrí el enlace desde el navegador de la PS4.
2. Esperá a que termine la comprobación del firmware y de los archivos.
3. Cuando el estado indique `READY`, podés pulsar `INICIAR`.

Si la comprobación no termina correctamente, el launcher deja el inicio deshabilitado.

## Firmware 14.00

SiSTRo publicó GoldHEN **v2.4b18.13 beta** con soporte para firmware 14.00. El autor advierte que pueden aparecer errores por tratarse de una versión beta.

Publicación: https://ko-fi.com/s/e694c36022

El host no tiene una ruta propia para 14.00. Al detectar esa versión, bloquea el inicio interno y muestra enlaces a dos servicios externos que se compartieron para pruebas:

- FeedChats Web14: https://feedchats.fr/web14/jb.html
- Sentrix Raw13: https://ps4.sentrix.ac/raw13/jb.html

Estos enlaces no forman parte del código de H4SENSI. El contenido puede cambiar en cualquier momento y no se ha verificado directamente el código que entregan actualmente esos dominios. En el repositorio público relacionado con Raw13, la ruta 14.00 aparece identificada como desarrollo experimental (`14.00-hx1400-dev`), no como una ruta probada de H4SENSI.

GoldHEN v2.4b18.13 se publica como beta y añade soporte para 14.00. La versión del payload y el exploit son componentes separados: disponer de GoldHEN compatible no garantiza que cualquier host o cadena de exploit funcione.

El ISO de Poy Gaming recibido para revisión es una modificación de terceros. Su propio `NOTICE.TXT` indica que no es una publicación oficial de SiSTRo. No se incorpora al repositorio ni se presenta como el binario oficial de GoldHEN.

Usá estos hosts externos bajo tu responsabilidad. Guardá tu trabajo antes de probar y tené presente que un fallo en una cadena de kernel puede bloquear la consola.

## Caché sin conexión

Para guardar los archivos disponibles en la consola, abrí `cache.html` con conexión y esperá a que finalice el proceso. La caché se administra mediante el Service Worker.

## Estructura

- `index.html`: launcher.
- `cache.html`: preparación de la caché local.
- `sw.js`: gestión de archivos en caché.
- `700/`, `900/`, `css/` y `patches/`: motores y archivos utilizados por las rutas del proyecto.
