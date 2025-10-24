# Ansible Explained - Uitgebreide Handleiding

## Inhoudsopgave
1. [Wat is Ansible?](#wat-is-ansible)
2. [Ansible Concepten](#ansible-concepten)
3. [Ansible Roles - Diepgaande Uitleg](#ansible-roles)
4. [Praktisch Voorbeeld: Nginx Role](#praktisch-voorbeeld)
5. [Foutoplossing en Best Practices](#foutoplossing)
6. [Apache2 Role Aanpassen](#apache2-role)

---

## Wat is Ansible?

Ansible is een **automation engine** die gebruikt wordt voor:
- **Configuration Management**: Servers configureren
- **Application Deployment**: Applicaties uitrollen
- **Cloud Provisioning**: Cloud infrastructuur beheren
- **Orchestration**: Meerdere systemen coördineren

### Hoe werkt Ansible?

```
┌─────────────────────────────────────┐
│   Ansible Control Node              │
│   (Je lokale machine)                │
│                                      │
│   - Playbooks (YAML)                 │
│   - Inventory (hosts)                │
│   - Roles                            │
└──────────────┬──────────────────────┘
               │
       SSH/WinRM verbindingen
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼───┐
│ Node 1 │          │ Node 2 │
│        │          │        │
└────────┘          └────────┘
```

**Belangrijke eigenschappen:**
- Geen agents nodig op de nodes
- Geen databases nodig
- Verbindt via SSH (Linux) of WinRM (Windows)
- Modules worden tijdelijk naar nodes gepusht en daarna verwijderd
- Gebruikt Python (≥3.8) op de nodes

---

## Ansible Concepten

### 1. Playbook
Een YAML-bestand dat beschrijft **wat** er moet gebeuren op **welke hosts**.

```yaml
---
- name: Deploy Nginx
  hosts: webservers
  become: true
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
```

### 2. Inventory
Lijst van hosts waarop Ansible werkt.

**INI formaat** (`/etc/ansible/hosts`):
```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
```

**YAML formaat**:
```yaml
webservers:
  hosts:
    web1.example.com:
    web2.example.com:
```

### 3. Modules
Herbruikbare units die specifieke taken uitvoeren:

| Module | Functie |
|--------|---------|
| `apt`/`yum` | Packages installeren |
| `service` | Services beheren |
| `copy` | Bestanden kopiëren |
| `template` | Jinja2 templates gebruiken |
| `shell`/`command` | Commands uitvoeren |
| `file` | Bestanden/directories aanmaken |

### 4. Handlers
Taken die alleen uitgevoerd worden als er iets **gewijzigd** is:

```yaml
tasks:
  - name: Update nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx

handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
```

### 5. Variables en Facts

**Variables** (eigen gedefinieerd):
```yaml
vars:
  nginx_port: 80
  server_name: "www.example.com"
```

**Facts** (automatisch verzameld door Ansible):
```yaml
- debug:
    msg: "IP: {{ ansible_default_ipv4.address }}"
    # Hostname: {{ ansible_facts['nodename'] }}
    # OS: {{ ansible_os_family }}
    # CPU: {{ ansible_facts['processor'][0] }}
    # RAM: {{ ansible_facts['memtotal_mb'] }}
```

### 6. Templates
Jinja2 templates voor dynamische bestanden:

**Template** (`index.html.j2`):
```html
<!DOCTYPE html>
<html>
<head><title>{{ server_name }}</title></head>
<body>
  <h1>Server Info</h1>
  <p>Hostname: {{ ansible_facts['nodename'] }}</p>
  <p>IP: {{ ansible_default_ipv4.address }}</p>
</body>
</html>
```

**Gebruik**:
```yaml
- name: Deploy index.html
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
```

---

## Ansible Roles - Diepgaande Uitleg

### Wat is een Role?

Een **role** is een gestructureerde manier om playbooks te organiseren. Het bundelt alle elementen (tasks, templates, variables, handlers) in één herbruikbare eenheid.

### Role Structuur

```
nginx_role/
├── defaults/
│   └── main.yml          # Default variabelen (laagste prioriteit)
├── files/
│   └── check_port.sh     # Statische bestanden
├── handlers/
│   └── main.yml          # Event handlers
├── meta/
│   └── main.yml          # Role metadata (auteur, dependencies)
├── tasks/
│   └── main.yml          # Hoofdtaken van de role
├── templates/
│   ├── default.j2        # Jinja2 templates
│   └── index.html.j2
├── vars/
│   └── main.yml          # Variabelen (hogere prioriteit dan defaults)
└── README.md
```

### Directory Uitleg

#### 1. `tasks/main.yml` - De Kern
Bevat alle taken die uitgevoerd worden:

```yaml
---
# Update package cache
- name: Update apt cache
  ansible.builtin.apt:
    update_cache: true
  when: ansible_os_family == 'Debian'

# Install nginx
- name: Installeer nginx en tools
  ansible.builtin.apt:
    name:
      - nginx
      - curl
      - psmisc
    state: present

# Deploy configuration
- name: Plaats nginx-config
  ansible.builtin.template:
    src: default.j2
    dest: /etc/nginx/sites-enabled/default
  notify: restart nginx
```

**Belangrijke concepten:**
- `when:` - Conditionele executie
- `notify:` - Trigger handlers
- `register:` - Output opslaan in variabele
- `changed_when: false` - Markeer als niet gewijzigd

#### 2. `vars/main.yml` - Variabelen
```yaml
---
nginx_port: 80
nginx_server_name: "{{ ansible_nodename }}"
```

**Verschil vars vs defaults:**
- `defaults/`: Makkelijk overschrijfbaar, laagste prioriteit
- `vars/`: Hogere prioriteit, moeilijker overschrijfbaar

#### 3. `templates/` - Dynamische Bestanden

**Nginx configuratie** (`default.j2`):
```jinja2
server {
    listen {{ nginx_port }} default_server;
    server_name {{ nginx_server_name }};
    root /var/www/html;
    index index.html index.htm;
}
```

**HTML met facts** (`index.html.j2`):
```html
<!DOCTYPE html>
<html>
<head><title>Ansible Nginx</title></head>
<body>
  <h1>Nginx via Ansible role</h1>
  <ul>
    <li>Hostname: {{ ansible_facts['nodename'] }}</li>
    <li>IP: {{ ansible_default_ipv4.address }}</li>
    <li>CPU: {{ ansible_facts['processor'][0] }}</li>
    <li>RAM (MB): {{ ansible_facts['memtotal_mb'] }}</li>
  </ul>
</body>
</html>
```

#### 4. `files/` - Statische Bestanden
Bestanden die gekopieerd worden zonder wijzigingen:

**Port check script** (`check_port.sh`):
```bash
#!/bin/bash
set -euo pipefail
PORT=80
if ss -ltn | awk '{print $4}' | grep -q ":${PORT}$"; then
  echo "Running"
else
  echo "Not Running"
fi
```

**Gebruik**:
```yaml
- name: Copy port-check script
  ansible.builtin.copy:
    src: check_port.sh
    dest: /usr/local/bin/check_port
    mode: "0755"
```

#### 5. `handlers/main.yml` - Event Handlers
```yaml
---
- name: restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

Handlers worden **één keer** uitgevoerd aan het eind, zelfs als meerdere taken ze triggeren.

#### 6. `meta/main.yml` - Metadata
```yaml
---
galaxy_info:
  author: jan.celis@kdg.be
  description: Install and configure Nginx webserver
  license: GPL-3.0
  min_ansible_version: 2.8
  platforms:
    - name: Ubuntu
dependencies: []
```

---

## Praktisch Voorbeeld: Nginx Role

### Stap 1: Voorbereiding

```bash
# Installeer Ansible
sudo apt update
sudo apt install ansible openssh-server ansible-lint -y

# Maak directory structuur
mkdir -p ~/ansible-web/roles
cd ~/ansible-web/roles
```

### Stap 2: Role Aanmaken

```bash
# Genereer role structuur
ansible-galaxy init nginx_role

# Structuur:
# nginx_role/
# ├── defaults/
# ├── files/
# ├── handlers/
# ├── meta/
# ├── tasks/
# ├── templates/
# └── vars/
```

### Stap 3: Bestanden Invullen

#### `vars/main.yml`
```yaml
---
nginx_port: 80
nginx_server_name: "{{ ansible_nodename }}"
```

#### `templates/default.j2`
```jinja2
server {
    listen {{ nginx_port }} default_server;
    server_name {{ nginx_server_name }};
    root /var/www/html;
    index index.html index.htm;
}
```

#### `templates/index.html.j2`
```html
<!DOCTYPE html>
<html>
<head><title>Ansible Nginx</title></head>
<body>
  <h1>Nginx via Ansible role</h1>
  <ul>
    <li>Hostname: {{ ansible_facts['nodename'] }}</li>
    <li>IP: {{ ansible_default_ipv4.address }}</li>
    <li>CPU: {{ ansible_facts['processor'][0] }}</li>
    <li>RAM (MB): {{ ansible_facts['memtotal_mb'] }}</li>
  </ul>
</body>
</html>
```

#### `files/check_port.sh`
```bash
#!/bin/bash
set -euo pipefail
PORT=80
if ss -ltn | awk '{print $4}' | grep -q ":${PORT}$"; then
  echo "Running"
else
  echo "Not Running"
fi
```

```bash
chmod +x ~/ansible-web/roles/nginx_role/files/check_port.sh
```

#### `handlers/main.yml`
```yaml
---
- name: restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

#### `tasks/main.yml`
```yaml
---
- name: Update apt cache
  ansible.builtin.apt:
    update_cache: true
  when: ansible_os_family == 'Debian'

- name: Stop en disable apache2
  ansible.builtin.service:
    name: apache2
    state: stopped
    enabled: false
  ignore_errors: true

- name: Verwijder apache2
  ansible.builtin.apt:
    name: apache2
    state: absent

- name: Installeer nginx en tools
  ansible.builtin.apt:
    name:
      - nginx
      - curl
      - psmisc
    state: present

- name: Plaats nginx-config
  ansible.builtin.template:
    src: default.j2
    dest: /etc/nginx/sites-enabled/default
  notify: restart nginx

- name: Maak /var/www/html aan
  ansible.builtin.file:
    path: /var/www/html
    state: directory

- name: Plaats index.html
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
  notify: restart nginx

- name: Start en enable nginx
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true

- name: Copy port-check script
  ansible.builtin.copy:
    src: check_port.sh
    dest: /usr/local/bin/check_port
    mode: "0755"

- name: Controleer poortstatus
  ansible.builtin.command: /usr/local/bin/check_port
  register: portcheck
  changed_when: false

- name: Toon status
  ansible.builtin.debug:
    msg: "{{ portcheck.stdout }}"
```

### Stap 4: Playbook Maken

#### `playbook_nginx_deploy.yml`
```yaml
---
- name: Deploy Nginx via role
  hosts: nodes
  become: true
  gather_facts: true
  roles:
    - nginx_role
```

### Stap 5: Inventory Configureren

```bash
sudo mkdir -p /etc/ansible
sudo vi /etc/ansible/hosts
```

**Inventory** (`/etc/ansible/hosts`):
```ini
[nodes]
localhost ansible_connection=local
```

### Stap 6: Testen en Uitvoeren

```bash
# Test verbinding
ansible all -m ping

# Lint check
ansible-lint playbook_nginx_deploy.yml

# Uitvoeren
ansible-playbook -b playbook_nginx_deploy.yml
```

**Output**:
```
PLAY [Deploy Nginx via role] ***************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [nginx_role : Update apt cache] *******************************************
changed: [localhost]

...

TASK [nginx_role : Toon status] ************************************************
ok: [localhost] => {
    "msg": "Running"
}

PLAY RECAP *********************************************************************
localhost         : ok=13   changed=8    unreachable=0    failed=0
```

---

## Foutoplossing

### Veelvoorkomende Fouten

#### 1. YAML Syntax Error: Multiple Documents
```
ERROR! found another document
The error appears to be in 'vars/main.yml': line 4
```

**Probleem**: Dubbele `---` in YAML bestand
```yaml
---
# vars file
---  # ❌ FOUT: Tweede document marker
nginx_port: 80
```

**Oplossing**: Eén `---` per bestand
```yaml
---
# vars file
nginx_port: 80
```

#### 2. Localhost Connection
Als je alleen localhost wilt testen:

```ini
[nodes]
localhost ansible_connection=local
```

#### 3. Permission Denied
Gebruik `-b` (become) voor sudo:
```bash
ansible-playbook -b playbook.yml
```

### Best Practices

1. **Gebruik ansible.builtin prefix**
   ```yaml
   # Goed ✓
   ansible.builtin.apt:
   
   # Werkt ook, maar minder expliciet
   apt:
   ```

2. **Altijd YAML linting**
   ```bash
   yamllint roles/nginx_role/
   ansible-lint playbook_nginx_deploy.yml
   ```

3. **Idempotentie**: Playbooks moeten veilig meerdere keren uitgevoerd kunnen worden
   ```yaml
   # Goed - installeert alleen als niet aanwezig
   - name: Install nginx
     apt:
       name: nginx
       state: present
   ```

4. **Error handling**
   ```yaml
   - name: Stop apache
     service:
       name: apache2
       state: stopped
     ignore_errors: true  # Continue bij fout
   ```

5. **Check mode** (dry-run)
   ```bash
   ansible-playbook --check playbook.yml
   ```

---

## Apache2 Role Aanpassen

Om dezelfde role voor Apache2 te maken, pas je de volgende bestanden aan:

### `vars/main.yml`
```yaml
---
apache_port: 80
apache_server_name: "{{ ansible_nodename }}"
```

### `templates/apache-default.j2`
```apache
<VirtualHost *:{{ apache_port }}>
    ServerName {{ apache_server_name }}
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

### `tasks/main.yml`
```yaml
---
- name: Update apt cache
  ansible.builtin.apt:
    update_cache: true
  when: ansible_os_family == 'Debian'

- name: Stop en disable nginx
  ansible.builtin.service:
    name: nginx
    state: stopped
    enabled: false
  ignore_errors: true

- name: Verwijder nginx
  ansible.builtin.apt:
    name: nginx
    state: absent

- name: Installeer apache2 en tools
  ansible.builtin.apt:
    name:
      - apache2
      - curl
    state: present

- name: Plaats apache2-config
  ansible.builtin.template:
    src: apache-default.j2
    dest: /etc/apache2/sites-available/000-default.conf
  notify: restart apache2

- name: Maak /var/www/html aan
  ansible.builtin.file:
    path: /var/www/html
    state: directory

- name: Plaats index.html
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
  notify: restart apache2

- name: Enable apache site
  ansible.builtin.command: a2ensite 000-default
  changed_when: false

- name: Start en enable apache2
  ansible.builtin.service:
    name: apache2
    state: started
    enabled: true

- name: Controleer poortstatus
  ansible.builtin.command: /usr/local/bin/check_port
  register: portcheck
  changed_when: false

- name: Toon status
  ansible.builtin.debug:
    msg: "{{ portcheck.stdout }}"
```

### `handlers/main.yml`
```yaml
---
- name: restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted

- name: reload apache2
  ansible.builtin.service:
    name: apache2
    state: reloaded
```

### Verschillen Nginx vs Apache2

| Aspect | Nginx | Apache2 |
|--------|-------|---------|
| Config locatie | `/etc/nginx/sites-enabled/` | `/etc/apache2/sites-available/` |
| Config syntax | Nginx blocks | Apache VirtualHost |
| Service naam | `nginx` | `apache2` |
| Enable site | Automatisch | `a2ensite` command |
| Reload | `nginx -s reload` | `systemctl reload apache2` |

---

## Stopplaybook Maken

### `playbook_nginx_remove.yml`
```yaml
---
- name: Remove Nginx
  hosts: nodes
  become: true
  tasks:
    - name: Stop nginx service
      ansible.builtin.service:
        name: nginx
        state: stopped
        enabled: false
      ignore_errors: true
    
    - name: Remove nginx package
      ansible.builtin.apt:
        name: nginx
        state: absent
        purge: true
    
    - name: Remove config files
      ansible.builtin.file:
        path: "{{ item }}"
        state: absent
      loop:
        - /etc/nginx
        - /var/www/html/index.html
        - /usr/local/bin/check_port
    
    - name: Verify nginx removed
      ansible.builtin.command: which nginx
      register: nginx_check
      failed_when: false
      changed_when: false
    
    - name: Show result
      ansible.builtin.debug:
        msg: "Nginx {{ 'still installed' if nginx_check.rc == 0 else 'successfully removed' }}"
```

---

## Handige Commando's Overzicht

```bash
# Role aanmaken
ansible-galaxy init role_name

# Playbook testen (dry-run)
ansible-playbook --check playbook.yml

# Playbook uitvoeren
ansible-playbook playbook.yml
ansible-playbook -b playbook.yml  # met sudo

# Specifieke hosts
ansible-playbook -i inventory.ini playbook.yml
ansible-playbook --limit webservers playbook.yml

# Verbinding testen
ansible all -m ping
ansible webservers -m ping

# Facts verzamelen
ansible localhost -m setup

# Linting
yamllint roles/
ansible-lint playbook.yml

# Verbose output
ansible-playbook -v playbook.yml   # verbose
ansible-playbook -vvv playbook.yml # very verbose
```

---

## Conclusie

Deze handleiding heeft de volgende onderwerpen behandeld:

1. ✅ Basis Ansible concepten (playbooks, inventory, modules)
2. ✅ Role structuur en alle componenten
3. ✅ Praktisch nginx voorbeeld met volledige code
4. ✅ Foutoplossing en YAML syntax
5. ✅ Apache2 variant
6. ✅ Best practices en handige commando's

**Key Takeaways:**
- Roles organiseren code in herbruikbare eenheden
- Templates maken configuratie dynamisch
- Handlers voorkomen onnodige service restarts
- Facts geven automatisch systeeminformatie
- Idempotentie is essentieel voor betrouwbare automation

Voor meer informatie: [Ansible Documentation](https://docs.ansible.com/)