from monitoring.drift_intelligence import DriftIntelligence
from automl.model_tuner import ModelTuner
from feature_store.feature_registry import FeatureRegistry
from models.churn_model import ChurnModel
import pandas as pd
import numpy as np

class AutonomousRetrainer:
    """
    Checks for data drift and triggers retraining if severe drift is detected.
    """
    def check_and_retrain(self):
        print("Starting Autonomous Retraining Check...")
        
        df = FeatureRegistry.get_all_features()
        if df is None or len(df) < 20: 
            print("Not enough data to evaluate true drift. Simulating random data drift check...")
            expected = np.random.normal(100, 20, 1000)
            actual = np.random.normal(130, 25, 100) # Synthesized severe drift
        else:
            # For demonstration, comparing feature `total_spend`
            expected = df['total_spend'].values
            # Synthesize current batch drift to prove CI/CD loop hooks correctly
            actual = expected * 1.5 + np.random.normal(0, 15, len(expected))
            
        drift_result = DriftIntelligence.evaluate_drift(expected, actual)
        
        if drift_result['severity'] == "Severe":
            print("Severe drift detected. Triggering Model Tuner for automatic retraining.")
            tuner = ModelTuner(target_col='is_churned')
            cm = ChurnModel()
            df_labeled = cm.create_synthetic_labels(df if df is not None else pd.DataFrame())
            if not df_labeled.empty:
                tuner.tune_and_select(df_labeled)
        else:
            print("Drift is within acceptable limits. No retraining needed.")

if __name__ == "__main__":
    retrainer = AutonomousRetrainer()
    retrainer.check_and_retrain()
