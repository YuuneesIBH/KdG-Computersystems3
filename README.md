# 📚 Examenprep - CS3 Computerssystemen

Volledige examenprepository voor het vak **Computerssystemen 3** met alle oplossingen, labo's en theorie.

---

## 📂 Repository Structuur

```
examenprep/
├── 📁 oplossingen/           # Uitgewerkte examenvragen
│   ├── cs3-exdef.md         # Examen definitieve versie
│   ├── exam_prep.md         # Examen voorbereiding guide
│   └── uitgevoerde_commands.txt
├── 📁 cs3examen.txt         # Examenvragen lijst
├── 📁 mogelijke_examenvragen_2025.txt
├── 📁 oefeningen/           # Praktische oefeningen per onderwerp
│   ├── Les1 - Linux Tuning
│   ├── Les2 - Deb
│   ├── Les3 - DNS
│   ├── Les4 - LVM
│   ├── Les5 - portscan
│   ├── Les6 - TLS
│   ├── Les6a - Python
│   ├── Les6b - scapy
│   ├── Les7 - AppArmor
│   ├── Les8 - Ansible
│   └── Les9 - Nagios
└── 📁 theorie/              # Theoretische documenten
    ├── Handige_Theorie-CS3-ISB.pdf
    └── virtualization_quiz.html
```

---

## 🎯 Examenlabo's (Belangrijkste onderdelen)

### 🔒 Labo 1: HTTPS met Easy-RSA
**Doel:** TLS-certificaat configureren voor `https://web.uwachternaam.local`

**Kernpunten:**
- Easy-RSA installatie en PKI setup
- CA (Certificate Authority) aanmaken
- Servercertificaat genereren en ondertekenen
- Apache SSL configuratie
- Firefox certificaat import

**Zie:** `oplossingen/cs3-exdef.md` → Examenlabo 1

---

### ⚙️ Labo 2: Ansible Role - Pure-FTPd
**Doel:** Complete Ansible role met template en handlers

**Kernpunten:**
- Ansible role structuur (`ansible-galaxy role init`)
- Pure-FTPd installatie
- vsftpd en proftpd-core verwijderen
- Custom banner via Jinja2 template
- Handler voor service restart
- ansible-lint compliance

**Zie:** `oplossingen/cs3-exdef.md` → Examenlabo 2

---

## 🚀 Quick Start

### Examenlabo 1 - HTTPS opzetten

```bash
# 1. Installeer Easy-RSA
sudo apt install easy-rsa -y

# 2. Setup PKI
mkdir ~/easy-rsa && cd ~/easy-rsa
cp -r /usr/share/easy-rsa/* .
./easyrsa init-pki
./easyrsa build-ca nopass

# 3. Certificaat maken
./easyrsa gen-req web.achternaam.local nopass
./easyrsa sign-req server web.achternaam.local

# 4. Apache SSL configureren
# Zie complete guide in oplossingen/cs3-exdef.md
```

### Examenlabo 2 - Ansible FTP Role

```bash
# 1. Installeer vereisten
sudo apt update
sudo apt install -y ansible ansible-lint git

# 2. Maak role structuur
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles
cd ~/ACHTERNAAM-VOORNAAM/roles
ansible-galaxy role init ACHTERNAAM-pure-ftpd

# 3. Configureer role
# Gebruik de sudo tee commando's uit cs3-exdef.md

# 4. Run playbook
cd ~/ACHTERNAAM-VOORNAAM
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml

# 5. Test FTP
ftp localhost
# Verwacht: 220-FTP server ACHTERNAAM
```

---

## 📖 Lessen & Oefeningen

| Les | Onderwerp | Beschrijving |
|-----|-----------|--------------|
| **Les1** | Linux Tuning | Systeemoptimalisatie en performance |
| **Les2** | Deb Packages | Debian package management |
| **Les3** | DNS | Domain Name System configuratie |
| **Les4** | LVM | Logical Volume Management |
| **Les5** | Portscan | Netwerk scanning en beveiliging |
| **Les6** | TLS | Transport Layer Security |
| **Les6a** | Python | Scripting en automatisering |
| **Les6b** | Scapy | Packet manipulation |
| **Les7** | AppArmor | Mandatory Access Control |
| **Les8** | Ansible | Configuration management |
| **Les9** | Nagios | Network monitoring |

---

## 🔧 Belangrijke Commando's

### Ansible

```bash
# Role aanmaken
ansible-galaxy role init NAAM-role

# Syntax check
ansible-playbook --syntax-check playbook.yml

# Lint check
ansible-lint .

# Playbook uitvoeren
ansible-playbook -i inventory.ini playbook.yml

# Verbose output (debugging)
ansible-playbook playbook.yml -vvv
```

### Apache/SSL

```bash
# SSL module activeren
sudo a2enmod ssl

# Site activeren
sudo a2ensite jouw-site.conf

# Configuratie testen
sudo apache2ctl configtest

# Apache herstarten
sudo systemctl restart apache2

# Logs bekijken
sudo tail -f /var/log/apache2/error.log
```

### Pure-FTPd

```bash
# Status checken
sudo systemctl status pure-ftpd

# Service herstarten
sudo systemctl restart pure-ftpd

# Logs bekijken
sudo journalctl -u pure-ftpd -n 50

# FTP testen
ftp localhost
```

---

## 📝 Examentips

### Voor het examen

1. ✅ **Lees de opgave 2x** - vooral de details over bestandsnamen
2. ✅ **Gebruik exacte namen** - `ACHTERNAAM` in hoofdletters waar gevraagd
3. ✅ **Test altijd** - voer playbooks minstens 2x uit
4. ✅ **Maak screenshots** - vooral van werkende configuraties
5. ✅ **Plak output** - volledige ansible-playbook output in examendocument
6. ✅ **Gebruik ansible-lint** - moet 0 errors geven
7. ✅ **Check handler werking** - moet enkel triggeren bij changes

### Tijdens het examen

- **Gebruik `sudo tee`** voor betrouwbare file creation
- **Maak backups** van werkende configs
- **Verifieer stap voor stap** - test niet pas op het einde
- **Let op whitespace** in YAML files (2 spaties indenting)
- **Controleer notify namen** - moeten exact matchen met handler

### Veelgemaakte fouten

❌ **Verkeerde directory** - altijd `cd ~/PROJECT` voordat je commando's uitvoert  
❌ **Ontbrekende directories** - maak `files/` en `templates/` aan  
❌ **Handler naam mismatch** - `notify:` moet exact handler naam zijn  
❌ **Git niet geïnstalleerd** - ansible-lint faalt zonder git  
❌ **YAML syntax** - let op spaties en `:` plaatsing  

---

## 🎓 Examenvragen (mogelijk)

### Theorie

- **Vraag:** Waarom een handler gebruiken in Ansible?  
  **Antwoord:** Om services enkel te herstarten wanneer een configuratie effectief wijzigt. Dit voorkomt onnodige service restarts.

- **Vraag:** Verschil tussen `copy` en `template`?  
  **Antwoord:** `copy` kopieert bestanden exact; `template` gebruikt Jinja2 voor variabelen.

- **Vraag:** Waarom `ansible-galaxy role init` gebruiken?  
  **Antwoord:** Maakt automatisch de correcte Ansible directory structuur volgens best practices.

- **Vraag:** Wat doet een CA (Certificate Authority)?  
  **Antwoord:** Ondertekent en valideert certificaten voor veilige communicatie.

### Praktisch

- Toon dat HTTPS werkt met groen slotje
- Bewijs dat FTP banner via variable werkt
- Laat zien dat handler alleen bij wijziging triggert
- Demonstreer ansible-lint clean output

---

## 📚 Nuttige Resources

- **Ansible Docs:** https://docs.ansible.com/
- **Easy-RSA Guide:** https://easy-rsa.readthedocs.io/
- **Apache SSL:** https://httpd.apache.org/docs/2.4/ssl/
- **Pure-FTPd:** https://www.pureftpd.org/

---

## 🛠️ Troubleshooting

### Ansible-lint errors

```bash
# Installeer git
sudo apt install -y git

# Check specifiek bestand
ansible-lint playbook.yml
```

### Apache SSL error

```bash
# Check modules
sudo apache2ctl -M | grep ssl

# Check certificaten
ls -la /etc/apache2/ssl/

# Logs
sudo tail -f /var/log/apache2/error.log
```

### FTP werkt niet

```bash
# Service status
sudo systemctl status pure-ftpd

# Restart
sudo systemctl restart pure-ftpd

# Check banner file
sudo cat /etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
```