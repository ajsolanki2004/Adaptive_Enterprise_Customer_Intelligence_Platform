import time
import json
import random
from queue import Queue

# Global in-memory message queue to simulate Kafka topic 'ecommerce_events'
message_queue = Queue()

class MockKafkaProducer:
    def __init__(self, topic="ecommerce_events"):
        self.topic = topic
        print(f"Mock Kafka Producer initialized on topic '{self.topic}'")
        
    def produce(self, message):
        message_queue.put(message)
        print(f"[Producer] Sent: {message}")

def simulate_events():
    producer = MockKafkaProducer()
    event_types = ["purchase", "login", "page_view"]
    
    print("Starting event simulation. Press Ctrl+C to stop.")
    try:
        while True:
            event = {
                "event_id": random.randint(1000, 9999),
                "customer_id": random.randint(1, 100),
                "event_type": random.choice(event_types),
                "amount": round(random.uniform(10.0, 500.0), 2) if random.random() > 0.5 else 0.0,
                "timestamp": time.time()
            }
            producer.produce(json.dumps(event))
            time.sleep(random.uniform(0.5, 3.0))
    except KeyboardInterrupt:
        print("Producer stopped.")

if __name__ == "__main__":
    simulate_events()
