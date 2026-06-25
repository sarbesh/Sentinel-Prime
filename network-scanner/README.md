# Network Scanner (Kali Linux)

## Purpose
Scan network for devices, open ports/services, detect vulnerabilities, and associate with device names.

## Architecture
The network scanner runs inside the **Kali Linux** container (backend). Uses `kalilinux/kali-rolling` with `kali-linux-headless` metapackage.

## Installed Tools
The `kali-linux-headless` package includes 100+ security tools:

### Network Scanning
- **nmap** - Network mapper, port scanning, OS detection
- **masscan** - Fast TCP port scanner
- **zmap** - Fast single-packet network scanner
- **fping** - Ping multiple hosts quickly
- **hping3** - Active network packet crafter
- **netcat-openbsd** - Swiss army knife for networking

### Web Scanning
- **nikto** - Web server scanner
- **dirb** - Web content scanner
- **gobuster** - Directory/file brute-forcer
- **wpscan** - WordPress security scanner
- **joomscan** - Joomla CMS scanner
- **wapiti** - Web application vulnerability scanner
- **whatweb** - Web technology fingerprinting

### Vulnerability Assessment
- **sqlmap** - SQL injection automated tool
- **metasploit-framework** - Penetration testing framework
- **nuclei** - Vulnerability scanner using templates

### Password Attacks
- **hydra** - Login cracker
- **john** - Password cracker

### Information Gathering
- **enum4linux** - Windows/Samba enumeration
- **smbclient** - SMB/CIFS client
- **ldap-utils** - LDAP utilities
- **snmp** - SNMP tools
- **sslscan** - SSL/TLS scanner
- **sslyze** - SSL/TLS configuration scanner

### Network Analysis
- **tcpdump** - Packet analyzer
- **wireshark** - Network protocol analyzer

### Exploitation
- **msfconsole** - Metasploit framework console
- **searchsploit** - Exploit database search

## Features
- **Ping Scan**: Discover pingable devices on the network
- **No-Ping Scan**: Detect hosts that don't respond to ping but have open ports (`-Pn` flag)
- **Deep Scan**: Comprehensive scan with OS detection, service version detection, and vulnerability assessment
- **Vulnerability Detection**: Identify known vulnerable services with CVE information and exploit availability

## Network Configuration
The backend uses `network_mode: host` in docker-compose to:
- Scan the host's network directly
- Access all network interfaces
- Perform ARP discovery and port scanning

## API/Integration

### Endpoints
- `POST /scans/network` - Run a network scan
- `GET /scans/vulnerabilities` - List all vulnerabilities
- `GET /scans/vulnerabilities/{id}` - Get specific vulnerability
- `POST /scans/vulnerabilities/{id}/acknowledge` - Acknowledge vulnerability

### Scan Types
- `ping` - Quick ping scan to find online hosts
- `port` / `noping` - Port scan with `-Pn` (no ping) flag
- `deep` - Deep scan with OS detection, service versioning, and vulnerability checking
- `quick` - Fast scan with common ports

### Example Request
```bash
curl -X POST http://localhost:8000/scans/network \
  -H "Content-Type: application/json" \
  -d '{
    "target": "192.168.1.0/24",
    "scan_type": "ping"
  }'
```

## Vulnerability Database
The scanner includes a database of known vulnerabilities for common services:
- Apache, Nginx (HTTP)
- OpenSSH, Dropbear (SSH)
- vsftpd, ProFTPD (FTP)
- Samba
- MySQL, PostgreSQL
- Redis, MongoDB
- Docker API
- SMB/RDP

## Extending with More Tools

### Example: Adding nikto web scan
```python
import subprocess

def run_nikto(host):
    result = subprocess.run(
        ["nikto", "-h", host],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Example: Adding SQLMap
```python
def run_sqlmap(target):
    result = subprocess.run(
        ["sqlmap", "-u", target, "--batch"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Example: Adding Nuclei scan
```python
def run_nuclei(target):
    result = subprocess.run(
        ["nuclei", "-u", target, "-severity", "critical,high,medium"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### Example: Adding masscan
```python
def run_masscan(network, ports):
    result = subprocess.run(
        ["masscan", "-p", ports, network, "--rate=1000"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Contributing
- Add new scanner modules using Kali tools
- Improve vulnerability detection
- Add more CVE mappings
- Integrate additional security tools
