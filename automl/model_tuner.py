import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from feature_store.feature_registry import FeatureRegistry
from database.registry_manager import RegistryManager
import warnings

warnings.filterwarnings('ignore')

class ModelTuner:
    """AutoML engine testing multiple classifiers automatically."""
    
    def __init__(self, target_col='is_churned'):
        self.target_col = target_col
        self.models = {
            'RandomForest': RandomForestClassifier(random_state=42),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'XGBoost': XGBClassifier(eval_metric='logloss')
        }
        
    def tune_and_select(self, df):
        print("Starting AutoML Tuning...")
        if self.target_col not in df.columns:
             print(f"Target column '{self.target_col}' not found in data.")
             return None
             
        X = df.drop(columns=['customer_id', self.target_col], errors='ignore')
        y = df[self.target_col]
        
        if len(X) < 2:
            print("Not enough data to run AutoML")
            return None
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        best_acc = 0
        best_model_name = ""
        best_model = None
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            print(f"{name} accuracy: {acc:.4f}")
            
            if acc > best_acc:
                best_acc = acc
                best_model_name = name
                best_model = model
                
        print(f"Best model selected: {best_model_name} with API: {best_acc:.4f}")
        
        # Save best model to disk
        model_path = "models/saved/best_automl_model.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(best_model, model_path)
        
        # Register best model in DB
        RegistryManager.register_model(
            name=f"automl_{self.target_col}_{best_model_name}",
            version=1,
            accuracy=float(best_acc),
            status="production"
        )
        return best_model
