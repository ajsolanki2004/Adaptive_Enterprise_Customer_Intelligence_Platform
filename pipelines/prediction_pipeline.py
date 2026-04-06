from feature_store.feature_registry import FeatureRegistry
from models.churn_model import ChurnModel
from models.clv_model import CLVModel

def run_prediction_pipeline(customer_id):
    print(f"=== Running Predictions for Customer {customer_id} ===")
    
    df = FeatureRegistry.get_customer_features(customer_id)
    if df is None or df.empty:
        print("Customer features not found in DB.")
        return
        
    churn = ChurnModel()
    clv = CLVModel()
    
    try:
        c_prob = churn.predict_proba(df)[0]
        c_val = clv.predict(df)[0]
        
        print(f"Customer Loss Probability: {c_prob:.2f}")
        print(f"Predicted CLV: ${c_val:.2f}")
    except Exception as e:
        print(f"Error during prediction: {e}. Models might not be trained. Run training pipeline first.")

if __name__ == "__main__":
    run_prediction_pipeline(1)
