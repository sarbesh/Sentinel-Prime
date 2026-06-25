import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/sentinel_prime")
    
    # OTX API
    OTX_API_KEY: str = os.getenv("OTX_API_KEY", "")
    
    # Abuse.ch API keys (if needed)
    ABUSECH_API_KEY: str = os.getenv("ABUSECH_API_KEY", "")
    
    # DHCP listener settings
    DHCP_LISTENER_INTERFACE: str = os.getenv("DHCP_LISTENER_INTERFACE", "eth0")
    DHCP_LISTENER_PORT: int = int(os.getenv("DHCP_LISTENER_PORT", 67))
    
    # Threat intel update interval (in seconds)
    THREAT_INTEL_UPDATE_INTERVAL: int = int(os.getenv("THREAT_INTEL_UPDATE_INTERVAL", 3600))
    
    class Config:
        env_file = ".env"

settings = Settings()