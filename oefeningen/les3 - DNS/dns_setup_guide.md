# DNS Setup Guide - BIND9 Configuration

## Prerequisites
- Virtual Ubuntu machine with BIND9
- Network configuration:
  - eth0: Host Only adapter
  - eth1: NAT

**Reference**: [Ubuntu BIND9 Server Howto](https://help.ubuntu.com/community/BIND9ServerHowto)
> Note: The Ubuntu reference documentation may not be completely up-to-date

## Installation

Install BIND9 and utilities:

```bash
sudo apt install bind9 bind9utils -y
```

This will also install additional packages:
- bind9-host
- bind9-libs  
- bind9-utils

## Primary Master DNS Server Configuration

### 1. Configure Local Zone

Edit the local configuration file:

```bash
sudo vi /etc/bind/named.conf.local
```

Add your domain zone (replace `elazzouzi.local` with your domain):

```bind
//
// Do any local configuration here
//

zone "elazzouzi.local" {
    type master;
    file "/etc/bind/db.elazzouzi.local";
};
```

### 2. Create Zone File

Create the zone file with www and mail subdomains:

```bash
sudo vi /etc/bind/db.elazzouzi.local
```

Zone file content:

```bind
$TTL    604800
@   IN  SOA ns.elazzouzi.local. root.elazzouzi.local. (
        2025092701 ; serial
        604800     ; refresh
        86400      ; retry
        2419200    ; expire
        604800 )   ; minimum

; Nameserver
@       IN  NS      ns.elazzouzi.local.
ns      IN  A       192.168.64.11

; Hosts
www     IN  A       192.168.64.11
mail    IN  A       192.168.64.11

; Mail
@       IN  MX 10   mail.elazzouzi.local.
```

### 3. Validate Configuration

Test your DNS configuration files:

```bash
sudo named-checkconf
sudo named-checkzone elazzouzi.local /etc/bind/db.elazzouzi.local
```

No output from `named-checkconf` indicates no issues.

## DNS Resolution Configuration

### Method 1: Using systemd-resolved (Recommended)

Edit the resolved configuration:

```bash
sudo vi /etc/systemd/resolved.conf
```

Add these lines:

```ini
[Resolve]
DNS=192.168.64.11
Domains=elazzouzi.local
```

Restart the service:

```bash
sudo systemctl restart systemd-resolved
```

### Method 2: Direct resolv.conf (Alternative)

```bash
sudo vi /etc/resolv.conf
```

Add:

```
nameserver 192.168.64.11
options edns0 trust-ad
search .
```

## Testing Forward Lookup

Test DNS resolution with multiple tools:

```bash
# Check BIND9 service status
systemctl status bind9

# Test with dig
dig www.elazzouzi.lan

# Test with nslookup  
nslookup www.elazzouzi.lan

# Test with host
host www.elazzouzi.lan
```

Expected successful output:
```
; <<>> DiG 9.18.39-0ubuntu0.22.04.1-Ubuntu <<>> www.elazzouzi.lan
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 20135
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; ANSWER SECTION:
www.elazzouzi.lan.	604800	IN	A	192.168.64.11

;; Query time: 0 msec
;; SERVER: 192.168.64.11#53(192.168.64.11) (UDP)
```

## Reverse Lookup Configuration

### 1. Add Reverse Zone

Edit the local configuration:

```bash
sudo vi /etc/bind/named.conf.local
```

Add the reverse zone:

```bind
zone "64.168.192.in-addr.arpa" {
    type master;
    file "/etc/bind/db.192";
};
```

### 2. Create Reverse Zone File

Create the reverse lookup file:

```bash
sudo cp /etc/bind/db.127 /etc/bind/db.192
sudo vi /etc/bind/db.192
```

Or create directly:

```bash
sudo tee /etc/bind/db.192 > /dev/null << 'EOF'
$TTL    604800
@   IN  SOA ns.elazzouzi.lan. root.elazzouzi.lan. (
        2025092701 ; serial
        604800     ; refresh
        86400      ; retry
        2419200    ; expire
        604800 )   ; minimum

; Nameserver
@   IN  NS  ns.elazzouzi.lan.

; PTR records
11  IN  PTR ns.elazzouzi.lan.
11  IN  PTR www.elazzouzi.lan.
11  IN  PTR mail.elazzouzi.lan.
EOF
```

### 3. Validate and Restart

```bash
sudo named-checkzone 64.168.192.in-addr.arpa /etc/bind/db.192
sudo systemctl restart bind9
```

### 4. Test Reverse Lookup

```bash
# Test with dig
dig -x 192.168.64.11

# Test with nslookup
nslookup 192.168.64.11

# Test with host
host 192.168.64.11
```

Expected output shows PTR records:
```
;; ANSWER SECTION:
11.64.168.192.in-addr.arpa. 604800 IN	PTR	ns.elazzouzi.lan.
11.64.168.192.in-addr.arpa. 604800 IN	PTR	mail.elazzouzi.lan.
11.64.168.192.in-addr.arpa. 604800 IN	PTR	www.elazzouzi.lan.
```

## Enable Ping Resolution

### 1. Configure Name Service Switch

Edit nsswitch configuration:

```bash
sudo vi /etc/nsswitch.conf
```

Ensure the hosts line includes `dns`:

```
hosts:          files dns myhostname
```

### 2. Fix Firewall Issues (if needed)

If ping fails, check and adjust iptables:

```bash
# Check for ICMP rules
sudo iptables -L -n | grep icmp

# Remove ICMP blocking rules if present
sudo iptables -D INPUT -p icmp -j DROP
sudo iptables -D OUTPUT -p icmp -j DROP
```

### 3. Test Ping Resolution

```bash
ping www.elazzouzi.lan
```

Successful output:
```
PING www.elazzouzi.lan (192.168.64.11) 56(84) bytes of data.
64 bytes from ns.elazzouzi.lan (192.168.64.11): icmp_seq=1 ttl=64 time=0.018 ms
64 bytes from mail.elazzouzi.lan (192.168.64.11): icmp_seq=2 ttl=64 time=0.032 ms
```

## Troubleshooting

### Common Issues

1. **SERVFAIL errors**: Often related to `.local` domain conflicts with mDNS
   - Solution: Use `.lan` or another TLD instead of `.local`

2. **DNS not resolving**: Check systemd-resolved configuration
   - Verify DNS server is set correctly
   - Restart systemd-resolved service

3. **Ping not working**: Check firewall rules
   - ICMP packets may be blocked by iptables

### Configuration Files Summary

Key files modified:
- `/etc/bind/named.conf.local` - Zone definitions
- `/etc/bind/db.elazzouzi.local` - Forward zone file
- `/etc/bind/db.192` - Reverse zone file
- `/etc/systemd/resolved.conf` - DNS resolution configuration
- `/etc/nsswitch.conf` - Name service switch configuration

### Network Configuration

- **IP Address**: 192.168.64.11 (Host Only adapter)
- **Domain**: elazzouzi.local (or elazzouzi.lan)
- **Subdomains**: www, mail, ns

This setup provides a complete DNS server with both forward and reverse lookup capabilities for local domain resolution.