# Linux Performance Monitoring en Systeem Beheer Tutorial

Deze tutorial behandelt verschillende aspecten van Linux performance monitoring, process accounting, netwerk beheer, swap configuratie en systeem diagnostics.

## 1. Performance Meting met `time`

### Bestandskopie timing
```bash
time cp /media/cdrom/grootbestand.iso /tmp/test.iso
```

Het `time` commando toont drie belangrijke metrieken:
- **Real time**: Totale tijd van start tot eind
- **User time**: CPU tijd besteed in user mode
- **Sys time**: CPU tijd besteed in kernel mode

**Tip**: Voer de test meerdere keren uit om cache-effecten te zien - de tweede keer zal meestal sneller zijn door filesystem caching.

## 2. Process Accounting met `acct`

### Installatie en activatie
```bash
sudo apt-get install acct
sudo touch /var/account/pacct
sudo chmod 664 /var/account/pacct
sudo accton /var/account/pacct
```

### Recente commando's bekijken
```bash
lastcomm | head
```

**Voorbeeld uitvoer:**
```
accton                 root     pts/1      0.00 secs Sun Sep 21 11:07
date                   root     __         0.00 secs Sun Sep 21 11:07
sleep                  root     __         0.00 secs Sun Sep 21 11:07
sudo             S     ubuntu   pts/0      0.00 secs Sun Sep 21 11:07
```

### Process statistieken
```bash
sa
```

**Top processen in het voorbeeld:**
1. **lsb_release** - 332 executions, 0.05cp CPU time
2. **apt-check** - 2 executions, 0.05cp CPU time  
3. **apt-get** - 3 executions, 0.03cp CPU time
4. **gzip** - 49 executions, 0.01cp CPU time

## 3. Systeem Monitoring met `vmstat`

### Resource monitoring
```bash
vmstat 2 10  # Elke 2 seconden, 10 metingen
```

**Belangrijke kolommen:**
- **r**: Processen die wachten op CPU
- **b**: Processen die wachten op I/O
- **swpd**: Virtueel geheugen gebruikt
- **free**: Vrij geheugen
- **buff/cache**: Buffer en cache geheugen

**Resultaten uit het voorbeeld:**
- **Maximaal aantal processen dat wacht op CPU (r)**: 1
- **Maximaal aantal processen dat wacht op I/O (b)**: 0

## 4. Kernel Cache Analyse

### Slab cache bekijken
```bash
sudo slabtop
```

**Belangrijke informatie:**
- Toont kernel cache usage
- **buffer_head** gebruikt vaak het meeste geheugen
- Kijk naar de **CACHE_SIZE** kolom voor geheugengebruik

## 5. Inter-Process Communication (IPC) Status

### IPC resources controleren
```bash
ipcs
```

**Controleert drie IPC mechanismen:**
- **Message Queues**: Voor message passing
- **Shared Memory Segments**: Voor gedeeld geheugen  
- **Semaphore Arrays**: Voor synchronisatie

**In het voorbeeld**: Alle secties zijn leeg, dus geen IPC communicatie actief.

## 6. Process Memory Analyse

### Libraries van een proces bekijken
```bash
ldd /usr/bin/vi
```

**Voorbeeld uitvoer:**
```
linux-vdso.so.1 (0x0000ffffa7ea0000)
libm.so.6 => /lib/aarch64-linux-gnu/libm.so.6
libtinfo.so.6 => /lib/aarch64-linux-gnu/libtinfo.so.6
libselinux.so.1 => /lib/aarch64-linux-gnu/libselinux.so.1
```

### Memory mapping van een proces
```bash
# Eerst vi process ID vinden
ps aux | grep vi

# Memory mapping bekijken
sudo pmap -x <PID>
```

**Verschil tussen ldd en pmap:**
- **ldd**: Toont alle libraries die het programma **zou kunnen** gebruiken
- **pmap**: Toont de daadwerkelijk **geladen** memory regions van een draaiend proces

## 7. Disk Performance Testing

### hdparm installatie en gebruik
```bash
sudo apt-get install hdparm

# Beschikbare disks bekijken
lsblk

# Disk performance testen
sudo hdparm -tT /dev/vda
```

**Voorbeeld resultaat:**
```
/dev/vda:
 Timing cached reads:   46180 MB in  1.99 seconds = 23181.10 MB/sec
 Timing buffered disk reads: 4286 MB in  3.00 seconds = 1427.25 MB/sec
```

**Betekenis:**
- **Cached reads**: Snelheid van data uit RAM cache
- **Buffered disk reads**: Werkelijke disk read snelheid

## 8. Netwerk Monitoring met `lsof`

### Processen die netwerk gebruiken
```bash
sudo lsof -i
```

**Belangrijke processen uit het voorbeeld:**
- **systemd-resolve**: DNS resolver (poort 53)
- **cupsd**: Print server (poort 631)  
- **sshd**: SSH daemon (poort 22)
- **nginx**: Web server (poort 80)
- **avahi-daemon**: Service discovery

## 9. Virtual Network Interfaces

### Dummy interface aanmaken
```bash
# Dummy module laden
sudo modprobe dummy

# Interface aanmaken
sudo ip link add dummy1 type dummy

# IP adres toewijzen
sudo ip addr add 1.2.3.4/24 dev dummy1

# Interface activeren
sudo ip link set dummy1 up

# Testen
ping -c 4 1.2.3.4

# Interface verwijderen
sudo ip link del dummy1
```

## 10. CPU Limiting

### Oneindige loop script maken
```bash
tee loop.sh > /dev/null <<'EOF'
#!/bin/bash
# Oneindige loop
while true; do
  :   # doet niks, houdt CPU bezig
done
EOF

chmod +x loop.sh
```

### CPU usage beperken
```bash
# Script op achtergrond starten
./loop.sh &

# cpulimit installeren
sudo apt-get install cpulimit

# CPU usage beperken tot 10%
sudo cpulimit --pid <PID> --limit 10
```

## 11. Swap Management

### Swapfile aanmaken
```bash
# 512MB swapfile aanmaken
sudo dd if=/dev/zero of=/pagefile.sys bs=1M count=512

# Permissions instellen
sudo chmod 600 /pagefile.sys

# Swap formatteren
sudo mkswap /pagefile.sys

# Swap activeren
sudo swapon /pagefile.sys

# Status controleren
swapon --show
free -h
```

### Waarom swapartitie vs swapfile?

**Swapartitie voordelen:**
- **Performance**: Directe disk access, geen filesystem overhead
- **Betrouwbaarheid**: Niet afhankelijk van filesystem integriteit
- **Fragmentatie**: Geen fragmentatie issues

**Swapfile voordelen:**
- **Flexibiliteit**: Eenvoudig aan te maken en te vergroten
- **Beheer**: Geen partitie management nodig

## 12. Swap Behavior Tuning

### Swappiness parameter aanpassen
```bash
# Huidige waarde bekijken
cat /proc/sys/vm/swappiness

# Maximaal swappen (100 = agressief swappen)
sudo sysctl vm.swappiness=100

# Verificatie
cat /proc/sys/vm/swappiness
```

### Memory stress testing
```bash
# Stress tool installeren
sudo apt-get install stress

# Memory stress test
stress --vm 2 --vm-bytes 256M --timeout 30s
```

**Swappiness waarden:**
- **0**: Swap alleen bij absoluut noodzaak
- **60**: Default waarde (balanced)
- **100**: Agressief swappen, prefereer swap boven cache

## 13. Source Code Compilation

### C/C++ programma's compileren
```bash
# C programma compileren
gcc -o program program.c

# C++ programma compileren  
g++ -o program program.cpp

# Programma uitvoeren
./program
```

**Voor webserver gerelateerde programma's:**
```bash
# Apache starten (indien nodig voor b.c)
sudo systemctl start apache2
sudo systemctl status apache2
```

## Nuttige Monitoring Commando's

### Algemene system monitoring
```bash
# CPU usage
top
htop

# Memory usage
free -h
cat /proc/meminfo

# Disk usage
df -h
du -sh /path/to/directory

# Network connections
netstat -tuln
ss -tuln

# Process tree
pstree

# System load
uptime
w

# Kernel ring buffer
dmesg | tail

# System logs
journalctl -f
```

### Performance profiling tools
```bash
# IO statistics
iostat -x 1

# Network statistics  
ifstat

# Process monitoring
pidstat 1

# System activity reporter
sar -u 1 10
```

## Best Practices

1. **Monitoring**: Gebruik meerdere tools voor complete system overview
2. **Baseline**: Etableer normale waarden voor je systeem
3. **Trending**: Monitor trends over tijd, niet alleen momentopnames
4. **Documentation**: Documenteer configuratie wijzigingen
5. **Testing**: Test performance wijzigingen in gecontroleerde omgeving
6. **Automation**: Automatiseer routine monitoring tasks

## Troubleshooting Tips

- **Hoge load**: Controleer met `top`, `vmstat`, en `iostat`
- **Memory issues**: Check met `free`, `pmap`, en `/proc/meminfo`
- **Network problems**: Gebruik `lsof -i`, `netstat`, en `tcpdump`
- **Disk issues**: Monitor met `iostat`, `iotop`, en `df`
- **Process issues**: Analyseer met `ps`, `pstree`, en `strace`