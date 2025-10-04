"""
CTGenie Model Service
Handles model loading, prediction, and SHAP explanations
"""

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shap


class CTGenieModel:
    """Wrapper for CTG prediction model with SHAP explanations"""

    def __init__(self, model_dir: str = "../data/models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.metadata = {}
        self.class_names = ['Normal', 'Suspect', 'Pathological']
        self.explainer = None

    def load(self) -> bool:
        """Load model and preprocessing artifacts"""
        try:
            # Load model - try native JSON format first (more compatible)
            from xgboost import XGBClassifier

            json_model_path = self.model_dir / "xgboost_model.json"
            pkl_model_path = self.model_dir / "xgboost_model.pkl"

            if json_model_path.exists():
                # Load using native XGBoost format (preferred)
                self.model = XGBClassifier()
                self.model.load_model(json_model_path)
                print(f"✅ Loaded model from {json_model_path} (native format)")
            elif pkl_model_path.exists():
                # Fallback to pickle
                self.model = joblib.load(pkl_model_path)
                print(f"✅ Loaded model from {pkl_model_path} (pickle format)")
            else:
                print(f"⚠️  Model not found at {json_model_path} or {pkl_model_path}")
                return False

            # Load scaler - try v2 first (compatible version)
            scaler_v2_path = self.model_dir / "scaler_v2.pkl"
            scaler_path = self.model_dir / "scaler.pkl"

            if scaler_v2_path.exists():
                self.scaler = joblib.load(scaler_v2_path)
                print(f"✅ Loaded scaler from {scaler_v2_path}")
            elif scaler_path.exists():
                try:
                    self.scaler = joblib.load(scaler_path)
                    print(f"✅ Loaded scaler from {scaler_path}")
                except Exception as e:
                    print(f"⚠️  Could not load scaler: {e}")
                    self.scaler = None
            else:
                print(f"⚠️  Scaler not found, predictions may be inaccurate")
                self.scaler = None

            # Load feature names
            features_path = self.model_dir / "feature_names.json"
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
                print(f"✅ Loaded {len(self.feature_names)} feature names")
            else:
                print(f"⚠️  Feature names not found")
                return False

            # Load metadata
            metadata_path = self.model_dir / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print(f"✅ Loaded metadata (accuracy: {self.metadata.get('test_accuracy', 'unknown')})")

            # Try to initialize SHAP explainer (non-critical)
            try:
                self._init_shap_explainer()
            except Exception as shap_error:
                print(f"⚠️  SHAP initialization skipped: {shap_error}")
                self.explainer = None

            return True

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _init_shap_explainer(self):
        """Initialize SHAP explainer for the model"""
        try:
            # Use TreeExplainer for XGBoost
            self.explainer = shap.TreeExplainer(self.model)
            print(f"✅ SHAP explainer initialized")
        except Exception as e:
            print(f"⚠️  Could not initialize SHAP explainer: {e}")
            self.explainer = None

    def preprocess_features(self, features: Dict[str, float]) -> np.ndarray:
        """
        Preprocess raw CTG features for model input

        Args:
            features: Dictionary of CTG feature values

        Returns:
            Scaled feature array ready for prediction
        """
        # Create DataFrame with features in correct order
        feature_values = []
        for fname in self.feature_names:
            if fname in features:
                feature_values.append(features[fname])
            else:
                # Missing feature - use 0 or median (should log warning)
                print(f"⚠️  Missing feature: {fname}, using 0")
                feature_values.append(0.0)

        # Convert to numpy array and reshape
        X = np.array(feature_values).reshape(1, -1)

        # Scale if scaler is available
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
            print("⚠️  No scaler available, using raw features")

        return X_scaled

    def predict(self, features: Dict[str, float]) -> Tuple[int, np.ndarray, np.ndarray]:
        """
        Predict NSP class from CTG features

        Args:
            features: Dictionary of CTG feature values

        Returns:
            Tuple of (predicted_class, class_probabilities, shap_values)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load() first.")

        # Preprocess
        X_scaled = self.preprocess_features(features)

        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        # Calculate SHAP values
        shap_values = None
        if self.explainer is not None:
            try:
                raw_shap = self.explainer.shap_values(X_scaled)

                # If multi-class, shap_values is a list of arrays
                if isinstance(raw_shap, list) and len(raw_shap) > 0:
                    # Use SHAP values for predicted class
                    shap_values = raw_shap[int(prediction)][0]
                elif isinstance(raw_shap, np.ndarray):
                    if raw_shap.ndim == 3:
                        # 3D array for multi-class: shape is (n_samples, n_features, n_classes)
                        # Get SHAP values for first sample and predicted class
                        shap_values = raw_shap[0, :, int(prediction)]
                    else:
                        shap_values = raw_shap[0]
                else:
                    shap_values = raw_shap
            except Exception as e:
                print(f"⚠️  SHAP calculation failed: {e}")
                shap_values = None

        return int(prediction), probabilities, shap_values

    def get_shap_explanation(self, shap_values: np.ndarray, top_k: int = 10) -> Dict[str, float]:
        """
        Get top contributing features from SHAP values

        Args:
            shap_values: SHAP values array
            top_k: Number of top features to return

        Returns:
            Dictionary of {feature_name: shap_value}
        """
        if shap_values is None:
            return {}

        # Get absolute values for ranking
        abs_shap = np.abs(shap_values)

        # Get top k indices
        top_indices = np.argsort(abs_shap)[-top_k:][::-1]

        # Create explanation dictionary
        explanation = {}
        for idx in top_indices:
            if idx < len(self.feature_names):
                feature_name = self.feature_names[idx]
                explanation[feature_name] = float(shap_values[idx])

        return explanation

    def validate_features(self, features: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate that required features are present

        Args:
            features: Dictionary of CTG feature values

        Returns:
            Tuple of (is_valid, list_of_missing_features)
        """
        missing = []
        for fname in self.feature_names:
            if fname not in features:
                missing.append(fname)

        is_valid = len(missing) == 0
        return is_valid, missing

    def get_model_info(self) -> Dict:
        """Get model metadata and information"""
        return {
            "loaded": self.model is not None,
            "model_type": self.metadata.get("model_type", "Unknown"),
            "version": self.metadata.get("version", "Unknown"),
            "n_features": len(self.feature_names),
            "test_accuracy": self.metadata.get("test_accuracy"),
            "class_names": self.class_names,
            "shap_available": self.explainer is not None
        }


# Singleton instance
_model_instance = None


def get_model() -> CTGenieModel:
    """Get or create model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = CTGenieModel()
    return _model_instance
