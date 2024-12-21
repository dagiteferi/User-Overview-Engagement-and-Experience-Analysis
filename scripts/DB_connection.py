import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class PostgresConnection:
    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        self.dbname = dbname or os.getenv('DB_DATABASE')
        self.user = user or os.getenv('DB_USER')
        self.password = password or os.getenv('DB_PASSWORD')
        self.host = host or os.getenv('DB_HOST')
        self.port = port or os.getenv('DB_PORT')
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            print("Connected to PostgreSQL database!")
        except Exception as e:
            print(f"Error: {e}")
            self.conn = None

    def execute_query(self, query):
        if self.cursor is None:
            print("Cursor is None. Check your connection.")
            return None
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def close_connection(self):
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()
            print("Connection closed.")
