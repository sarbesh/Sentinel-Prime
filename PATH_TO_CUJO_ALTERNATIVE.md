# Sentinel Prime: Path to CUJO-like Universal Deployment

## Executive Summary

This document outlines the strategic path to transform Sentinel Prime into a **universal network security appliance** that can run on any hardware (old laptops, desktop CPUs, Raspberry Pi, embedded routers) while delivering CUJO-level botnet detection, IoT security, and threat intelligence.

---

## Strategic Analysis: Three Deployment Approaches

### Approach 1: Monolithic Appliance (Like CUJO Original)
**Description**: Single pre-built image with all components bundled, deployed as a dedicated OS.

#### Pros:
- ✅ **Simplicity**: One download, one boot, everything works
- ✅ **Performance**: Optimized for specific hardware profiles
- ✅ **Security**: Minimal attack surface, read-only filesystem
- ✅ **User Experience**: Plug-and-play like a consumer appliance
- ✅ **Support**: Single known configuration reduces debugging

#### Cons:
- ❌ **Hardware Limitations**: Must support specific architectures (x86_64, ARM)
- ❌ **Flexibility**: Hard to customize or update individual components
- ❌ **Adoption Barrier**: Requires dedicated hardware, can't test easily
- ❌ **Maintenance**: Each hardware variant needs separate build/test
- ❌ **Developer Friction**: Hard to develop against full appliance

**Verdict**: ❌ **NOT RECOMMENDED** as primary approach - too restrictive for open-source adoption

---

### Approach 2: Container-First (Docker/Kubernetes)
**Description**: All components as microservices in containers, orchestrated via Docker Compose or K8s.

#### Pros:
- ✅ **Portability**: Runs anywhere Docker runs (laptops, servers, cloud, Pi)
- ✅ **Modularity**: Easy to update/replace individual components
- ✅ **Developer Friendly**: Easy to test, debug, extend
- ✅ **Scalability**: Can scale components independently
- ✅ **Integration**: Easy to add new services (ML, logging, etc.)
- ✅ **Cloud-Native**: Can deploy to AWS, Azure, GCP, or on-prem

#### Cons:
- ❌ **Performance Overhead**: Docker networking adds latency (5-15% throughput loss)
- ❌ **Complexity**: Requires Docker knowledge, orchestration setup
- ❌ **Resource Usage**: Multiple containers = more RAM/CPU overhead
- ❌ **Network Mode**: Requires host networking for packet capture (security trade-off)
- ❌ **Boot Time**: Slower startup vs bare metal

**Verdict**: ⚠️ **PARTIAL SOLUTION** - Great for development and server deployment, but not ideal for embedded/router use

---

### Approach 3: Hybrid Modular Architecture (RECOMMENDED)
**Description**: Core engine as lightweight binaries + optional container deployment + multiple deployment modes.

#### Architecture Layers:
```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Deployment Abstraction                        │
│  - Appliance ISO (for old laptops/servers)             │
│  - Docker Compose (for servers/cloud/testing)          │
│  - OpenWrt Package (for routers)                       │
│  - Binary Tarball (for any Linux)                      │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Orchestration (sentinel-core)                │
│  - Service manager (systemd or supervisor)             │
│  - Health monitoring & auto-restart                    │
│  - Configuration management                            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Security Engine                               │
│  - Suricata (IDS/IPS)                                  │
│  - Zeek (Network analysis)                             │
│  - Custom ML Detector (ONNX Runtime)                   │
│  - DNS Security (Blocky integration)                   │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Packet Capture                                │
│  - eBPF/XDP (modern kernels)                           │
│  - AF_PACKET (fallback for older kernels)              │
│  - Netfilter hooks (for integrated firewall)           │
└─────────────────────────────────────────────────────────┘
```

#### Pros:
- ✅ **Maximum Flexibility**: Deploy anywhere from Pi to enterprise server
- ✅ **Performance**: Native binaries for speed-critical paths
- ✅ **Modularity**: Mix-and-match components based on hardware capability
- ✅ **Gradual Adoption**: Start with Docker, migrate to appliance later
- ✅ **Hardware Agnostic**: Supports x86_64, ARMv7, ARM64, MIPS (router CPUs)
- ✅ **Developer Friendly**: Easy to test individual components
- ✅ **Community Contributions**: Easy for others to add deployment targets

#### Cons:
- ❌ **Complexity**: More moving parts to maintain
- ❌ **Testing Matrix**: Must test across all deployment modes
- ❌ **Documentation**: More deployment guides needed
- ❌ **Initial Development**: Higher upfront engineering cost

**Verdict**: ✅ **STRONGLY RECOMMENDED** - Best balance of performance, flexibility, and adoption potential

---

## Recommended Implementation Path

### Phase 0: Foundation (Weeks 1-2)
**Goal**: Establish core architecture and deployment framework

#### Tasks:
1. **Create `sentinel-core` CLI tool** (Go or Rust)
   - Service orchestration
   - Health monitoring
   - Configuration management
   - Auto-updates

2. **Define component interfaces**
   - Packet capture → Flow processor
   - Flow processor → ML detector
   - ML detector → Firewall enforcer
   - All components → Central logger

3. **Set up CI/CD pipeline**
   - Multi-arch builds (x86_64, ARM64, ARMv7)
   - Automated testing on Raspberry Pi, x86 VMs
   - Container image builds
   - ISO image generation

4. **Create deployment templates**
   - Docker Compose (for testing/server)
   - Systemd unit files (for appliance mode)
   - OpenWrt Makefile (for router mode)
   - Installation script (for generic Linux)

**Deliverables**:
- Working `sentinel-core` binary
- Docker Compose setup
- Basic installation script
- CI/CD pipeline

---

### Phase 1: Core Engine (Weeks 3-8)
**Goal**: Build functional botnet detection system

#### Tasks:
1. **Packet Capture Module**
   - Implement eBPF-based flow extractor
   - Fallback to AF_PACKET for older kernels
   - Support multiple network interfaces
   - Flow aggregation (1-second windows)

2. **Suricata Integration**
   - Pre-configured IoT/botnet rulesets
   - Automated rule updates
   - EVE-JSON log parsing
   - Real-time alert forwarding

3. **Device Fingerprinting**
   - Passive OS detection (p0f-style)
   - DHCP fingerprinting
   - mDNS/SSDP device discovery
   - MAC address randomization handling

4. **Basic ML Detector**
   - Train Isolation Forest on IoT-23 dataset
   - Export to ONNX format
   - Implement real-time inference pipeline
   - Detect beaconing, port scanning, anomalies

5. **Web UI (MVP)**
   - Device list with status
   - Recent alerts
   - Basic configuration
   - Real-time traffic visualization

**Hardware Targets**:
- ✅ x86_64 laptops/servers
- ✅ Raspberry Pi 4/5 (4GB+)
- ✅ Docker (any platform with Docker)

**Deliverables**:
- Functional botnet detection
- Device inventory
- Working web dashboard
- Deployment guides for x86 and Pi

---

### Phase 2: Advanced Threat Detection (Weeks 9-16)
**Goal**: Match CUJO's detection capabilities

#### Tasks:
1. **Encrypted Traffic Analysis**
   - JA3/JA4 TLS fingerprinting
   - Detect malicious clients by TLS stack
   - Identify C2 channels by packet patterns
   - SNI (Server Name Indication) analysis

2. **Behavioral Baselining**
   - Per-device traffic profiles
   - Time-based patterns (day/night behavior)
   - Protocol usage baselines
   - Anomaly scoring system

3. **DNS Security Integration**
   - Integrate Blocky or custom DNS proxy
   - DGA (Domain Generation Algorithm) detection
   - DNS tunneling detection
   - Malicious domain blocklists

4. **Lateral Movement Detection**
   - Internal port scanning alerts
   - SMB/RDP anomaly detection
   - Inter-device communication graphs
   - Compromise propagation tracking

5. **Threat Intelligence Feeds**
   - Integrate abuse.ch, Spamhaus, Emerging Threats
   - Automated IOC (Indicators of Compromise) updates
   - Correlation engine (alerts + IOCs)
   - Community threat sharing (optional)

**Hardware Targets**:
- ✅ x86_64 with 4+ cores
- ✅ Raspberry Pi 5 (8GB)
- ✅ Intel NUC / Mini PCs
- ⚠️ Raspberry Pi 4 (reduced feature set)

**Deliverables**:
- CUJO-matching detection capabilities
- Encrypted traffic analysis
- Automated threat response
- Comprehensive threat intelligence

---

### Phase 3: Active Defense & Automation (Weeks 17-24)
**Goal**: Automated threat response like CUJO

#### Tasks:
1. **Dynamic Firewall Engine**
   - nftables rule generation
   - Automated device quarantine
   - Rate limiting for suspicious devices
   - Geoblocking capabilities

2. **VLAN Isolation**
   - Automated VLAN assignment for infected devices
   - Guest network integration
   - IoT device network segmentation
   - Remediation workflow (temporarily allow access)

3. **Incident Response Playbooks**
   - Automated responses by threat type
   - Escalation rules (alert → quarantine → block)
   - User notification system (email, Telegram, etc.)
   - Forensic data preservation

4. **Remediation Assistant**
   - Step-by-step guides for users
   - Device-specific recommendations
   - Firmware update notifications
   - Password change reminders

5. **Advanced ML Models**
   - Deep learning for encrypted traffic classification
   - Federated learning for community model updates
   - Unsupervised clustering for zero-day detection
   - Reinforcement learning for adaptive response

**Hardware Targets**:
- ✅ x86_64 servers (full features)
- ✅ High-end mini PCs
- ⚠️ Raspberry Pi 5 (basic quarantine only)
- ❌ Low-end routers (read-only mode)

**Deliverables**:
- Automated threat containment
- VLAN isolation
- User notification system
- Advanced ML models

---

### Phase 4: Embedded & Router Deployment (Weeks 25-36)
**Goal**: Run on routers and embedded devices

#### Tasks:
1. **OpenWrt Integration**
   - Create OpenWrt package
   - Optimize for MIPS/ARM router CPUs
   - Limited feature set for low-end hardware
   - LuCI web interface integration

2. **Resource Optimization**
   - Reduce memory footprint (< 256MB RAM)
   - CPU-efficient packet sampling
   - Flow aggregation to reduce ML load
   - Selective component loading

3. **Router-Specific Features**
   - WAN/LAN interface detection
   - Bridge mode support
   - PPPoE passthrough
   - Dual-WAN handling

4. **Low-End Hardware Profiles**
   - **Profile A** (Router, <256MB RAM): DNS filtering + basic signatures
   - **Profile B** (Router, 512MB RAM): + Flow analysis + simple ML
   - **Profile C** (Pi/Mini PC, 2GB+ RAM): Full feature set

5. **Zero-Touch Deployment**
   - Pre-configured ISO images for old laptops
   - USB boot images for Raspberry Pi
   - Factory firmware images for supported routers
   - Cloud-init integration for server deployment

**Hardware Targets**:
- ✅ GL.iNet routers (OpenWrt-based)
- ✅ Banana Pi, Orange Pi
- ✅ Old Android TV boxes (with custom ROM)
- ✅ Legacy laptops (5+ years old)
- ✅ PC Engines APU/APU2

**Deliverables**:
- OpenWrt package
- Sub-256MB RAM deployment mode
- Router-friendly UI
- Zero-touch deployment images

---

### Phase 5: Polish & Community (Weeks 37-48)
**Goal**: Production-ready, community-driven project

#### Tasks:
1. **Documentation**
   - User guides for each deployment mode
   - Hardware compatibility list
   - Troubleshooting wiki
   - Video tutorials

2. **Community Features**
   - Optional threat sharing (opt-in, anonymized)
   - Community-maintained rulesets
   - Plugin system for custom detectors
   - Marketplace for detection modules

3. **Enterprise Features** (Optional paid tier)
   - Centralized management dashboard
   - Multi-site deployment
   - SIEM integration (Splunk, ELK)
   - Compliance reporting

4. **Security Hardening**
   - Penetration testing
   - Security audit
   - Secure boot support
   - TPM integration for key storage

5. **Performance Optimization**
   - Benchmark suite
   - Auto-tuning for hardware
   - Throughput optimization
   - Memory usage reduction

**Deliverables**:
- Production release (v1.0)
- Full documentation
- Active community forum
- Enterprise support options

---

## Hardware Compatibility Matrix

| Hardware | RAM | Storage | Deployment Mode | Expected Throughput | Feature Set |
|----------|-----|---------|-----------------|---------------------|-------------|
| **Raspberry Pi 5 (8GB)** | 8GB | microSD/SSD | Appliance/Docker | 800 Mbps - 1 Gbps | Full |
| **Raspberry Pi 4 (4GB)** | 4GB | microSD | Appliance/Docker | 400-600 Mbps | Standard |
| **Raspberry Pi 4 (2GB)** | 2GB | microSD | Appliance | 200-300 Mbps | Basic |
| **Old Laptop (Core i5, 8GB)** | 8GB+ | HDD/SSD | Appliance (ISO boot) | 500-800 Mbps | Full |
| **Mini PC (J4125, 4GB)** | 4GB | eMMC/SSD | Appliance/Docker | 600-900 Mbps | Full |
| **GL.iNet Router (MT1300)** | 256MB | 16MB flash | OpenWrt package | 100-150 Mbps | Limited |
| **GL.iNet Router (MT2500)** | 512MB | 128MB flash | OpenWrt package | 200-300 Mbps | Standard |
| **x86 Server (8+ cores)** | 16GB+ | SSD | Docker/K8s/Appliance | 2-5 Gbps+ | Full + Enterprise |
| **Android TV Box (RK3318)** | 2GB | 16GB eMMC | Custom ROM | 150-250 Mbps | Basic |
| **PC Engines APU2** | 4GB | mSATA SSD | Appliance (ISO) | 400-600 Mbps | Standard |

---

## Critical Technical Decisions

### 1. Packet Capture: eBPF vs Traditional
**Decision**: **eBPF-first with AF_PACKET fallback**

**Rationale**:
- eBPF provides 3-5x better performance on modern kernels (5.4+)
- Zero-copy packet processing
- Can run custom logic in kernel safely
- Fallback to AF_PACKET for older kernels (Pi 3, some routers)

### 2. ML Inference: Edge vs Cloud
**Decision**: **Edge-only by default, optional cloud sync**

**Rationale**:
- Privacy is key differentiator from CUJO
- Modern edge devices (Pi 4+, J4125) can handle ONNX inference
- Reduces latency (no round-trip to cloud)
- Optional federated learning for community benefit without privacy loss

### 3. Rules Engine: Suricata vs Custom
**Decision**: **Suricata for signatures + Custom ML for anomalies**

**Rationale**:
- Suricata has mature, battle-tested rulesets
- Active community and commercial support
- Custom ML needed for behavioral detection (CUJO's strength)
- Best of both worlds: known threats + zero-days

### 4. Deployment: Single Image vs Multi-Container
**Decision**: **Hybrid - native binaries for production, Docker for dev**

**Rationale**:
- Native binaries = best performance (critical for packet processing)
- Docker = easy testing, development, server deployment
- Support both via `sentinel-core` orchestration layer
- Users can choose based on their needs

### 5. Storage: Full PCAP vs Flow Metadata Only
**Decision**: **Flow metadata only (default), optional PCAP on alert**

**Rationale**:
- Full PCAP requires massive storage (terabytes for busy networks)
- Flow metadata sufficient for ML detection
- Capture PCAP only when threat detected (forensic analysis)
- Reduces hardware requirements dramatically

---

## Risk Mitigation Strategies

### Risk 1: Performance Bottlenecks
**Mitigation**:
- Profile early on target hardware (Pi 4, routers)
- Implement adaptive sampling (reduce load on low-end devices)
- Use eBPF for zero-copy capture
- Multi-threading where possible (Suricata already supports)

### Risk 2: False Positives Blocking Legitimate Traffic
**Mitigation**:
- Default to "Alert Only" mode for first 7 days (baselining)
- User confirmation required for first quarantine action
- Whitelist critical services (DNS, DHCP, common IoT)
- Easy rollback mechanism

### Risk 3: Hardware Incompatibility
**Mitigation**:
- Extensive hardware testing program (community-driven)
- Clear compatibility matrix in documentation
- Graceful degradation (reduce features on unsupported hardware)
- Virtual appliance for testing before hardware purchase

### Risk 4: Complexity Overwhelming Users
**Mitigation**:
- Sensible defaults (install and forget)
- Progressive disclosure (basic UI → advanced settings)
- Guided setup wizard
- Video tutorials for common scenarios

---

## Success Metrics

### Technical KPIs:
- **Throughput**: >80% of line rate on recommended hardware
- **Latency**: <5ms added latency for network traffic
- **Memory Usage**: <512MB for full feature set, <128MB for basic mode
- **Detection Rate**: >90% on IoT-23 dataset, <1% false positive rate
- **Boot Time**: <30 seconds to full protection

### Adoption KPIs (Year 1):
- **GitHub Stars**: 5,000+
- **Active Installations**: 10,000+
- **Hardware Partners**: 3+ (Pi, mini PC, router manufacturers)
- **Community Contributors**: 50+
- **Documentation Translations**: 5+ languages

---

## Conclusion & Recommendation

**The Hybrid Modular Architecture (Approach 3) is the optimal path forward** because it:

1. ✅ **Maximizes Hardware Compatibility**: From old laptops to modern routers
2. ✅ **Balances Performance & Flexibility**: Native binaries + container options
3. ✅ **Enables Gradual Adoption**: Start simple, add features as hardware allows
4. ✅ **Supports Community Growth**: Easy contributions, multiple deployment targets
5. ✅ **Competitive with CUJO**: Matches detection capabilities, exceeds on privacy

**Immediate Next Steps:**
1. Create `sentinel-core` CLI tool architecture
2. Set up CI/CD with multi-arch builds
3. Build eBPF packet capture prototype
4. Deploy Suricata on Raspberry Pi 4 for benchmarking
5. Train initial ML model on IoT-23 dataset

**Timeline**: 12 months to full v1.0 release with all deployment modes.

**Budget**: Primarily developer time. Hardware costs ~$1,000 (test devices: Pi 4/5, routers, mini PCs).

This approach positions Sentinel Prime as the **definitive open-source alternative to CUJO** - capable of running on anything from a $5 Raspberry Pi Zero to a $5,000 enterprise server, while maintaining privacy, transparency, and community-driven development.

---

*Document Version: 1.0*  
*Last Updated: June 22, 2026*  
*Status: Ready for Implementation*