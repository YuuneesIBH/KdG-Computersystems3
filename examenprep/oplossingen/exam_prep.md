# Computersystemen 2 - Complete Examen Guide G501

**Examen:** Mondeling - 15/01/26 om 11 uur  
**Locatie:** G501  
**Wat wordt NIET gevraagd:** SELinux, Nagios, iSCSI, Loadbalancing

---

## 📋 Examenvragen Overzicht

1. LVM: Logical Volumes aanmaken en verwijderen
2. Systemd: Eigen service maken
3. DNS: Bind9 met forward en reverse zones
4. Apache: HTTPS site configureren
5. ProFTPD: FTPS site configureren
6. Scapy: Portscan script schrijven
7. DEB: Debian pakket maken volgens policies
8. AppArmor: Profiel aanmaken
9. Ansible: Role aanmaken met ansible-lint compliance

---

## 1️⃣ LVM (Logical Volume Management)

### Context
Je krijgt twee extra schijven:
- `vda` = OS-schijf (niet aanraken!)
- `vdb` = 5GB (voor LVM oefeningen)
- `vdc` = 5GB (optioneel voor VG uitbreiding)

### Stap 1.1: Schijven checken
```bash
lsblk -f
```
**Uitleg:** Check of `vdb` en `vdc` leeg zijn (geen filesystem, geen mount).

### Stap 1.2: Physical Volume (PV) aanmaken
```bash
pvcreate /dev/vdb
pvdisplay /dev/vdb
```
**Uitleg:** Maak van `/dev/vdb` een Physical Volume (basisbouwsteen van LVM).

### Stap 1.3: Volume Group (VG) aanmaken
```bash
vgcreate vg_data /dev/vdb
vgdisplay vg_data
```
**Uitleg:** Maak een Volume Group `vg_data` aan - een pool van opslag waar je LVs uit knipt.

### Stap 1.4: Logical Volume (LV) aanmaken
```bash
lvcreate -L 2G -n lv_app vg_data
lvs
```
**Uitleg:** Maak een Logical Volume van 2GB (vergelijkbaar met een partitie).

### Stap 1.5: Filesystem maken
```bash
mkfs.ext4 /dev/vg_data/lv_app
```
**Uitleg:** Een LV is "ruwe storage" - zet er een filesystem op zodat Linux het kan mounten.

### Stap 1.6: Mountpoint aanmaken en mounten
```bash
mkdir -p /mnt/app
mount /dev/vg_data/lv_app /mnt/app
df -hT | grep /mnt/app
```
**Uitleg:**
- `mkdir` maakt de mountlocatie
- `mount` activeert het volume
- `df -hT` toont dat het effectief gemount is + filesystemtype

### Stap 1.7: Persistent maken via fstab
```bash
# UUID ophalen
blkid /dev/vg_data/lv_app

# Bewerk fstab
nano /etc/fstab
```
**Voeg toe (pas UUID aan):**
```
UUID=XXXX-XXXX  /mnt/app  ext4  defaults  0  2
```

**Test zonder reboot:**
```bash
umount /mnt/app
mount -a
df -hT | grep /mnt/app
```
**Uitleg:** `mount -a` test fstab. Als dit faalt, weet je het NU, niet na reboot!

### Stap 1.8: Resize (EXAMENKILLER!)
```bash
lvextend -L +500M -r /dev/vg_data/lv_app
```
**Uitleg:**
- `lvextend` vergroot het LV
- `-r` vergroot ook meteen het filesystem (ext4 resize2fs)
- Dit is de snelste en veiligste manier

**Check:**
```bash
lvs
df -hT | grep /mnt/app
```

### Stap 1.9: VG uitbreiden met vdc (extra punten)
```bash
pvcreate /dev/vdc
vgextend vg_data /dev/vdc
vgs
```
**Uitleg:** Voeg een tweede fysieke disk toe aan dezelfde VG voor extra ruimte. Dit toont dat je snapt hoe LVM "scalable" werkt.

### Stap 1.10: Verwijderen (opruimen)
```bash
# Eerst unmount
umount /mnt/app

# fstab entry verwijderen
nano /etc/fstab  # verwijder de regel

# LVM opruimen (in omgekeerde volgorde: LV → VG → PV)
lvremove -y /dev/vg_data/lv_app
vgremove -y vg_data
pvremove -y /dev/vdb
pvremove -y /dev/vdc
```

---

## 2️⃣ Systemd Service Maken

### Stap 2.1: Script maken
```bash
nano /usr/local/bin/hello-service.sh
```

**Voorbeeldscript:**
```bash
#!/bin/bash
while true; do
    echo "Service is running at $(date)"
    sleep 5
done
```

**Executable maken:**
```bash
chmod +x /usr/local/bin/hello-service.sh
```
**Uitleg:** `/usr/local/bin` is voor eigen scripts. `chmod +x` is nodig, anders faalt ExecStart.

### Stap 2.2: Unit file maken
```bash
nano /etc/systemd/system/hello.service
```

**Inhoud:**
```ini
[Unit]
Description=Hello Service Test
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/hello-service.sh
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Stap 2.3: Laden, enablen en starten
```bash
systemctl daemon-reload
systemctl enable --now hello.service
systemctl status --no-pager hello.service
```
**Uitleg:**
- `daemon-reload` laat systemd de nieuwe unit herlezen
- `enable --now` = starten ÉN autostart bij boot
- `status` toont of het draait

**Logs tonen (extra punten):**
```bash
journalctl -u hello.service -n 20 --no-pager
```

---

## 3️⃣ DNS (Bind9) - Forward + Reverse

### Stap 3.1: Installatie
```bash
apt update
apt install -y bind9 dnsutils
systemctl enable --now bind9
systemctl status --no-pager bind9
```
**Uitleg:** `bind9` is de server, `dnsutils` geeft `dig` om te testen.

### Stap 3.2: Forward zone configureren
```bash
nano /etc/bind/named.conf.local
```

**Voeg toe:**
```bind
zone "example.local" {
    type master;
    file "/etc/bind/db.example.local";
};
```

### Stap 3.3: Forward zone file maken
```bash
cp /etc/bind/db.local /etc/bind/db.example.local
nano /etc/bind/db.example.local
```

**Voorbeeldinhoud:**
```bind
$TTL    604800
@       IN      SOA     ns1.example.local. admin.example.local. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns1.example.local.
ns1     IN      A       192.168.10.1
host1   IN      A       192.168.10.10
host2   IN      A       192.168.10.20
```

**Belangrijk:**
- SOA met serial number
- NS record
- A record voor nameserver zelf
- Punt achter FQDN waar nodig!

### Stap 3.4: Reverse zone configureren
```bash
nano /etc/bind/named.conf.local
```

**Voeg toe:**
```bind
zone "10.168.192.in-addr.arpa" {
    type master;
    file "/etc/bind/db.192.168.10";
};
```

### Stap 3.5: Reverse zone file maken
```bash
cp /etc/bind/db.127 /etc/bind/db.192.168.10
nano /etc/bind/db.192.168.10
```

**Voorbeeldinhoud:**
```bind
$TTL    604800
@       IN      SOA     ns1.example.local. admin.example.local. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns1.example.local.
1       IN      PTR     ns1.example.local.
10      IN      PTR     host1.example.local.
20      IN      PTR     host2.example.local.
```

**Belangrijk:** PTR moet eindigen op punt!

### Stap 3.6: Valideren en herladen
```bash
named-checkconf -z
systemctl reload bind9
```
**Uitleg:** `-z` checkt alle zones in één keer.

### Stap 3.7: Testen
```bash
# Forward lookup
dig @127.0.0.1 host1.example.local +short

# Reverse lookup
dig @127.0.0.1 -x 192.168.10.10 +short
```

---

## 4️⃣ HTTPS Site met Apache

### Stap 4.1: Installatie + modules
```bash
apt install -y apache2 openssl
a2enmod ssl rewrite
systemctl enable --now apache2
```
**Uitleg:** `ssl` module is nodig voor HTTPS, `rewrite` voor auto-redirect.

### Stap 4.2: Certificaat maken (self-signed)
```bash
mkdir -p /etc/ssl/localcerts
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/localcerts/site.key \
  -out /etc/ssl/localcerts/site.crt
```
**Uitleg:** Self-signed is OK op examen - je toont dat je TLS snapt.

### Stap 4.3: Website content
```bash
mkdir -p /var/www/site
echo "<h1>HTTPS OK</h1>" > /var/www/site/index.html
```

### Stap 4.4: VHost configuratie
```bash
nano /etc/apache2/sites-available/site.conf
```

**Inhoud:**
```apache
<VirtualHost *:80>
    ServerName site.local
    DocumentRoot /var/www/site
    
    Redirect permanent / https://site.local/
</VirtualHost>

<VirtualHost *:443>
    ServerName site.local
    DocumentRoot /var/www/site
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/localcerts/site.crt
    SSLCertificateKeyFile /etc/ssl/localcerts/site.key
    
    <Directory /var/www/site>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

**Belangrijk:**
- DocumentRoot hetzelfde voor beide
- Poort 80 redirect naar 443
- SSLEngine on voor HTTPS

### Stap 4.5: Enablen en testen
```bash
a2ensite site.conf
a2dissite 000-default.conf
apache2ctl configtest
systemctl reload apache2
```
**Uitleg:** `configtest` voorkomt dat je Apache kapot reload!

**Testen:**
```bash
curl -I http://localhost
curl -Ik https://localhost
```

---

## 5️⃣ FTPS (ProFTPD + TLS)

### Stap 5.1: Installatie
```bash
apt install -y proftpd-basic openssl
systemctl enable --now proftpd
```

### Stap 5.2: Certificaat maken
```bash
mkdir -p /etc/proftpd/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/proftpd/ssl/proftpd.key \
  -out /etc/proftpd/ssl/proftpd.crt

chmod 600 /etc/proftpd/ssl/proftpd.key
```
**Uitleg:** Key moet protected zijn (600).

### Stap 5.3: ProFTPD configureren
```bash
nano /etc/proftpd/proftpd.conf
```

**Voeg toe/wijzig:**
```apache
# TLS configuratie
<IfModule mod_tls.c>
    TLSEngine on
    TLSLog /var/log/proftpd/tls.log
    TLSProtocol TLSv1.2
    
    TLSRSACertificateFile /etc/proftpd/ssl/proftpd.crt
    TLSRSACertificateKeyFile /etc/proftpd/ssl/proftpd.key
    
    TLSRequired on
</IfModule>

# Passive mode (nodig in VM/netwerken!)
PassivePorts 60000 65000
```

### Stap 5.4: Herstarten en testen
```bash
proftpd -t  # Config test
systemctl restart proftpd
```

**TLS testen:**
```bash
openssl s_client -connect 127.0.0.1:21 -starttls ftp
```

---

## 6️⃣ Scapy Portscan Script

### Stap 6.1: Installatie
```bash
apt install -y python3 python3-pip
pip3 install scapy
```
**Uitleg:** Scapy gebruikt raw sockets, dus root nodig!

### Stap 6.2: SYN Scan Script
```bash
nano /usr/local/bin/portscan.py
chmod +x /usr/local/bin/portscan.py
```

**Script:**
```python
#!/usr/bin/env python3
from scapy.all import *
import sys

def syn_scan(target, ports):
    """
    Perform SYN scan on target
    SYN+ACK = open
    RST+ACK = closed
    No response = filtered
    """
    results = {'open': [], 'closed': [], 'filtered': []}
    
    for port in ports:
        # Send SYN packet
        pkt = IP(dst=target)/TCP(dport=port, flags="S")
        resp = sr1(pkt, timeout=1, verbose=0)
        
        if resp is None:
            results['filtered'].append(port)
        elif resp.haslayer(TCP):
            if resp[TCP].flags == 0x12:  # SYN+ACK
                results['open'].append(port)
                # Send RST to close connection
                sr(IP(dst=target)/TCP(dport=port, flags="R"), timeout=1, verbose=0)
            elif resp[TCP].flags == 0x14:  # RST+ACK
                results['closed'].append(port)
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target_ip>")
        sys.exit(1)
    
    target = sys.argv[1]
    ports = [21, 22, 23, 25, 80, 443, 3306, 8080]
    
    print(f"Scanning {target}...")
    results = syn_scan(target, ports)
    
    print("\n=== Results ===")
    print(f"Open ports: {results['open']}")
    print(f"Closed ports: {results['closed']}")
    print(f"Filtered ports: {results['filtered']}")
```

**Uitvoeren (als root):**
```bash
sudo python3 /usr/local/bin/portscan.py 192.168.1.1
```

### SYN Scan Logica
- Stuur **SYN** packet (`flags="S"`)
- Antwoord analyseren:
  - **SA (0x12)** = open
  - **RA (0x14)** = closed
  - **None** = filtered

---

## 7️⃣ DEB Pakket Maken

### Stap 7.1: Tools installeren
```bash
apt install -y devscripts debhelper lintian fakeroot build-essential
```

### Stap 7.2: Pakketstructuur aanmaken
```bash
mkdir -p myapp-1.0/debian
cd myapp-1.0
```

### Stap 7.3: Control file
```bash
nano debian/control
```

**Inhoud:**
```
Source: myapp
Section: utils
Priority: optional
Maintainer: Your Name <you@example.com>
Build-Depends: debhelper (>= 10)
Standards-Version: 4.1.3

Package: myapp
Architecture: all
Depends: ${misc:Depends}
Description: My Application
 A simple example application
 .
 This is the extended description.
```

### Stap 7.4: Changelog
```bash
nano debian/changelog
```

**Inhoud:**
```
myapp (1.0-1) unstable; urgency=low

  * Initial release

 -- Your Name <you@example.com>  Wed, 15 Jan 2025 10:00:00 +0100
```

### Stap 7.5: Rules file
```bash
nano debian/rules
chmod +x debian/rules
```

**Inhoud:**
```makefile
#!/usr/bin/make -f

%:
	dh $@
```

### Stap 7.6: Copyright
```bash
nano debian/copyright
```

**Inhoud:**
```
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: myapp
Source: https://example.com/myapp

Files: *
Copyright: 2025 Your Name <you@example.com>
License: GPL-3+
```

### Stap 7.7: Bouwen
```bash
debuild -us -uc
```
**Uitleg:** Maakt `.deb` en `.changes` files.

### Stap 7.8: Lintian check
```bash
cd ..
lintian myapp_1.0-1_all.deb
```
**Uitleg:** Docenten kijken naar control file + lintian output!

---

## 8️⃣ AppArmor Profiel

### Stap 8.1: Installatie
```bash
apt install -y apparmor apparmor-utils
aa-status
```

### Stap 8.2: Profiel genereren
```bash
aa-genprof /usr/bin/jouw-applicatie
```
**Uitleg:** Tool observeert gedrag en maakt automatisch rules.

**Interactief proces:**
1. Start de applicatie in een ander terminal
2. Gebruik alle functionaliteit
3. Keer terug naar `aa-genprof` terminal
4. Scan voor events
5. Accepteer of weiger acties

### Stap 8.3: Profiel bewerken (handmatig)
```bash
nano /etc/apparmor.d/usr.bin.jouw-applicatie
```

**Voorbeeld profiel:**
```
#include <tunables/global>

/usr/bin/jouw-applicatie {
  #include <abstractions/base>
  
  # Executable permissions
  /usr/bin/jouw-applicatie mr,
  
  # Config files
  /etc/jouw-applicatie/** r,
  
  # Data directory
  /var/lib/jouw-applicatie/** rw,
  
  # Logs
  /var/log/jouw-applicatie/** w,
  
  # Network (indien nodig)
  network inet stream,
  network inet6 stream,
}
```

### Stap 8.4: Profiel laden en enforcen
```bash
# Reload profiel
apparmor_parser -r /etc/apparmor.d/usr.bin.jouw-applicatie

# Enforce mode
aa-enforce /etc/apparmor.d/usr.bin.jouw-applicatie

# Check status
aa-status
```

### Stap 8.5: Troubleshooting
```bash
# Logs bekijken
journalctl -xe | grep -i apparmor
dmesg | grep -i apparmor

# Complain mode (voor debugging)
aa-complain /etc/apparmor.d/usr.bin.jouw-applicatie
```

---

## 9️⃣ Ansible Role + ansible-lint

### Stap 9.1: Installatie
```bash
apt install -y ansible ansible-lint
```

### Stap 9.2: Role initialiseren
```bash
ansible-galaxy role init myrole
cd myrole
```

**Structuur:**
```
myrole/
├── defaults/
│   └── main.yml
├── files/
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
├── templates/
├── tests/
│   ├── inventory
│   └── test.yml
└── vars/
    └── main.yml
```

### Stap 9.3: Tasks definiëren
```bash
nano tasks/main.yml
```

**Voorbeeld (Apache installatie):**
```yaml
---
- name: Install Apache2
  ansible.builtin.apt:
    name: apache2
    state: present
    update_cache: true
  become: true

- name: Ensure Apache is running
  ansible.builtin.service:
    name: apache2
    state: started
    enabled: true
  become: true
  notify: Restart Apache

- name: Copy index.html
  ansible.builtin.copy:
    src: files/index.html
    dest: /var/www/html/index.html
    owner: www-data
    group: www-data
    mode: '0644'
  become: true
  notify: Restart Apache
```

### Stap 9.4: Handlers definiëren
```bash
nano handlers/main.yml
```

**Inhoud:**
```yaml
---
- name: Restart Apache
  ansible.builtin.service:
    name: apache2
    state: restarted
  become: true
```

### Stap 9.5: Defaults
```bash
nano defaults/main.yml
```

**Inhoud:**
```yaml
---
apache_port: 80
apache_document_root: /var/www/html
```

### Stap 9.6: Meta informatie
```bash
nano meta/main.yml
```

**Inhoud:**
```yaml
---
galaxy_info:
  author: Your Name
  description: Apache web server role
  license: MIT
  min_ansible_version: '2.9'
  
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
  
  galaxy_tags:
    - web
    - apache

dependencies: []
```

### Stap 9.7: Ansible-lint uitvoeren
```bash
ansible-lint
```

**Veel voorkomende problemen:**
- Gebruik `ansible.builtin.module` i.p.v. gewoon `module`
- Geen `shell` of `command` modules (gebruik specifieke modules)
- Idempotency: gebruik `state: present/absent`
- Handler pattern gebruiken
- `become: true` waar nodig

### Stap 9.8: Role testen
```bash
nano tests/test.yml
```

**Inhoud:**
```yaml
---
- hosts: localhost
  roles:
    - myrole
```

**Uitvoeren:**
```bash
ansible-playbook tests/test.yml -i tests/inventory
```

---

## 🎯 Examenstrategie Tips

### Algemeen
1. **Lees de opdracht VOLLEDIG** voordat je begint
2. **Check syntax** met validation tools (named-checkconf, apache2ctl configtest, etc.)
3. **Test VOOR reboot** (mount -a, systemctl status, etc.)
4. **Logs zijn je vriend** (journalctl, dmesg, /var/log/)

### Per Onderwerp

**LVM:**
- Vergeet `-r` niet bij lvextend (examenkiller!)
- fstab met UUID, niet met /dev/vg/lv
- Test met mount -a

**Systemd:**
- daemon-reload NA elke wijziging
- enable --now voor autostart
- Check logs met journalctl -u

**DNS:**
- Punt achter FQDN!
- named-checkconf -z checkt ALLES
- Test forward én reverse

**Apache/ProFTPD:**
- configtest voordat je reload/restart
- Self-signed cert is OK
- Passive ports voor FTP!

**Scapy:**
- Root rechten nodig
- SYN scan is eenvoudigst
- Flags: S=SYN, SA=0x12, RA=0x14

**DEB:**
- lintian is belangrijk
- Control file moet kloppen
- debian/rules moet +x zijn

**AppArmor:**
- aa-genprof voor automatisch profiel
- Complain mode voor debugging
- Check logs met journalctl

**Ansible:**
- ansible-lint VOOR inleveren
- Gebruik ansible.builtin.* modules
- Handler pattern voor restarts
- Idempotency is key

---

## 🔧 Handige Commands Cheatsheet

### Systeem Info
```bash
lsblk -f              # Block devices + filesystem
df -hT                # Disk usage + type
blkid                 # UUID's ophalen
systemctl status      # Service status
journalctl -xe        # Logs bekijken
```

### Validation
```bash
named-checkconf -z    # DNS zones check
apache2ctl configtest # Apache syntax
proftpd -t            # ProFTPD syntax
ansible-lint          # Ansible role lint
lintian *.deb         # DEB package lint
```

### Network Testing
```bash
dig @server hostname  # DNS query
curl -I url           # HTTP headers
openssl s_client      # TLS test
ss -tulpn             # Open ports
```

### File Permissions
```bash
chmod +x script       # Executable maken
chmod 600 keyfile     # Private key
chown user:group file # Owner wijzigen
```

---

## ✅ Pre-Exam Checklist

- [ ] Ik kan LVM volumes aanmaken, resizen en verwijderen
- [ ] Ik kan een systemd service schrijven en enablen
- [ ] Ik kan DNS forward en reverse zones configureren
- [ ] Ik kan Apache HTTPS configureren met SSL
- [ ] Ik kan ProFTPD met TLS configureren
- [ ] Ik kan een Scapy portscan script schrijven
- [ ] Ik kan een DEB pakket maken dat lintian test doorstaat
- [ ] Ik kan een AppArmor profiel genereren en enforcen
- [ ] Ik kan een Ansible role maken die ansible-lint doorstaat
- [ ] Ik ken alle validation commands uit mijn hoofd

**Succes! 🚀**