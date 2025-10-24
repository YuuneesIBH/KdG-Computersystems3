# AppArmor Security Tutorial - Uitleg

## Wat is AppArmor?

AppArmor is een **Mandatory Access Control (MAC)** beveiligingssysteem voor Linux. Het werkt als een extra beveiligingslaag bovenop de normale Linux bestandspermissies. AppArmor beperkt wat programma's kunnen doen door middel van **profielen**.

### Kernconcepten

- **Profile**: Een set regels die bepaalt wat een programma wel/niet mag doen
- **Enforce mode**: Het profiel wordt actief afgedwongen - verboden acties worden geblokkeerd
- **Complain mode**: Het profiel logt overtredingen maar blokkeert ze niet (voor testen)
- **Unconfined**: Geen AppArmor-beperkingen actief

## Oefening Overzicht

In deze oefening hebben we twee programma's beveiligd:
1. **getstuff** - Een mono/.NET programma dat httpserver.py downloadt
2. **httpserver** - Een Python webserver op localhost:1234

## Stap-voor-Stap Analyse

### Stap 1: Installatie en Setup

```bash
# Installeer benodigde software
sudo apt install apparmor apparmor-utils auditd mono-complete python3 -y

# Controleer AppArmor status
sudo aa-status
```

**Belangrijke directories volgens REF1 (Mono best practices):**
- `/usr/lib/getstuff/` - Hier komt het eigenlijke programma
- `/usr/bin/getstuff` - Wrapper script dat het programma start

Deze structuur scheidt:
- **Executable code** (in /usr/lib/)
- **User commands** (in /usr/bin/)

### Stap 2: AppArmor Profiel Aanmaken

```bash
sudo aa-genprof /usr/bin/getstuff
```

**Wat gebeurt er?**

1. AppArmor zet het programma in **complain mode**
2. Je start het programma in een andere terminal
3. AppArmor **loggt alle systeemaanroepen** in `/var/log/audit/audit.log`
4. Je scant de logs en besluit wat toegestaan wordt

**Belangrijke keuze bij "Execute: /usr/bin/mono-sgen":**

De opties betekenen:
- **(I)nherit** - Mono draait met hetzelfde profiel als getstuff
- **(C)hild** - Mono krijgt zijn eigen sub-profiel
- **(P)rofile** - Gebruik een bestaand systeem-profiel
- **(X) ix On** - Inherit execution (mix van inherit en execute)
- **(U)nconfined** - Mono draait zonder beperkingen

### Stap 3: Root kan niet meer downloaden

**Wat testen we?**

```bash
sudo su
cd /root
/usr/bin/getstuff  # Dit faalt!
```

**Waarom faalt het?**

Als je kijkt naar de audit logs:

```
apparmor="DENIED" operation="open" name="/usr/local/sbin/" 
apparmor="DENIED" operation="open" name="/etc/mono/config"
apparmor="DENIED" operation="mknod" name="/dev/shm/mono.5804"
```

Het programma probeert:
- Directories te lezen in `/usr/local/sbin/`, `/usr/bin/`, etc.
- Mono configuratie te lezen (`/etc/mono/config`)
- Temp files aan te maken in `/dev/shm/`

**Al deze acties worden geblokkeerd** omdat ze niet in het profiel staan!

### Stap 4: Root toegang geven tot /root

**Oplossing:** Het profiel uitbreiden

```bash
sudo vi /etc/apparmor.d/usr.bin.getstuff
```

Voeg toe:

```
/root/** rw,
```

Dit betekent:
- `/root/**` - Alle bestanden onder /root (recursief)
- `rw` - Read + Write toegang

**Andere rechten die we gaven:**

```
capability sys_nice,           # Procesplanning aanpassen
owner /usr/local/sbin/ r,      # Lees directories
owner /etc/mono/config r,      # Lees mono config
include <abstractions/audio>   # Voor /dev/shm/ toegang
owner /dev/shm/mono.* w,       # Temp files aanmaken
```

**Let op de patronen:**
- `mono.5804` wordt `mono.*` - Om procesID's te matchen
- `owner` keyword - Alleen de eigenaar (root) krijgt toegang

### Stap 5 & 6: HTTPServer Beveiligen

**Setup:**

```bash
# Wrapper script
sudo tee /usr/bin/httpserver > /dev/null << 'EOF'
#!/bin/bash
python3 /usr/lib/getstuff/httpserver.py
EOF

sudo chmod +x /usr/bin/httpserver
```

**Profiel aanmaken:**

```bash
sudo aa-genprof /usr/bin/httpserver
```

**Belangrijke keuze: "Execute: /usr/bin/python3.10"**

Je moet kiezen hoe Python wordt uitgevoerd. Voor een webserver:
- **(C)hild** - Python krijgt een sub-profiel (meest restrictief)
- **(I)nherit** - Python deelt het profiel met httpserver

## Belangrijke Beveiligingsconcepten

### 1. Principle of Least Privilege

AppArmor volgt het principe: **geef alleen de minimale rechten die nodig zijn**.

**Voorbeeld uit de oefening:**
- Gewone gebruikers kunnen getstuff uitvoeren vanuit hun home directory
- Root kan het alleen uitvoeren als we expliciet `/root/** rw` toevoegen
- Zonder dat profiel-regel kan zelfs root niet downloaden!

### 2. Temp Files en PID's

**Probleem:** Temp files bevatten vaak proces-ID's:
```
/dev/shm/mono.5804
/dev/shm/mono.8269
```

**Oplossing:** Gebruik wildcards:
```
owner /dev/shm/mono.* w,
```

### 3. Abstractions

AppArmor heeft herbruikbare profiel-fragmenten:

```
include <abstractions/base>      # Basis systeemtoegang
include <abstractions/bash>      # Voor bash scripts
include <abstractions/consoles>  # Voor terminal toegang
include <abstractions/audio>     # Voor /dev/shm/ toegang
```

**Voordeel:** Je hoeft niet alles handmatig te specificeren!

### 4. Modes van Executie

Bij het starten van andere programma's:

| Mode | Betekenis | Gebruik |
|------|-----------|---------|
| `ix` | Inherit, maar discrete profiel check | Scripts die helper commands aanroepen |
| `px` | Nieuw profiel, strikt gescheiden | Privilege escalation voorkomen |
| `ux` | Unconfined, geen AppArmor | Legacy software (gevaarlijk!) |
| `Cx` | Child profiel, deel van parent | Sub-componenten |

**In de oefening:**
```
/usr/bin/mono-sgen mrix,
```
- `m` = Allow memory mapping executable
- `r` = Read toegang
- `i` = Inherit execution
- `x` = Execute toegang

## Audit Logs Lezen

**Voorbeeld uit de oefening:**

```
type=AVC msg=audit(1761308692.016:566): 
  apparmor="DENIED" 
  operation="open" 
  profile="/usr/bin/getstuff" 
  name="/usr/local/sbin/" 
  requested_mask="r" 
  denied_mask="r" 
  fsuid=0 
  ouid=0
```

**Analyse:**
- `apparmor="DENIED"` - Actie geblokkeerd
- `operation="open"` - Probeerde een bestand te openen
- `name="/usr/local/sbin/"` - Welk bestand/directory
- `requested_mask="r"` - Wilde lezen
- `denied_mask="r"` - Lezen werd geweigerd
- `fsuid=0` - Door root gebruiker

## Praktische Tips

### Profiel Opnieuw Maken

```bash
# Verwijder bestaand profiel
sudo rm /etc/apparmor.d/usr.bin.getstuff

# Start opnieuw
sudo aa-genprof /usr/bin/getstuff
```

### Profile Status Bekijken

```bash
sudo aa-status
```

Output toont:
- Hoeveel profielen in enforce/complain mode
- Welke processen actief geconfined zijn

### Handmatig Profiel Bewerken

```bash
sudo vi /etc/apparmor.d/usr.bin.getstuff
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.getstuff  # Herlaad
```

### Van Complain naar Enforce

```bash
sudo aa-enforce /usr/bin/getstuff
```

## Security Lessons

### Lesson 1: Root is niet alles

**Traditioneel Linux:** Root kan alles.

**Met AppArmor:** Zelfs root wordt beperkt door profielen!

In stap 3 kon root niet downloaden ondanks volledige systeemrechten.

### Lesson 2: Defense in Depth

AppArmor is een **extra laag** bovenop:
- User/group permissions (chmod, chown)
- SELinux/AppArmor (MAC)
- Firewalls (netwerk niveau)
- Sudo policies (privilege escalation)

### Lesson 3: Test grondig

De oefening benadrukt:
- Test als **gewone gebruiker** én als **root**
- Test vanuit **verschillende directories**
- Test **alle functionaliteit** (zoals browser access voor httpserver)

## Veelgemaakte Fouten

### 1. Te Ruime Rechten

❌ **Fout:**
```
/** rwx,  # Alles toegankelijk!
```

✅ **Goed:**
```
/home/*/** rw,        # Alleen home directories
/root/** rw,          # Alleen /root voor root
owner /tmp/myapp.* w, # Alleen eigen temp files
```

### 2. Wildcards Vergeten

❌ **Fout:**
```
/dev/shm/mono.5804 w,  # Werkt alleen voor dit PID!
```

✅ **Goed:**
```
owner /dev/shm/mono.* w,  # Werkt voor alle PIDs
```

### 3. Owner Keyword Vergeten

Zonder `owner` kunnen **alle gebruikers** het bestand benaderen:

```
/tmp/sensitive.txt rw,        # Iedereen!
owner /tmp/sensitive.txt rw,  # Alleen eigenaar
```

## Conclusie

**AppArmor biedt:**
- ✅ Extra beveiligingslaag zelfs voor root
- ✅ Beperking van programma's tot strict noodzakelijke rechten
- ✅ Detectie van onverwacht gedrag
- ✅ Logging van beveiligingsgebeurtenissen

**Deze oefening demonstreert:**
- Hoe je profielen interactief aanmaakt met `aa-genprof`
- Het belang van grondig testen (verschillende gebruikers/scenarios)
- Het gebruik van abstractions en patterns (wildcards)
- Dat zelfs root beperkt kan worden door MAC systemen

**Best Practice:** Start altijd in complain mode, test uitgebreid, en schakel pas daarna over naar enforce mode!