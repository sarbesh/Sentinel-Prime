import asyncio
import logging
import time
from datetime import datetime, timezone
import requests
from app.core.database import SessionLocal
from app.models import ThreatIntelligence
from app.core.config import settings

logger = logging.getLogger(__name__)

class ThreatIntelUpdater:
    def __init__(self):
        self.otx_api_key = settings.OTX_API_KEY
        self.abusech_api_key = settings.ABUSECH_API_KEY
        self.update_interval = settings.THREAT_INTEL_UPDATE_INTERVAL
        self.running = False

    async def start_updater(self):
        """Start the threat intelligence updater in a background task."""
        self.running = True
        logger.info("Starting threat intelligence updater")
        while self.running:
            try:
                await self.update_feeds()
            except Exception as e:
                logger.error(f"Error updating threat intelligence feeds: {e}")
            # Wait for the next update interval
            await asyncio.sleep(self.update_interval)

    def stop_updater(self):
        self.running = False

    async def update_feeds(self):
        """Update threat intelligence feeds from OTX and Abuse.ch."""
        logger.info("Updating threat intelligence feeds")
        await self._update_otx()
        await self._update_abusech()
        logger.info("Finished updating threat intelligence feeds")

    async def _update_otx(self):
        """Fetch indicators from OTX (AlienVault Open Threat Exchange)."""
        if not self.otx_api_key:
            logger.warning("OTX API key not set, skipping OTX update")
            return

        # Example: Fetching pulses (you can adjust the type of data you want)
        # OTX API documentation: https://otx.alienvault.com/api
        headers = {"X-OTX-API-KEY": self.otx_api_key}
        # We'll fetch pulses modified in the last day (adjust as needed)
        url = "https://otx.alienvault.com/api/v1/pulses/since/1"
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            pulses = data.get("results", [])
            logger.info(f"Fetched {len(pulses)} pulses from OTX")
            db = SessionLocal()
            for pulse in pulses:
                # Extract indicators from the pulse
                for indicator in pulse.get("indicators", []):
                    indicator_type = indicator.get("type")
                    indicator_value = indicator.get("indicator")
                    # Map OTX indicator types to our types (simplified)
                    # You may want to adjust this mapping
                    type_mapping = {
                        "IPv4": "ip",
                        "IPv6": "ip",
                        "domain": "domain",
                        "hostname": "domain",
                        "URL": "url",
                        "FileHash-MD5": "hash",
                        "FileHash-SHA1": "hash",
                        "FileHash-SHA256": "hash",
                    }
                    db_type = type_mapping.get(indicator_type, "other")
                    # Check if we already have this indicator to avoid duplicates
                    existing = db.query(ThreatIntelligence).filter(
                        ThreatIntelligence.indicator == indicator_value,
                        ThreatIntelligence.indicator_type == db_type,
                        ThreatIntelligence.source == "OTX"
                    ).first()
                    if not existing:
                        ti = ThreatIntelligence(
                            indicator=indicator_value,
                            indicator_type=db_type,
                            source="OTX",
                            confidence=int(pulse.get("tlp", 0)),  # TLP as confidence, adjust as needed
                            description=pulse.get("name"),
                        )
                        db.add(ti)
                db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error fetching from OTX: {e}")

    async def _update_abusech(self):
        """Fetch indicators from Abuse.ch feeds."""
        # Abuse.ch has multiple feeds: SSLBlacklist, URLHaus, FeodoTracker, etc.
        # We'll implement a few as examples.
        feeds = [
            ("SSLBlacklist", "https://sslbl.abuse.ch/export/sslbl.csv"),
            ("URLHaus", "https://urlhaus.abuse.ch/downloads/csv/"),
            # Add more feeds as needed
        ]
        for feed_name, url in feeds:
            try:
                logger.info(f"Fetching Abuse.ch feed: {feed_name}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                # Parse CSV (skip header lines that start with #)
                lines = response.text.splitlines()
                db = SessionLocal()
                for line in lines:
                    if line.startswith("#") or not line.strip():
                        continue
                    # Parse CSV line (simple split by comma, but note that URLs may contain commas)
                    # For simplicity, we assume the first column is the indicator and adjust per feed.
                    # In a real implementation, use a proper CSV parser.
                    parts = line.split(",")
                    if feed_name == "SSLBlacklist":
                        # Format: # first_seen_utc,ssl_md5,ssl_sha1,ssl_sha256,subject,serial_number,threat,score,confidence,urlhaus_url,threat_type,malware,urlhaus_reference
                        # We'll use the SSL hashes as indicators
                        if len(parts) >= 4:
                            for hash_val in parts[1:4]:  # md5, sha1, sha256
                                if hash_val and len(hash_val) in [32, 40, 64]:  # basic length check
                                    existing = db.query(ThreatIntelligence).filter(
                                        ThreatIntelligence.indicator == hash_val,
                                        ThreatIntelligence.indicator_type == "hash",
                                        ThreatIntelligence.source == "Abuse.ch"
                                    ).first()
                                    if not existing:
                                        ti = ThreatIntelligence(
                                            indicator=hash_val,
                                            indicator_type="hash",
                                            source="Abuse.ch",
                                            confidence=int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else None,
                                            description=f"SSLBlacklist feed: {parts[4]}" if len(parts) > 4 else "SSLBlacklist",
                                        )
                                        db.add(ti)
                    elif feed_name == "URLHaus":
                        # Format: # id,dateadded,url,url_status,threat,tags,urlhaus_link,reporter
                        # We'll use the URL as indicator
                        if len(parts) >= 3:
                            url_val = parts[2]
                            if url_val.startswith("http"):
                                existing = db.query(ThreatIntelligence).filter(
                                    ThreatIntelligence.indicator == url_val,
                                    ThreatIntelligence.indicator_type == "url",
                                    ThreatIntelligence.source == "Abuse.ch"
                                ).first()
                                if not existing:
                                    ti = ThreatIntelligence(
                                        indicator=url_val,
                                        indicator_type="url",
                                        source="Abuse.ch",
                                        description=f"URLHaus feed: {parts[4]}" if len(parts) > 4 else "URLHaus",
                                    )
                                    db.add(ti)
                db.commit()
                db.close()
                logger.info(f"Finished processing Abuse.ch feed: {feed_name}")
            except Exception as e:
                logger.error(f"Error fetching Abuse.ch feed {feed_name}: {e}")

# Global updater instance
updater = ThreatIntelUpdater()