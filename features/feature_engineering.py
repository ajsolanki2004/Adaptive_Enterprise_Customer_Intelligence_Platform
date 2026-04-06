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
        conn = get_connection()
        query = "SELECT * FROM transactions"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("No transactions found. Skipping feature engineering.")
            conn.close()
            return

        # Feature Engineering: RFM (Recency, Frequency, Monetary) style
        # 1. total_spend: Sum of amounts
        # 2. purchase_frequency: Count of transactions
        # 3. avg_purchase_value: Mean of amounts
        # 4. recency_days: Days since last purchase (relative to max date in dataset)
        
        # Convert purchase_date to datetime if not already
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        max_date = df['purchase_date'].max()
        
        features = df.groupby('customer_id').agg(
            total_spend=('amount', 'sum'),
            purchase_frequency=('amount', 'count'),
            avg_purchase_value=('amount', 'mean'),
            last_purchase=('purchase_date', 'max')
        ).reset_index()
        
        features['recency_days'] = (max_date - features['last_purchase']).dt.days
        features.drop(columns=['last_purchase'], inplace=True)
        
        # Save to database (Upsert)
        cursor = conn.cursor()
        for _, row in features.iterrows():
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
