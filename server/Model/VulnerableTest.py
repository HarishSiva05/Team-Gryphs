import sqlite3

def create_database():
    """
    Create a sample database with a users table for demonstration.
    """
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
    conn.commit()
    conn.close()

def login(username, password):
    """
    Login function that is vulnerable to SQL injection.
    """
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Vulnerable query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing query: {query}")
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        print("Login successful!")
    else:
        print("Login failed!")
    conn.close()

if __name__ == "__main__":
    # Step 1: Create the database
    create_database()

    # Step 2: Simulate a legitimate login attempt
    print("Legitimate Login Attempt:")
    login('admin', 'password123')

    # Step 3: Simulate a SQL Injection attack
    print("\nSQL Injection Attack:")
    malicious_username = "admin' --"
    malicious_password = "doesnt_matter"
    login(malicious_username, malicious_password)
