from config.db_config import get_connection

class RealtimeFeatureUpdater:
    """Updates the customer feature store incrementally upon new events."""
    
    def update(self, event):
        """
        Takes raw streaming events and instantly updates the pre-calculated ML features.
        This ensures our AI models don't serve predictions based on out-of-date information.
        """
        # 1. We only care about purchase events for RFM (Recency, Frequency, Monetary) scaling
        if event.get('event_type') != 'purchase' or event.get('amount', 0) <= 0:
            return None 
            
        customer_id = event['customer_id']
        amount = event['amount']
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 2. Fetch their historical stats before this new purchase arrived
            cursor.execute("SELECT avg_purchase_value, purchase_frequency, total_spend FROM customer_features WHERE customer_id = %s", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                # 3. Mathematically merge the new purchase into their historical lifetime aggregates
                avg_val, freq, total = row
                new_freq = freq + 1
                new_total = total + amount
                new_avg = new_total / new_freq
                
                # Update the DB and reset their 'Recency' to 0 days since they literally just bought something
                cursor.execute("""
                    UPDATE customer_features 
                    SET avg_purchase_value=%s, purchase_frequency=%s, total_spend=%s, recency_days=0
                    WHERE customer_id=%s
                """, (float(new_avg), float(new_freq), float(new_total), int(customer_id)))
            else:
                # 4. If this is a brand new customer, initialize their feature row
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
