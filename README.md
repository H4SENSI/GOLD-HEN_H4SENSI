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

El host todavía no tiene una ruta BD-J integrada ni pruebas propias en 14.00. Al detectar esa versión, muestra el aviso y bloquea el inicio desde el launcher.

El ISO de Poy Gaming recibido para revisión es una modificación de terceros. Su propio `NOTICE.TXT` indica que no es una publicación oficial de SiSTRo y que no se midió su tasa de éxito en hardware. No se incorpora al repositorio ni se presenta como el binario oficial de GoldHEN.

## Caché sin conexión

Para guardar los archivos disponibles en la consola, abrí `cache.html` con conexión y esperá a que finalice el proceso. La caché se administra mediante el Service Worker.

## Estructura

- `index.html`: launcher.
- `cache.html`: preparación de la caché local.
- `sw.js`: gestión de archivos en caché.
- `700/`, `900/`, `css/` y `patches/`: motores y archivos utilizados por las rutas del proyecto.
