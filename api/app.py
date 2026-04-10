"""
RESTful API for the AECIP platform.
Exposes predictions and customer intelligence via HTTP endpoints.
"""
from flask import Flask, request, jsonify
from decision_engine.action_recommender import ActionRecommender
from models.churn_model import ChurnModel
from models.clv_model import CLVModel
import pandas as pd

app = Flask(__name__)

# Initialize predictive models (loads .pkl files from disk)
churn_model = ChurnModel()
clv_model = CLVModel()

@app.route('/segment', methods=['POST'])
def segment():
    # Receive JSON payload containing customer traits
    data = request.json
    # Return a mocked segment (in a true prod environment, this would call adaptive_segmentation.py)
    return jsonify({"customer_id": data.get('customer_id'), "segment": "High Value"})

@app.route('/predict-churn', methods=['POST'])
def predict_churn():
    # Extract data securely from the incoming POST request
    data = request.json
    # Convert JSON dictionaries directly into a Pandas DataFrame for ML processing
    df = pd.DataFrame([data])
    try:
        # Generate prediction array and pull the highest-confidence probability
        prob = churn_model.predict_proba(df)[0]
    except:
        # Graceful fallback: If models are untrained, default to 50% coin-flip logic
        prob = 0.50 
    # Return formatted JSON back to the caller
    return jsonify({"customer_id": data.get('customer_id'), "churn_risk": float(prob)})

@app.route('/predict-clv', methods=['POST'])
def predict_clv():
    data = request.json
    df = pd.DataFrame([data])
    try:
        # Generate the regression output (expected dollar value)
        clv = clv_model.predict(df)[0]
    except:
        clv = 1000.0 # graceful fallback
    return jsonify({"customer_id": data.get('customer_id'), "predicted_clv": float(clv)})

@app.route('/customer-profile', methods=['GET'])
def customer_profile():
    customer_id = request.args.get('customer_id', 1)
    
    return jsonify({
        "customer_id": customer_id,
        "segment": "High Value",
        "churn_risk": 0.35,
        "predicted_clv": 4200.0
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
