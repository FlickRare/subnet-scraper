#!/usr/bin/env python3
"""
A simple script to detect if the host system is Windows or Linux.
"""
import platform

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

if __name__ == "__main__":
    os_type = check_os()
    print(f"Detected OS: {os_type}")