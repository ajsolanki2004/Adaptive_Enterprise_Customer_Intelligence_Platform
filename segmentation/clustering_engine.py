from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

class ClusteringEngine:
    def __init__(self, n_clusters=3, random_state=42):
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.scaler = StandardScaler()
        
    def fit_predict(self, features_df):
        """Fits the KMeans model and returns a dataframe with cluster assignments."""
        if 'customer_id' not in features_df.columns:
            raise ValueError("Dataframe must contain 'customer_id' column")
            
        clustering_data = features_df.drop(columns=['customer_id'])
        scaled_data = self.scaler.fit_transform(clustering_data)
        
        labels = self.model.fit_predict(scaled_data)
        
        result_df = features_df[['customer_id']].copy()
        result_df['segment_id'] = labels
        return result_df
