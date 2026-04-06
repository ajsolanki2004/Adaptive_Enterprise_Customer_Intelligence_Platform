from config.db_config import get_connection

class RegistryManager:
    """Manages ML model metadata stored in PostgreSQL"""
    
    @staticmethod
    def register_model(name, version, accuracy, status="production"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_registry (model_name, version, accuracy, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (model_name, version)
                DO UPDATE SET
                    accuracy = EXCLUDED.accuracy,
                    status = EXCLUDED.status,
                    training_date = CURRENT_TIMESTAMP
            """, (name, int(version), float(accuracy), status))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Successfully registered model {name} (v{version}) => {status}")
        except Exception as e:
            print(f"Error registering model: {e}")
