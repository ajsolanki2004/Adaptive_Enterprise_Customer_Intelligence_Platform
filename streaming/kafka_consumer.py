import json
import time
import random
from streaming.kafka_producer import message_queue
from streaming.realtime_feature_updater import RealtimeFeatureUpdater
from decision_engine.realtime_actions import RealtimeActionEngine

class MockKafkaConsumer:
    """Consumes generated events from the producer queue in-memory."""
    def __init__(self, topic="ecommerce_events"):
        self.topic = topic
        self.feature_updater = RealtimeFeatureUpdater()
        self.action_engine = RealtimeActionEngine()
        print(f"Mock Kafka Consumer initialized on topic '{self.topic}'")
        
    def consume(self):
        print("Consumer listening for events...")
        try:
            while True:
                # 1. Constantly poll the event bus for new user traffic
                if not message_queue.empty():
                    msg_str = message_queue.get()
                    event = json.loads(msg_str)
                    print(f"\n[Consumer] Received event: {event['event_type']} from customer {event['customer_id']}")
                    
                    # 2. Re-calculate the customer's Machine Learning traits instantly in the database
                    self.feature_updater.update(event)
                    
                    # 3. Simulate grabbing the current AI predictions for this user
                    # (In a true production environment, we'd query the DB or call the models here)
                    mock_predictions = {
                        'segment_id': random.randint(0, 3),
                        'churn_risk': random.uniform(0.1, 0.9),
                        'predicted_clv': random.uniform(100, 3000)
                    }
                    
                    # 4. Pass the real-time activity and the AI scores into the Business Logic Engine
                    self.action_engine.process_event(event['customer_id'], mock_predictions)
                    
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Consumer stopped.")

if __name__ == "__main__":
    consumer = MockKafkaConsumer()
    consumer.consume()
