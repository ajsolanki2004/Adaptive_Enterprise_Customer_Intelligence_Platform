class ActionRecommender:
    """Translates model predictions into business actions using configurable rules."""
    
    @staticmethod
    def get_recommendation(segment_id, churn_prob, clv):
        """
        Evaluates predictions to assign standard marketing actions.
        """
        # Handling high-risk customers based on value
        if churn_prob > 0.6:
            if clv > 2000:
                return "Retention Campaign - VIP Offer"
            else:
                return "Discount Campaign - Win-Back"
                
        # Handling low-risk, high engagement
        if churn_prob < 0.3:
            if clv > 3000:
                return "Premium Cross-Sell / Upsell"
            else:
                return "Loyalty Reward Program Invite"
                
        # Moderate risk/value 
        return "Standard Monthly Newsletter"
