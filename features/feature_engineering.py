import pandas as pd
from config.db_config import get_connection
import warnings

warnings.filterwarnings('ignore')

def generate_features():
    """
    Reads transactions from the database and aggregates them into customer features.
    Saves the computed features to the customer_features table.
    """
    try:
        # 1. Open database connection and select all raw transaction logs
        conn = get_connection()
        query = "SELECT * FROM transactions"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("No transactions found. Skipping feature engineering.")
            conn.close()
            return

        # 2. Feature Engineering: We are building an RFM (Recency, Frequency, Monetary) matrix.
        # Machine learning models can't easily read loose lists of transactions. 
        # They need flat, aggregated behaviors per customer.
        
        # Ensure our timestamps are explicitly typed
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        
        # Calculate the absolute newest date in the dataset to act as "today" for 'Recency' calculations
        max_date = df['purchase_date'].max()
        
        # 3. Aggregate all loose transactions into 4 distinct macro-level behavioral metrics
        features = df.groupby('customer_id').agg(
            total_spend=('amount', 'sum'),           # Overall lifetime value so far
            purchase_frequency=('amount', 'count'),  # How many total separate orders they placed
            avg_purchase_value=('amount', 'mean'),   # How much they spend per visit on average
            last_purchase=('purchase_date', 'max')   # Exact datetime of their final order
        ).reset_index()
        
        # 4. Transform 'last_purchase' into a physical integer ('days since last seen')
        features['recency_days'] = (max_date - features['last_purchase']).dt.days
        features.drop(columns=['last_purchase'], inplace=True)
        
        # 5. Save the engineered ML features back to the database using an "Upsert"
        cursor = conn.cursor()
        for _, row in features.iterrows():
            # If the feature row already exists, update it. If not, insert it.
            cursor.execute("""
                INSERT INTO customer_features (customer_id, avg_purchase_value, purchase_frequency, recency_days, total_spend)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) 
                DO UPDATE SET 
                    avg_purchase_value = EXCLUDED.avg_purchase_value,
                    purchase_frequency = EXCLUDED.purchase_frequency,
                    recency_days = EXCLUDED.recency_days,
                    total_spend = EXCLUDED.total_spend
            """, (
                int(row['customer_id']),
                float(row['avg_purchase_value']),
                float(row['purchase_frequency']),
                int(row['recency_days']),
                float(row['total_spend'])
            ))
            
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Successfully engineered features for {len(features)} customers.")
        
    except Exception as e:
        print(f"Error in feature engineering: {e}")

if __name__ == "__main__":
    generate_features()
