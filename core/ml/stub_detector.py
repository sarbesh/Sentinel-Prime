#!/usr/bin/env python3
"""
Sentinel Prime Stub Anomaly Detector
Functional stub for testing until pre-trained model is integrated.
Returns realistic anomaly scores based on simple heuristics.
"""

import numpy as np
from typing import Dict, List

class StubAnomalyDetector:
    """
    Stub detector using heuristic rules.
    Replace with real ONNX model when available.
    """
    
    def __init__(self):
        self.threshold = 0.6
        self.rules = [
            {'feature': 'packets_per_second', 'threshold': 100, 'weight': 0.3},
            {'feature': 'bytes_per_second', 'threshold': 50000, 'weight': 0.2},
            {'feature': 'periodicity_score', 'threshold': 0.7, 'weight': 0.3},
            {'feature': 'port_entropy', 'threshold': 0.8, 'weight': 0.2}
        ]
    
    def predict(self, features: np.ndarray) -> float:
        """
        Predict anomaly score using simple heuristics.
        
        Args:
            features: Normalized feature vector from feature_extractor
            
        Returns:
            Anomaly score (0.0 - 1.0)
        """
        score = 0.0
        
        # Apply heuristic rules
        for rule in self.rules:
            feature_idx = [
                'packet_count', 'byte_count', 'duration',
                'packets_per_second', 'bytes_per_second',
                'avg_packet_size', 'direction', 'port_entropy',
                'periodicity_score'
            ].index(rule['feature'])
            
            if features[feature_idx] > rule['threshold']:
                score += rule['weight']
        
        return min(score, 1.0)
    
    def is_anomaly(self, score: float) -> bool:
        """Determine if score indicates anomaly."""
        return score > self.threshold

# Test
if __name__ == '__main__':
    detector = StubAnomalyDetector()
    
    # Normal traffic
    normal = np.array([0.1, 0.1, 0.1, 0.05, 0.05, 0.1, 0, 0.2, 0.1])
    print(f"Normal traffic score: {detector.predict(normal):.3f}")
    
    # Suspicious traffic (high periodicity, high rate)
    suspicious = np.array([0.8, 0.7, 0.3, 0.9, 0.8, 0.5, 0, 0.3, 0.9])
    print(f"Suspicious traffic score: {detector.predict(suspicious):.3f}")
