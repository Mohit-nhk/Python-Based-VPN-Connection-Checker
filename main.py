import subprocess
import requests
import socket

# Configuration: Replace with your VPN's expected public IP (e.g., from provider)
expected_vpn_ip = "219.100.37.234"  # Example: "185.123.45.67"

def check_vpn_status():
    """Check VPN status via ping to a public server."""
    try:
        # Ping 8.8.8.8 (Google DNS) with 1 packet, timeout 5s (Windows style)
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "5000", "8.8.8.8"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, "VPN appears active (ping successful)."
        else:
            return False, "VPN may be inactive (ping failed)."
    except Exception as e:
        return False, f"Error checking VPN: {str(e)}"

def get_public_ip():
    """Fetch current public IP using an external service."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            return response.json()["ip"]
        else:
            return None
    except Exception as e:
        return None

def check_ip_leak(current_ip):
    """Check for IP leaks by comparing current IP to expected VPN IP."""
    if current_ip == expected_vpn_ip:
        return True, "No IP leak detected."
    else:
        return False, f"Potential IP leak: Current IP ({current_ip}) does not match VPN IP ({expected_vpn_ip})."

def check_open_ports():
    """Check for open ports on localhost (basic scan of common ports)."""
    common_ports = [22, 80, 443]  # SSH, HTTP, HTTPS
    open_ports = []
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    if open_ports:
        return False, f"Open ports detected on localhost: {open_ports}. Ensure they're needed and secured."
    else:
        return True, "No common open ports detected on localhost."

def main():
    print("VPN Status and Security Checker\n")
    
    # Check VPN status
    vpn_active, vpn_msg = check_vpn_status()
    print(f"VPN Status: {'PASS' if vpn_active else 'FAIL'} - {vpn_msg}")
    
    # Get public IP and check for leaks
    current_ip = get_public_ip()
    if current_ip:
        leak_safe, leak_msg = check_ip_leak(current_ip)
        print(f"IP Leak Check: {'PASS' if leak_safe else 'FAIL'} - {leak_msg}")
    else:
        print("IP Leak Check: FAIL - Unable to fetch public IP.")
    
    # Check for open ports
    ports_safe, ports_msg = check_open_ports()
    print(f"Open Ports Check: {'PASS' if ports_safe else 'FAIL'} - {ports_msg}")
    
    # Overall summary
    all_pass = vpn_active and leak_safe and ports_safe
    print(f"\nOverall: {'SECURE' if all_pass else 'ISSUES DETECTED'}")

if __name__ == "__main__":
    main()