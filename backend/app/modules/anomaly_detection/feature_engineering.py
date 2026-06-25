"""
Feature Engineering for Network Flow Analysis
Extracts features for botnet detection from network flows
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import deque
import time


@dataclass
class NetworkFlowFeatures:
    """Represents extracted features from a network flow"""
    # Connection periodicity (beaconing detection)
    connection_interval_std: float = 0.0
    connection_interval_mean: float = 0.0
    beaconing_score: float = 0.0
    
    # Packet size distribution
    packet_size_mean: float = 0.0
    packet_size_std: float = 0.0
    packet_size_min: float = 0.0
    packet_size_max: float = 0.0
    packet_size_entropy: float = 0.0
    
    # Connection duration patterns
    connection_duration: float = 0.0
    duration_category: int = 0  # 0: short, 1: medium, 2: long
    
    # Port usage anomalies
    dst_port: int = 0
    src_port: int = 0
    port_entropy: float = 0.0
    is_common_port: bool = True
    port_frequency_score: float = 0.0
    
    # Additional network features
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    protocol: int = 0  # TCP=6, UDP=17, etc.
    flags_count: int = 0
    
    # TLS/JA3 features
    ja3_hash: str = ""
    ja4_hash: str = ""
    tls_version: int = 0
    cipher_suite: int = 0
    
    # Temporal features
    timestamp: float = field(default_factory=time.time)
    hour_of_day: int = 0
    day_of_week: int = 0


class FeatureExtractor:
    """
    Extracts features from raw network flow data
    Optimized for low-latency inference on edge devices
    """
    
    # Common ports that are typically legitimate
    COMMON_PORTS = {
        20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 143, 161, 194,
        443, 465, 514, 587, 993, 995, 1433, 1521, 3306, 3389,
        5432, 5900, 6379, 8080, 8443, 8888, 27017
    }
    
    # Port frequency distribution (normalized)
    PORT_FREQUENCY = {
        80: 0.15, 443: 0.25, 22: 0.05, 53: 0.08, 25: 0.03,
        110: 0.02, 143: 0.02, 21: 0.02, 23: 0.01, 3389: 0.03,
        8080: 0.04, 8443: 0.03, 'default': 0.001
    }
    
    def __init__(self, window_size: int = 100):
        """
        Initialize feature extractor
        
        Args:
            window_size: Number of flows to keep in rolling window for statistics
        """
        self.window_size = window_size
        self.flow_history: deque = deque(maxlen=window_size)
        self.connection_times: Dict[str, deque] = {}  # per device
        self.port_history: deque = deque(maxlen=window_size)
        
    def extract_features(self, flow: Dict) -> NetworkFlowFeatures:
        """
        Extract all features from a single network flow
        
        Args:
            flow: Dictionary containing raw flow data
            
        Returns:
            NetworkFlowFeatures object with extracted features
        """
        features = NetworkFlowFeatures()
        
        # Basic flow information
        features.bytes_sent = flow.get('bytes_sent', 0)
        features.bytes_received = flow.get('bytes_received', 0)
        features.packets_sent = flow.get('packets_sent', 0)
        features.packets_received = flow.get('packets_received', 0)
        features.protocol = flow.get('protocol', 6)
        features.flags_count = flow.get('flags_count', 0)
        
        # Port features
        features.dst_port = flow.get('dst_port', 0)
        features.src_port = flow.get('src_port', 0)
        features.is_common_port = features.dst_port in self.COMMON_PORTS
        features.port_frequency_score = self._calculate_port_frequency(features.dst_port)
        
        # Packet size analysis
        packet_sizes = flow.get('packet_sizes', [])
        if packet_sizes:
            features.packet_size_mean = np.mean(packet_sizes)
            features.packet_size_std = np.std(packet_sizes)
            features.packet_size_min = min(packet_sizes)
            features.packet_size_max = max(packet_sizes)
            features.packet_size_entropy = self._calculate_entropy(packet_sizes)
        
        # Connection duration
        features.connection_duration = flow.get('duration', 0.0)
        if features.connection_duration < 1.0:
            features.duration_category = 0
        elif features.connection_duration < 60.0:
            features.duration_category = 1
        else:
            features.duration_category = 2
        
        # TLS features
        features.ja3_hash = flow.get('ja3_hash', '')
        features.ja4_hash = flow.get('ja4_hash', '')
        features.tls_version = flow.get('tls_version', 0)
        features.cipher_suite = flow.get('cipher_suite', 0)
        
        # Temporal features
        features.timestamp = flow.get('timestamp', time.time())
        features.hour_of_day = int(time.localtime(features.timestamp).tm_hour)
        features.day_of_week = int(time.localtime(features.timestamp).tm_wday)
        
        # Connection periodicity (requires historical data)
        device_id = flow.get('device_id', 'unknown')
        self._update_connection_history(device_id, features.timestamp)
        periodicity_features = self._calculate_periodicity(device_id)
        features.connection_interval_mean = periodicity_features[0]
        features.connection_interval_std = periodicity_features[1]
        features.beaconing_score = periodicity_features[2]
        
        # Update rolling history
        self.flow_history.append(features)
        self.port_history.append(features.dst_port)
        
        # Calculate port entropy across recent flows
        if len(self.port_history) > 10:
            features.port_entropy = self._calculate_entropy(list(self.port_history))
        
        return features
    
    def _calculate_entropy(self, values: List) -> float:
        """Calculate Shannon entropy of a distribution"""
        if not values:
            return 0.0
        
        unique, counts = np.unique(values, return_counts=True)
        probabilities = counts / len(values)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return float(entropy)
    
    def _calculate_port_frequency(self, port: int) -> float:
        """Calculate how common/uncommon a port is"""
        return self.PORT_FREQUENCY.get(port, self.PORT_FREQUENCY['default'])
    
    def _update_connection_history(self, device_id: str, timestamp: float):
        """Update connection history for a device"""
        if device_id not in self.connection_times:
            self.connection_times[device_id] = deque(maxlen=50)
        self.connection_times[device_id].append(timestamp)
    
    def _calculate_periodicity(self, device_id: str) -> Tuple[float, float, float]:
        """
        Calculate connection periodicity metrics
        
        Returns:
            Tuple of (mean_interval, std_interval, beaconing_score)
        """
        if device_id not in self.connection_times or len(self.connection_times[device_id]) < 3:
            return (0.0, 0.0, 0.0)
        
        times = list(self.connection_times[device_id])
        intervals = np.diff(times)
        
        if len(intervals) < 2:
            return (float(np.mean(intervals)), 0.0, 0.0)
        
        mean_interval = float(np.mean(intervals))
        std_interval = float(np.std(intervals))
        
        # Beaconing score: low std relative to mean indicates periodic behavior
        # Botnets often have very regular beaconing intervals
        if mean_interval > 0:
            cv = std_interval / mean_interval  # Coefficient of variation
            # Lower CV = more periodic = higher beaconing score
            beaconing_score = max(0.0, 1.0 - cv)
        else:
            beaconing_score = 0.0
        
        return (mean_interval, std_interval, beaconing_score)
    
    def get_feature_vector(self, features: NetworkFlowFeatures) -> np.ndarray:
        """
        Convert features to numpy array for model input
        
        Returns normalized feature vector
        """
        vector = np.array([
            features.connection_interval_std,
            features.connection_interval_mean,
            features.beaconing_score,
            features.packet_size_mean / 1500.0,  # Normalize by typical MTU
            features.packet_size_std / 1500.0,
            features.packet_size_min / 1500.0,
            features.packet_size_max / 1500.0,
            features.packet_size_entropy / 8.0,  # Normalize by max entropy
            features.connection_duration / 300.0,  # Normalize by 5 min
            features.duration_category / 2.0,
            features.dst_port / 65535.0,
            features.src_port / 65535.0,
            features.port_entropy / 16.0,
            0.0 if features.is_common_port else 1.0,
            features.port_frequency_score,
            np.log1p(features.bytes_sent) / 20.0,
            np.log1p(features.bytes_received) / 20.0,
            features.packets_sent / 1000.0,
            features.packets_received / 1000.0,
            features.protocol / 255.0,
            features.flags_count / 10.0,
            features.tls_version / 10.0,
            features.hour_of_day / 23.0,
            features.day_of_week / 6.0
        ], dtype=np.float32)
        
        return vector
    
    def batch_extract(self, flows: List[Dict]) -> np.ndarray:
        """
        Extract features from multiple flows efficiently
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            2D numpy array of shape (n_flows, n_features)
        """
        vectors = []
        for flow in flows:
            features = self.extract_features(flow)
            vector = self.get_feature_vector(features)
            vectors.append(vector)
        
        return np.vstack(vectors)