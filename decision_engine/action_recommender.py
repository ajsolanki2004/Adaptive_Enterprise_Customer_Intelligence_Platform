class ActionRecommender:
    """Translates model predictions into business actions using configurable rules."""
    
    @staticmethod
    def get_recommendation(segment_id, churn_prob, clv):
        """
        Evaluates predictions to assign standard marketing actions.
        """
        # Scenario 1: Red Alert - Customer is highly likely to leave (60%+)
        if churn_prob > 0.6:
            # Check their lifetime value. Are they worth saving?
            if clv > 2000:
                return "Retention Campaign - VIP Offer" # Very valuable, throw money at them
            else:
                return "Discount Campaign - Win-Back"   # Low value, send a standard discount
                
        # Scenario 2: High Loyalty - Customer is very unlikely to leave (< 30%)
        if churn_prob < 0.3:
            # Check value
            if clv > 3000:
                return "Premium Cross-Sell / Upsell"    # Whale customer, sell them more
            else:
                return "Loyalty Reward Program Invite"  # Standard loyalist, keep them engaged
                
        # Scenario 3: Everyone else in the middle
        return "Standard Monthly Newsletter"
