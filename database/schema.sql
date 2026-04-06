-- Phase 0: Database Schema for AECIP

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    amount FLOAT,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_features (
    customer_id INT PRIMARY KEY REFERENCES customers(customer_id),
    avg_purchase_value FLOAT,
    purchase_frequency FLOAT,
    recency_days INT,
    total_spend FLOAT
);

CREATE TABLE IF NOT EXISTS model_registry (
    model_name VARCHAR(255),
    version INT,
    accuracy FLOAT,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    PRIMARY KEY (model_name, version)
);

CREATE TABLE IF NOT EXISTS segmentation_results (
    customer_id INT PRIMARY KEY REFERENCES customers(customer_id),
    segment_id INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drift_metrics (
    id SERIAL PRIMARY KEY,
    psi_score FLOAT,
    kl_score FLOAT,
    composite_score FLOAT,
    severity_level VARCHAR(50),
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
