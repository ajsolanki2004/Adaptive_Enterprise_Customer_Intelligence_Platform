"""
Database initialization routine.
Handles database creation, schema execution, and dummy data generation.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import random
import datetime

from config.db_config import get_connection

def create_database():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "5432")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "enterprise_segmentation_v2")
    
    try:
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Database '{dbname}' created successfully.")
        else:
            print(f"Database '{dbname}' already exists.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def create_schema():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            cursor.execute(f.read())
        conn.commit()
        cursor.close()
        conn.close()
        print("Schema successfully executed.")
    except Exception as e:
        print(f"Error executing schema: {e}")

def seed_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT count(*) FROM customers")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded.")
            return

        print("Seeding dummy customers and transactions...")
        for i in range(1, 101):
            cursor.execute("INSERT INTO customers (name, email) VALUES (%s, %s)", (f"Customer_{i}", f"customer{i}@example.com"))
            
            # Generate 1 to 20 transactions for each customer over the last 90 days
            num_transactions = random.randint(1, 20)
            for _ in range(num_transactions):
                amount = round(random.uniform(5.0, 500.0), 2)
                days_ago = random.randint(1, 90)
                t_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                cursor.execute("INSERT INTO transactions (customer_id, amount, purchase_date) VALUES (%s, %s, %s)", (i, amount, t_date))
                
        conn.commit()
        cursor.close()
        conn.close()
        print("Database seeded with 100 customers and their transactions.")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    create_database()
    create_schema()
    seed_data()
