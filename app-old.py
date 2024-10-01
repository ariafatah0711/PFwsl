import subprocess
import time
import signal
import sys
import argparse

def getArgument():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Automation Port Forwarding WSL',
    )
    parser.add_argument("-I", "-int", "--interface", metavar="interface", default="Wi-Fi", type=str, required=False, help="masukan interface")
    parser.add_argument("-p", "--port", metavar="portProxy", type=str, nargs='+', required=True, help="masukan port dalam format <listen_port>:<connect_port>")
    parser.add_argument("-i", "--ip",  metavar="connect ip", default="172.27.139.111", type=str, required=False, help="masukan connected ip")
    
    return parser.parse_args()

class netsh:
    def __init__(self) -> None:
        pass
    
    def get_interface_ip(self, interface_name):
        result = subprocess.run(['powershell', '-Command', 
                                 f"(Get-NetIPAddress -InterfaceAlias {interface_name} -AddressFamily IPv4).IPAddress"],
                                 capture_output=True, text=True)
        ip_address = result.stdout.strip()
        if not ip_address:
            print(f"[-] Interface {interface_name} tidak memiliki IP Address!")
            sys.exit(1)
        return ip_address

    def add_portproxy_rule(self, listen_ip, listen_port, connect_ip, connect_port):
        result = subprocess.run(['netsh', 'interface', 'portproxy', 'add', 'v4tov4',
                                 f'listenaddress={listen_ip}', f'listenport={listen_port}',
                                 f'connectaddress={connect_ip}', f'connectport={connect_port}'],
                                 capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to add portproxy rule: {result.stderr.strip()}")
        else:
            print(f"[+] Successfully added portproxy rule: {listen_ip}:{listen_port} -> {connect_ip}:{connect_port}")

    def delete_portproxy_rule(self, listen_ip, listen_port):
        subprocess.run(['netsh', 'interface', 'portproxy', 'delete', 'v4tov4',
                        f'listenaddress={listen_ip}', f'listenport={listen_port}'])

    def signal_handler(self, sig, frame):
        print("\n[+] Proxy stopped. Removing all port proxy rules...")
        for port in ports:
            self.delete_portproxy_rule(listen_ip, port.split(":")[0])
        sys.exit(0)

args = getArgument()
PFwsl = netsh()

interface_name = args.interface
listen_ip = PFwsl.get_interface_ip(interface_name)
connect_ip = args.ip
ports = args.port

print(f"[+] Setting up port forwarding from {listen_ip}...\n")

for port in ports:
    listen_port, connect_port = port.split(":")
    PFwsl.add_portproxy_rule(listen_ip, listen_port, connect_ip, connect_port)

signal.signal(signal.SIGINT, PFwsl.signal_handler)

print("\n[+] Proxy running... Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

for port in ports:
    listen_port = port.split(":")[0]
    PFwsl.delete_portproxy_rule(listen_ip, listen_port)
