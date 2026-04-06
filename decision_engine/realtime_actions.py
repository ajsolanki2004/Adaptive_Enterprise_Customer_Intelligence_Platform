from decision_engine.action_recommender import ActionRecommender

class RealtimeActionEngine:
    """Processes streaming real-time events and returns immediate business actions."""
    
    @staticmethod
    def process_event(customer_id, event_payload, models_dict=None):
        """
        Takes real-time customer data payload (e.g. from Kafka), passes through
        model scoring implicitly, and generates an action.
        """
        # In full production, this bridges feature inference and model prediction
        segment = event_payload.get('segment_id', 0)
        churn_prob = event_payload.get('churn_risk', 0.15)
        clv = event_payload.get('predicted_clv', 1500)
        
        action = ActionRecommender.get_recommendation(segment, churn_prob, clv)
        print(f"[{customer_id}] Real-time event triggered action: '{action}'")
        return action
