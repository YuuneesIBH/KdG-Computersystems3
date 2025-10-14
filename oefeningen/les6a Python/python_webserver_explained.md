# Les 6 Python - Webserver Opdracht Uitleg

## Overzicht

Deze les behandelt het maken van een eenvoudige webserver in Python3 met behulp van de `http.server` module. We bouwen stapsgewijs een webserver uit met verschillende functionaliteiten.

## Benodigde Modules

### Standaard Python Modules
- **http.server**: Voor het opzetten van een HTTP server
  - `BaseHTTPRequestHandler`: Basis class voor request handling
  - `HTTPServer`: De eigenlijke server implementatie
- **mimetypes**: Voor het automatisch detecteren van bestandstypes
- **os**: Voor bestandssysteem operaties en controles
- **psutil**: Voor systeeminformatie (moet geïnstalleerd worden)

### Extra Module Installatie
```bash
sudo pip3 install psutil
```

---

## Stap 1 & 2: Basis Webserver op 127.0.0.1

### Code Uitleg

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Deze methode wordt aangeroepen bij elke GET request
        if self.path == "/index.html" or self.path == "/":
            try:
                with open("index.html", "r") as f:
                    content = f.read()
                
                self.send_response(200)  # HTTP status code: OK
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())
            except FileNotFoundError:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "File not found")

def run():
    server_address = ("127.0.0.1", 1234)  # Localhost, poort 1234
    httpd = HTTPServer(server_address, MyHandler)
    print("Server draait op http://127.0.0.1:1234")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
```

### Belangrijke Concepten

- **127.0.0.1**: Localhost IP-adres (alleen toegankelijk vanaf eigen machine)
- **Poort 1234**: Poorten onder 1024 vereisen root rechten, daarom kiezen we 1234
- **do_GET()**: Methode die alle GET requests afhandelt
- **self.path**: Bevat het gevraagde pad (bijv. "/index.html")
- **encode()**: Converteert string naar bytes voor verzending

---

## Stap 3: Meerdere Bestandstypes met MIME-types

### Code Uitleg

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import os

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Bepaal bestandsnaam uit het pad
        filename = self.path.strip("/")
        if filename == "":
            filename = "index.html"
        
        if os.path.exists(filename):
            # Automatisch MIME-type detecteren
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                mime_type = "application/octet-stream"
            
            try:
                # Open in binary mode voor alle bestandstypes
                with open(filename, "rb") as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header("Content-type", mime_type)
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Server error: {e}")
        else:
            self.send_error(404, "File not found")
```

### MIME-type Voorbeelden

| Extensie | MIME-type | Beschrijving |
|----------|-----------|--------------|
| .html | text/html | HTML pagina |
| .txt | text/plain | Platte tekst |
| .jpg/.jpeg | image/jpeg | JPEG afbeelding |
| .png | image/png | PNG afbeelding |
| .css | text/css | Stylesheet |
| .js | application/javascript | JavaScript |
| .pdf | application/pdf | PDF document |

### Waarom Binary Mode ("rb")?

- Tekst bestanden kunnen als string worden gelezen
- Afbeeldingen, PDF's en andere binaire bestanden moeten in binary mode
- **"rb"** werkt voor beide types, daarom gebruiken we dit altijd

---

## Stap 4: Client IP-adres Controle

### Code Toevoeging

```python
def do_GET(self):
    # Haal client IP-adres op
    client_ip = self.client_address[0]
    
    # Controleer of client localhost is
    if client_ip != "127.0.0.1":
        self.send_error(404, f"Access denied for {client_ip}")
        return
    
    # Rest van de code...
```

### Beveiligingsconcepten

- **self.client_address**: Tuple met (IP-adres, poort nummer)
- **[0]**: Eerste element is het IP-adres
- **Toegangscontrole**: Alleen localhost kan de server bereiken
- **404 vs 403**: We gebruiken 404 (niet gevonden) in plaats van 403 (verboden) om de server te "verbergen"

---

## Stap 5: Proces Lijst met psutil

### Voorbeeld Implementatie

```python
import psutil

def do_GET(self):
    if self.path == "/ps.cgi":
        try:
            # Genereer HTML met proceslijst
            html = "<html><head><title>Process List</title></head><body>"
            html += "<h1>Actieve Processen</h1><table border='1'>"
            html += "<tr><th>PID</th><th>Naam</th><th>CPU%</th><th>Memory%</th></tr>"
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    html += f"<tr>"
                    html += f"<td>{info['pid']}</td>"
                    html += f"<td>{info['name']}</td>"
                    html += f"<td>{info['cpu_percent']:.1f}%</td>"
                    html += f"<td>{info['memory_percent']:.1f}%</td>"
                    html += f"</tr>"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            html += "</table></body></html>"
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_error(500, f"Error: {e}")
```

### psutil Functionaliteit

- **process_iter()**: Iterator over alle processen
- **['pid', 'name', ...]**: Welke informatie we willen ophalen
- **NoSuchProcess**: Exception als proces stopt tijdens iteratie
- **AccessDenied**: Exception bij onvoldoende rechten
- **CPU & Memory percentage**: Real-time resource gebruik

---

## Stap 6: Bestandslijst Directory

### Code Voorbeeld

```python
import os

def do_GET(self):
    if self.path == "/files":
        try:
            files = os.listdir(".")
            
            html = "<html><head><title>File List</title></head><body>"
            html += "<h1>Bestanden in Directory</h1><ul>"
            
            for file in files:
                html += f"<li><a href='/{file}'>{file}</a></li>"
            
            html += "</ul></body></html>"
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception as e:
            self.send_error(500, f"Error: {e}")
```

### OS Module Functies

- **os.listdir(".")**: Lijst van bestanden in huidige directory
- **os.path.exists()**: Controleer of bestand/directory bestaat
- **os.path.isfile()**: Is het een bestand?
- **os.path.isdir()**: Is het een directory?

---

## Stap 7 & 8: GUI met EasyGUI

### Installatie

```bash
sudo apt-get install python3-easygui python3-pip
pip3 install easygui
```

### Apache Control Panel Code

```python
import os
import easygui

def apache_status():
    """Haal Apache status op"""
    result = os.popen("systemctl status apache2 | grep Active").read()
    return result.strip() if result else "Geen status gevonden."

def main():
    while True:
        # Haal huidige status op
        status = apache_status()
        
        # Toon buttonbox met status en keuzes
        choice = easygui.buttonbox(
            msg=f"Apache status:\n\n{status}\n\nWat wil je doen?",
            title="Apache Control Panel",
            choices=["Start Apache", "Stop Apache", "Exit"]
        )
        
        # Verwerk keuze
        if choice == "Start Apache":
            os.system("sudo systemctl start apache2")
        elif choice == "Stop Apache":
            os.system("sudo systemctl stop apache2")
        elif choice == "Exit":
            break

if __name__ == "__main__":
    main()
```

### EasyGUI Componenten

- **buttonbox()**: Toont dialoog met knoppen
  - `msg`: Bericht om te tonen
  - `title`: Titel van het venster
  - `choices`: Lijst van knop labels
- **msgbox()**: Eenvoudige melding
- **enterbox()**: Tekst input
- **choicebox()**: Selectie uit lijst

### Systeem Commando's

- **os.popen()**: Voer commando uit en lees output
- **os.system()**: Voer commando uit (geen output terug)
- **systemctl start/stop/status**: Systemd service management

---

## Testing de Webserver

### Met Lynx (Terminal Browser)

```bash
# Test basis pagina
lynx http://127.0.0.1:1234/

# Test specifiek bestand
lynx http://127.0.0.1:1234/index.html
lynx http://127.0.0.1:1234/index.txt

# Test afbeelding (toont metadata)
lynx http://127.0.0.1:1234/image.jpg

# Test proceslijst
lynx http://127.0.0.1:1234/ps.cgi
```

### Met cURL (Debugging)

```bash
# Toon headers en content
curl -i http://127.0.0.1:1234/index.html

# Alleen headers
curl -I http://127.0.0.1:1234/index.html

# Test van externe IP (moet falen)
curl -i http://[jouw-externe-ip]:1234/
```

---

## HTTP Status Codes

### Veel Gebruikte Codes

| Code | Naam | Betekenis |
|------|------|-----------|
| 200 | OK | Succesvol |
| 404 | Not Found | Bestand niet gevonden |
| 403 | Forbidden | Geen toegang |
| 500 | Internal Server Error | Server fout |
| 301 | Moved Permanently | Permanent verplaatst |
| 302 | Found | Tijdelijk verplaatst |

---

## Beveiliging Overwegingen

### 1. IP-adres Filtering
- Beperk toegang tot localhost
- Voorkom externe toegang tot gevoelige informatie

### 2. Path Traversal Attacks
```python
# GEVAARLIJK - kwetsbaar voor path traversal
filename = self.path

# BETER - valideer en beperk pad
filename = os.path.basename(self.path.strip("/"))
if ".." in filename:
    self.send_error(403, "Access denied")
    return
```

### 3. File Permissions
- Server moet alleen lezen kunnen, niet schrijven
- Draai server als gewone gebruiker (niet root)

### 4. Error Messages
- Toon geen gedetailleerde foutmeldingen aan clients
- Log gedetailleerde fouten server-side

---

## Veelgemaakte Fouten

### 1. Poort Al in Gebruik
```
OSError: [Errno 98] Address already in use
```
**Oplossing**: Stop andere server of kies andere poort

### 2. Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Oplossing**: Controleer bestandsrechten of draai met sudo (voor poorten < 1024)

### 3. Module Not Found
```
ModuleNotFoundError: No module named 'psutil'
```
**Oplossing**: `pip3 install psutil`

### 4. Encoding Errors
```
TypeError: a bytes-like object is required, not 'str'
```
**Oplossing**: Gebruik `.encode()` voor strings naar bytes conversie

---

## Best Practices

### 1. Code Organisatie
- Scheid concerns: routing, file handling, response generation
- Gebruik functies voor herbruikbare logica
- Houd request handler methods kort

### 2. Error Handling
- Gebruik try-except blokken
- Log fouten voor debugging
- Geef duidelijke error responses

### 3. Resource Management
- Gebruik `with` statement voor bestanden
- Sluit resources netjes af
- Beperk memory gebruik bij grote bestanden

### 4. Testing
- Test alle endpoints
- Test error scenarios
- Test met verschillende browsers/clients

---

## Uitbreidingen en Extra Oefeningen

### 1. POST Request Support
Voeg formulier support toe met `do_POST()` methode

### 2. Session Management
Implementeer cookies voor gebruikerssessies

### 3. Template Engine
Gebruik Jinja2 voor dynamische HTML generatie

### 4. Database Integratie
Koppel SQLite database voor data opslag

### 5. Authentication
Voeg basic authentication toe met headers

---

## Referenties

- [Python http.server Documentation](https://docs.python.org/3/library/http.server.html)
- [Python BaseHTTPServer Wiki](http://wiki.python.org/moin/BaseHttpServer)
- [EasyGUI Tutorial](http://easygui.sourceforge.net/tutorial.html)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

## Samenvatting

In deze les hebben we geleerd:

1. ✅ Een basis webserver opzetten op localhost
2. ✅ HTML bestanden serveren
3. ✅ Meerdere bestandstypes ondersteunen met MIME-types
4. ✅ Client IP-adres controle implementeren
5. ✅ Systeeminformatie tonen met psutil
6. ✅ Bestandslijsten genereren
7. ✅ GUI maken met EasyGUI voor service management
8. ✅ Apache webserver besturen via Python GUI

Deze concepten vormen de basis voor webontwikkeling en server-side scripting in Python.