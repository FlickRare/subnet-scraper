#!/usr/bin/env python3
"""
A script to detect if the host system is Windows or Linux and ping the 192.168.1.0/24 subnet.
"""
import platform
import subprocess
import ipaddress
import time
import argparse
import csv
import os
import sys
from datetime import datetime

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

def ping_ip_windows(ip, timeout=100, count=1):
    """
    Pings a single IP address from a Windows device.
    
    Args:
        ip (str): IP address to ping
        timeout (int): Timeout in milliseconds (default: 100)
        count (int): Number of ping attempts (default: 1)
        
    Returns:
        bool: True if the IP responded, False otherwise
    """
    ip_str = str(ip)
    try:
        # Windows ping command with timeout in milliseconds
        cmd = ["ping", "-n", str(count), "-w", str(timeout), ip_str]
        
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
            return True
        else:
            return False
            
    except Exception as e:
        return False

def ping_ip_linux(ip, timeout=0.1, count=1):
    """
    Pings a single IP address from a Linux device.
    
    Args:
        ip (str): IP address to ping
        timeout (float): Timeout in seconds (default: 0.1)
        count (int): Number of ping attempts (default: 1)
        
    Returns:
        bool: True if the IP responded, False otherwise
    """
    ip_str = str(ip)
    try:
        # Linux ping command with timeout in seconds
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout * 1000)), ip_str]
        
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
            return True
        else:
            return False
            
    except Exception as e:
        return False

def parse_args():
    """
    Parse command line arguments and convert subnet(s) to list of IP addresses.
    
    Returns:
        tuple: (list of IP addresses to ping, dictionary mapping subnets to their IPs)
    """
    parser = argparse.ArgumentParser(description="Ping all hosts in a subnet")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--network", help="Subnet to ping in CIDR notation (e.g., 192.168.1.0/24)")
    group.add_argument("-i", "--input", help="CSV file containing subnets to ping (one subnet per line)")
    args = parser.parse_args()
    
    ip_list = []
    subnet_map = {}  # Maps subnet to list of IPs in that subnet
    
    # Process subnet from command line
    if args.network:
        try:
            network = ipaddress.IPv4Network(args.network)
            subnet_ips = [str(ip) for ip in network.hosts()]
            ip_list.extend(subnet_ips)
            subnet_map[args.network] = subnet_ips
            print(f"Parsed subnet {args.network} into {len(subnet_ips)} IP addresses")
        except ValueError as e:
            print(f"Error parsing subnet: {e}")
            exit(1)
    
    # Process subnets from CSV file
    elif args.input:
        try:
            with open(args.input, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    if row:  # Skip empty rows
                        subnet = row[0].strip()  # Assume subnet is in the first column
                        try:
                            network = ipaddress.IPv4Network(subnet)
                            subnet_ips = [str(ip) for ip in network.hosts()]
                            ip_list.extend(subnet_ips)
                            subnet_map[subnet] = subnet_ips
                            print(f"Parsed subnet {subnet} into {len(subnet_ips)} IP addresses")
                        except ValueError as e:
                            print(f"Warning: Skipping invalid subnet '{subnet}': {e}")
            
            if not ip_list:
                print("Error: No valid subnets found in the CSV file")
                exit(1)
        except FileNotFoundError:
            print(f"Error: CSV file '{args.input}' not found")
            exit(1)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            exit(1)
    
    print(f"Total IP addresses to ping: {len(ip_list)}")
    return ip_list, subnet_map

def display_progress(subnet, current, total, reachable_count=None):
    """
    Display simple progress information for the current subnet being pinged.
    
    Args:
        subnet (str): The subnet being pinged
        current (int): Current IP index
        total (int): Total number of IPs in the subnet
        reachable_count (int, optional): Number of reachable hosts so far
    """
    # Only show progress at start, 25%, 50%, 75% and completion
    progress_points = [1, int(total * 0.25), int(total * 0.5), int(total * 0.75), total]
    
    if current in progress_points or current == total:
        percent = int(100 * current / total)
        if reachable_count is not None and current == total:
            print(f"Scanning subnet {subnet}... 100% complete. Found {reachable_count} reachable hosts.")
        else:
            print(f"Scanning subnet {subnet}... {percent}% complete ({current}/{total})")

def output(results, subnet_map):
    """
    Output the ping results to CSV files, one per subnet.
    
    Args:
        results (dict): Dictionary with IP addresses as keys and boolean values indicating if they responded
        subnet_map (dict): Dictionary mapping subnet to list of IPs in that subnet
    """
    # Get current date in DDMMMYYYY format (e.g., 15JUN2025)
    current_date = datetime.now().strftime("%d%b%Y").upper()
    
    # Process each subnet
    for subnet, ips in subnet_map.items():
        # Create filename: DDMMMYYYY_ping results_network ID.csv
        # Replace '/' with '_' in subnet for filename
        subnet_clean = subnet.replace('/', '_')
        filename = f"{current_date}_ping results_{subnet_clean}.csv"
        
        print(f"Writing results for subnet {subnet} to {filename}")
        
        # Create directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        filepath = os.path.join('results', filename)
        
        # Write results to CSV
        with open(filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header
            csv_writer.writerow(['IP Address', 'Reachable'])
            
            # Write data for IPs in this subnet
            for ip in ips:
                csv_writer.writerow([ip, str(results.get(ip, False)).lower()])
        
        print(f"Results saved to {filepath}")

def main():
    """
    Main function that orchestrates the subnet scanning process.
    """
    # Parse command line arguments and get list of IPs
    ip_list, subnet_map = parse_args()
    
    # Detect OS
    os_type = check_os()
    print(f"Detected OS: {os_type}")
    
    # Select the appropriate ping function based on OS
    if os_type == 'windows':
        ping_function = ping_ip_windows
    elif os_type == 'linux':
        ping_function = ping_ip_linux
    else:
        print(f"Unsupported OS: {os_type}")
        return
    
    # Create results dictionary
    results = {}
    
    # Process each subnet separately
    for subnet, subnet_ips in subnet_map.items():
        print(f"\nStarting scan of subnet {subnet} ({len(subnet_ips)} hosts)...")
        
        # Track reachable hosts for this subnet
        subnet_reachable = 0
        
        # Ping each IP in the subnet
        for i, ip in enumerate(subnet_ips, 1):
            # Ping the IP
            is_reachable = ping_function(ip)
            results[ip] = is_reachable
            
            # Update reachable count if host is up
            if is_reachable:
                subnet_reachable += 1
            
            # Display simplified progress at key points
            display_progress(subnet, i, len(subnet_ips),
                            reachable_count=subnet_reachable if i == len(subnet_ips) else None)
            
            # Small delay to avoid flooding the network
            time.sleep(0.1)
    
    # Summarize results in CLI
    reachable = sum(1 for is_reachable in results.values() if is_reachable)
    print(f"\nScan complete: {reachable} out of {len(ip_list)} hosts are reachable")
    
    # Output results to CSV files
    output(results, subnet_map)

if __name__ == "__main__":
    main()