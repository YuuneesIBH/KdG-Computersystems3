# Computersystemen 3 - Examenprep

Complete examenprepository voor CS3 met uitgewerkte oplossingen, praktische labo's en theorie.

---

## 📂 Repository Structuur

```
examenprep/
├── oplossingen/              # Uitgewerkte examenvragen
│   ├── cs3-exdef.md         # Definitieve examenoplossingen
│   ├── exam_prep.md         # Examenvoorbereiding guide
│   └── uitgevoerde_commands.txt
│
├── oefeningen/              # Praktische labo's per onderwerp
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
│
├── theorie/                 # Theoretische documenten
│   ├── Handige_Theorie-CS3-ISB.pdf
│   └── virtualization_quiz.html
│
├── werkelijke_ex/           # Examenvragen archief
│   ├── vraag1/
│   └── vraag2/
│
├── cs3examen.txt
├── mogelijke_examenvragen_2025.txt
└── README.md
```

---

## 📚 Inhoud

### Oplossingen
Bevat volledig uitgewerkte oplossingen voor de examenlabo's met stapsgewijze instructies en command history.

### Oefeningen
Negen lessen met praktische opdrachten:
- **Les 1:** Linux systeemoptimalisatie en performance tuning
- **Les 2:** Debian package management (dpkg, apt)
- **Les 3:** DNS configuratie met BIND
- **Les 4:** Logical Volume Management (LVM)
- **Les 5:** Network scanning met Nmap
- **Les 6:** TLS/SSL certificaten en Easy-RSA
- **Les 6a:** Python scripting en automatisering
- **Les 6b:** Packet manipulation met Scapy
- **Les 7:** AppArmor security profiles
- **Les 8:** Ansible configuration management
- **Les 9:** Nagios monitoring setup

### Theorie
Studiemateriaal met theoretische achtergrond en quizzen voor examenbereiding.

### Werkelijke Examenvragen
Archief met echte examenvragen uit vorige jaren.

---

## 🎯 Belangrijkste Examenlabo's

### Labo 1: HTTPS met Easy-RSA
Configureer een beveiligde webserver met TLS-certificaten:
- PKI opzetten met Easy-RSA
- CA en servercertificaat genereren
- Apache SSL/TLS configuratie
- Browser certificaat validatie

### Labo 2: Ansible Role - Pure-FTPd
Ontwikkel een volledige Ansible role:
- Role structuur met `ansible-galaxy`
- Pure-FTPd installatie en configuratie
- Jinja2 templates voor custom banner
- Handlers voor service management
- Code quality met `ansible-lint`

---

## 🚀 Quick Start

```bash
# Examenlabo 1 - HTTPS Setup
sudo apt install easy-rsa -y
mkdir ~/easy-rsa && cd ~/easy-rsa
cp -r /usr/share/easy-rsa/* .
./easyrsa init-pki
./easyrsa build-ca nopass
# Zie oplossingen/cs3-exdef.md voor volledige guide

# Examenlabo 2 - Ansible Role
sudo apt install -y ansible ansible-lint git
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles
cd ~/ACHTERNAAM-VOORNAAM/roles
ansible-galaxy role init ACHTERNAAM-pure-ftpd
# Zie oplossingen/cs3-exdef.md voor configuratie
```

---

## 🔧 Handige Commando's

**Ansible:**
```bash
ansible-galaxy role init NAAM          # Role aanmaken
ansible-playbook --syntax-check FILE   # Syntax validatie
ansible-lint .                         # Code quality check
ansible-playbook -i inventory FILE     # Playbook uitvoeren
```

**Apache/SSL:**
```bash
sudo a2enmod ssl                       # SSL module activeren
sudo apache2ctl configtest             # Configuratie testen
sudo systemctl restart apache2         # Service herstarten
```

**Pure-FTPd:**
```bash
sudo systemctl status pure-ftpd        # Status controleren
sudo journalctl -u pure-ftpd -n 50     # Logs bekijken
ftp localhost                          # FTP testen
```

---

## 💡 Examentips

- Lees de opgave grondig en let op exacte bestandsnamen
- Gebruik `ACHTERNAAM` in hoofdletters waar gevraagd
- Test playbooks minimaal 2x voor zekerheid
- Gebruik `sudo tee` voor betrouwbare file creation
- Controleer dat handlers alleen bij changes triggeren
- Verifieer dat `ansible-lint` 0 errors geeft
- Maak screenshots van werkende configuraties

**Veelgemaakte fouten:**
- Werken in verkeerde directory
- Handler naam mismatch met notify
- YAML indentation errors (gebruik 2 spaties)
- Git niet geïnstalleerd (vereist voor ansible-lint)

---

## 📖 Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Easy-RSA Guide](https://easy-rsa.readthedocs.io/)
- [Apache SSL Documentation](https://httpd.apache.org/docs/2.4/ssl/)
- [Pure-FTPd](https://www.pureftpd.org/)

---

**Academiejaar:** 2025-2026  
**Vak:** CS3 Computersystemen