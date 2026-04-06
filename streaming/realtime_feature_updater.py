from config.db_config import get_connection

class RealtimeFeatureUpdater:
    """Updates the customer feature store incrementally upon new events."""
    
    def update(self, event):
        """
        Process a single streaming event and update DB features inline.
        """
        if event.get('event_type') != 'purchase' or event.get('amount', 0) <= 0:
            return None # We only update RFM features on purchases
            
        customer_id = event['customer_id']
        amount = event['amount']
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Fetch existing aggregates
            cursor.execute("SELECT avg_purchase_value, purchase_frequency, total_spend FROM customer_features WHERE customer_id = %s", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                avg_val, freq, total = row
                new_freq = freq + 1
                new_total = total + amount
                new_avg = new_total / new_freq
                
                cursor.execute("""
                    UPDATE customer_features 
                    SET avg_purchase_value=%s, purchase_frequency=%s, total_spend=%s, recency_days=0
                    WHERE customer_id=%s
                """, (float(new_avg), float(new_freq), float(new_total), int(customer_id)))
            else:
                cursor.execute("""
                    INSERT INTO customer_features (customer_id, avg_purchase_value, purchase_frequency, recency_days, total_spend)
                    VALUES (%s, %s, %s, %s, %s)
                """, (int(customer_id), float(amount), 1.0, 0, float(amount)))
                
            conn.commit()
            cursor.close()
            conn.close()
            print(f"[{customer_id}] Feature Store Updated: Spend +${amount:.2f}")
            return {"customer_id": customer_id, "amount_added": amount}
            
        except Exception as e:
            print(f"Error updating real-time features: {e}")
            return None
