# 1. Introducción
## D1n0 - Alejandro Maman INSO3A U-TAD - 2025/2026

### Estructura de una organización
```
Internet <---> Firewall <---> DMZ con servidores <---> Red interna <---> Proveedores / pre.company.corp
```

### Red Team
Consiste en la simulación de un ataque dirigido sobre una determinada organización, utilizando para ello las mismas **Técnicas, Tácticas y Procedimientos (TTPs)** que seguiría un atacante real.

El objetivo es **comprobar** cuál es el nivel de exposición, riesgo e impacto que tendría sobre una entidad. A su vez, verificar las capacidades de detección y respuesta existentes por parte del Blue Team.

### Resumen general
Cualquier ejercicio está compuesto de tres objetivos:
- Verificar la **exposición del objetivo** y la posibilidad de crear un vector de acceso
- Verificar la **capacidad de compromiso interno**, nivel de madurez e impacto real del ataque
- Verificar la **capacidad real de preparación** frente a un incidente (detección y respuesta)

### Ámbitos de actuación
- **Digital**: Activos con interacción digital (sistemas en Internet, redes Wi-Fi, etc.)
- **Física**: Activos con interacción física (videovigilancia, control de acceso, guardias, etc.)
- **Humana**: Personas de la organización (phishing, vishing, acceso físico, etc.)

Es importante que donde esté permitido se busque crear vectores que combinen diferentes ámbitos.

### Modelado de amenaza y acceso
- **Threat model**: Determina qué tipología de atacante se va a simular.
- **Breach model**: Se recomienda dedicar entre un **25% y 50%** del tiempo a la búsqueda del vector de acceso, y el resto a la intrusión interna.

### Equipos involucrados
- **Red Team**: Equipo ofensivo externo, sin conocimiento previo de la entidad.
- **Blue Team**: Equipo de seguridad interno (prevención, detección, respuesta).
- **White Team**: Personas internas que conocen el ejercicio (perfiles de alto nivel, auditoría).
- **Purple Team**: Equipo mixto (ofensivo + interno). Aporta rapidez pero no es caja negra pura.

### Pensamiento crítico
En muchos casos es más importante crear vectores imaginativos que explotar vulnerabilidades:
- Enumeración de usuarios mediante redes Wi-Fi
- Pruebas de fuerza bruta en redes WPA2-Enterprise
- Identificación de usuario interno → uso en VPN
- Visibilidad con la infraestructura interna

### Condiciones necesarias
- Desconocimiento del ejercicio dentro de la organización (especialmente el Blue Team)
- Ocultación del origen de las pruebas del Red Team
- Evitar en todo momento la detección
- Creación de vectores realistas y combinados
- Profundidad de la intrusión y demostración de impacto

### Medición de capacidades de detección y respuesta
Se pueden plantear **baterías de pruebas controladas** para identificar el nivel de agresividad necesario para que salten alertas, y analizar posteriormente la respuesta al incidente y capacidades forenses.

### Beneficios del Red Team
- Identificación de vectores de ataque críticos
- Evaluación del nivel de exposición y riesgo
- Evaluación de capacidades de prevención, detección y respuesta
- Identificación de principales vulnerabilidades y debilidades
- Ampliar las capacidades del Blue Team

### Siempre hay un Blue Team — aspectos a recordar
- Existencia de monitorización entre subredes internas
- Monitorización del tráfico de salida (proxies)
- Antivirus en la mayoría de equipos internos
- Herramientas que monitoricen cambios en el AD
- Honeypots en sistemas, redes y AD
- Evitar la creación o alteración de recursos locales

---

## Infraestructura

### Infraestructura básica
Diferenciación según objetivo:
- **Plataforma de anonimato**: TOR, VPN (pública/privada/anónima), VPS (normales/anónimos)
- **Plataforma de enumeración**: VPN + VPS normales + VPS anónimos
- **Plataforma de intrusión**: VPS normales/anónimos según el activo objetivo
- **Plataforma de persistencia**: VPS como receptores + Cloud como IP Laundry (redirectores) + dominios (Domain Fronting)

### Aspectos destacados de VPS
- Establecer medidas básicas (usuario sin shell, SSH con certificado)
- Contar con un VPS propio/confiable desde donde saltar a los otros
- Usar VPS en diferentes países (preferiblemente enfrentados)
- Establecer **kill-switch** para evitar salida de paquetes si cae la VPN
- Contratar los VPS "chungos" de forma mensual

---

## Tunelización y saltos

### Técnicas de tunelización
Consiste en introducir un protocolo dentro de otro. Protocolos soportados: **DNS, UDP, SSH, ICMP**, etc.

### Creación de túneles SSH
```bash
# Túnel dinámico (SOCKS proxy)
ssh -D <puerto local> <usuario>@<IP servidor>

# Túnel local
ssh -L <p.local>:<maquina objetivo>:<p.objetivo> <usuario>@<IP servidor>
```
Luego configurar `proxychains` para usar el puerto local levantado.

### Múltiples túneles SSH (encadenados)
```bash
# Túnel local de Kali al servidor intermedio
ssh -L <p.local>:127.0.0.1:<p.objetivo> <usuario>@<IP servidor>

# Desde la máquina intermedia, túnel al destino final
ssh -D <p.objetivo> <usuario>@<IP servidor final>
```

### SSH + TOR
```bash
service tor start
nano proxychains.conf  # cambiar última línea: socks5 127.0.0.1 9050
proxychains ssh -D <puerto local> <usuario>@<IP servidor>
```

---

## Técnicas avanzadas

### Uso de dominios (Phishing / Persistencia / Exfiltración)
- Similares al de la entidad
- Haber caducado recientemente (pueden estar categorizados)
- Servicio de dominios expirados: http://expireddomains.net/
- Las acciones de ingeniería social se desarrollan de forma manual, no automática

### Visual Spoofing (Homoglyph Attack)
Uso de Unicode para engañar visualmente en la interpretación de un dominio. Caracteres de diferentes idiomas que son visualmente idénticos.
- Generador: http://www.irongeek.com/homoglyph-attack-generator.php

### Domain Fronting
Uso de proveedores como Amazon, Google o Azure para ocultar la IP real de los VPS. Útil para recepción de persistencia desde la máquina comprometida hacia servicios confiables.
- https://cloud.google.com/appengine/
- https://aws.amazon.com/cloudfront/
- https://azure.microsoft.com/

---
