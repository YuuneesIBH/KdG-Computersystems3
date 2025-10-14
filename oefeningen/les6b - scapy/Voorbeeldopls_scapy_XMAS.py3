#!/usr/bin/env python3
#######################################################################
__author__      = "jan.celis@kdg.be"
__description__ = "XMAS scan flags URGENT, FIN and PRIORITY"
__license__     = "GPLv3 https://www.gnu.org/licenses/gpl-3.0.nl.html"
__version__     = "1.0"    
__requires__    = "sudo apt install python3-scapy"
#######################################################################       

import sys
import os
import time
from scapy.all import * 
from datetime import datetime

dstip=     "192.168.56.107"   
dstports=  [80,21,443]  
interface= "vboxnet0" #"enp0s3"
dstportss= ",".join(str(e) for e in dstports) 
dstflags=  "FPU" 
nmap=      "nmap --open -n -sX " + dstip + " -p" + dstportss    
#######################################################################
""" XMAS   Response Closed: RST, ACK
           Response Filtered or Open: Nothing
"""

nu=datetime.utcnow()
# Opmerking niet datetime.now() want dat is ten opzichte van je eigen timezone
print("\nStarting "+sys.argv[0]+" "+__version__+" at "+nu.strftime("%Y-%m-%d %H:%M"))
print("Scan report for "+dstip)
starttijd = time.time()
ip=IP(dst=dstip)
tcp=TCP(dport=dstports,flags=dstflags)
pakketten=sr(ip/tcp,timeout=1,iface=interface,verbose=0)
ans,unans=pakketten
conf.dstmac=""

def latency_ping(host, count=3): # latency test met ping
  packet = Ether()/IP(dst=host)/ICMP()
  conf.dstmac=packet.sprintf("%Ether.dst%") # heeft ook MAC adres
  t=0.0
  for x in range(count):
      ans,unans=srp(packet,iface=interface, filter='icmp', verbose=0)
      rx = ans[0][1]
      tx = ans[0][0]
      delta = rx.time-tx.sent_time
      t+=delta
  return (t/count)

closed=0             # tellen aantal gescande gesloten poorten
for an in ans:
    closed+=closed

if len(pakketten)>0 :    # als er pakketten zijn is Host up
    print("Host is up ("+str(latency_ping(dstip))+ "s latency).")
if closed > 0:
    print("Not shown: "+ closed +" closed ports")

 
print("PORT  STATE   SERVICE" )
for unan in unans:       # Open poorten geven geen antwoord
    print(str(unan[1].dport)+"    open|filtered" )

eindtijd  = time.time()
print("MAC Address: "+conf.dstmac)
print("Done. 1 IP address scanned in ", eindtijd - starttijd, "seconds")

os.system(nmap)  # om  te vergelijken met nmap
