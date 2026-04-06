import psycopg2
import os

def get_connection():
    """
    Returns a connection to the PostgreSQL database.
    Update these credentials based on your local database setup.
    """
    dbname = os.getenv("DB_NAME", "enterprise_segmentation_v2")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "5432")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
