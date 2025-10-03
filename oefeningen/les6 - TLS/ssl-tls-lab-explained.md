# SSL/TLS Configuratie Apache2 en ProFTPD
## Lab Documentatie - KdG Students

**Auteur:** Younes Elazzouzi  
**Email:** younes.elazzouzi@student.kdg.be  
**Datum:** 3 Oktober 2025  
**Platform:** Ubuntu 22.04 (Jammy)  
**Onderwerp:** SSL/TLS configuratie voor Apache2 webserver en ProFTPD met self-signed certificaten

---

## Inhoudsopgave

1. [Apache2 met SSL/TLS](#1-apache2-met-ssltls)
2. [Easy-RSA PKI Setup](#2-easy-rsa-pki-setup)
3. [Certificate Authority (CA)](#3-certificate-authority-ca)
4. [Server Certificaat Genereren](#4-server-certificaat-genereren)
5. [Apache2 SSL Configuratie](#5-apache2-ssl-configuratie)
6. [TLS Protocol Beveiliging](#6-tls-protocol-beveiliging)
7. [ProFTPD Installatie](#7-proftpd-installatie)
8. [ProFTPD TLS Configuratie](#8-proftpd-tls-configuratie)
9. [Testing en Verificatie](#9-testing-en-verificatie)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Apache2 met SSL/TLS

### 1.1 Installatie

```bash
# Installeer Apache2 en OpenSSL
sudo apt update
sudo apt install apache2 openssl -y
```

### 1.2 SSL Module Activeren

```bash
# Activeer de SSL module
sudo a2enmod ssl

# Verificeer dat de module is geactiveerd
apache2ctl -M | grep ssl
```

**Output:**
```
Module ssl already enabled
```

### 1.3 Ports Configuratie

Controleer of Apache luistert op poort 443:

```bash
sudo vi /etc/apache2/ports.conf
```

**Inhoud:**
```apache
Listen 80

<IfModule ssl_module>
    Listen 443
</IfModule>

<IfModule mod_gnutls.c>
    Listen 443
</IfModule>
```

---

## 2. Easy-RSA PKI Setup

### 2.1 Easy-RSA Installeren

```bash
# Installeer Easy-RSA
sudo apt install easy-rsa -y

# Maak een working directory
mkdir ~/easy-rsa
ln -s /usr/share/easy-rsa/* ~/easy-rsa/
chmod 700 ~/easy-rsa
cd ~/easy-rsa
```

### 2.2 PKI Initialiseren

```bash
# Initialiseer de PKI structuur
./easyrsa init-pki
```

**Output:**
```
init-pki complete; you may now create a CA or requests.
Your newly created PKI dir is: /home/ubuntu/easy-rsa/pki
```

---

## 3. Certificate Authority (CA)

### 3.1 CA Certificaat Aanmaken

```bash
cd ~/easy-rsa
./easyrsa build-ca
```

**Tijdens het proces:**
- Kies een **sterke passphrase** voor de CA private key
- Common Name: `KdG_CA`

**Output:**
```
CA creation complete and you may now import and sign cert requests.
Your new CA certificate file for publishing is at:
/home/ubuntu/easy-rsa/pki/ca.crt
```

### 3.2 CA Certificaat Verplaatsen

```bash
sudo cp ~/easy-rsa/pki/ca.crt /etc/ssl/certs/cacert.pem
```

### 3.3 CA Verificatie

```bash
openssl x509 -in /etc/ssl/certs/cacert.pem -noout -issuer -subject
```

**Output:**
```
issuer=CN = KdG_CA
subject=CN = KdG_CA
```

---

## 4. Server Certificaat Genereren

### 4.1 Certificate Signing Request (CSR)

```bash
cd ~/easy-rsa

# Genereer server key en CSR (zonder passphrase voor automatisch opstarten)
./easyrsa gen-req mijnweb nopass
```

**Tijdens het proces:**
- Common Name: `www.mijnweb.local`

**Output:**
```
Keypair and certificate request completed. Your files are:
req: /home/ubuntu/easy-rsa/pki/reqs/mijnweb.req
key: /home/ubuntu/easy-rsa/pki/private/mijnweb.key
```

### 4.2 CSR Signeren met CA

```bash
./easyrsa sign-req server mijnweb
```

**Tijdens het proces:**
- Type `yes` om te bevestigen
- Voer de **CA passphrase** in

**Output:**
```
Certificate created at: /home/ubuntu/easy-rsa/pki/issued/mijnweb.crt
```

### 4.3 Certificaten Installeren

```bash
# Maak directories aan
sudo mkdir -p /etc/pki/tls/certs /etc/pki/tls/private

# Kopieer certificaten
sudo cp ~/easy-rsa/pki/issued/mijnweb.crt /etc/pki/tls/certs/mijnsslserver.crt
sudo cp ~/easy-rsa/pki/private/mijnweb.key /etc/pki/tls/private/mijnsslserver.key

# Zet correcte permissies
sudo chmod 640 /etc/pki/tls/private/mijnsslserver.key
sudo chown root:ssl-cert /etc/pki/tls/private/mijnsslserver.key
```

### 4.4 Certificaat Verificatie

```bash
# Verificeer server certificaat
openssl x509 -in /etc/pki/tls/certs/mijnsslserver.crt -noout -issuer -subject

# Check validity
openssl x509 -in /etc/pki/tls/certs/mijnsslserver.crt -noout -dates
```

**Output:**
```
issuer=CN = KdG_CA
subject=CN = www.mijnweb.local
notBefore=Oct  3 13:27:26 2025 GMT
notAfter=Jan  6 13:27:26 2028 GMT
```

---

## 5. Apache2 SSL Configuratie

### 5.1 Virtual Host Aanmaken

```bash
sudo touch /etc/apache2/sites-available/sslsite.conf
sudo vi /etc/apache2/sites-available/sslsite.conf
```

**Configuratie:**
```apache
<VirtualHost *:443>
    DocumentRoot /var/www/html
    ServerName www.mijnweb.local

    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/mijnsslserver.crt
    SSLCertificateKeyFile /etc/pki/tls/private/mijnsslserver.key
    SSLCACertificateFile /etc/ssl/certs/cacert.pem
    
    # Optioneel: Logging
    ErrorLog ${APACHE_LOG_DIR}/ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/ssl_access.log combined
</VirtualHost>
```

### 5.2 Site Activeren

```bash
# Activeer de SSL site
sudo a2ensite sslsite

# Test configuratie
sudo apache2ctl configtest

# Herstart Apache
sudo systemctl restart apache2

# Verificeer status
sudo systemctl status apache2
```

### 5.3 Hosts File Configureren

```bash
# Voeg lokale DNS entry toe
echo "127.0.0.1 www.mijnweb.local" | sudo tee -a /etc/hosts
```

---

## 6. TLS Protocol Beveiliging

### 6.1 Minimale TLS Versie Instellen

**Vereiste:** Alleen TLS 1.2 en hoger toestaan (geen SSLv3, TLSv1.0, TLSv1.1)

```bash
sudo vi /etc/apache2/mods-available/ssl.conf
```

**Zoek en wijzig de volgende regels:**
```apache
# Disable oude protocols
SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1

# Gebruik sterke cipher suites
SSLCipherSuite HIGH:!aNULL:!MD5

# Geef server cipher voorkeur
SSLHonorCipherOrder on
```

### 6.2 Apache Herstarten

```bash
sudo systemctl restart apache2
```

### 6.3 TLS Versie Verificatie

```bash
# Test TLS 1.1 (moet falen)
openssl s_client -connect www.mijnweb.local:443 -tls1_1

# Test TLS 1.2 (moet slagen)
openssl s_client -connect www.mijnweb.local:443 -tls1_2

# Test TLS 1.3 (moet slagen)
openssl s_client -connect www.mijnweb.local:443 -tls1_3
```

**Verwachte output voor TLS 1.1:**
```
error:0A0000BF:SSL routines:tls_setup_handshake:no protocols available
```

**Verwachte output voor TLS 1.2/1.3:**
```
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 2048 bit
```

---

## 7. ProFTPD Installatie

### 7.1 Installatie

```bash
sudo apt update
sudo apt install proftpd openssl -y
```

**Tijdens installatie:** Kies **standalone** mode

### 7.2 FTP User Aanmaken

```bash
# Maak dedicated FTP user
sudo adduser ftpuser

# Kies een sterk wachtwoord
# Vul optionele velden in of laat leeg
```

### 7.3 Basis FTP Test (zonder TLS)

```bash
# Installeer FTP client
sudo apt install ftp -y

# Test verbinding
ftp localhost
```

**In FTP prompt:**
```
Name: ftpuser
Password: [jouw_wachtwoord]
ftp> ls
ftp> quit
```

---

## 8. ProFTPD TLS Configuratie

### 8.1 TLS Module Activeren

```bash
sudo vi /etc/proftpd/proftpd.conf
```

**Zoek en uncomment deze regel:**
```apache
Include /etc/proftpd/tls.conf
```

### 8.2 TLS Configuratie

```bash
# Maak nieuwe TLS configuratie
sudo tee /etc/proftpd/tls.conf > /dev/null << 'EOF'
<IfModule mod_tls.c>
    TLSEngine on
    TLSLog /var/log/proftpd/tls.log
    TLSProtocol TLSv1.2 TLSv1.3

    # Hergebruik Apache certificaten
    TLSRSACertificateFile /etc/pki/tls/certs/mijnsslserver.crt
    TLSRSACertificateKeyFile /etc/pki/tls/private/mijnsslserver.key
    TLSCACertificateFile /etc/ssl/certs/cacert.pem

    # Client verificatie uitschakelen
    TLSVerifyClient off
    
    # TLS verplicht maken
    TLSRequired on

    # Compatibiliteit opties
    TLSOptions NoSessionReuseRequired
</IfModule>
EOF
```

### 8.3 Passive Mode Configureren (Optioneel)

Voor betere compatibiliteit met firewalls:

```bash
sudo vi /etc/proftpd/proftpd.conf
```

**Voeg toe aan het einde:**
```apache
# Passive ports voor data transfers
PassivePorts 49152 65534
```

### 8.4 ProFTPD Herstarten

```bash
# Restart service
sudo systemctl restart proftpd

# Check status
sudo systemctl status proftpd

# Check logs
sudo tail -f /var/log/proftpd/proftpd.log
```

---

## 9. Testing en Verificatie

### 9.1 Apache HTTPS Test

#### Browser Test
1. Open browser: `https://www.mijnweb.local`
2. Accepteer self-signed certificaat waarschuwing
3. Bekijk certificaat details (Common Name = www.mijnweb.local, Issuer = KdG_CA)

#### Command Line Test
```bash
# Volledige SSL handshake
openssl s_client -connect www.mijnweb.local:443 -showcerts

# Certificaat chain bekijken
openssl s_client -connect www.mijnweb.local:443 -showcerts 2>/dev/null | grep -A 1 "subject="
```

**Verwachte output:**
```
subject=CN = www.mijnweb.local
issuer=CN = KdG_CA
```

### 9.2 ProFTPD FTPS Test

#### Met lftp (Command Line)

```bash
# Installeer lftp
sudo apt install lftp -y

# Verbind met FTPS
lftp -u ftpuser ftps://localhost

# Na inloggen
pwd          # Toon current directory
ls           # List files
quit         # Exit
```

#### Met FileZilla (GUI)

**Vereist:** FileZilla moet geïnstalleerd zijn

```bash
sudo apt install filezilla -y
filezilla &
```

**FileZilla Configuratie:**

1. **Site Manager** (Ctrl+S)
2. **New Site** → Naam: "FTPS Test"
3. **Instellingen:**
   - **Protocol:** FTP - File Transfer Protocol
   - **Host:** localhost (of server IP)
   - **Port:** 21
   - **Encryption:** **Require explicit FTP over TLS** ✓
   - **Logon Type:** Normal
   - **User:** ftpuser
   - **Password:** [jouw_wachtwoord]

4. **Connect**
5. **Certificaat waarschuwing:** Klik "OK" / "Always trust this certificate"

**Succesvolle verbinding:**
- Status: "Directory listing successful"
- TLS connection established
- Files verschijnen in remote panel

### 9.3 TLS Logs Verificatie

```bash
# Apache TLS logs
sudo tail -20 /var/log/apache2/ssl_access.log

# ProFTPD TLS logs
sudo tail -20 /var/log/proftpd/tls.log
```

**ProFTPD TLS log voorbeeld:**
```
TLS/TLS-C requested, starting TLS handshake
TLSv1.3 connection accepted, using cipher TLS_AES_256_GCM_SHA384
```

---

## 10. Troubleshooting

### 10.1 Apache Problemen

#### Error: "Could not reliably determine server's FQDN"

```bash
# Voeg ServerName toe aan Apache config
echo "ServerName localhost" | sudo tee -a /etc/apache2/apache2.conf
sudo systemctl restart apache2
```

#### Error: Port 80/443 already in use

```bash
# Check wat er op de poort draait
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicterende service (bijv. nginx)
sudo systemctl stop nginx
sudo systemctl disable nginx
```

#### SSL Certificaat Errors

```bash
# Verificeer certificaat paths
ls -l /etc/pki/tls/certs/mijnsslserver.crt
ls -l /etc/pki/tls/private/mijnsslserver.key

# Check permissies
sudo chmod 644 /etc/pki/tls/certs/mijnsslserver.crt
sudo chmod 640 /etc/pki/tls/private/mijnsslserver.key
```

### 10.2 ProFTPD Problemen

#### Error: "Connection refused" bij data transfers

**Probleem:** Passive mode werkt niet

**Oplossing 1:** Gebruik active mode
```bash
lftp -u ftpuser -e "set ftp:passive-mode false" ftps://localhost
```

**Oplossing 2:** Configureer passive ports
```bash
# Voeg toe aan /etc/proftpd/proftpd.conf
PassivePorts 49152 65534

# Open firewall (indien van toepassing)
sudo ufw allow 49152:65534/tcp
```

#### TLS Handshake Fails

```bash
# Check TLS logs
sudo tail -50 /var/log/proftpd/tls.log

# Verificeer certificaat pad in tls.conf
sudo cat /etc/proftpd/tls.conf | grep Certificate

# Test certificaat handmatig
openssl s_client -connect localhost:21 -starttls ftp
```

#### ProFTPD Start Errors

```bash
# Check configuratie syntax
sudo proftpd -t

# Check gedetailleerde logs
sudo journalctl -xeu proftpd.service

# Herstart met verbose mode
sudo proftpd -nd9
```

### 10.3 Algemene Debug Commands

```bash
# Check open poorten
sudo netstat -tlnp | grep -E ':(80|443|21)'

# Check service status
sudo systemctl status apache2
sudo systemctl status proftpd

# Check logs real-time
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/proftpd/proftpd.log

# Test DNS resolution
ping www.mijnweb.local
```

---

## Samenvatting Behaalde Doelen

### ✅ Apache2 SSL/TLS
- Apache2 geïnstalleerd met SSL module
- Self-signed Certificate Authority opgezet (Easy-RSA)
- Server certificaat gegenereerd en gesigneerd door CA
- Virtual Host geconfigureerd voor HTTPS (poort 443)
- TLS 1.2 en 1.3 enforced (oudere protocols disabled)
- Certificaat chain correct geconfigureerd

### ✅ ProFTPD FTPS
- ProFTPD geïnstalleerd in standalone mode
- FTP user aangemaakt (ftpuser)
- TLS module geactiveerd en geconfigureerd
- Explicit FTPS (AUTH TLS) werkend
- Certificaten hergebruikt van Apache setup
- Getest met zowel lftp als FileZilla

### ✅ Beveiliging
- Alle communicatie encrypted met TLS
- Minimale TLS versie: 1.2
- Sterke cipher suites gebruikt
- Private keys correct beveiligd (permissies)
- Self-signed CA voor internal testing

---

## Certificaat Informatie

### CA Certificaat
- **Locatie:** `/etc/ssl/certs/cacert.pem`
- **Common Name:** KdG_CA
- **Validity:** 10 jaar
- **Key Type:** RSA 2048-bit

### Server Certificaat
- **Locatie:** `/etc/pki/tls/certs/mijnsslserver.crt`
- **Common Name:** www.mijnweb.local
- **Issuer:** KdG_CA
- **Validity:** 825 dagen
- **Key Type:** RSA 2048-bit
- **Signature Algorithm:** SHA256

### Private Key
- **Locatie:** `/etc/pki/tls/private/mijnsslserver.key`
- **Passphrase:** Geen (nopass - voor automatisch opstarten)
- **Permissies:** 640 (root:ssl-cert)

---

## Belangrijke Bestanden

### Apache2
```
/etc/apache2/sites-available/sslsite.conf  → Virtual Host configuratie
/etc/apache2/mods-available/ssl.conf       → SSL module instellingen
/etc/apache2/ports.conf                     → Poort configuratie
/var/log/apache2/ssl_access.log            → HTTPS access logs
/var/log/apache2/ssl_error.log             → HTTPS error logs
```

### ProFTPD
```
/etc/proftpd/proftpd.conf                  → Main configuratie
/etc/proftpd/tls.conf                      → TLS configuratie
/var/log/proftpd/proftpd.log               → FTP logs
/var/log/proftpd/tls.log                   → TLS handshake logs
```

### Certificaten
```
/etc/ssl/certs/cacert.pem                  → CA certificaat (public)
/etc/ssl/private/cakey.pem                 → CA private key
/etc/pki/tls/certs/mijnsslserver.crt       → Server certificaat
/etc/pki/tls/private/mijnsslserver.key     → Server private key
~/easy-rsa/pki/                            → Easy-RSA PKI directory
```

---

## Referenties

- [Apache SSL/TLS Documentation](https://httpd.apache.org/docs/2.4/ssl/)
- [ProFTPD TLS Documentation](http://www.proftpd.org/docs/contrib/mod_tls.html)
- [Easy-RSA Documentation](https://easy-rsa.readthedocs.io/)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

---

**Lab Voltooid:** 3 Oktober 2025  
**Status:** ✅ Alle doelstellingen behaald