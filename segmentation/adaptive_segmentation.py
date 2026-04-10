from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
from feature_store.feature_registry import FeatureRegistry
from config.db_config import get_connection

class AdaptiveSegmentation:
    """
    Dynamically finds the best 'K' clusters by sweeping through a range
    and selecting the configuration with the highest Silhouette Score.
    """
    def __init__(self, min_clusters=2, max_clusters=6):
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.scaler = StandardScaler()
        
    def find_best_k(self, data):
        """Sweeps K values and returns the K with highest silhouette score."""
        best_k = self.min_clusters
        best_score = -1
        
        print("Evaluating multiple cluster sizes for Adaptive Segmentation...")
        
        # 1. We don't know how many distinct "personas" exist in the data yet
        # 2. Loop through 2, 3, 4, 5, and 6 cluster arrangements to test them
        for k in range(self.min_clusters, self.max_clusters + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(data)
            
            # 3. Calculate Silhouette Score (how well-spaced boundaries are)
            score = silhouette_score(data, labels)
            print(f"k={k} score={score:.4f}")
            
            # 4. Save the cluster amount (K) that resulted in the mathematically cleanest boundaries
            if score > best_score:
                best_score = score
                best_k = k
                
        print(f"Best K selected: {best_k}")
        return best_k
        
    def run_segmentation(self):
        """Main orchestrator for clustering"""
        # 1. Pull the pre-calculated behavior traits from the registry
        df = FeatureRegistry.get_all_features()
        if df is None or df.empty:
            print("No features available for segmentation.")
            return None
            
        # 2. Remove the customer_id string, as K-Means only handles raw numbers
        clustering_data = df.drop(columns=['customer_id'])
        
        # 3. Scale all data so things like "Total Spend" ($500) don't vastly outweigh "Recency" (3 days)
        scaled_data = self.scaler.fit_transform(clustering_data)
        
        # 4. Automatically figure out how many segments currently exist using Silhouette math
        best_k = self.find_best_k(scaled_data)
        
        # 5. Fit the final K-Means model using the optimized value of K and generate assigned labels
        model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        labels = model.fit_predict(scaled_data)
        
        # 6. Map the resulting AI grouping IDs back to the real customer IDs
        df['segment_id'] = labels
        result_df = df[['customer_id', 'segment_id']]
        
        # 7. Write the final assignments back to PostgreSQL
        self.save_results(result_df)
        return result_df
        
    def save_results(self, results_df):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            for _, row in results_df.iterrows():
                cursor.execute("""
                    INSERT INTO segmentation_results (customer_id, segment_id)
                    VALUES (%s, %s)
                    ON CONFLICT (customer_id)
                    DO UPDATE SET
                        segment_id = EXCLUDED.segment_id,
                        updated_at = CURRENT_TIMESTAMP
                """, (int(row['customer_id']), int(row['segment_id'])))
                
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Saved optimized customer segments for {len(results_df)} customers.")
        except Exception as e:
            print(f"Error saving segments to database: {e}")

if __name__ == "__main__":
    seg = AdaptiveSegmentation()
    seg.run_segmentation()
