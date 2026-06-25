#!/usr/bin/env python3
"""
Sentinel Prime ML Feature Extractor
Extract features from network flows for anomaly detection.

Created by: David Park (ML Engineer)  
Ticket: TICKET-0002
"""

import numpy as np
from typing import Dict, List, Optional
from collections import defaultdict

class FlowFeatureExtractor:
    """Extract features from network flows for ML anomaly detection."""
    
    def __init__(self):
        self.feature_names = [
            'packet_count',
            'byte_count',
            'duration_seconds',
            'packets_per_second',
            'bytes_per_second',
            'avg_packet_size',
            'is_inbound',
            'port_entropy',
            'periodicity_score'
        ]
        self.num_features = len(self.feature_names)
    
    def extract_features(self, flow_stats: Dict) -> np.ndarray:
        """
        Extract feature vector from flow statistics.
        
        Args:
            flow_stats: Dictionary with flow statistics
            
        Returns:
            numpy array of features (normalized)
        """
        features = []
        
        # Basic statistics
        packet_count = flow_stats.get('packet_count', 0)
        byte_count = flow_stats.get('byte_count', 0)
        duration = flow_stats.get('duration', 1.0)
        
        features.append(packet_count)
        features.append(byte_count)
        features.append(duration)
        
        # Rate-based features
        features.append(packet_count / max(duration, 0.1))  # packets/sec
        features.append(byte_count / max(duration, 0.1))    # bytes/sec
        
        # Size features
        features.append(byte_count / max(packet_count, 1))  # avg packet size
        
        # Direction flag
        features.append(1 if flow_stats.get('is_inbound', False) else 0)
        
        # Entropy features (simplified)
        features.append(self._calculate_port_entropy(flow_stats))
        
        # Periodicity (simplified - would use FFT in production)
        features.append(self._calculate_periodicity(flow_stats))
        
        # Normalize features
        features_array = np.array(features, dtype=np.float32)
        return self.normalize(features_array)
    
    def _calculate_port_entropy(self, flow_stats: Dict) -> float:
        """Calculate port entropy (measure of randomness)."""
        # Simplified implementation
        return 0.5
    
    def _calculate_periodicity(self, flow_stats: Dict) -> float:
        """Calculate periodicity score (beaconing detection)."""
        # Simplified - would use inter-arrival time variance in production
        return 0.3
    
    def normalize(self, features: np.ndarray) -> np.ndarray:
        """Normalize feature vector."""
        # Simple min-max normalization
        max_vals = np.array([
            1000,     # packet_count
            1000000,  # byte_count
            3600,     # duration
            1000,     # packets/sec
            100000,   # bytes/sec
            1500,     # avg packet size
            1,        # direction
            8,        # entropy
            1         # periodicity
        ])
        
        return features / max_vals
    
    def batch_extract(self, flows: List[Dict]) -> np.ndarray:
        """Extract features from multiple flows."""
        feature_vectors = []
        
        for flow_stats in flows:
            features = self.extract_features(flow_stats)
            feature_vectors.append(features)
        
        return np.array(feature_vectors)
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names

# Test the extractor
if __name__ == '__main__':
    extractor = FlowFeatureExtractor()
    
    test_flow = {
        'packet_count': 150,
        'byte_count': 125000,
        'duration': 10.5,
        'is_inbound': True
    }
    
    features = extractor.extract_features(test_flow)
    print(f"Feature vector shape: {features.shape}")
    print(f"Feature names: {extractor.get_feature_names()}")
    print(f"Extracted features: {features}")