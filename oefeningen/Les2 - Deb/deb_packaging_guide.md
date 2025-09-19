# Complete DEB Packaging Guide - Snake Game Praktijkvoorbeeld

## 1. Voorbereiding Environment

### Email en Username Instellen
```bash
#!/bin/bash
cat >>~/.bashrc <<EOF
DEBEMAIL="younes.elazzouzi@student.kdg.be"
DEBFULLNAME="Younes El Azzouzi"
export DEBEMAIL DEBFULLNAME
EOF

source ~/.bashrc

# Controleren
env | grep -E "DEBEMAIL|DEBFULLNAME"
```

### Nodige Pakketten Installeren
```bash
sudo apt-get install -y dh-make debhelper fakeroot devscripts lintian python3-tk
```

## 2. Maken van de Package Structuur

### Create Script voor Snake Package
```bash
#!/bin/bash
# Create my first debian package
package="snake"
version="1"
mkdir -p "${package}/${package}-${version}"
cd "${package}/${package}-${version}"

# Maak het executable script
cat > ${package} <<EOF
#!/bin/sh
exec python3 /usr/lib/snake/snake.py "\$@"
EOF

chmod 755 $package
cd ..
tar -cvzf ${package}-${version}.tar.gz ${package}-${version}
```

### DH_MAKE Uitvoeren
```bash
cd snake/snake-1
dh_make --native
# Kies: s (single binary)
# Bevestig details met Y
```

## 3. Debian Directory Configureren

### Control File Aanpassen
**Locatie:** `debian/control`

```
Source: snake
Section: games
Priority: optional
Maintainer: Younes El Azzouzi <younes.elazzouzi@student.kdg.be>
Build-Depends: debhelper-compat (= 13)
Standards-Version: 4.6.2
Rules-Requires-Root: no

Package: snake
Architecture: all
Depends: ${misc:Depends}, python3, python3-tk
Description: Arcadespel in Python (Tkinter)
 Een eenvoudige Snake-app in Python met Tkinter. Installeert een launcher
 in het menu en het commando "snake" dat /usr/lib/snake/snake.py start.
```

**Belangrijke velden:**
- **Section:** `games` (voor spellen)
- **Architecture:** `all` (platformonafhankelijk)
- **Dependencies:** python3, python3-tk voor Tkinter
- **Description:** Korte lijn + uitgebreide beschrijving (met spaties)

### Manpage Aanmaken
```bash
# Hernoem template
mv manpage.1.ex snake.1

# Maak manpages file
echo "debian/snake.1" > manpages
```

**Inhoud snake.1:**
```
.TH Snake 1 "September 19 2025"
.SH NAME
snake \- start de snake game
.SH SYNOPSIS
.B snake
.SH DESCRIPTION
Start de Python/Tkinter Snake applicatie.
.SH SEE ALSO
python3(1)
```

### Install File - Cruciale Component
**Locatie:** `debian/install`

```
snake usr/games
snake.py usr/lib/snake/
debian/snake.desktop usr/share/applications/
```

**Waarom usr/games?**
- Games horen in `/usr/games/` i.p.v. `/usr/bin/`
- Volgt Debian policy voor spelletjes

### Desktop Entry voor Menu Integratie
**Locatie:** `debian/snake.desktop`

```ini
[Desktop Entry]
Name=Snake
Comment=Snake game in Python
GenericName=Snake
Exec=python3 /usr/lib/snake/snake.py
Icon=snake
Terminal=false
Type=Application
Categories=Game;
```

### Menu File (Debian Legacy)
**Locatie:** `debian/menu`

```
?package(snake):needs="X11" section="Applications/Games" \
 title="Snake" command="/usr/bin/snake"
```

### Rules File Minimaliseren
**Locatie:** `debian/rules`

```makefile
#!/usr/bin/make -f
%:
	dh $@
```

## 4. Cleanup en Bouwen

### Templates Verwijderen
```bash
rm -f debian/*.ex debian/*.EX debian/README.* \
      debian/manpage.*.ex debian/salsa-ci.yml.ex \
      debian/postinst.ex debian/postrm.ex debian/preinst.ex debian/prerm.ex \
      debian/snake.cron.d.ex debian/snake.doc-base.ex \
      debian/menu 2>/dev/null || true
```

### Package Bouwen
```bash
debuild -us -uc
```

**Flags:**
- `-us`: unsigned source
- `-uc`: unsigned changes

## 5. Veelvoorkomende Issues en Oplossingen

### Lintian Fouten
```bash
# Controleer package
lintian -i --color always ../snake_1_all.deb
```

**Veel voorkomende fouten:**
- **E: helper-templates-in-copyright** → Copyright file opschonen
- **W: binary-without-manpage** → Manpage toevoegen
- **W: readme-debian-contains-debmake-template** → README.Debian verwijderen

### Wrapper Script Probleem
**Probleem:** Snake launcher toonde Zenity warning i.p.v. game

**Oorzaak:** Wrapper bevatte nog demo-code van slides:
```bash
# FOUT - dit was van de Zenity demo
zenity --warning --text="`exec uname -a`"
```

**Oplossing:** Correcte wrapper inhoud:
```bash
#!/bin/sh
exec python3 /usr/lib/snake/snake.py "$@"
```

### Install Paths Corrigeren
Zorg dat je install file verwijst naar de juiste locaties:
```
snake usr/games          # Executable naar games directory  
snake.py usr/lib/snake/   # Python script naar lib directory
debian/snake.desktop usr/share/applications/  # Desktop entry
```

## 6. Package Installeren en Testen

### Installatie
```bash
sudo dpkg -i ../snake_1_all.deb
```

### Testen
```bash
# Via commandline
snake

# Via menu - zoek naar "Snake" in applicatiemenu
```

## 7. Directory Structuur Overzicht

```
snake/snake-1/
├── snake                    # Executable wrapper
├── snake.py                # Python game code
└── debian/
    ├── changelog           # Package versie geschiedenis
    ├── control            # Package metadata
    ├── rules              # Build script
    ├── install            # File installatie mapping
    ├── snake.1            # Manual page
    ├── manpages           # Lijst van manual pages
    ├── snake.desktop      # Desktop entry
    └── copyright          # Copyright informatie
```

## 8. Best Practices

### File Permissions
- Executables: `755`
- Documentation: `644`
- Manual pages: `644`

### Debian Policy Compliance
- Games in `/usr/games/`
- Libraries in `/usr/lib/pakket/`
- Icons in `/usr/share/pixmaps/`
- Desktop entries in `/usr/share/applications/`
- Documentation in `/usr/share/doc/pakket/`

### Architecture Guidelines
- `all`: Platform-independent (scripts, data)
- `amd64`: x86_64 binaries
- `i386`: 32-bit binaries
- `any`: Compile for target architecture

## 9. Handtekenen (Optioneel)

### GPG Key Aanmaken
```bash
gpg --gen-key
gpg --armor --export email@domain.com > public_key.asc
```

### Package Handtekenen
```bash
# Met debuild (automatisch)
debuild

# Bestaande deb handtekenen
dpkg-sig --sign builder package.deb
```

Deze guide combineert de theoretische kennis uit de slides met praktische ervaring van het bouwen van een Snake-game DEB package, inclusief alle gevonden problemen en oplossingen.