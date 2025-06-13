#!/usr/bin/env python3
"""
A script to detect if the host system is Windows or Linux and ping the 192.168.1.0/24 subnet.
"""
import platform
import subprocess
import ipaddress
import time
import argparse

def check_os():
    """
    Checks if the host system is Windows or Linux.
    
    Returns:
        str: 'windows', 'linux', or 'other' depending on the detected OS
    """
    system = platform.system().lower()
    
    if 'windows' in system:
        return 'windows'
    elif 'linux' in system:
        return 'linux'
    else:
        return 'other'

def ping_subnet_windows(subnet="192.168.1.0/24", timeout=100, count=1):
    """
    Pings all IP addresses in the specified subnet from a Windows device.
    
    Args:
        subnet (str): The subnet to ping in CIDR notation (default: 192.168.1.0/24)
        timeout (int): Timeout in milliseconds (default: 100)
        count (int): Number of ping attempts per IP (default: 1)
        
    Returns:
        dict: Dictionary with IP addresses as keys and boolean values indicating if they responded
    """
    results = {}
    network = ipaddress.IPv4Network(subnet)
    
    print(f"Pinging subnet {subnet} from Windows...")
    
    for ip in network.hosts():
        ip_str = str(ip)
        try:
            # Windows ping command with timeout in milliseconds
            cmd = ["ping", "-n", str(count), "-w", str(timeout), ip_str]
            print(f"Executing: {' '.join(cmd)}")
            
            # Run the ping command and capture output
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False  # Explicitly set check to False to avoid raising an exception on non-zero exit code
            )
            
            # Check if ping was successful (return code 0)
            if result.returncode == 0 and "Reply from" in result.stdout:
                results[ip_str] = True
                print(f"{ip_str} is reachable")
            else:
                results[ip_str] = False
                print(f"{ip_str} is not reachable")
                
        except Exception as e:
            results[ip_str] = False
            print(f"Error pinging {ip_str}: {e}")
        
        # Small delay to avoid flooding the network
        time.sleep(0.1)
    
    return results

def ping_subnet_linux(subnet="192.168.1.0/24", timeout=0.1, count=1):
    """
    Pings all IP addresses in the specified subnet from a Linux device.
    
    Args:
        subnet (str): The subnet to ping in CIDR notation (default: 192.168.1.0/24)
        timeout (float): Timeout in seconds (default: 0.1)
        count (int): Number of ping attempts per IP (default: 1)
        
    Returns:
        dict: Dictionary with IP addresses as keys and boolean values indicating if they responded
    """
    results = {}
    network = ipaddress.IPv4Network(subnet)
    
    print(f"Pinging subnet {subnet} from Linux...")
    
    for ip in network.hosts():
        ip_str = str(ip)
        try:
            # Linux ping command with timeout in seconds
            cmd = ["ping", "-c", str(count), "-W", str(int(timeout * 1000)), ip_str]
            print(f"Executing: {' '.join(cmd)}")
            
            # Run the ping command and capture output
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False  # Explicitly set check to False to avoid raising an exception on non-zero exit code
            )
            
            # Check if ping was successful (return code 0)
            if result.returncode == 0:
                results[ip_str] = True
                print(f"{ip_str} is reachable")
            else:
                results[ip_str] = False
                print(f"{ip_str} is not reachable")
                
        except Exception as e:
            results[ip_str] = False
            print(f"Error pinging {ip_str}: {e}")
        
        # Small delay to avoid flooding the network
        time.sleep(0.1)
    
    return results

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Ping all hosts in a subnet")
    parser.add_argument("-n", "--network", required=True, help="Subnet to ping in CIDR notation (e.g., 192.168.1.0/24)")
    return parser.parse_args()

def main():
    """
    Main function that orchestrates the subnet scanning process.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Detect OS
    os_type = check_os()
    print(f"Detected OS: {os_type}")
    
    # Call the appropriate ping function based on OS
    if os_type == 'windows':
        ping_subnet_windows(subnet=args.network)
    elif os_type == 'linux':
        ping_subnet_linux(subnet=args.network)
    else:
        print(f"Unsupported OS: {os_type}")

if __name__ == "__main__":
    main()