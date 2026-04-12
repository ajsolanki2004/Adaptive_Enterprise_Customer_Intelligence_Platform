# AECIP: Adaptive Enterprise Customer Intelligence Platform

**AECIP** is a full-stack, enterprise-grade machine learning platform designed to provide autonomous, real-time customer intelligence. It moves beyond static analytics by implementing an adaptive lifecycle—from data ingestion and feature engineering to model deployment and automated retraining.

## 🚀 Key Features

- **Predictive Analytics**:
  - **Customer Loss Prediction**: Real-time identification of customers at risk of churn (rebranded as "Customer Loss").
  - **Customer Lifetime Value (CLV)**: High-precision forecasting of individual customer revenue potential.
- **Autonomous ML (AutoML)**:
  - **Drift Detection**: Automatic monitoring of statistical shifts in data distributions.
  - **Self-Retraining Pipelines**: The system detects performance degradation and triggers retraining without manual intervention.
- **AI Decision Intelligence Dashboard**: A premium, dark-mode Streamlit interface that includes:
  - **Decision Center**: Automated action simulation (retention & win-back campaigns) with priority/urgency signals and ROI estimates.
  - **AI Insights**: Strategic natural-language narrative generation explaining the "Why" behind the data.
  - **XAI Explainer**: Visual model explainability (SHAP/LIME approximations) showing exactly which behavioral traits drive predictions.
  - **Business Impact Layer**: Financial ROI simulation for executed strategies.
  - **Conversational AI Assistant**: Interactive data querying and intelligence agent.
  - **Feedback Loop Visualization**: Adaptive pipeline monitoring and system architecture tracking.
- **Scalable Infrastructure**:
  - **Feature Store**: Centralized management for training and serving features.
  - **Event Streaming**: Integration with Kafka for processing real-time customer behavior.
  - **RESTful API**: Flask-based API for seamless integration with external CRM and ERP systems.

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **ML Frameworks**: Scikit-learn, XGBoost, Pandas, NumPy
- **Visualization**: Streamlit (Executive Dashboard)
- **Backend**: Flask (API Layer)
- **Database**: PostgreSQL (Structured data storage)
- **Streaming**: Confluent Kafka (Simulated event processing)
- **Pipelines**: Custom modular pipelines for Training, Prediction, and Monitoring.

## 📁 Project Structure

```bash
├── api/             # Flask REST API implementation
├── automl/          # Automated model selection and optimization
├── dashboard/       # Streamlit application for business intelligence
├── database/        # Schema definitions and DB initialization scripts
├── decision_engine/ # Business logic and strategy recommendation system
├── feature_store/   # Centralized feature definitions and management
├── models/          # Persistent storage for trained ML weights/artifacts
├── monitoring/      # Drift detection and performance tracking
├── pipelines/       # End-to-end Training and Prediction workflows
├── retraining/      # Autonomous retraining logic
└── streaming/       # Kafka producers/consumers for real-time data
```

## 🚥 Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initialize Database**:
    ```bash
    python database/init_db.py
    ```
3.  **Run the Platform**:
    Use the `main.py` CLI to launch different modules:
    - **Train Models**: `python main.py --mode train`
    - **Run Predictions**: `python main.py --mode predict --customer_id 1`
    - **Start Dashboard**: `python main.py --mode dashboard`
    - **Start API**: `python main.py --mode api`
    - **Monitor Drift**: `python main.py --mode monitor`
    - **Simulate Event Stream**: `python main.py --mode stream`

---

### Project Vision

AECIP aims to bridge the gap between "Black Box" machine learning and actual business value by providing a transparent, self-healing system that evolves alongside shifting customer behaviors.
