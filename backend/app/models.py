from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String(17), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    hostname = Column(String(255), nullable=True)
    vendor = Column(String(255), nullable=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    # Vector for similarity search (if needed for threat patterns)
    # For example, we could store a feature vector of the device's behavior
    # feature_vector = Column(Vector(128))  # Adjust dimension as needed

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(String(255), nullable=False, index=True)  # e.g., IP, domain, hash
    indicator_type = Column(String(50), nullable=False)  # e.g., 'ip', 'domain', 'hash'
    source = Column(String(50), nullable=False)  # e.g., 'OTX', 'Abuse.ch'
    confidence = Column(Integer, nullable=True)  # Confidence level if provided
    description = Column(Text, nullable=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    # Vector for similarity search (e.g., for storing embeddings of threat descriptions)
    # description_vector = Column(Vector(384))  # Adjust dimension based on embedding model

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    scan_type = Column(String(50), nullable=False)  # e.g., 'nmap', 'vulnerability'
    result = Column(Text, nullable=True)  # JSON or text result
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())