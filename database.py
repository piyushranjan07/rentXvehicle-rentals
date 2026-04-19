import mysql.connector
from dotenv import load_dotenv
load_dotenv()
import os

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE")
        )
        if conn.is_connected():
            return conn
    except Exception as e:
        print("Error:", e)
        return None 