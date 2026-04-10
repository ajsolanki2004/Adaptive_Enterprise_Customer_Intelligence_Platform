from feature_store.feature_registry import FeatureRegistry
from models.churn_model import ChurnModel
from models.clv_model import CLVModel

def run_prediction_pipeline(customer_id):
    # 1. Start the prediction workflow for a single specific customer
    print(f"=== Running Predictions for Customer {customer_id} ===")
    
    # 2. Extract that customer's engineered features (spend frequency, recency, etc.) from the DB
    df = FeatureRegistry.get_customer_features(customer_id)
    if df is None or df.empty:
        print("Customer features not found in DB.")
        return
        
    # 3. Load the pre-trained Machine Learning Models from local storage
    churn = ChurnModel()
    clv = CLVModel()
    
    try:
        # 4. Generate the exact mathematical probability that this customer will leave
        c_prob = churn.predict_proba(df)[0]
        # 5. Predict the total future revenue this customer will generate
        c_val = clv.predict(df)[0]
        
        print(f"Customer Loss Probability: {c_prob:.2f}")
        print(f"Predicted CLV: ${c_val:.2f}")
    except Exception as e:
        # If no models exist yet, catch the exception to prevent crashes
        print(f"Error during prediction: {e}. Models might not be trained. Run training pipeline first.")

if __name__ == "__main__":
    run_prediction_pipeline(1)
