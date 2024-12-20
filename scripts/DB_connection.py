import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class PostgresConnection:
    def __init__(self):
        self.dbname = os.getenv('DB_DATABASE')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
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

# Establishing the database connection
db = PostgresConnection()
db.connect()

if db.conn:
    # Example query
    query = "SELECT * FROM xdr_data"
    result = db.execute_query(query)

    if result:
        # Convert the result to a Pandas DataFrame
        df = pd.DataFrame(result, columns=[desc[0] for desc in db.cursor.description])
        print(df.head())  # Display the first few rows of the DataFrame
    else:
        print("No results returned from the query.")
    
    # Close the connection when done
    db.close_connection()
else:
    print("Error: No database connection.")
