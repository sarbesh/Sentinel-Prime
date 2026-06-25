import json
import logging
import os
from datetime import datetime
from typing import List, Optional

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")

if VECTOR_DB_URL:
    try:
        engine = create_engine(VECTOR_DB_URL, poolclass=NullPool)
        
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vector_devices (
                    id SERIAL PRIMARY KEY,
                    mac_address VARCHAR(50) UNIQUE NOT NULL,
                    ip_address VARCHAR(50),
                    hostname VARCHAR(255),
                    vendor VARCHAR(255),
                    os_detection VARCHAR(255),
                    first_seen TIMESTAMP DEFAULT NOW(),
                    last_seen TIMESTAMP DEFAULT NOW()
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_vector_devices_mac 
                ON vector_devices(mac_address)
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vector_services (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    version VARCHAR(100),
                    UNIQUE(service_name, version)
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_vector_services_name 
                ON vector_services(service_name)
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vector_device_services (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES vector_devices(id) ON DELETE CASCADE,
                    service_id INTEGER REFERENCES vector_services(id) ON DELETE CASCADE,
                    port INTEGER,
                    protocol VARCHAR(20),
                    discovered_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(device_id, service_id, port)
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_vector_device_services_device 
                ON vector_device_services(device_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_vector_device_services_service 
                ON vector_device_services(service_id)
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scan_embeddings (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES vector_devices(id) ON DELETE CASCADE,
                    scan_type VARCHAR(50),
                    embedding VECTOR(384),
                    raw_text TEXT,
                    metadata JSONB,
                    scanned_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_scan_embeddings_device 
                ON scan_embeddings(device_id)
            """))
            
            conn.commit()
        logger.info("Vector database initialized with new schema")
    except Exception as e:
        logger.warning(f"Vector DB not available: {e}")
        engine = None
else:
    logger.warning("VECTOR_DB_URL not set, vector storage disabled")
    engine = None


def generate_embedding(text: str) -> List[float]:
    """Generate a simple embedding from text using character n-grams."""
    text = text.lower()
    embedding = np.zeros(384)
    
    for i, char in enumerate(text[:384]):
        embedding[i] = ord(char) / 255.0
    
    for i in range(len(text) - 1):
        idx = (ord(text[i]) * 256 + ord(text[i + 1])) % 384
        embedding[idx] += 1.0
    
    embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
    
    return embedding.tolist()


def get_or_create_device(
    mac_address: str,
    ip_address: str = None,
    hostname: str = None,
    vendor: str = None,
    os_detection: str = None,
) -> Optional[int]:
    """Get or create a device and return its ID."""
    if not engine:
        return None
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id FROM vector_devices 
                    WHERE mac_address = :mac
                """),
                {"mac": mac_address}
            ).fetchone()
            
            if result:
                conn.execute(
                    text("""
                        UPDATE vector_devices 
                        SET ip_address = :ip, hostname = :hostname, 
                            vendor = :vendor, os_detection = :os,
                            last_seen = NOW()
                        WHERE id = :id
                    """),
                    {
                        "id": result[0],
                        "ip": ip_address,
                        "hostname": hostname,
                        "vendor": vendor,
                        "os": os_detection,
                    }
                )
                conn.commit()
                return result[0]
            
            result = conn.execute(
                text("""
                    INSERT INTO vector_devices 
                    (mac_address, ip_address, hostname, vendor, os_detection)
                    VALUES (:mac, :ip, :hostname, :vendor, :os)
                    RETURNING id
                """),
                {
                    "mac": mac_address,
                    "ip": ip_address,
                    "hostname": hostname,
                    "vendor": vendor,
                    "os": os_detection,
                }
            ).fetchone()
            conn.commit()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Failed to get/create device: {e}")
        return None


def get_or_create_service(
    service_name: str,
    version: str = None,
) -> Optional[int]:
    """Get or create a service and return its ID."""
    if not engine:
        return None
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id FROM vector_services 
                    WHERE service_name = :name AND (version = :version OR (version IS NULL AND :version IS NULL))
                """),
                {"name": service_name, "version": version}
            ).fetchone()
            
            if result:
                return result[0]
            
            result = conn.execute(
                text("""
                    INSERT INTO vector_services (service_name, version)
                    VALUES (:name, :version)
                    RETURNING id
                """),
                {"name": service_name, "version": version}
            ).fetchone()
            conn.commit()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Failed to get/create service: {e}")
        return None


def link_device_service(
    device_id: int,
    service_id: int,
    port: int = None,
    protocol: str = None,
) -> bool:
    """Link a device to a service with port info."""
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO vector_device_services (device_id, service_id, port, protocol)
                    VALUES (:device_id, :service_id, :port, :protocol)
                    ON CONFLICT (device_id, service_id, port) DO NOTHING
                """),
                {
                    "device_id": device_id,
                    "service_id": service_id,
                    "port": port,
                    "protocol": protocol,
                }
            )
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to link device service: {e}")
        return False


def store_scan_embedding(
    mac_address: str,
    ip_address: str,
    hostname: str = None,
    vendor: str = None,
    os_detection: str = None,
    scan_type: str = None,
    services: List[dict] = None,
    vulnerabilities: List[dict] = None,
    raw_data: dict = None,
) -> Optional[int]:
    """Store scan data with proper device/service mapping. Returns device_id."""
    if not engine:
        logger.warning("Vector DB not available, skipping embedding storage")
        return None
    
    services = services or []
    vulnerabilities = vulnerabilities or []
    
    try:
        device_id = get_or_create_device(
            mac_address=mac_address,
            ip_address=ip_address,
            hostname=hostname,
            vendor=vendor,
            os_detection=os_detection,
        )
        
        if not device_id:
            return None
        
        for svc in services:
            service_name = svc.get("service", "unknown")
            version = svc.get("version")
            port = svc.get("port")
            protocol = svc.get("protocol", "tcp")
            
            service_id = get_or_create_service(service_name, version)
            if service_id:
                link_device_service(device_id, service_id, port, protocol)
        
        raw_text = f"""
            IP: {ip_address}
            MAC: {mac_address}
            OS: {os_detection or 'unknown'}
            Hostname: {hostname or 'unknown'}
            Services: {json.dumps(services)}
            Vulnerabilities: {json.dumps(vulnerabilities)}
        """
        
        embedding = generate_embedding(raw_text)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        
        metadata = {
            "services": services,
            "vulnerabilities": vulnerabilities,
            "port_count": len(services),
            "vuln_count": len(vulnerabilities),
            "critical_vulns": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
        }
        
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO scan_embeddings 
                    (device_id, scan_type, embedding, raw_text, metadata)
                    VALUES (:device_id, :scan_type, :embedding, :text, :metadata)
                """),
                {
                    "device_id": device_id,
                    "scan_type": scan_type,
                    "embedding": embedding_str,
                    "text": raw_text,
                    "metadata": json.dumps(metadata),
                }
            )
            conn.commit()
        
        logger.info(f"Stored embedding for {mac_address} ({ip_address})")
        return device_id
        
    except Exception as e:
        logger.error(f"Failed to store embedding: {e}")
        return None


def get_device_services(device_id: int) -> List[dict]:
    """Get all services for a device."""
    if not engine:
        return []
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT ds.port, ds.protocol, ds.discovered_at,
                           s.service_name, s.version
                    FROM vector_device_services ds
                    JOIN vector_services s ON ds.service_id = s.id
                    WHERE ds.device_id = :device_id
                    ORDER BY ds.port
                """),
                {"device_id": device_id}
            )
            
            return [
                {
                    "port": row[0],
                    "protocol": row[1],
                    "discovered_at": row[2].isoformat() if row[2] else None,
                    "service_name": row[3],
                    "version": row[4],
                }
                for row in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Failed to get device services: {e}")
        return []


def get_service_devices(service_name: str = None, version: str = None) -> List[dict]:
    """Get all devices running a specific service (optionally with version)."""
    if not engine:
        return []
    
    try:
        with engine.connect() as conn:
            if service_name:
                if version:
                    result = conn.execute(
                        text("""
                            SELECT d.mac_address, d.ip_address, d.hostname, 
                                   ds.port, ds.protocol, ds.discovered_at
                            FROM vector_device_services ds
                            JOIN vector_devices d ON ds.device_id = d.id
                            JOIN vector_services s ON ds.service_id = s.id
                            WHERE s.service_name = :name AND s.version = :version
                            ORDER BY d.last_seen DESC
                        """),
                        {"name": service_name, "version": version}
                    )
                else:
                    result = conn.execute(
                        text("""
                            SELECT d.mac_address, d.ip_address, d.hostname,
                                   ds.port, ds.protocol, ds.discovered_at
                            FROM vector_device_services ds
                            JOIN vector_devices d ON ds.device_id = d.id
                            JOIN vector_services s ON ds.service_id = s.id
                            WHERE s.service_name = :name
                            ORDER BY d.last_seen DESC
                        """),
                        {"name": service_name}
                    )
            else:
                result = conn.execute(
                    text("""
                        SELECT DISTINCT s.service_name, s.version, 
                               COUNT(ds.id) as device_count
                        FROM vector_services s
                        JOIN vector_device_services ds ON s.id = ds.service_id
                        GROUP BY s.id
                        ORDER BY device_count DESC
                    """)
                )
                return [
                    {
                        "service_name": row[0],
                        "version": row[1],
                        "device_count": row[2],
                    }
                    for row in result.fetchall()
                ]
            
            return [
                {
                    "mac_address": row[0],
                    "ip_address": row[1],
                    "hostname": row[2],
                    "port": row[3],
                    "protocol": row[4],
                    "discovered_at": row[5].isoformat() if row[5] else None,
                }
                for row in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Failed to get service devices: {e}")
        return []


def get_all_devices() -> List[dict]:
    """Get all devices in vector storage."""
    if not engine:
        return []
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, mac_address, ip_address, hostname, vendor, 
                           os_detection, first_seen, last_seen
                    FROM vector_devices
                    ORDER BY last_seen DESC
                """)
            )
            
            return [
                {
                    "id": row[0],
                    "mac_address": row[1],
                    "ip_address": row[2],
                    "hostname": row[3],
                    "vendor": row[4],
                    "os_detection": row[5],
                    "first_seen": row[6].isoformat() if row[6] else None,
                    "last_seen": row[7].isoformat() if row[7] else None,
                }
                for row in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Failed to get all devices: {e}")
        return []


def get_all_services() -> List[dict]:
    """Get all unique services."""
    if not engine:
        return []
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT s.id, s.service_name, s.version, 
                           COUNT(ds.id) as device_count
                    FROM vector_services s
                    LEFT JOIN vector_device_services ds ON s.id = ds.service_id
                    GROUP BY s.id
                    ORDER BY device_count DESC, s.service_name
                """)
            )
            
            return [
                {
                    "id": row[0],
                    "service_name": row[1],
                    "version": row[2],
                    "device_count": row[3],
                }
                for row in result.fetchall()
            ]
    except Exception as e:
        logger.error(f"Failed to get all services: {e}")
        return []


def search_similar_hosts(query: str, limit: int = 5) -> List[dict]:
    """Search for similar hosts using vector similarity."""
    if not engine:
        return []
    
    try:
        query_embedding = generate_embedding(query)
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT e.id, e.device_id, e.scan_type, 
                           e.raw_text, e.metadata, e.scanned_at,
                           1 - (e.embedding <=> :embedding::vector) as similarity,
                           d.mac_address, d.ip_address, d.hostname
                    FROM scan_embeddings e
                    JOIN vector_devices d ON e.device_id = d.id
                    ORDER BY e.embedding <=> :embedding::vector
                    LIMIT :limit
                """),
                {"embedding": embedding_str, "limit": limit}
            )
            
            rows = result.fetchall()
            return [
                {
                    "id": row[0],
                    "device_id": row[1],
                    "scan_type": row[2],
                    "raw_text": row[3],
                    "metadata": json.loads(row[4]) if row[4] else {},
                    "scanned_at": row[5].isoformat() if row[5] else None,
                    "similarity": row[6],
                    "mac_address": row[7],
                    "ip_address": row[8],
                    "hostname": row[9],
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


def get_embedding_stats() -> dict:
    """Get statistics about stored embeddings."""
    if not engine:
        return {"status": "unavailable"}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM scan_embeddings")).fetchone()
            total = result[0] if result else 0
            
            result = conn.execute(text("SELECT COUNT(*) FROM vector_devices")).fetchone()
            device_count = result[0] if result else 0
            
            result = conn.execute(text("SELECT COUNT(*) FROM vector_services")).fetchone()
            service_count = result[0] if result else 0
            
            result = conn.execute(text("SELECT COUNT(*) FROM vector_device_services")).fetchone()
            mapping_count = result[0] if result else 0
            
            return {
                "status": "available",
                "total_embeddings": total,
                "device_count": device_count,
                "service_count": service_count,
                "device_service_mappings": mapping_count,
            }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"status": "error", "message": str(e)}
