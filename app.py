import subprocess
import time
import sys, os
import argparse
import ctypes
import win32api

# default value
ip_wsl = "172.27.139.111"
interface = "Wi-Fi"
version = "1.0.0"

try:
    from colorama import init, Fore, Style
    init()
    HEADER = Fore.MAGENTA
    OKGREEN = Fore.GREEN
    ORANGE = Fore.YELLOW
    FAIL = Fore.RED
    ENDC = Style.RESET_ALL
except ImportError:
    HEADER = ''
    OKGREEN = ''
    ORANGE = ''
    FAIL = ''
    ENDC = ''

class col:
    HEADER = HEADER
    OKGREEN = OKGREEN
    ORANGE = ORANGE
    FAIL = FAIL
    ENDC = ENDC

def getArgument():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f'Automation Port Forwarding for WSL (Windows Subsystem for Linux) Ver: {version}',
        epilog=f'''
Action:
  python3 app.py show
  python3 app.py reset

Example: 
  python3 app.py 8080:8080
  python3 app.py -l 192.168.10.1 -r 172.27.139.111 -p 8081:2000
  python3 app.py -I Ethernet -p 8081:8081 8082:8082
        '''
    )
    parser.add_argument("-I", "--interface", metavar="interface", default=interface, type=str, help="enter network interface")
    parser.add_argument("-p", "--port", metavar="portProxy", type=str, nargs='+', help="enter ports in the format <listen_port>:<connect_port>")
    parser.add_argument("-l", metavar="local ip", default=None, type=str, help="enter local IP address")
    parser.add_argument("-r", metavar="remote ip", default=ip_wsl, type=str, help="enter remote IP address")
    parser.add_argument("-v", action="store_true", help="verbose mode")

    parser.add_argument("action", type=str, nargs='?', default=None, help="specify action")
    
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
            print(f"{col.FAIL}[-] Interface {interface_name} tidak memiliki IP Address!{col.ENDC}")
            sys.exit(1)
        return ip_address

    def add_portproxy_rule(self, listen_ip, listen_port, connect_ip, connect_port):
        result = subprocess.run(['netsh', 'interface', 'portproxy', 'add', 'v4tov4',
                                 f'listenaddress={listen_ip}', f'listenport={listen_port}',
                                 f'connectaddress={connect_ip}', f'connectport={connect_port}'],
                                 capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[+] Successfully added portproxy rule: {col.OKGREEN}{listen_ip}:{listen_port} {col.ENDC}-> {col.ORANGE}{connect_ip}:{connect_port}{col.ENDC}")
        else:
            print(f"{col.FAIL}[-] Failed to add portproxy rule: {result.stderr.strip()} {col.ENDC}")

    def delete_portproxy_rule(self, listen_ip, listen_port):
        subprocess.run(['netsh', 'interface', 'portproxy', 'delete', 'v4tov4',
                        f'listenaddress={listen_ip}', f'listenport={listen_port}'],
                        capture_output=True, text=True)

    def add_firewall_rule(self, listen_port):
        # rule_name = f"PortProxyRule_{listen_port}"
        # if rule_name in subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
        #     capture_output=True, text=True).stdout:
        #     return
        
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        'name=PortProxyRule_{}'.format(listen_port),
                        'dir=in', 'action=allow',
                        'protocol=TCP', 'localport={}'.format(listen_port)], capture_output=True, text=True)

    def delete_firewall_rule(self, listen_port):
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                        'name=PortProxyRule_{}'.format(listen_port)], capture_output=True, text=True)
    
    def show_rule(self):
        resultPort = subprocess.run(["netsh", "interface", "portproxy", "show", "all"], capture_output=True, text=True)
        resultFirewall = subprocess.run(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"], capture_output=True, text=True)

        if resultPort.stdout.rstrip():
            print(f"{col.HEADER}[*] Portproxy rules: {col.ENDC}")
            print(resultPort.stdout.strip())
        else:
            print(f"{col.HEADER}[*] No portproxy rules found. {col.ENDC}\n")

        rule_name = "PortProxyRule_"
        rule_names = [line.split(':')[-1].strip() for line in resultFirewall.stdout.splitlines() if rule_name in line]
        if rule_names:
            print(f"\n{col.HEADER}[*] Firewall rules related to PortProxy: {col.ENDC}")
            print("\n".join(rule_names))
        else:
            print(f"{col.HEADER}[*] No firewall rules found.{col.ENDC}")

    def delete_rule(self):
        for port in ports:
            listen_port = port.split(":")[0]
            self.delete_portproxy_rule(listen_ip, listen_port)
            self.delete_firewall_rule(listen_port)
        
    def reset(self, listen_ip):
        resultPort = subprocess.run(["netsh", "interface", "portproxy", "show", "all"], capture_output=True, text=True)
        subprocess.run(["netsh", "interface", "portproxy", "reset"], capture_output=True, text=True)
        print(f"{col.OKGREEN}[*] reset portproxy rule")
        time.sleep(1)

        for line in resultPort.stdout.splitlines()[2:]:
            if line.strip():
                listen_port = line.split()[1]
                try:
                    listen_port = int(listen_port)
                except ValueError: continue
                
                print(f"{col.OKGREEN}[*] removing port {listen_port}{col.ENDC}")
                self.delete_firewall_rule(listen_port)

    # def signal_handler(self, sig, frame):
    #     print("[+] Proxy stopped. Removing all port proxy rules and firewall rules...")
    #     self.delete_rule()
    #     sys.exit()

def validate_port(port):
    port_pairs = port
    listen_ports = []
    connect_ports = []

    for pair in port_pairs:
        pair_err = f"{col.FAIL}{pair}{col.ENDC}"
        pair_suc = f"{col.OKGREEN}8080:8081{col.ENDC}"
        try:
            listen_port, connect_port = pair.split(':')
        except ValueError:
            print(f"{col.FAIL}[-] {col.ENDC}Invalid port mapping format: {pair_err}. Use {col.HEADER}<listen_port>:<connect_port>. ex: {pair_suc}"); exit()

        if not listen_port.isdigit() or not connect_port.isdigit():
            print(f"{col.FAIL}[-] {col.ENDC}Ports should be integers: {pair_err}. ex: {pair_suc}")

        if listen_port in listen_ports:
            print(f"{col.FAIL}[-] Duplicate listen port: {listen_port}.{col.ENDC}")
        if connect_port in connect_ports:
            print(f"{col.FAIL}[-] Duplicate connect port: {connect_port}.{col.ENDC}")

        listen_ports.append(listen_port)
        connect_ports.append(connect_port)
    return

def run_as_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def cleanup(event):
    print("[+] Proxy stopped. Removing all port proxy rules and firewall rules...")
    PFwsl.delete_rule()
    os._exit(0)

if __name__ == "__main__":
    args = getArgument()
    PFwsl = netsh()
    
    interface_name = args.interface
    connect_ip = args.r
    ports = args.port

    if args.action == "reset":
        run_as_admin()
        if args.l == None: listen_ip = PFwsl.get_interface_ip(interface_name)
        else: listen_ip = args.l
        PFwsl.reset(listen_ip); exit()
    if args.action == "show": 
        PFwsl.show_rule(); exit()
    if args.port:
        validate_port(args.port)
        run_as_admin()
    else: 
        print(f"{col.FAIL}[-] Argument -p/--port diperlukan.")
        sys.exit()

    if args.l == None: listen_ip = PFwsl.get_interface_ip(interface_name)
    else: listen_ip = args.r

    print(f"[+] Setting up port forwarding from {listen_ip}...")

    for port in ports:
        listen_port, connect_port = port.split(":")
        PFwsl.add_portproxy_rule(listen_ip, listen_port, connect_ip, connect_port)
        PFwsl.add_firewall_rule(listen_port)

    win32api.SetConsoleCtrlHandler(cleanup, True)

    if args.v:
        print("\n".strip())
        PFwsl.show_rule()
    
    # signal.signal(signal.SIGINT, PFwsl.signal_handler)
    # signal.signal(signal.SIGTERM, PFwsl.signal_handler)

    print("\n[+] Proxy running... Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        cleanup(None)