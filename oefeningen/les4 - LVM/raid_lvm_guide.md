# RAID + LVM Setup Guide - CentOS

## 1. Virtuele Machine Configuratie

### VM Specificaties:
- **OS**: Red Hat Linux 64 bit (CentOS)
- **RAM**: 2048MB
- **Storage**: 
  - Twee identieke schijven van 20GB (raid1.vdi, raid2.vdi)
  - 1 schijf van 100MB (home1.vmdk)
  - 1 schijf van 200MB (home2.vmdk)
- **Netwerk**: NAT + Host-Only netwerkkaart

### Belangrijke Opmerkingen:
- Maak eerst alle schijven aan voordat je de VM opstart
- Kies "CentOS Server" tijdens installatie (geen GUI)
- Verwijder de standaard schijf die UTM/VM software aanmaakt
- Selecteer "Custom" bij opslagconfiguratie

## 2. Partitionering en RAID Setup

### Stap 1: Partities aanmaken op eerste schijf (vdb)

```bash
fdisk /dev/vdb
```

Maak de volgende partities aan:
- **vdb1**: 1000MB (voor /boot RAID)
- **vdb2**: 1000MB (voor swap RAID)
- **vdb3**: Resterende ruimte (~18GB) (voor root LVM)

### Stap 2: Partitietypes instellen op RAID

```bash
fdisk /dev/vdb
# Gebruik 't' command om partitietypes te wijzigen
# Stel alle partities in op type 'fd' (Linux raid autodetect)
t
1
fd
t
2  
fd
t
3
fd
w  # Schrijf wijzigingen
```

### Stap 3: RAID Arrays aanmaken

**Opmerking**: In deze setup gebruiken we degraded RAID1 (met slechts 1 schijf) vanwege macOS compatibiliteitsproblemen.

```bash
# RAID1 voor /boot partitie
mdadm --create /dev/md1 --level=1 --raid-devices=1 --force /dev/vdb1
# Antwoord 'y' voor write-intent bitmap
# Antwoord 'y' om door te gaan

# RAID1 voor swap partitie
mdadm --create /dev/md2 --level=1 --raid-devices=1 --force /dev/vdb2
# Antwoord 'y' voor write-intent bitmap
# Antwoord 'y' om door te gaan

# RAID1 voor root partitie (LVM)
mdadm --create /dev/md3 --level=1 --raid-devices=1 --force /dev/vdb3
# Antwoord 'y' om door te gaan
```

### Stap 4: RAID Status controleren

```bash
cat /proc/mdstat
```

Expected output:
```
Personalities : [raid1] 
md3 : active raid1 vdb3[0]
      18905088 blocks super 1.2 [1/1] [U]
      
md2 : active raid1 vdb2[0]
      1022976 blocks super 1.2 [1/1] [U]
      bitmap: 0/1 pages [0KB], 65536KB chunk

md1 : active raid1 vdb1[0]
      1022976 blocks super 1.2 [1/1] [U]
      bitmap: 0/1 pages [0KB], 65536KB chunk
```

## 3. LVM Setup voor Root Partitie

### Stap 1: Physical Volume aanmaken

```bash
pvcreate /dev/md3
```

### Stap 2: Volume Group aanmaken

```bash
vgcreate vg-root /dev/md3
```

### Stap 3: Logical Volume aanmaken

```bash
lvcreate -n root -L 15G vg-root
```

### Stap 4: Filesystem aanmaken

```bash
mkfs.ext4 /dev/vg-root/root
```

## 4. Home Directory Setup (LVM zonder RAID)

### Stap 1: Physical Volumes aanmaken

```bash
pvcreate /dev/vdc  # 100MB schijf
pvcreate /dev/vdd  # 200MB schijf
```

### Stap 2: Volume Group aanmaken

```bash
vgcreate VolGroupHome /dev/vdc /dev/vdd
```

### Stap 3: Logical Volume aanmaken

```bash
lvcreate -n LogVolHome -l 100%FREE VolGroupHome
```

### Stap 4: Filesystem aanmaken

```bash
mkfs.ext4 /dev/VolGroupHome/LogVolHome
```

## 5. Boot Partitie en Swap Setup

### Boot partitie formatteren

```bash
mkfs.ext4 /dev/md1
```

### Swap partitie aanmaken

```bash
mkswap /dev/md2
```

## 6. Verificatie en Testing

### RAID Status controleren

```bash
cat /proc/mdstat
mdadm --detail /dev/md1
mdadm --detail /dev/md2
mdadm --detail /dev/md3
```

### LVM Status controleren

```bash
pvdisplay
vgdisplay
lvdisplay
```

### Filesystems testen

```bash
# Test mount points aanmaken
mkdir -p /mnt/test-root
mkdir -p /mnt/test-home

# Mount en test
mount /dev/vg-root/root /mnt/test-root
mount /dev/VolGroupHome/LogVolHome /mnt/test-home

# Controleer beschikbare ruimte
df -h

# Unmount na test
umount /mnt/test-root /mnt/test-home
```

## 7. Configuratie Overzicht

### Uiteindelijke Setup:
- **md1**: /boot partitie (1GB, RAID1, ext4)
- **md2**: swap partitie (1GB, RAID1)
- **md3**: LVM Physical Volume voor root (18GB, RAID1)
  - **vg-root/root**: root filesystem (15GB, ext4)
- **VolGroupHome/LogVolHome**: home directory (292MB, spanning vdc+vdd)

### Voordelen van deze Setup:
1. **Redundantie**: RAID1 mirror voor kritieke partities
2. **Flexibiliteit**: LVM voor eenvoudige resize operaties
3. **Schaalbaarheid**: Gemakkelijk uitbreiden van volume groups
4. **Betrouwbaarheid**: Gescheiden storage voor verschillende doeleinden

## 8. Troubleshooting Tips

### Veel voorkomende problemen:
1. **"Device busy" errors**: Zorg dat partities niet gemount zijn
2. **RAID niet starten**: Controleer partitie types (fd)
3. **LVM errors**: Verifieer dat PV correct aangemaakt zijn
4. **macOS VM issues**: Gebruik degraded RAID1 als workaround

### Nuttige commands:
```bash
# RAID status
cat /proc/mdstat

# LVM cleanup (indien nodig)
lvremove -f /dev/vg-name/lv-name
vgremove -f vg-name
pvremove /dev/device

# Filesystem check
fsck /dev/device
```

## 9. Documentatie en Verificatie

Bewaar configuratie details:
```bash
# Maak rapport aan
cat /proc/mdstat > /root/raidok.txt
echo "=== RAID Details ===" >> /root/raidok.txt
mdadm --detail /dev/md1 >> /root/raidok.txt
mdadm --detail /dev/md2 >> /root/raidok.txt
mdadm --detail /dev/md3 >> /root/raidok.txt
echo "=== LVM Configuration ===" >> /root/raidok.txt
pvdisplay >> /root/raidok.txt
vgdisplay >> /root/raidok.txt
lvdisplay >> /root/raidok.txt
echo "=== Mounted Filesystems ===" >> /root/raidok.txt
df -h >> /root/raidok.txt
```

Deze setup biedt een robuuste basis voor een Linux server met redundantie en flexibele storage management.