# Scapy Complete Guide - Python3 Edition

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Sniffing Packets](#sniffing-packets)
5. [Sending Packets](#sending-packets)
6. [Send & Receive](#send--receive)
7. [Packet Layers](#packet-layers)
8. [Working with PCAP Files](#working-with-pcap-files)
9. [Network Scanning](#network-scanning)
10. [Advanced Techniques](#advanced-techniques)
11. [Practical Exercises](#practical-exercises)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Scapy?

Scapy is a powerful Python-based interactive packet manipulation program. It can:
- **Forge** and **decode** packets of many protocols
- **Send** them on the wire
- **Capture** and analyze network traffic
- Replace tools like hping, nmap (85%), arpspoof, tcpdump, and more

### Key Features
- ✅ Full control over packet construction
- ✅ Protocol dissection and analysis
- ✅ Fuzzing capabilities
- ✅ Network discovery and scanning
- ✅ PCAP file manipulation
- ✅ Python integration for automation

### Use Cases
- Network testing and security auditing
- Protocol reverse engineering
- Penetration testing
- Traffic generation and simulation
- Educational purposes

---

## Installation

### Ubuntu/Debian Installation

```bash
# Update package list
sudo apt update

# Install Scapy and dependencies
sudo apt install -y nmap wireshark tcpdump python3-scapy \
                    python3-pycryptodome ipython3 \
                    python3-graphviz imagemagick

# Verify installation
scapy -h
```

### Alternative: pip Installation

```bash
pip3 install scapy
```

### Network Setup for Labs

For hands-on exercises, configure VirtualBox/VMware with:
- **Host-Only Adapter**: For isolated network testing
- **NAT Adapter**: For internet access

Example network: `192.168.56.0/24`

---

## Basic Concepts

### OSI Layer Model in Scapy

```
Layer 7 (Application) → HTTP, DNS, DHCP
Layer 4 (Transport)   → TCP, UDP
Layer 3 (Network)     → IP, ICMP, ARP
Layer 2 (Data Link)   → Ethernet (Ether)
Layer 1 (Physical)    → Bits on wire
```

### Packet Structure

Every Scapy packet is a **layered** structure:

```python
# Simple ICMP packet
IP(dst="192.168.1.1") / ICMP()

# With payload
IP(dst="192.168.1.1") / ICMP() / "HelloWorld"

# Full Ethernet frame
Ether() / IP(dst="192.168.1.1") / TCP(dport=80)
```

### The `/` Operator

The `/` operator **layers** protocols on top of each other:
- `IP()/ICMP()` = IP packet containing ICMP
- Each layer can override default values

---

## Sniffing Packets

### Basic Sniffing

```python
#!/usr/bin/env python3
from scapy.all import sniff

# Sniff 10 packets
packets = sniff(count=10)
packets.summary()
```

### Advanced Sniffing with Filters

```python
from scapy.all import sniff

def packet_callback(pkt):
    """Callback function for each packet"""
    print(pkt.summary())
    if pkt.haslayer('IP'):
        print(f"  Source: {pkt['IP'].src}")
        print(f"  Dest: {pkt['IP'].dst}")

# Sniff with BPF filter
sniff(filter="tcp port 80", prn=packet_callback, count=10)
```

### Common BPF Filters

| Filter | Description |
|--------|-------------|
| `tcp` | Only TCP packets |
| `udp` | Only UDP packets |
| `icmp` | Only ICMP packets |
| `arp` | Only ARP packets |
| `port 80` | Packets on port 80 |
| `host 192.168.1.1` | Packets from/to specific host |
| `net 192.168.1.0/24` | Packets in subnet |
| `tcp and port 443` | HTTPS traffic |

### Interface-Specific Sniffing

```python
# Sniff on specific interface
sniff(iface="eth0", count=10)

# List available interfaces
from scapy.all import get_if_list
print(get_if_list())
```

### Root Privileges Check

```python
from os import getuid

if getuid() != 0:
    print("Warning: Run with sudo for full functionality!")
```

---

## Sending Packets

### Layer 3 Sending: `send()`

Sends packets at **Layer 3** (IP layer):

```python
from scapy.all import send, IP, ICMP

# Simple ICMP ping
send(IP(dst="192.168.1.1")/ICMP())

# With TTL modification
send(IP(dst="192.168.1.1", ttl=10)/ICMP())

# Multiple packets
send(IP(dst="192.168.1.1")/ICMP(), count=5)
```

### Layer 2 Sending: `sendp()`

Sends packets at **Layer 2** (Ethernet layer):

```python
from scapy.all import sendp, Ether, IP, ICMP

# Complete Ethernet frame
sendp(Ether()/IP(dst="192.168.1.1")/ICMP())

# With specific MAC
sendp(Ether(src="00:11:22:33:44:55")/IP(dst="192.168.1.1")/ICMP())
```

### TCP Packet Examples

```python
from scapy.all import IP, TCP

# SYN packet
send(IP(dst="192.168.1.1")/TCP(dport=80, flags="S"))

# SYN-ACK packet
send(IP(dst="192.168.1.1")/TCP(dport=80, flags="SA"))

# RST packet
send(IP(dst="192.168.1.1")/TCP(dport=80, flags="R"))
```

---

## Send & Receive

### `sr()` - Send and Receive Multiple

Returns **answered** and **unanswered** packets:

```python
from scapy.all import sr, IP, ICMP

# Send and receive
ans, unans = sr(IP(dst="192.168.1.0/24")/ICMP(), timeout=2)

# Display answered packets
ans.summary()

# Display unanswered
unans.summary()
```

### `sr1()` - Send and Receive One

Returns **only the first** response:

```python
from scapy.all import sr1, IP, ICMP

# Single request-response
reply = sr1(IP(dst="192.168.1.1")/ICMP(), timeout=2)

if reply:
    reply.show()
else:
    print("No response")
```

### `srp()` - Layer 2 Send/Receive

```python
from scapy.all import srp, Ether, ARP

# ARP request
ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24"), 
                 timeout=2)

for snd, rcv in ans:
    print(f"{rcv.psrc} is at {rcv.hwsrc}")
```

### Analyzing Responses

```python
from scapy.all import sr, IP, TCP

ans, unans = sr(IP(dst="192.168.1.1")/TCP(dport=[22,80,443], flags="S"), 
                timeout=2)

for snd, rcv in ans:
    if rcv[TCP].flags == "SA":  # SYN-ACK = open
        print(f"Port {rcv[TCP].sport} is OPEN")
    elif rcv[TCP].flags == "RA":  # RST-ACK = closed
        print(f"Port {rcv[TCP].sport} is CLOSED")
```

---

## Packet Layers

### Viewing Layer Details

```python
from scapy.all import IP, TCP

# Create packet
pkt = IP(dst="192.168.1.1")/TCP(dport=80, flags="S")

# Show detailed structure
pkt.show()

# Show specific layer
pkt[IP].show()
pkt[TCP].show()
```

### Building Packets Layer by Layer

```python
from scapy.all import Ether, IP, TCP

# Method 1: Direct composition
packet = Ether()/IP(dst="192.168.1.1")/TCP(dport=80, flags="S")

# Method 2: Layer by layer
layer2 = Ether(src="00:11:22:33:44:55")
layer3 = IP(dst="192.168.1.1", ttl=64)
layer4 = TCP(sport=12345, dport=80, flags="S")

packet = layer2/layer3/layer4
```

### Accessing Layer Fields

```python
# Get source IP
src_ip = pkt[IP].src

# Get TCP flags
flags = pkt[TCP].flags

# Check if layer exists
if pkt.haslayer(TCP):
    print("Has TCP layer")

# Get layer by name
ip_layer = pkt.getlayer(IP)
```

### Common Protocols and Fields

#### IP Layer
```python
IP(
    src="192.168.1.100",    # Source IP
    dst="192.168.1.1",      # Destination IP
    ttl=64,                 # Time to Live
    id=12345,               # Identification
    flags="DF"              # Don't Fragment
)
```

#### TCP Layer
```python
TCP(
    sport=12345,            # Source port
    dport=80,               # Destination port
    flags="S",              # SYN flag
    seq=1000,               # Sequence number
    ack=0,                  # Acknowledgment number
    window=8192             # Window size
)
```

#### UDP Layer
```python
UDP(
    sport=53,               # Source port
    dport=53                # Destination port
)
```

#### ICMP Layer
```python
ICMP(
    type=8,                 # Echo request
    code=0                  # Code
)
```

---

## Working with PCAP Files

### Reading PCAP Files

```python
from scapy.all import rdpcap

# Read entire file
packets = rdpcap("/path/to/file.pcap")

# Display summary
packets.summary()

# Access individual packets
packets[0].show()

# Iterate through packets
for pkt in packets:
    if pkt.haslayer('TCP'):
        print(f"TCP packet: {pkt[IP].src} -> {pkt[IP].dst}")
```

### Writing PCAP Files

```python
from scapy.all import wrpcap, sniff

# Capture and save
packets = sniff(count=100)
wrpcap("capture.pcap", packets)

# Save specific packets
http_packets = [pkt for pkt in packets if pkt.haslayer('TCP') and pkt[TCP].dport == 80]
wrpcap("http_only.pcap", http_packets)
```

### Replaying PCAP Files

```python
from scapy.all import rdpcap, send

# Read and replay
packets = rdpcap("attack.pcap")

for pkt in packets:
    send(pkt)
    # Optional: add delay
    # time.sleep(0.1)
```

### Opening in Wireshark

```python
from scapy.all import wireshark

# Open packets directly in Wireshark
packets = sniff(count=10)
wireshark(packets)
```

---

## Network Scanning

### Ping Sweep (ICMP)

```python
from scapy.all import sr1, IP, ICMP

def ping_sweep(network):
    """Ping sweep a network"""
    live_hosts = []
    
    for i in range(1, 255):
        ip = f"{network}.{i}"
        reply = sr1(IP(dst=ip)/ICMP(), timeout=1, verbose=0)
        
        if reply:
            print(f"[+] {ip} is alive")
            live_hosts.append(ip)
    
    return live_hosts

# Usage
ping_sweep("192.168.1")
```

### ARP Scan (Faster for LAN)

```python
from scapy.all import ARP, Ether, srp

def arp_scan(network):
    """ARP scan for active hosts"""
    # Create ARP request
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send and receive
    result = srp(packet, timeout=2, verbose=0)[0]
    
    # Parse results
    hosts = []
    for sent, received in result:
        hosts.append({'ip': received.psrc, 'mac': received.hwsrc})
        print(f"[+] {received.psrc:16} - {received.hwsrc}")
    
    return hosts

# Usage
arp_scan("192.168.1.0/24")
```

### TCP Port Scanner

```python
from scapy.all import sr, IP, TCP

def tcp_scan(target, ports):
    """SYN scan on specified ports"""
    # Send SYN packets
    ans, unans = sr(IP(dst=target)/TCP(sport=RandShort(), dport=ports, flags="S"), 
                    timeout=2, verbose=0)
    
    open_ports = []
    for sent, received in ans:
        if received[TCP].flags == "SA":  # SYN-ACK
            open_ports.append(received[TCP].sport)
            print(f"[+] Port {received[TCP].sport} is OPEN")
    
    return open_ports

# Usage
tcp_scan("192.168.1.1", [22, 80, 443, 3389])
```

### UDP Port Scanner

```python
from scapy.all import sr1, IP, UDP, ICMP

def udp_scan(target, ports):
    """UDP port scan"""
    open_ports = []
    
    for port in ports:
        pkt = IP(dst=target)/UDP(dport=port)
        resp = sr1(pkt, timeout=2, verbose=0)
        
        if resp is None:
            # No response = open|filtered
            print(f"[?] Port {port} open|filtered")
            open_ports.append(port)
        elif resp.haslayer(ICMP):
            if resp[ICMP].type == 3 and resp[ICMP].code == 3:
                # Port unreachable = closed
                print(f"[-] Port {port} closed")
        else:
            # Got UDP response = open
            print(f"[+] Port {port} OPEN")
            open_ports.append(port)
    
    return open_ports

# Usage
udp_scan("192.168.1.1", [53, 67, 161])
```

### XMAS Scan

```python
from scapy.all import sr, IP, TCP

def xmas_scan(target, ports):
    """XMAS scan (FIN, PSH, URG flags)"""
    ans, unans = sr(IP(dst=target)/TCP(dport=ports, flags="FPU"), 
                    timeout=2, verbose=0)
    
    for sent, received in ans:
        if received[TCP].flags == "RA":
            print(f"[-] Port {received[TCP].sport} is CLOSED")
    
    # No response = open|filtered
    for sent in unans:
        print(f"[?] Port {sent[TCP].dport} is open|filtered")

# Usage
xmas_scan("192.168.1.1", [22, 80, 443])
```

---

## Advanced Techniques

### DNS Queries

```python
from scapy.all import sr1, IP, UDP, DNS, DNSQR

def dns_query(domain, dns_server="8.8.8.8", qtype="A"):
    """Perform DNS query"""
    dns_req = IP(dst=dns_server)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype=qtype))
    
    response = sr1(dns_req, verbose=0, timeout=2)
    
    if response and response.haslayer(DNS):
        return response[DNS]
    return None

# Usage
result = dns_query("www.example.com")
if result:
    print(result.show())
```

### DHCP Discovery

```python
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, srp

def dhcp_discover(iface="eth0"):
    """Find DHCP servers"""
    dhcp_discover = (Ether(dst="ff:ff:ff:ff:ff:ff")/
                     IP(src="0.0.0.0", dst="255.255.255.255")/
                     UDP(sport=68, dport=67)/
                     BOOTP(chaddr=RandString(12,'0123456789abcdef'))/
                     DHCP(options=[("message-type", "discover"), "end"]))
    
    ans, unans = srp(dhcp_discover, iface=iface, timeout=5, verbose=0)
    
    for sent, received in ans:
        if received.haslayer(DHCP):
            print(f"[+] DHCP Server: {received[IP].src}")
            print(f"    Offered IP: {received[BOOTP].yiaddr}")

# Usage
dhcp_discover()
```

### Traceroute

```python
from scapy.all import traceroute

# Simple traceroute
result, unans = traceroute("www.example.com", maxttl=20)

# With graph output (requires graphviz)
result.graph(target="traceroute.png")

# TCP traceroute
result, unans = traceroute(["www.example.com"], dport=80, maxttl=20)
```

### Packet Fuzzing

```python
from scapy.all import send, IP, TCP, fuzz

# Fuzz TCP layer
send(IP(dst="192.168.1.1")/fuzz(TCP(dport=80)))

# Fuzz specific fields
send(IP(dst="192.168.1.1")/TCP(dport=80, flags=RandShort()))
```

### ARP Poisoning (Educational Only!)

```python
from scapy.all import sendp, Ether, ARP
import time

def arp_poison(target_ip, gateway_ip, iface="eth0"):
    """ARP cache poisoning"""
    target_mac = getmacbyip(target_ip)
    gateway_mac = getmacbyip(gateway_ip)
    
    while True:
        # Tell target we are the gateway
        sendp(Ether(dst=target_mac)/ARP(op="is-at", psrc=gateway_ip, 
              pdst=target_ip, hwdst=target_mac), iface=iface, verbose=0)
        
        # Tell gateway we are the target
        sendp(Ether(dst=gateway_mac)/ARP(op="is-at", psrc=target_ip, 
              pdst=gateway_ip, hwdst=gateway_mac), iface=iface, verbose=0)
        
        time.sleep(1)

# ⚠️ WARNING: Only use on networks you own!
```

---

## Practical Exercises

### Exercise 1: Network Discovery

Create a script that finds all active hosts and their open ports:

```python
#!/usr/bin/env python3
from scapy.all import *

def network_discovery(network):
    """Discover hosts and scan common ports"""
    print(f"[*] Scanning {network}...")
    
    # ARP scan for live hosts
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network), 
                     timeout=2, verbose=0)
    
    hosts = [rcv.psrc for snd, rcv in ans]
    print(f"[+] Found {len(hosts)} hosts")
    
    # Port scan each host
    common_ports = [21, 22, 23, 25, 80, 443, 3389]
    
    for host in hosts:
        print(f"\n[*] Scanning {host}...")
        ans, unans = sr(IP(dst=host)/TCP(dport=common_ports, flags="S"), 
                        timeout=1, verbose=0)
        
        for snd, rcv in ans:
            if rcv[TCP].flags == "SA":
                print(f"  [+] Port {rcv[TCP].sport} OPEN")

# Run
network_discovery("192.168.1.0/24")
```

### Exercise 2: Packet Logger

Log all HTTP requests:

```python
#!/usr/bin/env python3
from scapy.all import sniff, TCP, Raw
from datetime import datetime

def http_logger(pkt):
    """Log HTTP requests"""
    if pkt.haslayer(TCP) and pkt.haslayer(Raw):
        if pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
            payload = pkt[Raw].load.decode('utf-8', errors='ignore')
            
            if 'GET' in payload or 'POST' in payload:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] HTTP Request")
                print(f"  From: {pkt[IP].src}:{pkt[TCP].sport}")
                print(f"  To: {pkt[IP].dst}:{pkt[TCP].dport}")
                print(f"  Data: {payload[:200]}")

# Start sniffing
print("[*] Starting HTTP logger (Ctrl+C to stop)...")
sniff(filter="tcp port 80", prn=http_logger)
```

### Exercise 3: Custom Ping Tool

Build a custom ping tool with statistics:

```python
#!/usr/bin/env python3
from scapy.all import sr1, IP, ICMP
import time
import sys

def custom_ping(target, count=4):
    """Custom ping implementation"""
    print(f"PING {target}")
    
    replies = 0
    total_time = 0
    min_time = float('inf')
    max_time = 0
    
    for i in range(count):
        start = time.time()
        reply = sr1(IP(dst=target)/ICMP(seq=i), timeout=2, verbose=0)
        rtt = (time.time() - start) * 1000  # Convert to ms
        
        if reply:
            replies += 1
            total_time += rtt
            min_time = min(min_time, rtt)
            max_time = max(max_time, rtt)
            
            print(f"{len(reply)} bytes from {reply.src}: icmp_seq={i} ttl={reply.ttl} time={rtt:.2f}ms")
        else:
            print(f"Request timeout for icmp_seq {i}")
        
        time.sleep(1)
    
    # Statistics
    print(f"\n--- {target} ping statistics ---")
    print(f"{count} packets transmitted, {replies} received, {((count-replies)/count)*100:.1f}% packet loss")
    
    if replies > 0:
        avg_time = total_time / replies
        print(f"rtt min/avg/max = {min_time:.2f}/{avg_time:.2f}/{max_time:.2f} ms")

# Run
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <target>")
    sys.exit(1)

custom_ping(sys.argv[1])
```

---

## Troubleshooting

### Common Issues

#### 1. Permission Denied

**Problem**: `Operation not permitted` or `socket.error`

**Solution**:
```bash
# Run with sudo
sudo python3 script.py

# Or use capabilities (Linux)
sudo setcap cap_net_raw=eip /usr/bin/python3.x
```

#### 2. No Route Found for IPv6

**Problem**: `WARNING: No route found for IPv6 destination ::`

**Solution**: This is just a warning, can be ignored or disable IPv6:
```python
from scapy.all import conf
conf.use_pcap = True
```

#### 3. MAC Address Not Found

**Problem**: `WARNING: MAC address to reach destination not found`

**Solution**: Target is not on local network or doesn't respond to ARP:
```python
# Use send() instead of sendp()
send(IP(dst="8.8.8.8")/ICMP())  # Let OS handle routing
```

#### 4. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'scapy'`

**Solution**:
```bash
pip3 install scapy
# or
sudo apt install python3-scapy
```

### Debug Tips

```python
from scapy.all import conf

# Enable verbose mode
conf.verb = 2

# Disable verbose
conf.verb = 0

# Check interface
print(conf.iface)

# List all interfaces
from scapy.all import get_if_list
print(get_if_list())
```

---

## Best Practices

### 1. Always Use Timeouts

```python
# Good
sr1(IP(dst="192.168.1.1")/ICMP(), timeout=2)

# Bad (can hang forever)
sr1(IP(dst="192.168.1.1")/ICMP())
```

### 2. Suppress Output When Needed

```python
# Suppress verbose output
ans, unans = sr(IP(dst="192.168.1.0/24")/ICMP(), verbose=0)
```

### 3. Handle Exceptions

```python
try:
    reply = sr1(IP(dst="192.168.1.1")/ICMP(), timeout=2)
    if reply:
        reply.show()
except Exception as e:
    print(f"Error: {e}")
```

### 4. Use Context Managers for Files

```python
# Good practice
from scapy.all import PcapWriter

with PcapWriter("output.pcap", append=True) as pcap:
    pcap.write(packet)
```

### 5. Validate Input

```python
import sys
import ipaddress

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <ip>")
    sys.exit(1)

try:
    target = ipaddress.ip_address(sys.argv[1])
except ValueError:
    print("Invalid IP address")
    sys.exit(1)
```

---

## Quick Reference Card

### Essential Commands

```python
# Sniffing
sniff(count=10)                          # Sniff 10 packets
sniff(filter="tcp", count=10)            # With BPF filter
sniff(prn=lambda x: x.summary())         # With callback

# Sending
send(IP(dst="1.1.1.1")/ICMP())           # Layer 3
sendp(Ether()/IP(dst="1.1.1.1")/ICMP())  # Layer 2

# Send & Receive
sr1(IP(dst="1.1.1.1")/ICMP())            # One response
ans, unans = sr(IP(dst="1.1.1.1")/TCP()) # All responses

# PCAP
packets = rdpcap("file.pcap")            # Read
wrpcap("file.pcap", packets)             # Write

# Display
packet.show()                            # Detailed view
packet.summary()                         # One-line summary
ls(IP)                                   # Show layer fields
```

### Protocol Quick Reference

```python
# Ethernet
Ether(src="...", dst="...")

# IP
IP(src="...", dst="...", ttl=64)

# TCP
TCP(sport=..., dport=..., flags="S")

# UDP
UDP(sport=..., dport=...)

# ICMP
ICMP(type=8, code=0)

# ARP
ARP(op="who-has", pdst="...")

# DNS
DNS(qd=DNSQR(qname="example.com"))
```

---

## Legal and Ethical Considerations

### ⚠️ WARNING

- **Only test on networks you own or have explicit permission**
- Port scanning without permission may be **illegal**
- ARP poisoning is a **network attack**
- Packet injection can **disrupt services**
- Always follow **responsible disclosure** practices

### Ethical Use

✅ **Permitted**:
- Testing your own networks
- Educational lab environments
- Authorized penetration testing
- Security research with permission

❌ **Prohibited**:
- Unauthorized network scanning
- Attacks on production systems
- Data interception without consent
- Any illegal network activity

---

## Additional Resources

### Official Documentation
- Scapy Documentation: https://scapy.readthedocs.io/
- Scapy GitHub: https://github.com/secdev/scapy

### Learning Resources
- Scapy Guide: https://0xbharath.github.io/art-of-packet-crafting-with-scapy/
- Packet Analysis: https://www.wireshark.org/docs/
- Network Protocols: https://www.ietf.org/standards/rfcs/

### Community
- Scapy Mailing List
- Stack Overflow: #scapy
- Security Forums: r/netsec, r/AskNetsec

---

## Conclusion

Scapy is an incredibly powerful tool for network analysis, testing, and research. This guide covered:

✅ Basic packet manipulation  
✅ Network scanning techniques  
✅ PCAP file handling  
✅ Protocol analysis  
✅ Advanced attack techniques  

**Next Steps**:
1. Practice with the exercises
2. Build your own tools
3. Contribute to Scapy
4. Keep learning networking fundamentals

**Remember**: With great power comes great responsibility. Use Scapy ethically and legally!

---

*Last Updated: 2024 | For Python 3.x | Scapy 2.5+*