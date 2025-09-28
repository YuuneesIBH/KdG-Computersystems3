# CentOS RAID + LVM Setup - Stap voor Stap

## Stap 1: Controleer je schijven
```bash
lsblk
```
Je zou moeten zien:
- vda (20GB) - gebruikt voor je huidige systeem
- vdb (20GB) - leeg voor RAID
- vdc (100MB) - leeg voor home1
- vdd (200MB) - leeg voor home2

## Stap 2: RAID arrays aanmaken

### BIOS Boot partities (1MB elk)
```bash
# Partities aanmaken op beide RAID schijven
fdisk /dev/vdb
# Maak partitie 1: 1MB, type 'fd' (Linux RAID)

fdisk /dev/vdc
# Maak partitie 1: 1MB, type 'fd' (Linux RAID)
```

### RAID /boot partitie (1000MB)
```bash
# Maak partities voor /boot
fdisk /dev/vdb  # Partitie 2: 1000MB, type 'fd'
fdisk /dev/vdc  # Partitie 2: 1000MB, type 'fd'

# RAID array aanmaken
mdadm --create /dev/md1 --level=1 --raid-devices=2 /dev/vdb2 /dev/vdc2

# Formateren
mkfs.ext4 /dev/md1
```

### RAID swap partitie (2000MB)
```bash
# Maak partities voor swap
fdisk /dev/vdb  # Partitie 3: 2000MB, type 'fd'
fdisk /dev/vdc  # Partitie 3: 2000MB, type 'fd'

# RAID array aanmaken
mdadm --create /dev/md2 --level=1 --raid-devices=2 /dev/vdb3 /dev/vdc3

# Als swap formateren
mkswap /dev/md2
```

## Stap 3: LVM configuratie

### Physical Volumes aanmaken
```bash
# Rest van de RAID schijven
fdisk /dev/vdb  # Partitie 4: rest van schijf, type '8e' (Linux LVM)
fdisk /dev/vdc  # Partitie 4: rest van schijf, type '8e' (Linux LVM)

# Extra schijven
pvcreate /dev/vdb4
pvcreate /dev/vdc4
pvcreate /dev/vdd  # Hele 100MB schijf
```

### Volume Group aanmaken
```bash
vgcreate vg-root /dev/vdb4 /dev/vdc4
vgcreate VolGroupHome /dev/vdd  # 100MB schijf
```

### Logical Volumes aanmaken
```bash
# Root volume in vg-root
lvcreate -n root -L 16G vg-root

# Home volume in VolGroupHome
lvcreate -n LogVolHome -l 100%FREE VolGroupHome
```

## Stap 4: Filesystemen aanmaken
```bash
# Root filesystem
mkfs.ext4 /dev/vg-root/root

# Home filesystem
mkfs.ext4 /dev/VolGroupHome/LogVolHome
```

## Stap 5: Extra 200MB schijf toevoegen
```bash
# Extend VolGroupHome met 200MB schijf
vgextend VolGroupHome /dev/vdd  # 200MB schijf

# Online resize van LogVolHome
lvextend -l +100%FREE /dev/VolGroupHome/LogVolHome
resize2fs /dev/VolGroupHome/LogVolHome
```

## Stap 6: Mount points configureren
```bash
# Tijdelijk mounten om te testen
mkdir -p /mnt/test-root
mkdir -p /mnt/test-home

mount /dev/vg-root/root /mnt/test-root
mount /dev/VolGroupHome/LogVolHome /mnt/test-home
```

## Stap 7: RAID status controleren
```bash
cat /proc/mdstat
mdadm --detail /dev/md1
mdadm --detail /dev/md2
```

## Stap 8: RAID config opslaan
```bash
mdadm --examine --scan >> /etc/mdadm.conf
```

## Test commando's
```bash
# RAID status
cat /proc/mdstat > /root/raidok.txt

# LVM info
pvdisplay
vgdisplay  
lvdisplay

# Disk space
df -h
```