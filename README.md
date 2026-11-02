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

GoldHEN no tiene soporte oficial para firmware 14.00 en la versión publicada actualmente (v2.4b18). El método BD-JB para esta versión sigue siendo experimental e inestable. Si el launcher detecta 14.00, muestra un aviso y bloquea el inicio; no intenta cargar un binario de GoldHEN incompatible.

## Caché sin conexión

Para guardar los archivos disponibles en la consola, abrí `cache.html` con conexión y esperá a que finalice el proceso. La caché se administra mediante el Service Worker.

## Estructura

- `index.html`: launcher.
- `cache.html`: preparación de la caché local.
- `sw.js`: gestión de archivos en caché.
- `700/`, `900/`, `css/` y `patches/`: motores y archivos utilizados por las rutas del proyecto.
