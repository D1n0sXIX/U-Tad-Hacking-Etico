# 2. Reconocimiento de activos
## D1n0 - Alejandro Maman INSO3A U-TAD

### Introducción
Objetivo: mapear todos los activos e información posible. Ámbitos:
- **Perímetro**: activos expuestos en Internet
- **Wi-Fi**: redes y clientes
- **Ingeniería Social**: empleados
- **Físico**: medidas de seguridad físicas

### Identificación de activos en perímetro
- Infraestructura de red pública
- Infraestructura en Cloud
- Dominios y subdominios
- Servicios habilitados
- Aplicaciones web

### Análisis general de la compañía
Identificar: nombres anteriores, nombres en otros países, filiales, proveedores. Usar Wikipedia, noticias, web propia.

### Metodología para grandes empresas
Ciclo: **Sistemas autónomos → Rangos de red → Dominios → Subdominios → Superficie de ataque**

### Identificación de sistemas autónomos (ASN)
- Consultas a RIRs: https://whois.arin.net
- BGP Hurricane: http://bgp.he.net/

### Identificación de rangos de red
- WhoisXMLapi (Reverse IP Netblocks): https://ip-netblocks.whoisxmlapi.com/api
- Amass:
```bash
amass intel -org <organizacion>
```

### Identificación de dominios
- **Reverse CIDR/PTR**: IPIP, WhoisXMLapi, Bgp.tools
- **Reverse Whois**: WhoisXMLapi (busca dominios que contengan una palabra en su Whois)
- **Reverse NS/MX** (ViewDNS): dominios que comparten servidor de nombres/correos
  - https://viewdns.info/reversens/
  - https://viewdns.info/reversemx/

### Identificación de subdominios
- Servicios públicos: WhoisXMLAPI, Spyse, Omnisint
- Resolución inversa: ViewDNS
- Certificados: Shodan, crt.sh, Censys
- Otros: DNSdumpster, VirusTotal, Google Transparency
- Fuerza bruta activa: subscan, massdns, altdns
- Google Hacking

Herramientas automáticas: **amass**, **subfinder**

```bash
# Amass con fuentes
amass enum -d <dominio> -src
amass enum -passive -d <dominio> -src
```

Diccionario recomendado para brute force:
https://github.com/danielmiessler/SecLists/blob/master/Discovery/DNS/bitquark-subdomains-top100000.txt

### Identificación de infraestructura Cloud
```bash
# cloud_enum: https://github.com/initstring/cloud_enum
```

### Enumeración de la superficie de ataque
- Enumeración pasiva de puertos: Shodan
- Enumeración activa: Nmap, Masscan
- Identificación de apps web + capturas de pantalla: **GoWitness / EyeWitness**
- Identificación de tecnologías
- Identificación automatizada de vulnerabilidades: **Nuclei**
```bash
eyewitness -f <lista apps> --web --prepend-https
```

---

## Reconocimiento Wi-Fi

### Proceso de enumeración
1. Identificación de localizaciones (sedes, CPDs, oficinas, sucursales)
2. Enumeración pasiva (online, wigle.net)
3. Enumeración activa (Aircrack-ng)
4. Preparación de infraestructura

### Posibles vectores Wi-Fi
- Vulnerabilidades sobre redes **WEP** (captura + cracking)
- Vulnerabilidades sobre redes **WPA/WPA2** (captura de handshake)
- Ataques contra clientes en redes **WPA2-Enterprise** (dispositivos sin MDM o sin certificado)
- Ataques en redes **Open** (visibilidad interna por incorrecta segmentación)
- Fake AP + ingeniería social

---

## Reconocimiento de personal (Ingeniería Social)

### Estructuras de correo habituales
- `<inicial><apellido>@empresa.com`
- `<nombre>_<apellido>@empresa.com`
- `<nombre>.<apellido>@empresa.com`

### CrossLinked
Automatiza la extracción de empleados de LinkedIn indexados en Google/Bing.
```bash
python3 crosslinked.py -f '{first}.{last}@<dominio>' <empresa>
python3 crosslinked.py -f '{first}.{last}@bbva.es' bbva
```

### Perfiles objetivo (más susceptibles)
- Personas ajenas a la tecnología (RRHH, abogados)
- Personas mayores
- Empleados nuevos
- Sin cargo intermedio ni directivo

### Vectores de ingeniería social
- **Phishing**: obtención de credenciales por correo, sin malware, difícil de detectar
- **Malware por correo**: adjunto malicioso, compromiso remoto
- **Malware en USB**: dispositivo dejado en las proximidades
- **Vishing**: llamada para obtener credenciales o dar soporte a otro ataque

---

## Reconocimiento físico

### Objetivos de la intrusión física
- Infección de equipo interno
- Despliegue de implante hardware (Raspberry Pi + módulo 4G)
- Acceso a zonas sensibles (CPD)
- Obtención de información interna
- Robo de dispositivos (PCs, USBs)

### Información a obtener
- Posibles accesos al edificio
- Medidas de seguridad física
- Detalles del control de acceso
- Análisis de guardias de seguridad

### Posibles vectores físicos
- Puertas sin control de acceso
- RFID/NFC no robusto
- Ingeniería social con empleados
- Lograr un acceso legítimo (entrevista, visita)

---