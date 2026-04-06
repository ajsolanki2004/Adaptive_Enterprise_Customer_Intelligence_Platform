import pandas as pd
from config.db_config import get_connection
import warnings

warnings.filterwarnings('ignore')

class FeatureRegistry:
    """
    Centralized registry to retrieve engineered features for models or serving.
    """
    
    @staticmethod
    def get_customer_features(customer_id):
        """Fetch features for a specific customer."""
        try:
            conn = get_connection()
            query = "SELECT * FROM customer_features WHERE customer_id=%s"
            df = pd.read_sql(query, conn, params=(customer_id,))
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching features for customer {customer_id}: {e}")
            return None

    @staticmethod
    def get_all_features():
        """Fetch all engineered features across all customers for batch processing/training."""
        try:
            conn = get_connection()
            query = "SELECT * FROM customer_features"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching all features: {e}")
            return None
