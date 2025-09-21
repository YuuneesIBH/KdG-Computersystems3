# Linux Systemd en Service Management Tutorial

Deze tutorial behandelt het beheren van services in Linux met systemd, het analyseren van opstarttijden, en het maken van eigen custom services.

## 1. Installatie en verkenning van chkservice

### chkservice installeren

```bash
sudo apt install chkservice
```

### Geïnstalleerde bestanden bekijken

Om te zien welke bestanden een pakket heeft geïnstalleerd:

```bash
dpkg -L chkservice
```

**Uitvoer:**
```
/.
/usr
/usr/bin
/usr/bin/chkservice
/usr/share
/usr/share/doc
/usr/share/doc/chkservice
/usr/share/doc/chkservice/changelog.Debian.gz
/usr/share/doc/chkservice/copyright
/usr/share/man
/usr/share/man/man8
/usr/share/man/man8/chkservice.8.gz
```

## 2. Analyse van opstarttijden met systemd-analyze

### Services met langste opstarttijd weergeven

```bash
systemd-analyze blame
```

**Resultaat van langzaamste services:**
```
2.004s systemd-networkd-wait-online.service
1.189s snapd.service
962ms  dev-mapper-ubuntu\x2d\x2dvg\x2dubuntu\x2d\x2dlv.device
894ms  cloud-init-local.service
```

De 4 services die het meeste tijd in beslag nemen:
1. **systemd-networkd-wait-online.service** (2.004s)
2. **snapd.service** (1.189s) 
3. **dev-mapper-ubuntu-vg-ubuntu-lv.device** (962ms)
4. **cloud-init-local.service** (894ms)

## 3. Service beheer met systemctl

### Nginx service stoppen en starten

```bash
sudo systemctl stop nginx
sudo systemctl start nginx
systemctl is-active nginx
```

### Service logs bekijken

```bash
journalctl -u nginx
```

**Voorbeeld uitvoer:**
```
Sep 21 10:40:43 ubuntu systemd[1]: Starting A high performance web server...
Sep 21 10:40:43 ubuntu systemd[1]: Started A high performance web server...
Sep 21 10:41:12 ubuntu systemd[1]: Stopping A high performance web server...
Sep 21 10:41:12 ubuntu systemd[1]: nginx.service: Deactivated successfully.
Sep 21 10:41:12 ubuntu systemd[1]: Stopped A high performance web server...
```

## 4. Custom Service: Hello World Daemon

### Eenvoudige versie van het script

```bash
#!/bin/bash

case "$1" in
  start)
    while true
    do
      echo "Hello World op $(date)"
      sleep 10
    done
    ;;
  stop)
    exit 0
    ;;
  *)
    echo "Gebruik: $0 {start|stop}"
    exit 1
    ;;
esac
```

### Geavanceerde versie met PID management

Script maken in `/usr/local/sbin/helloworldd`:

```bash
sudo tee /usr/local/sbin/helloworldd >/dev/null <<'EOF'
#!/bin/bash
PIDFILE=/run/helloworldd.pid

start() {
  mkdir -p /run
  echo $$ > "$PIDFILE"
  while true; do
    echo "Hello World op $(date)"
    sleep 10
  done
}

stop() {
  [ -f "$PIDFILE" ] && kill "$(cat "$PIDFILE")" && rm -f "$PIDFILE"
}

case "$1" in
  start) start ;;
  stop)  stop  ;;
  *)     echo "Gebruik: $0 {start|stop}"; exit 1 ;;
esac
EOF

sudo chmod +x /usr/local/sbin/helloworldd
```

### Systemd service file maken

Service file aanmaken in `/etc/systemd/system/helloworldd.service`:

```bash
sudo tee /etc/systemd/system/helloworldd.service >/dev/null <<'EOF'
[Unit]
Description=Hello World Service

[Service]
Type=simple
ExecStart=/usr/local/sbin/helloworldd start
ExecStop=/usr/local/sbin/helloworldd stop
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### Service activeren en testen

```bash
# Systemd configuratie herladen
sudo systemctl daemon-reload

# Service starten
sudo systemctl start helloworldd

# Status controleren
systemctl status helloworldd

# Logs bekijken
journalctl -u helloworldd -n 20 --no-pager

# Service stoppen
sudo systemctl stop helloworldd

# Service status controleren
systemctl is-active helloworldd
```

## 5. Custom Firewall Service

### Vereisten installeren

```bash
sudo apt install iptables -y
```

### Firewalld script maken

Script in `/usr/local/sbin/firewalld`:

```bash
sudo tee /usr/local/sbin/firewalld >/dev/null <<'EOF'
#!/bin/bash

firewalld_stop() {
  iptables -F
  iptables -X
  iptables -P INPUT ACCEPT
  iptables -P FORWARD ACCEPT
  iptables -P OUTPUT ACCEPT
}

firewalld_start() {
  iptables -F
  iptables -X
  iptables -P INPUT ACCEPT
  iptables -P FORWARD ACCEPT
  iptables -P OUTPUT ACCEPT
  iptables -A INPUT -p icmp -j DROP
  iptables -A OUTPUT -p icmp -j DROP
}

case "$1" in
  start)
    firewalld_start
    ;;
  stop)
    firewalld_stop
    ;;
  restart|reload)
    firewalld_stop
    firewalld_start
    ;;
  *)
    echo "Gebruik: $0 {start|stop|restart|reload}"
    exit 1
    ;;
esac
EOF

sudo chmod +x /usr/local/sbin/firewalld
```

### Functionaliteit testen

```bash
# Firewall starten (blokkeert ICMP)
sudo /usr/local/sbin/firewalld start

# Ping test - zou moeten falen
ping -c 2 8.8.8.8

# Firewall stoppen (staat ICMP weer toe)
sudo /usr/local/sbin/firewalld stop

# Ping test - zou moeten slagen
ping -c 2 8.8.8.8
```

### Systemd service file voor firewalld

```bash
sudo tee /etc/systemd/system/firewalld.service >/dev/null <<'EOF'
[Unit]
Description=Custom Firewall Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/firewalld start
ExecStop=/usr/local/sbin/firewalld stop
ExecReload=/usr/local/sbin/firewalld reload
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
```

### Service configureren en activeren

```bash
# Systemd configuratie herladen
sudo systemctl daemon-reload

# Service starten
sudo systemctl start firewalld

# Status controleren
sudo systemctl status firewalld

# Service inschakelen voor automatische start
sudo systemctl enable firewalld
```

## Belangrijke systemd concepten

### Service Types
- **simple**: Het proces blijft op de voorgrond draaien
- **forking**: Het proces start een achtergrondproces en stopt zelf
- **oneshot**: Het proces voert een taak uit en stopt

### Nuttige systemctl commando's

```bash
# Service status bekijken
systemctl status <service>

# Service starten/stoppen/herstarten
sudo systemctl start <service>
sudo systemctl stop <service>
sudo systemctl restart <service>

# Service in-/uitschakelen voor automatische start
sudo systemctl enable <service>
sudo systemctl disable <service>

# Logs bekijken
journalctl -u <service>
journalctl -u <service> -f  # Follow mode

# Alle services weergeven
systemctl list-units --type=service
```

### Best Practices
- Plaats custom scripts in `/usr/local/sbin/`
- Plaats service files in `/etc/systemd/system/`
- Gebruik `systemctl daemon-reload` na wijzigingen aan service files
- Test scripts eerst handmatig voordat je ze als service configureert
- Gebruik beschrijvende namen en documentatie in je service files