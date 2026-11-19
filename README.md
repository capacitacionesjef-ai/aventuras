# Terreneitor

Un catálogo de planes de fin de semana para regalar. `Catalogo.xlsx` es la fuente de las tarjetas y de las fichas. Los precios, horarios y demás datos sin confirmar se muestran como pendientes.

## Activar GitHub Pages

1. Descomprime el ZIP y coloca el contenido de la carpeta `terreneitor-regalo` en la raíz de un repositorio con rama `main`. Incluye la carpeta oculta `.github`. Si usas otra rama, cambia el nombre de rama en `.github/workflows/publicar.yml`.
2. En el repositorio, entra a **Settings → Pages** y selecciona **GitHub Actions** en **Source**.
3. En **Actions**, abre **Publicar Terreneitor** y ejecuta **Run workflow** para iniciar la primera publicación si el envío inicial ocurrió antes de habilitar Pages. Al terminar, abre el enlace que aparece en el despliegue.

Si eliges un repositorio público, comparte únicamente fotos y contactos aptos para publicación. El sitio desplegado publica las fichas y sus imágenes.

## Añadir una salida o actualizar una ficha

1. Abre `Catalogo.xlsx`, hoja **Actividades**. Añade una fila debajo de las existentes. Usa un **ID** único y estable, por ejemplo `sendero-bonao`. Completa **Actividad**, **Destino** y **Descripción**. Mantén los encabezados.
2. En **Fotos**, pega enlaces HTTPS directos a imágenes o escribe rutas como `fotos/nueva-salida.jpg` y sube esas fotos a `recursos/fotos/`. Para varias fotos, coloca una ruta o enlace por línea dentro de la misma celda.
3. Completa contacto, ubicación, precio por persona, horario, duración, reserva, qué llevar y requisitos a medida que los confirmes. Ubicación y Reserva aceptan texto o un enlace HTTPS. Los teléfonos dominicanos de diez dígitos se publican con prefijo +1 en el enlace de llamada.
4. Guarda y sube el Excel actualizado a **main** con el mismo nombre. GitHub reconstruye y publica la web automáticamente. Los cambios guardados solo en tu computadora se publican cuando subes el archivo al repositorio. Si hay un error de validación, consulta la fila indicada en **Actions**, corrígela y vuelve a subir el Excel.

## Probar en tu computadora

Ejecuta `python -m pip install -r requirements.txt` y `python generar.py`. Abre `_site/index.html` en el navegador.
