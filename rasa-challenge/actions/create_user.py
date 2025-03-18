import sqlite3
import os
from cryptography.fernet import Fernet
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Function to load the encryption key
def load_key():
    return open("key.key", "rb").read()

# Function to encrypt the CPF
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

# Check if the database exists
def check_database():
    return os.path.exists('users.db')

# Connect to the database (or create a new one if it doesn't exist)
def connect_to_db():
    if not check_database():
        print("Database not found. Creating the database...")
        conn = sqlite3.connect('users.db')
        create_table(conn)  # Create the table if the database is new
    else:
        conn = sqlite3.connect('users.db')
    return conn

# Create the users table
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        cpf TEXT)''')
    conn.commit()

# Register a new user
def register_user(name, cpf):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Encrypt the CPF before saving
    encrypted_cpf = encrypt_data(cpf)
    
    cursor.execute('''INSERT INTO users (name, cpf) VALUES (?, ?)''', (name, encrypted_cpf))
    conn.commit()
    conn.close()

class ActionRegisterUser(Action):

    def name(self) -> str:
        return "action_create_user"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the slots with the user's data
        name = tracker.get_slot("name")
        cpf = tracker.get_slot("cpf")
        
        if not name or not cpf:
            dispatcher.utter_message(text="Please provide all the required information for registration.")
            return []
        
        # Register the user
        register_user(name, cpf)
        
        # Respond to the user
        dispatcher.utter_message(text=f"User {name} successfully registered!")

        return []
