# CS3 Examen - Complete Handleiding

## 📋 Overzicht

Dit document bevat alle stappen en commando's voor het CS3 examen. Vervang overal `ACHTERNAAM` en `VOORNAAM` door jouw eigen naam.

---

## 🔒 Examenlabo 1: HTTPS Configuratie met Easy-RSA

### Doel
Een TLS-certificaat configureren zodat `https://web.uwachternaam.local` een groen slotje toont in Firefox.

### Stap 1: Easy-RSA installeren

```bash
sudo apt update
sudo apt install easy-rsa -y
```

### Stap 2: PKI (Public Key Infrastructure) initialiseren

```bash
# Maak een werkdirectory aan
mkdir ~/easy-rsa
cd ~/easy-rsa

# Kopieer de easy-rsa scripts
cp -r /usr/share/easy-rsa/* .

# Initialiseer de PKI
./easyrsa init-pki
```

### Stap 3: CA (Certificate Authority) aanmaken

```bash
# Bouw de CA (druk gewoon Enter voor de naam of vul iets in)
./easyrsa build-ca nopass
```

### Stap 4: Servercertificaat aanmaken

```bash
# Genereer een certificaat voor jouw webserver
./easyrsa gen-req web.achternaam.local nopass

# Onderteken het certificaat met de CA
./easyrsa sign-req server web.achternaam.local
```

### Stap 5: Certificaten naar Apache kopiëren

```bash
# Maak de ssl directory aan als deze nog niet bestaat
sudo mkdir -p /etc/apache2/ssl

# Kopieer het servercertificaat
sudo cp ~/easy-rsa/pki/issued/web.achternaam.local.crt /etc/apache2/ssl/

# Kopieer de private key
sudo cp ~/easy-rsa/pki/private/web.achternaam.local.key /etc/apache2/ssl/

# Kopieer het CA certificaat
sudo cp ~/easy-rsa/pki/ca.crt /etc/apache2/ssl/
```

### Stap 6: Apache SSL configureren

```bash
# Activeer SSL module
sudo a2enmod ssl

# Bewerk de SSL configuratie
sudo nano /etc/apache2/sites-available/web.achternaam.local-ssl.conf
```

Voeg deze inhoud toe:

```apache
<VirtualHost *:443>
    ServerName web.achternaam.local
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/web.achternaam.local.crt
    SSLCertificateKeyFile /etc/apache2/ssl/web.achternaam.local.key
    SSLCACertificateFile /etc/apache2/ssl/ca.crt

    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

### Stap 7: Site activeren en Apache herstarten

```bash
# Activeer de SSL site
sudo a2ensite web.achternaam.local-ssl.conf

# Test de configuratie
sudo apache2ctl configtest

# Herstart Apache
sudo systemctl restart apache2
```

### Stap 8: CA certificaat importeren in Firefox

1. Kopieer het CA certificaat naar je lokale machine
2. Open Firefox
3. Ga naar: `Instellingen` → `Privacy & Beveiliging` → `Certificaten` → `Certificaten bekijken`
4. Klik op `Importeren`
5. Selecteer het `ca.crt` bestand
6. Vink aan: "Deze CA vertrouwen voor het identificeren van websites"

### Stap 9: Screenshot maken

Maak een screenshot van:
- Firefox met `https://web.uwachternaam.local` en het groene slotje
- De Apache configuratie file

---

## 🔧 Examenlabo 2: Ansible Pure-FTPd Configuratie

### Voorbereiding: Ansible installeren

```bash
# Update package lijst
sudo apt update

# Installeer Ansible en ansible-lint
sudo apt install -y ansible ansible-lint

# Installeer git (vereist voor ansible-lint)
sudo apt install -y git

# Verifieer installatie
ansible --version
ansible-lint --version
```

### Deel 1: Directory structuur aanmaken met ansible-galaxy

```bash
# Maak de hoofddirectory aan
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles
cd ~/ACHTERNAAM-VOORNAAM/roles

# Gebruik ansible-galaxy om een correcte role-structuur aan te maken
ansible-galaxy role init ACHTERNAAM-pure-ftpd

# Je zou moeten zien:
# - Role ACHTERNAAM-pure-ftpd was created successfully
```

**Waarom ansible-galaxy gebruiken?**
- Maakt automatisch de juiste directory structuur aan
- Volgt Ansible best practices
- Voorkomt fouten met ontbrekende mappen

### Deel 2: Tasks file aanmaken (met sudo tee methode)

**Optie 1: Met sudo tee (meest betrouwbaar voor copy-paste)**

```bash
sudo tee ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/tasks/main.yml > /dev/null <<'EOF'
---
- name: ACHTERNAAM remove vsftpd
  apt:
    name: vsftpd
    state: absent

- name: ACHTERNAAM remove proftpd-core
  apt:
    name: proftpd-core
    state: absent

- name: ACHTERNAAM install pure-ftpd
  apt:
    name: pure-ftpd
    state: present
    update_cache: yes

- name: ACHTERNAAM enable and start pure-ftpd
  service:
    name: pure-ftpd
    state: started
    enabled: yes

- name: ACHTERNAAM install FortunesFile config
  copy:
    src: FortunesFile-ACHTERNAAM
    dest: /etc/pure-ftpd/conf/FortunesFile
  notify: Restart pure-ftpd

- name: ACHTERNAAM deploy banner template
  template:
    src: pure-ftpd-ACHTERNAAM.banner.j2
    dest: /etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
  notify: Restart pure-ftpd
EOF
```

**Optie 2: Met nano/vi**

```bash
nano ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/tasks/main.yml
```

Voeg dezelfde inhoud toe als bij Optie 1.

### Deel 3: FortunesFile aanmaken

**Let op:** Maak eerst de `files` directory aan als deze niet bestaat:

```bash
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/files
```

**Met sudo tee:**

```bash
sudo tee ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/files/FortunesFile-ACHTERNAAM > /dev/null <<'EOF'
# Custom config /etc/pure-ftpd/conf/FortunesFile
# ACHTERNAAM voornaam
/etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
EOF
```

**Of met nano:**

```bash
nano ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/files/FortunesFile-ACHTERNAAM
```

Inhoud:
```
# Custom config /etc/pure-ftpd/conf/FortunesFile
# ACHTERNAAM voornaam
/etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
```

### Deel 4: Handler aanmaken

**Met sudo tee:**

```bash
sudo tee ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/handlers/main.yml > /dev/null <<'EOF'
---
- name: Restart pure-ftpd
  service:
    name: pure-ftpd
    state: restarted
EOF
```

**Of met nano:**

```bash
nano ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/handlers/main.yml
```

Inhoud:
```yaml
---
- name: Restart pure-ftpd
  service:
    name: pure-ftpd
    state: restarted
```

**Belangrijk:** De handler naam moet exact overeenkomen met de `notify:` in je tasks!

### Deel 5: Playbook aanmaken

```bash
nano playbook_ACHTERNAAM.yml
```

Voeg deze inhoud toe:

```yaml
---
- name: "ACHTERNAAM configure pure-ftpd"
  hosts: all
  become: true
  roles:
    - ACHTERNAAM-pure-ftpd
```

### Deel 6: Inventory file (optioneel maar aanbevolen)

```bash
nano inventory.ini
```

Voeg je node(s) toe:

```ini
[ftpservers]
jouw-node-ip-adres ansible_user=jouw_gebruiker
```

### Deel 7: Eerste test uitvoeren

```bash
# Test de playbook
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml

# Test de FTP verbinding
ftp jouw-node-ip-adres
```

### Deel 8: Backup maken

```bash
# Maak een backup directory
mkdir -p ~/ACHTERNAAM-VOORNAAM/backup

# Kopieer de werkende configuratie
cp -r ~/ACHTERNAAM-VOORNAAM/roles ~/ACHTERNAAM-VOORNAAM/backup/
cp ~/ACHTERNAAM-VOORNAAM/playbook_ACHTERNAAM.yml ~/ACHTERNAAM-VOORNAAM/backup/
```

### Deel 9: Template maken (vervang banner file)

**Let op:** Maak eerst de `templates` directory aan:

```bash
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/templates
```

**Met sudo tee:**

```bash
sudo tee ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/templates/pure-ftpd-ACHTERNAAM.banner.j2 > /dev/null <<'EOF'
{{ banner }}
EOF
```

**Of met nano:**

```bash
nano ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/templates/pure-ftpd-ACHTERNAAM.banner.j2
```

Inhoud:
```jinja2
{{ banner }}
```

### Deel 10: Variables file aanmaken (OPTIONEEL)

**Optie A: Variables in playbook (AANBEVOLEN - simpeler)**

De banner variable wordt direct in het playbook gedefinieerd (zie Deel 5).

**Optie B: Aparte vars file**

```bash
nano ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/vars/main.yml
```

Voeg deze inhoud toe:

```yaml
---
banner: "FTP server ACHTERNAAM"
```

**Let op:** Als je deze optie gebruikt, verwijder dan de `vars:` sectie uit je playbook!

### Deel 11: Tasks updaten voor template

**De tasks in Deel 2 bevatten al de template task!** Je hoeft niets te updaten.

Controleer dat je tasks file deze regel bevat:

```yaml
- name: ACHTERNAAM deploy banner template
  template:
    src: pure-ftpd-ACHTERNAAM.banner.j2
    dest: /etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
  notify: Restart pure-ftpd
```

✅ Als dit er staat, is deze stap al compleet!

### Deel 12: Ansible-lint uitvoeren

```bash
# Ga naar de project directory
cd ~/ACHTERNAAM-VOORNAAM

# Voer ansible-lint uit
ansible-lint .
```

**Als er geen output komt = PERFECT! ✅**

Dit betekent dat alle YAML bestanden voldoen aan de Ansible standaarden.

### Deel 13: Fouten oplossen (indien nodig)

**Als ansible-lint fouten geeft:**

1. **"Failed to locate command: git"**
   ```bash
   sudo apt install -y git
   ```

2. **YAML syntax fouten**
   - Controleer inspringen (gebruik altijd 2 spaties)
   - Zorg dat elke task een `name:` heeft
   - Controleer of alle `:` gevolgd worden door een spatie

3. **Module warnings**
   - Je kan `apt:` en `service:` gebruiken (korte notatie)
   - Of `ansible.builtin.apt:` en `ansible.builtin.service:` (FQCN)
   - Beide zijn correct voor dit examen

**Voorbeeld van correcte task:**

```yaml
- name: ACHTERNAAM install pure-ftpd
  apt:
    name: pure-ftpd
    state: present
    update_cache: yes
```

### Deel 14: Finale test en verificatie

```bash
# Voer de playbook uit
cd ~/ACHTERNAAM-VOORNAAM
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml
```

**Verwachte output:**
```
PLAY [ACHTERNAAM install and configure pure-ftpd] ********************

TASK [Gathering Facts] ***********************************************
ok: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM remove vsftpd] ***************
ok: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM remove proftpd-core] *********
ok: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM install pure-ftpd] ***********
changed: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM enable and start pure-ftpd] **
ok: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM install FortunesFile config] *
changed: [localhost]

TASK [ACHTERNAAM-pure-ftpd : ACHTERNAAM deploy banner template] ******
changed: [localhost]

RUNNING HANDLER [ACHTERNAAM-pure-ftpd : Restart pure-ftpd] ***********
changed: [localhost]

PLAY RECAP ***********************************************************
localhost      : ok=8    changed=4    unreachable=0    failed=0
```

**Controleer de bestanden op de server:**

```bash
# Bekijk FortunesFile
sudo cat /etc/pure-ftpd/conf/FortunesFile

# Bekijk banner
sudo cat /etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
```

**Test FTP verbinding:**

```bash
# Installeer ftp client indien nodig
sudo apt install -y ftp

# Test de verbinding
ftp localhost
```

**Je zou moeten zien:**
```
Connected to localhost.
220-FTP server ACHTERNAAM
220 This is a private system - No anonymous login
Name (localhost:ubuntu):
```

Typ `bye` om af te sluiten.

✅ **Als je de banner ziet, werkt alles perfect!**

### Deel 15: Output voor docent

```bash
# Voer de playbook uit en sla de output op
cd ~/ACHTERNAAM-VOORNAAM
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml | tee output_ACHTERNAAM.txt
```

**Plak de VOLLEDIGE inhoud van deze output in je examendocument!**

De output laat zien:
- ✅ Alle tasks zijn uitgevoerd
- ✅ De handler is correct getriggerd
- ✅ Geen fouten (`failed=0`)
- ✅ Pure-ftpd is geïnstalleerd en draait

---

## 📸 Extra verificatie commando's

### Controleer Pure-FTPd status

```bash
sudo systemctl status pure-ftpd
```

### Bekijk de directory structuur

```bash
tree ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/
```

**Verwachte structuur:**
```
ACHTERNAAM-pure-ftpd/
├── defaults/
├── files/
│   └── FortunesFile-ACHTERNAAM
├── handlers/
│   └── main.yml
├── meta/
├── README.md
├── tasks/
│   └── main.yml
├── templates/
│   └── pure-ftpd-ACHTERNAAM.banner.j2
├── tests/
└── vars/
```

### Test of banner variable werkt

Wijzig de banner in je playbook:

```bash
nano ~/ACHTERNAAM-VOORNAAM/playbook_ACHTERNAAM.yml
```

Verander:
```yaml
banner: "FTP server ACHTERNAAM v2"
```

Run de playbook opnieuw en test met `ftp localhost` - je zou de nieuwe banner moeten zien!

---

## ✅ Checklist voor inlevering

### Examenlabo 1:
- [ ] Screenshot van Firefox met groen slotje bij `https://web.uwachternaam.local`
- [ ] Screenshot van Apache2 SSL configuratie

### Examenlabo 2:
- [ ] Directory `ACHTERNAAM-VOORNAAM` met correcte structuur (via `ansible-galaxy`)
- [ ] Role `ACHTERNAAM-pure-ftpd` compleet met alle bestanden
- [ ] Playbook `playbook_ACHTERNAAM.yml` werkt zonder fouten
- [ ] Inventory file `inventory.ini` aanwezig
- [ ] FortunesFile correct geconfigureerd in `files/`
- [ ] Banner template in `templates/` met variable
- [ ] Handler herstart service bij wijzigingen
- [ ] Template implementatie werkt (banner via variable)
- [ ] `ansible-lint .` geeft geen fouten
- [ ] Output van playbook uitvoering geplakt in examendocument
- [ ] FTP test toont banner correct: `220-FTP server ACHTERNAAM`

---

## 💡 Belangrijke examenvragen en antwoorden

### Vraag 1: Waarom een handler gebruiken?
**Antwoord:** Om services enkel te herstarten wanneer een configuratie effectief wijzigt. Dit voorkomt onnodige service restarts en maakt de playbook efficiënter.

### Vraag 2: Wat is het verschil tussen `copy` en `template`?
**Antwoord:** 
- **copy**: Kopieert een bestand exact zoals het is
- **template**: Gebruikt Jinja2 om variabelen te vervangen in het bestand

### Vraag 3: Waarom `ansible-galaxy role init` gebruiken?
**Antwoord:** Het maakt automatisch de juiste Ansible directory structuur aan volgens best practices.

### Vraag 4: Waarom werkte ansible-galaxy niet?
**Antwoord:** Ansible was nog niet geïnstalleerd op de machine.

### Vraag 5: Wat doet `notify:` in een task?
**Antwoord:** Het triggert een handler, maar alleen als de task daadwerkelijk een wijziging heeft gemaakt (`changed`).

---

## 🎯 Snelle troubleshooting checklist

**Als ansible-playbook faalt:**
```bash
# Check syntax
ansible-playbook --syntax-check playbook_ACHTERNAAM.yml

# Run met verbose output
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml -vvv

# Test connectiviteit
ansible all -i inventory.ini -m ping
```

**Als ansible-lint fouten geeft:**
```bash
# Installeer git (vaak vereist)
sudo apt install -y git

# Check specifiek bestand
ansible-lint playbook_ACHTERNAAM.yml
```

**Als FTP niet werkt:**
```bash
# Check pure-ftpd status
sudo systemctl status pure-ftpd

# Herstart pure-ftpd
sudo systemctl restart pure-ftpd

# Check logs
sudo journalctl -u pure-ftpd -n 50

# Verifieer banner bestand
sudo cat /etc/pure-ftpd/pure-ftpd-ACHTERNAAM.banner
```

**Als bestanden ontbreken:**
```bash
# Maak directories aan
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/files
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/templates

# Check structuur
tree ~/ACHTERNAAM-VOORNAAM/
```

---

## 🆘 Troubleshooting

### Apache SSL werkt niet
```bash
# Controleer of SSL module geladen is
sudo apache2ctl -M | grep ssl

# Controleer certificaat permissies
ls -la /etc/apache2/ssl/

# Bekijk error logs
sudo tail -f /var/log/apache2/error.log
```

### Ansible playbook faalt
```bash
# Verhoog verbosity voor meer info
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml -vvv

# Test connectiviteit
ansible all -i inventory.ini -m ping

# Controleer syntax
ansible-playbook --syntax-check playbook_ACHTERNAAM.yml
```

### Pure-FTPd start niet
```bash
# Controleer status
sudo systemctl status pure-ftpd

# Bekijk logs
sudo journalctl -u pure-ftpd -n 50

# Herstart service manueel
sudo systemctl restart pure-ftpd
```

### "No such file or directory" bij tee commando's
```bash
# Maak de benodigde directories aan
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/files
mkdir -p ~/ACHTERNAAM-VOORNAAM/roles/ACHTERNAAM-pure-ftpd/templates

# Probeer daarna het tee commando opnieuw
```

### ansible-lint geeft "Failed to locate command: git"
```bash
sudo apt install -y git
```

---

## 📝 Handige commando's

```bash
# Ansible dry-run (geen wijzigingen)
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml --check

# Specifieke tags uitvoeren (als je tags gebruikt)
ansible-playbook -i inventory.ini playbook_ACHTERNAAM.yml --tags "config"

# Directory structuur tonen
tree ACHTERNAAM-VOORNAAM/

# Alle ansible bestanden valideren
find . -name "*.yml" -exec ansible-lint {} \;
```

**Succes met je examen! 🎓**