"""
Main entry point for the AECIP platform.
Provides a unified command-line interface for training, prediction, monitoring, and web services.
"""
import argparse
import subprocess
import os
import sys
from pipelines.training_pipeline import run_training_pipeline
from pipelines.prediction_pipeline import run_prediction_pipeline
from streaming.kafka_producer import simulate_events

def main():
    parser = argparse.ArgumentParser(description="Adaptive Enterprise Customer Intelligence Platform (AECIP) CLI")
    parser.add_argument('--mode', choices=['train', 'predict', 'monitor', 'stream', 'api', 'dashboard'], required=True)
    parser.add_argument('--customer_id', type=int, default=1, help='Customer ID for predict mode')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        run_training_pipeline()
    elif args.mode == 'predict':
        run_prediction_pipeline(args.customer_id)
    elif args.mode == 'monitor':
        from retraining.autonomous_retrainer import AutonomousRetrainer
        retrainer = AutonomousRetrainer()
        retrainer.check_and_retrain()
    elif args.mode == 'stream':
        simulate_events()
    elif args.mode == 'api':
        print("Starting API layer on port 5000...")
        subprocess.run([sys.executable, "-m", "flask", "run"], env=dict(os.environ, FLASK_APP="api/app.py"))
    elif args.mode == 'dashboard':
        print("Starting Executive Dashboard...")
        subprocess.run(["streamlit", "run", "dashboard/app.py"])

if __name__ == "__main__":
    main()
