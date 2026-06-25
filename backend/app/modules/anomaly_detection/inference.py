"""
Real-time Inference Pipeline
Processes flows from eBPF module with low latency
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Callable
from collections import deque
from dataclasses import dataclass
import threading
from queue import Queue, Empty
import json

from .isolation_forest import IsolationForestModel, AnomalyDetector
from .baselining import DeviceBaseliner
from .feature_engineering import FeatureExtractor, NetworkFlowFeatures


@dataclass
class InferenceResult:
    """Result from anomaly detection inference"""
    flow_id: str
    device_id: str
    timestamp: float
    
    # Anomaly detection results
    is_anomaly: bool
    anomaly_score: float
    prediction: int  # -1 or 1
    
    # Additional context
    feature_vector: Optional[np.ndarray] = None
    anomaly_details: Optional[List[str]] = None
    device_baseline_deviation: Optional[float] = None
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'flow_id': self.flow_id,
            'device_id': self.device_id,
            'timestamp': self.timestamp,
            'is_anomaly': self.is_anomaly,
            'anomaly_score': float(self.anomaly_score),
            'prediction': int(self.prediction),
            'anomaly_details': self.anomaly_details or [],
            'device_baseline_deviation': self.device_baseline_deviation,
            'processing_time_ms': self.processing_time_ms
        }


class RealTimeInference:
    """
    Low-latency inference engine optimized for edge devices
    Target: <10ms per flow batch
    """
    
    def __init__(
        self,
        model: IsolationForestModel,
        feature_extractor: FeatureExtractor,
        baseliner: DeviceBaseliner,
        batch_size: int = 32,
        max_latency_ms: float = 10.0
    ):
        """
        Initialize real-time inference engine
        
        Args:
            model: Trained Isolation Forest model
            feature_extractor: Feature extraction module
            baseliner: Device baselining system
            batch_size: Batch size for inference
            max_latency_ms: Target maximum latency in milliseconds
        """
        self.model = model
        self.feature_extractor = feature_extractor
        self.baseliner = baseliner
        self.batch_size = batch_size
        self.max_latency_ms = max_latency_ms
        
        self.detector = AnomalyDetector(model)
        
        # Flow buffer for batching
        self.flow_buffer: deque = deque(maxlen=batch_size * 2)
        self.pending_results: Queue = Queue()
        
        # Statistics
        self.inference_count = 0
        self.total_latency_ms = 0.0
        self.latency_history: deque = deque(maxlen=1000)
        
        # Threading for async processing
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
    
    def process_flow(self, flow: Dict) -> InferenceResult:
        """
        Process a single network flow
        
        Args:
            flow: Raw flow data from eBPF module
            
        Returns:
            InferenceResult with anomaly detection results
        """
        start_time = time.perf_counter()
        
        # Extract features
        features = self.feature_extractor.extract_features(flow)
        feature_vector = self.feature_extractor.get_feature_vector(features)
        
        # Get device ID
        device_id = flow.get('device_id', flow.get('src_ip', 'unknown'))
        
        # Anomaly detection
        X = feature_vector.reshape(1, -1)
        prediction, scores = self.detector.detect(X)
        
        anomaly_score = float(scores[0])
        is_anomaly = prediction[0] == -1
        
        # Baselining check
        baseline_deviation = None
        anomaly_details = []
        
        if device_id in self.baseliner.device_profiles:
            deviation, is_baseline_anomaly = self.baseliner.get_deviation_score(
                device_id, feature_vector
            )
            baseline_deviation = deviation
            
            if is_baseline_anomaly:
                anomaly_details.append(f"Baseline deviation: {deviation:.2f} sigma")
            
            # Check behavioral anomalies
            metadata = {
                'dst_port': flow.get('dst_port'),
                'protocol': flow.get('protocol'),
                'hour': features.hour_of_day
            }
            behavioral_anomalies = self.baseliner.check_behavioral_anomalies(
                device_id, metadata
            )
            anomaly_details.extend(behavioral_anomalies)
        
        # Update baseline (online learning)
        self.baseliner.update_baseline(
            device_id,
            feature_vector,
            metadata={
                'dst_port': flow.get('dst_port'),
                'protocol': flow.get('protocol')
            }
        )
        
        # Calculate latency
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        self.inference_count += 1
        self.total_latency_ms += latency_ms
        self.latency_history.append(latency_ms)
        
        # Create result
        result = InferenceResult(
            flow_id=flow.get('flow_id', f"flow_{self.inference_count}"),
            device_id=device_id,
            timestamp=time.time(),
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            prediction=int(prediction[0]),
            feature_vector=feature_vector,
            anomaly_details=anomaly_details if anomaly_details else None,
            device_baseline_deviation=baseline_deviation,
            processing_time_ms=latency_ms
        )
        
        return result
    
    def process_batch(self, flows: List[Dict]) -> List[InferenceResult]:
        """
        Process a batch of flows efficiently
        
        Args:
            flows: List of raw flow dictionaries
            
        Returns:
            List of InferenceResults
        """
        start_time = time.perf_counter()
        
        if not flows:
            return []
        
        # Extract features for all flows
        feature_vectors = []
        flow_data = []
        
        for flow in flows:
            features = self.feature_extractor.extract_features(flow)
            vector = self.feature_extractor.get_feature_vector(features)
            feature_vectors.append(vector)
            flow_data.append(flow)
        
        X = np.vstack(feature_vectors)
        
        # Batch inference
        predictions, scores = self.detector.detect(X)
        
        # Process results
        results = []
        for i, (flow, pred, score) in enumerate(zip(flow_data, predictions, scores)):
            device_id = flow.get('device_id', flow.get('src_ip', 'unknown'))
            
            # Baselining
            feature_vector = feature_vectors[i]
            baseline_deviation = None
            anomaly_details = []
            
            if device_id in self.baseliner.device_profiles:
                deviation, is_baseline_anomaly = self.baseliner.get_deviation_score(
                    device_id, feature_vector
                )
                baseline_deviation = deviation
                
                if is_baseline_anomaly:
                    anomaly_details.append(f"Baseline deviation: {deviation:.2f} sigma")
            
            # Update baseline
            self.baseliner.update_baseline(device_id, feature_vector)
            
            result = InferenceResult(
                flow_id=flow.get('flow_id', f"flow_{i}"),
                device_id=device_id,
                timestamp=time.time(),
                is_anomaly=pred == -1,
                anomaly_score=float(score),
                prediction=int(pred),
                anomaly_details=anomaly_details if anomaly_details else None,
                device_baseline_deviation=baseline_deviation,
                processing_time_ms=0.0  # Will be updated below
            )
            results.append(result)
        
        # Calculate batch latency
        end_time = time.perf_counter()
        batch_latency_ms = (end_time - start_time) * 1000
        
        # Update individual results with average latency
        avg_latency = batch_latency_ms / len(flows)
        for result in results:
            result.processing_time_ms = avg_latency
            self.inference_count += 1
            self.latency_history.append(avg_latency)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get inference statistics"""
        if not self.latency_history:
            return {
                'inference_count': self.inference_count,
                'avg_latency_ms': 0.0,
                'p50_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'p99_latency_ms': 0.0
            }
        
        latencies = list(self.latency_history)
        return {
            'inference_count': self.inference_count,
            'avg_latency_ms': float(np.mean(latencies)),
            'p50_latency_ms': float(np.percentile(latencies, 50)),
            'p95_latency_ms': float(np.percentile(latencies, 95)),
            'p99_latency_ms': float(np.percentile(latencies, 99)),
            'target_latency_ms': self.max_latency_ms,
            'meeting_target': np.mean(latencies) < self.max_latency_ms
        }


class InferencePipeline:
    """
    Complete inference pipeline with eBPF integration
    Supports callback-based result handling
    """
    
    def __init__(
        self,
        inference_engine: RealTimeInference,
        result_callback: Optional[Callable[[InferenceResult], None]] = None,
        queue_size: int = 1000
    ):
        """
        Initialize inference pipeline
        
        Args:
            inference_engine: RealTimeInference instance
            result_callback: Optional callback for anomaly results
            queue_size: Maximum queue size for flows
        """
        self.inference_engine = inference_engine
        self.result_callback = result_callback
        self.flow_queue: Queue = Queue(maxsize=queue_size)
        
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._processed_count = 0
        self._anomaly_count = 0
    
    def start(self):
        """Start the pipeline worker thread"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        print("Inference pipeline started")
    
    def stop(self):
        """Stop the pipeline"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        print("Inference pipeline stopped")
    
    def submit_flow(self, flow: Dict) -> bool:
        """
        Submit a flow for processing
        
        Args:
            flow: Raw flow data
            
        Returns:
            True if successfully queued, False if queue is full
        """
        try:
            self.flow_queue.put_nowait(flow)
            return True
        except:
            return False
    
    def _worker_loop(self):
        """Worker thread for processing flows"""
        batch = []
        batch_timeout = 0.01  # 10ms batch window
        
        while self._running:
            try:
                # Try to fill batch
                while len(batch) < self.inference_engine.batch_size:
                    try:
                        flow = self.flow_queue.get(timeout=batch_timeout)
                        batch.append(flow)
                    except Empty:
                        break
                
                if batch:
                    # Process batch
                    results = self.inference_engine.process_batch(batch)
                    
                    for result in results:
                        self._processed_count += 1
                        if result.is_anomaly:
                            self._anomaly_count += 1
                        
                        # Call callback for anomalies
                        if result.is_anomaly and self.result_callback:
                            self.result_callback(result)
                    
                    batch = []
                    
            except Exception as e:
                print(f"Pipeline error: {e}")
                batch = []
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        inference_stats = self.inference_engine.get_stats()
        return {
            'processed_flows': self._processed_count,
            'detected_anomalies': self._anomaly_count,
            'anomaly_rate': self._anomaly_count / max(1, self._processed_count),
            'queue_size': self.flow_queue.qsize(),
            **inference_stats
        }
    
    def process_direct(self, flows: List[Dict]) -> List[InferenceResult]:
        """
        Process flows directly without queuing (for testing/sync mode)
        
        Args:
            flows: List of flow dictionaries
            
        Returns:
            List of InferenceResults
        """
        results = self.inference_engine.process_batch(flows)
        
        for result in results:
            if result.is_anomaly and self.result_callback:
                self.result_callback(result)
            self._processed_count += 1
            if result.is_anomaly:
                self._anomaly_count += 1
        
        return results


# eBPF flow format conversion
def ebpf_flow_to_dict(ebpf_event: Dict) -> Dict:
    """
    Convert eBPF event to flow dictionary
    
    Args:
        ebpf_event: Raw eBPF event data
        
    Returns:
        Flow dictionary compatible with feature extraction
    """
    return {
        'flow_id': ebpf_event.get('id', f"flow_{time.time()}"),
        'device_id': ebpf_event.get('device_id', ebpf_event.get('src_ip', '')),
        'src_ip': ebpf_event.get('src_ip', ''),
        'dst_ip': ebpf_event.get('dst_ip', ''),
        'src_port': ebpf_event.get('src_port', 0),
        'dst_port': ebpf_event.get('dst_port', 0),
        'protocol': ebpf_event.get('protocol', 6),
        'bytes_sent': ebpf_event.get('bytes_out', 0),
        'bytes_received': ebpf_event.get('bytes_in', 0),
        'packets_sent': ebpf_event.get('packets_out', 0),
        'packets_received': ebpf_event.get('packets_in', 0),
        'duration': ebpf_event.get('duration', 0.0),
        'timestamp': ebpf_event.get('timestamp', time.time()),
        'flags_count': ebpf_event.get('tcp_flags', 0),
        'ja3_hash': ebpf_event.get('ja3', ''),
        'ja4_hash': ebpf_event.get('ja4', ''),
        'tls_version': ebpf_event.get('tls_version', 0),
        'cipher_suite': ebpf_event.get('cipher_suite', 0),
        'packet_sizes': ebpf_event.get('packet_sizes', [])
    }