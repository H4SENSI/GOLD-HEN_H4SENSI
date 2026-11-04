# GoldHEN Multi

Launcher web para PS4, mantenido por H4SENSI.

**Abrir el host:** https://h4sensi.github.io/GOLD-HEN_H4SENSI/

El launcher detecta el firmware del navegador de PS4, selecciona una ruta habilitada y comprueba los archivos que necesita antes de permitir el inicio. Una versión que tenga motor pero no esté explícitamente habilitada continúa bloqueada.

## Cómo funciona la comprobación

- `index.html` detecta la versión del firmware y resuelve la ruta correspondiente.
- `asset-manifest.json` fija el tamaño y el Git blob SHA-1 de cada archivo usado por las rutas actualmente habilitadas.
- El launcher comprueba los bytes descargados frente a ese manifiesto. Cuando WebCrypto está disponible también verifica el Git blob SHA-1 en el navegador; siempre exige el tamaño exacto.
- `sw.js` mantiene la caché offline versionada. Durante una comprobación solicita primero una copia de red y, si no hay conexión, permite comprobar la copia ya guardada.
- Los scripts de `scripts/` contrastan los hashes y tamaños del manifiesto con los archivos del repositorio para detectar desincronizaciones en CI.

El hash Git blob SHA-1 sirve para detectar archivos distintos o incompletos respecto del commit fijado. **No es una firma digital ni demuestra quién publicó el archivo**; tampoco protege frente a una modificación maliciosa simultánea del launcher y de su manifiesto.

## Firmware probado

En una PS4 con firmware **13.52** se registraron **9 ejecuciones correctas de 10 pruebas**. Es un resultado manual comunicado para esa configuración, no una garantía general ni una prueba automatizada reproducible.

Las rutas que aparecen en `ROUTE_READY` son las únicas que el launcher permite iniciar. Que un motor figure en el código no significa que esté habilitado o probado.

## Uso

1. Abrí el enlace desde el navegador de la PS4.
2. Esperá a que termine la detección del firmware y la comprobación de integridad de los archivos.
3. Solo cuando el estado indique `READY` se habilitará `INICIAR`.

Si falla la detección, el manifiesto o cualquiera de los archivos, el inicio queda bloqueado. Volvé a comprobar cuando tengas conexión y los archivos disponibles.

## Firmware 14.00

SiSTRo publicó GoldHEN **v2.4b18.13 beta** con soporte para firmware 14.00. El autor advierte que pueden aparecer errores por tratarse de una versión beta.

Publicación: https://ko-fi.com/s/e694c36022

**La ruta interna de H4SENSI para 14.00 permanece deshabilitada.** Al detectar esa versión, el launcher bloquea el inicio local y muestra enlaces a dos servicios externos que se compartieron para pruebas:

- FeedChats Web14: https://feedchats.fr/web14/jb.html
- Sentrix Raw13: https://ps4.sentrix.ac/raw13/jb.html

Estos enlaces no forman parte del código de H4SENSI. El contenido puede cambiar en cualquier momento y no se ha verificado directamente el código que entregan actualmente esos dominios. En el repositorio público relacionado con Raw13, la ruta 14.00 aparece identificada como desarrollo experimental (`14.00-hx1400-dev`), no como una ruta probada de H4SENSI.

La versión del payload y el exploit son componentes separados: disponer de un GoldHEN compatible no garantiza que cualquier host o cadena de exploit funcione. Los archivos `goldhen.bin` y `goldhen_2.4b18.12.bin` incluidos actualmente en este repositorio tienen el mismo contenido y corresponden al payload b18.12; el aviso sobre b18.13 beta no significa que ese payload esté incluido aquí.

El ISO de Poy Gaming recibido para revisión es una modificación de terceros. Su propio `NOTICE.TXT` indica que no es una publicación oficial de SiSTRo. No se incorpora al repositorio ni se presenta como el binario oficial de GoldHEN.

Usá los hosts externos bajo tu responsabilidad. Guardá tu trabajo antes de probar y tené presente que un fallo en una cadena de kernel puede bloquear la consola.

## Caché sin conexión

Para preparar la caché, abrí `cache.html` con conexión y esperá a que finalice la lista de archivos. Si la página informa archivos pendientes, no des por preparada la copia offline: repetí el proceso con conexión y revisá que el launcher termine la comprobación antes de usarlo sin red.

El Service Worker utiliza una versión de caché independiente, sincronizada con la URL de registro de `index.html` y `cache.html`. El antiguo manifiesto Application Cache se retiró porque era obsoleto y contenía una lista parcial.

## Validación para mantenedores

Desde la raíz del repositorio, ejecutá:

```bash
python scripts/check_pwa.py
python scripts/check_host_assets.py
```

GitHub Actions ejecuta las tres comprobaciones en los commits y pull requests. Si se reemplaza un archivo de una ruta habilitada, actualizá `asset-manifest.json` con su tamaño y Git blob SHA-1 y luego actualizá el pin y el tamaño del manifiesto en `index.html`. No habilites una ruta solamente porque sus archivos existan: primero verificá su procedencia y compatibilidad en hardware real.

## Estructura

- `index.html`: launcher y comprobación previa.
- `asset-manifest.json`: tamaños y hashes Git blob de los archivos de rutas habilitadas.
- `cache.html`: preparación de la caché local.
- `sw.js`: gestión versionada de archivos offline.
- `700/`, `900/`, `css/` y `patches/`: motores y archivos por ruta.
- `scripts/`: validaciones estáticas ejecutadas por CI.
- `THIRD_PARTY_NOTICES.md`: notas de procedencia y licencias de terceros.

## Licencia y redistribución

Este repositorio no declara una licencia general. La ausencia de un archivo LICENSE no concede permiso para reutilizar o redistribuir el contenido. Consultá `THIRD_PARTY_NOTICES.md` y confirmá las licencias y condiciones de cada componente antes de publicar copias o derivados.
