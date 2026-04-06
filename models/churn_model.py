import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from feature_store.feature_registry import FeatureRegistry
import warnings

warnings.filterwarnings('ignore')

class ChurnModel:
    def __init__(self, model_path="models/saved/churn_model.pkl"):
        self.model_path = model_path
        self.model = None

    def create_synthetic_labels(self, df):
        """Creates dummy labels for demonstration purposes if ground truth is not provided."""
        # Rule-based synthetic churn: churned if recency > 60 days and frequency is low
        df['is_churned'] = ((df['recency_days'] > 60) & (df['purchase_frequency'] < 3)).astype(int)
        return df

    def train(self):
        print("Training Churn Model...")
        df = FeatureRegistry.get_all_features()
        if df is None or df.empty:
            print("No data available for training.")
            return None

        # Normally we would fetch historical 'churn' flag, here we synthesize it for end-to-end completion
        df = self.create_synthetic_labels(df)
        
        X = df.drop(columns=['customer_id', 'is_churned'])
        y = df['is_churned']
        
        # Require at least 2 samples to split
        if len(X) < 2:
             print("Not enough data to train.")
             return None
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = XGBClassifier(eval_metric='logloss')
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Churn Model trained with Accuracy: {acc:.4f}")
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        return acc
        
    def predict_proba(self, customer_df):
        """Returns churn probabilities for given customer records."""
        if self.model is None:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                raise ValueError("Model not trained or saved yet.")
                
        X = customer_df.drop(columns=['customer_id'], errors='ignore')
        if 'is_churned' in X.columns:
            X = X.drop(columns=['is_churned'])
            
        probas = self.model.predict_proba(X)[:, 1]
        return probas

if __name__ == "__main__":
    cm = ChurnModel()
    cm.train()
