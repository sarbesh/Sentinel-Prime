"""
Adaptive Baselining System
Learns normal behavior per device type
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import time
import json
from pathlib import Path


@dataclass
class DeviceProfile:
    """Represents learned normal behavior for a device"""
    device_id: str
    device_type: str = "unknown"
    
    # Feature statistics
    feature_means: np.ndarray = field(default_factory=lambda: np.array([]))
    feature_stds: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Behavioral patterns
    typical_ports: set = field(default_factory=set)
    typical_protocols: set = field(default_factory=set)
    typical_connection_intervals: Tuple[float, float] = (0.0, 0.0)  # (mean, std)
    typical_bytes_sent: Tuple[float, float] = (0.0, 0.0)
    typical_bytes_received: Tuple[float, float] = (0.0, 0.0)
    
    # Activity patterns
    active_hours: set = field(default_factory=lambda: set(range(8, 22)))
    activity_level: float = 0.0  # Average connections per hour
    
    # Learning state
    n_samples: int = 0
    last_updated: float = field(default_factory=time.time)
    is_confident: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'feature_means': self.feature_means.tolist() if len(self.feature_means) > 0 else [],
            'feature_stds': self.feature_stds.tolist() if len(self.feature_stds) > 0 else [],
            'typical_ports': list(self.typical_ports),
            'typical_protocols': list(self.typical_protocols),
            'typical_connection_intervals': list(self.typical_connection_intervals),
            'typical_bytes_sent': list(self.typical_bytes_sent),
            'typical_bytes_received': list(self.typical_bytes_received),
            'active_hours': list(self.active_hours),
            'activity_level': self.activity_level,
            'n_samples': self.n_samples,
            'last_updated': self.last_updated,
            'is_confident': self.is_confident
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DeviceProfile':
        """Create from dictionary"""
        profile = cls(
            device_id=data['device_id'],
            device_type=data.get('device_type', 'unknown')
        )
        profile.feature_means = np.array(data.get('feature_means', []))
        profile.feature_stds = np.array(data.get('feature_stds', []))
        profile.typical_ports = set(data.get('typical_ports', []))
        profile.typical_protocols = set(data.get('typical_protocols', []))
        profile.typical_connection_intervals = tuple(data.get('typical_connection_intervals', (0.0, 0.0)))
        profile.typical_bytes_sent = tuple(data.get('typical_bytes_sent', (0.0, 0.0)))
        profile.typical_bytes_received = tuple(data.get('typical_bytes_received', (0.0, 0.0)))
        profile.active_hours = set(data.get('active_hours', range(8, 22)))
        profile.activity_level = data.get('activity_level', 0.0)
        profile.n_samples = data.get('n_samples', 0)
        profile.last_updated = data.get('last_updated', time.time())
        profile.is_confident = data.get('is_confident', False)
        
        return profile


class DeviceBaseliner:
    """
    Learns and maintains baselines for different device types
    Supports adaptive learning with forgetting factor
    """
    
    # Common device types and their typical behaviors
    DEVICE_TYPE_SIGNATURES = {
        'iot_camera': {
            'typical_ports': {80, 443, 554, 8080},  # HTTP, RTSP
            'high_upload': True,
            'periodic': True
        },
        'smart_speaker': {
            'typical_ports': {443, 8443},
            'high_download': True,
            'periodic': False
        },
        'smart_plug': {
            'typical_ports': {443, 8883},  # HTTPS, MQTT
            'low_bandwidth': True,
            'periodic': True
        },
        'router': {
            'typical_ports': {53, 80, 443, 1900},
            'high_connections': True,
            'periodic': False
        },
        'computer': {
            'typical_ports': set(range(1024, 65535)),
            'variable': True,
            'periodic': False
        }
    }
    
    def __init__(
        self,
        min_samples: int = 100,
        learning_rate: float = 0.1,
        confidence_threshold: float = 0.8,
        persistence_path: Optional[str] = None
    ):
        """
        Initialize device baseliner
        
        Args:
            min_samples: Minimum samples needed for confident baseline
            learning_rate: Rate of adaptive learning (0-1)
            confidence_threshold: Threshold for considering baseline reliable
            persistence_path: Path to save/load baselines
        """
        self.min_samples = min_samples
        self.learning_rate = learning_rate
        self.confidence_threshold = confidence_threshold
        self.persistence_path = Path(persistence_path) if persistence_path else None
        
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.type_profiles: Dict[str, Dict[str, np.ndarray]] = defaultdict(lambda: defaultdict(list))
        self.feature_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Load existing baselines
        if self.persistence_path and self.persistence_path.exists():
            self.load_baselines()
    
    def classify_device_type(self, device_id: str, features: np.ndarray) -> str:
        """
        Classify device type based on observed behavior
        
        Args:
            device_id: Device identifier
            features: Feature vector
            
        Returns:
            Device type string
        """
        # Simple heuristic classification
        # In practice, could use a separate classifier
        
        # Check port usage patterns
        if len(self.device_profiles) > 0 and device_id in self.device_profiles:
            profile = self.device_profiles[device_id]
            
            if profile.typical_ports & {554, 8554}:  # RTSP
                return 'iot_camera'
            elif profile.typical_ports & {8883}:  # MQTT
                return 'smart_plug'
            elif len(profile.typical_ports) > 100:  # Many ports
                return 'computer'
            elif profile.feature_means.size > 15 and profile.feature_means[15] > profile.feature_means[16]:
                # High upload vs download
                return 'iot_camera'
        
        # Default classification
        return 'unknown'
    
    def update_baseline(
        self,
        device_id: str,
        feature_vector: np.ndarray,
        device_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Update baseline for a device with new observation
        
        Args:
            device_id: Device identifier
            feature_vector: New feature observation
            device_type: Optional device type
            metadata: Optional metadata (ports, protocols, etc.)
        """
        # Initialize profile if new device
        if device_id not in self.device_profiles:
            self.device_profiles[device_id] = DeviceProfile(device_id=device_id)
        
        profile = self.device_profiles[device_id]
        
        # Update device type
        if device_type:
            profile.device_type = device_type
        else:
            profile.device_type = self.classify_device_type(device_id, feature_vector)
        
        # Update feature statistics with exponential moving average
        if profile.n_samples == 0:
            profile.feature_means = feature_vector.copy()
            profile.feature_stds = np.zeros_like(feature_vector)
        else:
            # EMA update
            alpha = self.learning_rate
            old_mean = profile.feature_means
            profile.feature_means = (1 - alpha) * old_mean + alpha * feature_vector
            
            # Update variance estimate
            diff = feature_vector - old_mean
            profile.feature_stds = np.sqrt(
                (1 - alpha) * (profile.feature_stds ** 2) + alpha * (diff ** 2)
            )
        
        profile.n_samples += 1
        profile.last_updated = time.time()
        profile.is_confident = profile.n_samples >= self.min_samples
        
        # Update metadata
        if metadata:
            if 'dst_port' in metadata:
                profile.typical_ports.add(metadata['dst_port'])
            if 'protocol' in metadata:
                profile.typical_protocols.add(metadata['protocol'])
        
        # Buffer for batch statistics
        self.feature_buffers[device_id].append(feature_vector)
        
        # Update type-level statistics
        type_key = profile.device_type
        self.type_profiles[type_key]['features'].append(feature_vector)
    
    def get_deviation_score(
        self,
        device_id: str,
        feature_vector: np.ndarray
    ) -> Tuple[float, bool]:
        """
        Calculate how much a feature vector deviates from baseline
        
        Args:
            device_id: Device identifier
            feature_vector: Feature observation
            
        Returns:
            Tuple of (deviation_score, is_anomalous)
        """
        if device_id not in self.device_profiles:
            return (0.0, False)
        
        profile = self.device_profiles[device_id]
        
        if profile.n_samples < 10:
            return (0.0, False)
        
        # Calculate Mahalanobis-like distance (simplified)
        diff = feature_vector - profile.feature_means
        
        # Avoid division by zero
        safe_stds = np.where(profile.feature_stds > 1e-10, profile.feature_stds, 1.0)
        z_scores = np.abs(diff / safe_stds)
        
        # Overall deviation score (mean z-score across features)
        deviation = float(np.mean(z_scores))
        
        # Check if anomalous
        is_anomalous = deviation > 3.0  # 3 sigma rule
        
        return (deviation, is_anomalous)
    
    def check_behavioral_anomalies(
        self,
        device_id: str,
        metadata: Dict
    ) -> List[str]:
        """
        Check for behavioral anomalies not captured by features
        
        Args:
            device_id: Device identifier
            metadata: Flow metadata (ports, time, etc.)
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        if device_id not in self.device_profiles:
            return anomalies
        
        profile = self.device_profiles[device_id]
        
        # Check for unusual ports
        if 'dst_port' in metadata:
            port = metadata['dst_port']
            if profile.is_confident and port not in profile.typical_ports:
                # Check if it's a truly unusual port
                if port not in {80, 443, 22, 53}:  # Very common ports
                    anomalies.append(f"Unusual port: {port}")
        
        # Check for unusual activity time
        if 'hour' in metadata:
            hour = metadata['hour']
            if profile.is_confident and hour not in profile.active_hours:
                anomalies.append(f"Unusual activity hour: {hour}")
        
        # Check for connection rate anomalies
        if 'connections_per_minute' in metadata:
            rate = metadata['connections_per_minute']
            expected_rate = profile.activity_level
            if expected_rate > 0 and rate > expected_rate * 5:
                anomalies.append(f"High connection rate: {rate}/min vs expected {expected_rate}/min")
        
        return anomalies
    
    def get_baseline_stats(self, device_id: str) -> Optional[Dict]:
        """Get baseline statistics for a device"""
        if device_id not in self.device_profiles:
            return None
        
        profile = self.device_profiles[device_id]
        return profile.to_dict()
    
    def save_baselines(self, path: Optional[str] = None):
        """Save baselines to disk"""
        save_path = Path(path) if path else self.persistence_path
        if not save_path:
            raise ValueError("No persistence path configured")
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            device_id: profile.to_dict()
            for device_id, profile in self.device_profiles.items()
        }
        
        # Aggregate type profiles
        type_data = {}
        for device_type, stats in self.type_profiles.items():
            if 'features' in stats and len(stats['features']) > 0:
                type_data[device_type] = {
                    'mean': np.mean(stats['features'], axis=0).tolist(),
                    'std': np.std(stats['features'], axis=0).tolist(),
                    'count': len(stats['features'])
                }
        
        data['type_profiles'] = type_data
        
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved baselines for {len(self.device_profiles)} devices to {save_path}")
    
    def load_baselines(self, path: Optional[str] = None):
        """Load baselines from disk"""
        load_path = Path(path) if path else self.persistence_path
        if not load_path or not load_path.exists():
            return
        
        with open(load_path, 'r') as f:
            data = json.load(f)
        
        # Remove type_profiles from device data
        type_profiles_data = data.pop('type_profiles', {})
        
        self.device_profiles = {}
        for device_id, profile_data in data.items():
            self.device_profiles[device_id] = DeviceProfile.from_dict(profile_data)
        
        # Restore type profiles
        for device_type, stats in type_profiles_data.items():
            self.type_profiles[device_type]['mean'] = np.array(stats.get('mean', []))
            self.type_profiles[device_type]['std'] = np.array(stats.get('std', []))
        
        print(f"Loaded baselines for {len(self.device_profiles)} devices from {load_path}")


@dataclass
class AdaptiveBaseline:
    """
    Wrapper for adaptive baseline with online learning
    """
    baseliner: DeviceBaseliner
    device_id: str
    window_size: int = 100
    
    def update(self, features: np.ndarray, metadata: Optional[Dict] = None):
        """Update baseline with new observation"""
        self.baseliner.update_baseline(self.device_id, features, metadata=metadata)
    
    def is_anomalous(self, features: np.ndarray) -> Tuple[float, bool, List[str]]:
        """
        Check if observation is anomalous
        
        Returns:
            Tuple of (deviation_score, is_anomalous, anomaly_details)
        """
        deviation, is_stat_anomaly = self.baseliner.get_deviation_score(self.device_id, features)
        
        behavioral_anomalies = []
        if metadata := getattr(self, '_last_metadata', None):
            behavioral_anomalies = self.baseliner.check_behavioral_anomalies(
                self.device_id, metadata
            )
        
        is_anomalous = is_stat_anomaly or len(behavioral_anomalies) > 0
        
        return (deviation, is_anomalous, behavioral_anomalies)