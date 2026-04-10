import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from feature_store.feature_registry import FeatureRegistry
import warnings

warnings.filterwarnings('ignore')

class CLVModel:
    def __init__(self, model_path="models/saved/clv_model.pkl"):
        self.model_path = model_path
        self.model = None

    def create_synthetic_labels(self, df):
        """Creates dummy CLV targets for demonstration purposes in absence of longitudinal data."""
        # Baseline CLV = total_spend * 1.5 + some random noise
        np.random.seed(42)
        noise = np.random.normal(0, 100, size=len(df))
        df['future_clv'] = df['total_spend'] * 1.5 + noise
        df['future_clv'] = df['future_clv'].clip(lower=0) 
        return df

    def train(self):
        print("Training CLV Model...")
        
        # 1. Pull the absolute latest engineered features from the Postgres Feature Store
        df = FeatureRegistry.get_all_features()
        if df is None or df.empty:
            print("No data available for training.")
            return None

        # 2. Synthesize the Customer Lifetime Value (CLV) targets if missing historicals
        df = self.create_synthetic_labels(df)
        
        # 3. Separate inputs (features) from the target (Future revenue)
        X = df.drop(columns=['customer_id', 'future_clv'])
        y = df['future_clv']
        
        if len(X) < 2:
             print("Not enough data to train.")
             return None
             
        # 4. Train-test split (80% training data, 20% validation data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 5. Build a Gradient Boosting Regressor (outputs continuous numbers/dollars instead of probabilities)
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # 6. Evaluate error margins using Root Mean Squared Error (RMSE)
        preds = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        print(f"CLV Model trained with RMSE: {rmse:.2f}")
        
        # 7. Save model to disk for fast API loading
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        return rmse
        
    def predict(self, customer_df):
        if self.model is None:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                raise ValueError("Model not trained or saved yet.")
                
        X = customer_df.drop(columns=['customer_id'], errors='ignore')
        if 'future_clv' in X.columns:
            X = X.drop(columns=['future_clv'])
            
        preds = self.model.predict(X)
        return preds

if __name__ == "__main__":
    cm = CLVModel()
    cm.train()
