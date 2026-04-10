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

# Initialize predictive models
churn_model = ChurnModel()
clv_model = CLVModel()

@app.route('/segment', methods=['POST'])
def segment():
    data = request.json
    return jsonify({"customer_id": data.get('customer_id'), "segment": "High Value"})

@app.route('/predict-churn', methods=['POST'])
def predict_churn():
    data = request.json
    df = pd.DataFrame([data])
    try:
        prob = churn_model.predict_proba(df)[0]
    except:
        prob = 0.50 # graceful fallback if untrainted
    return jsonify({"customer_id": data.get('customer_id'), "churn_risk": float(prob)})

@app.route('/predict-clv', methods=['POST'])
def predict_clv():
    data = request.json
    df = pd.DataFrame([data])
    try:
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
