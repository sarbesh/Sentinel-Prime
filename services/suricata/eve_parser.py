#!/usr/bin/env python3
"""
Sentinel Prime Suricata EVE-JSON Log Parser
Real-time alert forwarding and threat correlation.

Created by: Elena Volkov (Security Engineer)
Ticket: TICKET-0001
"""

import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sentinel-eve-parser')

class SuricataEVEParser:
    """Parse and process Suricata EVE-JSON logs in real-time."""
    
    def __init__(self, eve_log_path: str = '/var/log/suricata/eve.json'):
        self.eve_log_path = Path(eve_log_path)
        self.alert_counts = defaultdict(int)
        self.threat_actors = defaultdict(list)
        self.last_position = 0
        
    def parse_alert(self, event: Dict) -> Optional[Dict]:
        """Parse Suricata alert event."""
        if event.get('event_type') != 'alert':
            return None
        
        alert = event.get('alert', {})
        
        parsed_alert = {
            'timestamp': event.get('timestamp'),
            'signature_id': alert.get('signature_id'),
            'signature': alert.get('signature'),
            'severity': alert.get('severity'),
            'category': alert.get('category'),
            'src_ip': event.get('src_ip'),
            'dest_ip': event.get('dest_ip'),
            'src_port': event.get('src_port'),
            'dest_port': event.get('dest_port'),
            'proto': event.get('proto'),
            'direction': 'inbound' if event.get('flow_id', 0) % 2 == 0 else 'outbound'
        }
        
        return parsed_alert
    
    def correlate_threats(self, alert: Dict) -> Dict:
        """Correlate alerts to identify threat patterns."""
        src_ip = alert['src_ip']
        signature = alert['signature']
        
        # Track threat actors
        self.threat_actors[src_ip].append({
            'timestamp': alert['timestamp'],
            'signature': signature
        })
        
        # Count alert types
        self.alert_counts[signature] += 1
        
        # Check for pattern
        threat_level = 'low'
        if len(self.threat_actors[src_ip]) > 5:
            threat_level = 'medium'
        if len(self.threat_actors[src_ip]) > 10:
            threat_level = 'high'
        if self.alert_counts[signature] > 20:
            threat_level = 'critical'
        
        return {
            'alert': alert,
            'threat_level': threat_level,
            'occurrence_count': len(self.threat_actors[src_ip])
        }
    
    def forward_alert(self, enriched_alert: Dict):
        """Forward alert to Sentinel Prime backend."""
        # In production, this would send to backend API
        # For now, log critical alerts
        if enriched_alert['threat_level'] in ['high', 'critical']:
            logger.warning(
                f"🚨 THREAT DETECTED: {enriched_alert['alert']['signature']} "
                f"from {enriched_alert['alert']['src_ip']} "
                f"(Level: {enriched_alert['threat_level']})"
            )
    
    def process_eve_log(self):
        """Process EVE-JSON log file."""
        if not self.eve_log_path.exists():
            logger.warning(f"EVE log not found: {self.eve_log_path}")
            return
        
        logger.info(f"Processing EVE log: {self.eve_log_path}")
        
        with open(self.eve_log_path, 'r') as f:
            f.seek(self.last_position)
            
            while True:
                line = f.readline()
                if not line:
                    # Wait for new logs
                    time.sleep(1)
                    self.last_position = f.tell()
                    continue
                
                try:
                    event = json.loads(line)
                    alert = self.parse_alert(event)
                    
                    if alert:
                        logger.info(
                            f"Alert: {alert['signature']} | "
                            f"{alert['src_ip']}:{alert['src_port']} -> "
                            f"{alert['dest_ip']}:{alert['dest_port']} | "
                            f"Severity: {alert['severity']}"
                        )
                        
                        # Correlate and forward
                        enriched = self.correlate_threats(alert)
                        self.forward_alert(enriched)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                except Exception as e:
                    logger.error(f"Processing error: {e}")
    
    def generate_summary(self) -> Dict:
        """Generate threat summary report."""
        return {
            'total_alerts': sum(self.alert_counts.values()),
            'unique_signatures': len(self.alert_counts),
            'threat_actors': len(self.threat_actors),
            'top_alerts': dict(sorted(
                self.alert_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            'active_threats': [
                {
                    'ip': ip,
                    'alert_count': len(alerts),
                    'latest': alerts[-1] if alerts else None
                }
                for ip, alerts in self.threat_actors.items()
                if len(alerts) > 3
            ]
        }

def main():
    """Main entry point."""
    logger.info("🛡️  Starting Sentinel Prime EVE Parser...")
    
    parser = SuricataEVEParser()
    
    try:
        summary = parser.generate_summary()
        logger.info(f"Summary: {summary['total_alerts']} alerts, "
                   f"{summary['unique_signatures']} signatures, "
                   f"{summary['threat_actors']} threat actors")
        
        logger.info("Parser ready for real-time monitoring")
        parser.process_eve_log()
        
    except KeyboardInterrupt:
        logger.info("Parser stopped by user")
    except Exception as e:
        logger.error(f"Parser error: {e}")
        raise

if __name__ == '__main__':
    main()