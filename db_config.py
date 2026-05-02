import mysql.connector
import os
from dotenv import load_dotenv
from tkinter import messagebox

load_dotenv()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            auth_plugin="mysql_native_password"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        return None