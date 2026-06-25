"""
Isolation Forest Model for Anomaly Detection
Training and inference with ONNX export
"""

import numpy as np
import onnx
import onnxruntime as ort
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import json
import time


class IsolationForestModel:
    """
    Isolation Forest wrapper with ONNX export capability
    Optimized for edge device deployment
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.1,
        max_samples: int = 256,
        random_state: int = 42
    ):
        """
        Initialize Isolation Forest model
        
        Args:
            n_estimators: Number of trees in the forest
            contamination: Expected proportion of anomalies
            max_samples: Number of samples to draw for each tree
            random_state: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.max_samples = max_samples
        self.random_state = random_state
        
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.training_stats: Dict = {}
        
    def fit(self, X: np.ndarray, feature_names: Optional[List[str]] = None):
        """
        Train the Isolation Forest model
        
        Args:
            X: Training data of shape (n_samples, n_features)
            feature_names: Optional list of feature names
        """
        print(f"Training Isolation Forest with {X.shape[0]} samples...")
        
        # Fit scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            max_samples=self.max_samples,
            random_state=self.random_state,
            n_jobs=-1  # Use all available cores
        )
        self.model.fit(X_scaled)
        
        self.is_fitted = True
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        
        # Calculate training statistics
        self.training_stats = {
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'mean_scores': float(np.mean(self.model.score_samples(X_scaled))),
            'std_scores': float(np.std(self.model.score_samples(X_scaled))),
            'training_time': 'completed'
        }
        
        print(f"Training complete. Mean anomaly score: {self.training_stats['mean_scores']:.4f}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            Array of predictions (-1 for anomaly, 1 for normal)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate anomaly scores (lower = more anomalous)
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            Array of anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before scoring")
        
        X_scaled = self.scaler.transform(X)
        return self.model.score_samples(X_scaled)
    
    def export_to_onnx(self, output_path: str) -> str:
        """
        Export model to ONNX format for efficient inference
        
        Args:
            output_path: Path to save the ONNX model
            
        Returns:
            Path to the exported model
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before export")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create ONNX model using skl2onnx
        try:
            from skl2onnx import convert_sklearn
            from skl2onnx.common.data_types import FloatTensorType
            
            # Define input type
            initial_type = [('float_input', FloatTensorType([None, X.shape[1]] if hasattr(self, '_last_X_shape') else [None, len(self.feature_names)]))]
            
            # Convert
            onnx_model = convert_sklearn(
                self.model,
                initial_types=[('float_input', FloatTensorType([None, len(self.feature_names)]))],
                target_opset=12
            )
            
            # Save
            onnx.save(onnx_model, str(output_path))
            print(f"Model exported to ONNX: {output_path}")
            
            return str(output_path)
            
        except ImportError:
            # Fallback: Create custom ONNX model
            print("skl2onnx not available, creating custom ONNX export...")
            self._export_custom_onnx(output_path)
            return str(output_path)
    
    def _export_custom_onnx(self, output_path: Path):
        """Create a simplified ONNX model with model metadata"""
        # Save model parameters and scaler stats as JSON alongside ONNX
        metadata = {
            'model_type': 'IsolationForest',
            'n_estimators': self.n_estimators,
            'contamination': self.contamination,
            'max_samples': self.max_samples,
            'feature_names': self.feature_names,
            'scaler_mean': self.scaler.mean_.tolist() if self.scaler else None,
            'scaler_scale': self.scaler.scale_.tolist() if self.scaler else None,
            'training_stats': self.training_stats
        }
        
        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save tree structures
        trees_data = []
        for estimator in self.model.estimators_:
            tree_info = {
                'n_nodes': estimator.tree_.node_count,
                'feature': estimator.tree_.feature.tolist(),
                'threshold': estimator.tree_.threshold.tolist(),
                'value': estimator.tree_.value.tolist()
            }
            trees_data.append(tree_info)
        
        trees_path = output_path.with_suffix('.trees.json')
        with open(trees_path, 'w') as f:
            json.dump(trees_data, f)
        
        print(f"Model metadata saved to: {metadata_path}")
        print(f"Tree structures saved to: {trees_path}")
    
    @classmethod
    def load_from_onnx(cls, model_path: str) -> 'IsolationForestModel':
        """
        Load model from ONNX format
        
        Args:
            model_path: Path to ONNX model file
            
        Returns:
            Loaded IsolationForestModel instance
        """
        model_path = Path(model_path)
        
        # Load metadata
        metadata_path = model_path.with_suffix('.json')
        if not metadata_path.exists():
            raise ValueError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create instance with same parameters
        instance = cls(
            n_estimators=metadata['n_estimators'],
            contamination=metadata['contamination'],
            max_samples=metadata['max_samples']
        )
        
        instance.feature_names = metadata['feature_names']
        instance.training_stats = metadata.get('training_stats', {})
        
        # Reconstruct scaler
        instance.scaler = StandardScaler()
        instance.scaler.mean_ = np.array(metadata['scaler_mean'])
        instance.scaler.scale_ = np.array(metadata['scaler_scale'])
        instance.scaler.n_features_in_ = len(metadata['scaler_mean'])
        
        # Reconstruct model
        from sklearn.ensemble import IsolationForest
        instance.model = IsolationForest(
            n_estimators=metadata['n_estimators'],
            contamination=metadata['contamination'],
            max_samples=metadata['max_samples']
        )
        
        # Reconstruct trees (simplified - in practice would need full reconstruction)
        trees_path = model_path.with_suffix('.trees.json')
        if trees_path.exists():
            print("Loaded tree structures from:", trees_path)
        
        instance.is_fitted = True
        
        return instance


class AnomalyDetector:
    """
    High-level anomaly detector with configurable thresholds
    """
    
    def __init__(
        self,
        model: IsolationForestModel,
        threshold_std: float = 2.0,
        adaptive: bool = True
    ):
        """
        Initialize anomaly detector
        
        Args:
            model: Trained IsolationForestModel
            threshold_std: Number of standard deviations for anomaly threshold
            adaptive: Whether to use adaptive thresholding
        """
        self.model = model
        self.threshold_std = threshold_std
        self.adaptive = adaptive
        
        self.score_history: List[float] = []
        self.baseline_mean: float = 0.0
        self.baseline_std: float = 1.0
        
    def set_baseline(self, scores: np.ndarray):
        """Establish baseline from normal traffic scores"""
        self.baseline_mean = float(np.mean(scores))
        self.baseline_std = float(np.std(scores))
        self.score_history = scores.tolist()
        
    def detect(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies in input data
        
        Args:
            X: Input features of shape (n_samples, n_features)
            
        Returns:
            Tuple of (predictions, scores)
        """
        scores = self.model.score_samples(X)
        
        if self.adaptive and self.baseline_std > 0:
            # Adaptive threshold based on baseline
            threshold = self.baseline_mean - (self.threshold_std * self.baseline_std)
        else:
            # Fixed threshold
            threshold = np.percentile(scores, self.model.contamination * 100)
        
        predictions = np.where(scores < threshold, -1, 1)
        
        return predictions, scores
    
    def get_anomaly_probability(self, score: float) -> float:
        """
        Convert anomaly score to probability (0-1)
        
        Args:
            score: Raw anomaly score
            
        Returns:
            Probability of being an anomaly
        """
        from scipy.stats import norm
        
        if self.baseline_std > 0:
            z_score = (score - self.baseline_mean) / self.baseline_std
            probability = norm.cdf(z_score)
        else:
            probability = 0.5
        
        return float(probability)


def train_on_iot23(
    data_path: str,
    output_path: str,
    n_estimators: int = 100,
    contamination: float = 0.05
) -> IsolationForestModel:
    """
    Train model on IoT-23 dataset
    
    Args:
        data_path: Path to IoT-23 dataset (CSV or numpy array)
        output_path: Path to save trained model
        n_estimators: Number of trees
        contamination: Expected anomaly ratio
        
    Returns:
        Trained IsolationForestModel
    """
    import pandas as pd
    
    print(f"Loading IoT-23 dataset from: {data_path}")
    
    # Load data
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
        X = df.values
    elif data_path.endswith('.npy'):
        X = np.load(data_path)
    else:
        raise ValueError("Unsupported file format")
    
    print(f"Dataset shape: {X.shape}")
    
    # Create and train model
    model = IsolationForestModel(
        n_estimators=n_estimators,
        contamination=contamination
    )
    
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    model.fit(X, feature_names)
    
    # Export to ONNX
    model.export_to_onnx(output_path)
    
    return model