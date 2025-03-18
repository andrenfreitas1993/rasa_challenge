import sqlite3
import os
from cryptography.fernet import Fernet
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

# Function to decrypt the CPF
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()

# Function to check if the database exists
def check_database():
    return os.path.exists('users.db')

# Function to connect to the database (or create a new one if it doesn't exist)
def connect_to_db():
    if not check_database():
        print("Database not found. Creating database...")
        conn = sqlite3.connect('users.db')
        create_table(conn)  # Create the table if the database is new
    else:
        conn = sqlite3.connect('users.db')
    return conn

# Function to create the users table
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        cpf TEXT)''')
    conn.commit()

# Function to query the database for a user by CPF
def query_user_by_cpf(cpf):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Encrypt the provided CPF to query the database
    encrypted_cpf = encrypt_data(cpf)
    
    # Query the database for the user by encrypted CPF
    cursor.execute('''SELECT name, cpf FROM users WHERE cpf = ?''', (encrypted_cpf,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        name, encrypted_cpf = user
        decrypted_cpf = decrypt_data(encrypted_cpf)
        return name, decrypted_cpf
    else:
        return None, None

# Rasa Action to check if the user exists by CPF
class ActionCheckUserByCPF(Action):
    
    def name(self) -> str:
        return "action_check_user_by_cpf"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Retrieve the CPF from the slot
        cpf = tracker.get_slot("cpf")
        
        if not cpf:
            dispatcher.utter_message(text="Please provide a CPF to check.")
            return []
        
        # Query the database for the user
        name, decrypted_cpf = query_user_by_cpf(cpf)
        
        if name:
            dispatcher.utter_message(text=f"User found: Name: {name}, CPF: {decrypted_cpf}")
        else:
            dispatcher.utter_message(text="User not found with this CPF.")
        
        return []
