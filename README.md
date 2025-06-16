# Subnet Scraper

A multi-threaded subnet scanning utility that pings all hosts within specified network ranges and outputs results to CSV files.

## Features

- Multi-threaded scanning with Python's ThreadPoolExecutor
- Cross-platform compatibility (Windows/Linux)
- Support for direct subnet input or CSV file with multiple subnets
- Progress reporting with host ID ranges
- CSV output files with reachability results

## Installation

Requires Python 3.6+ with no additional dependencies.

```bash
git clone https://github.com/yourusername/subnet-scraper.git
cd subnet-scraper
```

## Usage

### Scan a single subnet

```bash
python3 subnet-scraper.py -n 192.168.1.0/24
```

### Scan multiple subnets from a CSV file

```bash
python3 subnet-scraper.py -i subnets.csv
```

The CSV file should contain one subnet per line in CIDR notation:
```
192.168.1.0/24
10.0.0.0/24
```

### Command Line Options

- `-n, --network`: Subnet in CIDR notation
- `-i, --input`: CSV file with subnets (one per line)
- `-h, --help`: Display help information

## How It Works

1. **Input Processing**: Parses arguments and processes subnet specifications
2. **OS Detection**: Uses appropriate ping command based on the operating system
3. **Thread Pool**: Concurrently pings all IP addresses with optimal thread count
4. **Progress Reporting**: Shows scanning progress with host ID ranges
5. **CSV Output**: Generates files in `results/` directory with naming convention:
   `DDMMMYYYY_ping results_network ID.csv`

Each CSV contains two columns: IP Address and Reachable (true/false).

## Example Output

```
Parsed subnet 192.168.1.0/24 into 254 IP addresses
Total IP addresses to ping: 254
Detected OS: linux

Starting scan of subnet 192.168.1.0/24 (254 hosts)...
Scanning subnet 192.168.1.0/24... 0% complete (.1 - .1)
Scanning subnet 192.168.1.0/24... 24% complete (.2 - .63)
Scanning subnet 192.168.1.0/24... 50% complete (.64 - .127)
Scanning subnet 192.168.1.0/24... 74% complete (.128 - .190)
Scanning subnet 192.168.1.0/24... 100% complete. Found 12 reachable hosts.

Scan complete: 12 out of 254 hosts are reachable
Writing results for subnet 192.168.1.0/24 to 16JUN2025_ping results_192.168.1.0_24.csv
Results saved to results/16JUN2025_ping results_192.168.1.0_24.csv
```

## Credits

Vibe coded with the RooCode VSCode extension and Claude 3.7 Sonnet.

**Note**: Always ensure you have permission to scan the networks you target.