from features.feature_engineering import generate_features
from segmentation.adaptive_segmentation import AdaptiveSegmentation
from models.churn_model import ChurnModel
from models.clv_model import CLVModel
from automl.model_tuner import ModelTuner

def run_training_pipeline():
    print("=== Starting AECIP Training Pipeline ===")
    
    print("\n1. Feature Engineering")
    generate_features()
    
    print("\n2. Customer Segmentation")
    seg = AdaptiveSegmentation()
    seg.run_segmentation()
    
    print("\n3. Training Base Churn Model")
    churn = ChurnModel()
    churn.train()
    
    print("\n4. Training Base CLV Model")
    clv = CLVModel()
    clv.train()
    
    print("\n5. Running AutoML Experiment")
    tuner = ModelTuner()
    from feature_store.feature_registry import FeatureRegistry
    df = FeatureRegistry.get_all_features()
    if df is not None and not df.empty:
        df_labeled = churn.create_synthetic_labels(df)
        tuner.tune_and_select(df_labeled)
        
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    run_training_pipeline()
