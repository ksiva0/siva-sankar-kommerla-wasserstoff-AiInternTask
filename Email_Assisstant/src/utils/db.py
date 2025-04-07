import sqlite3  

def connect_db():  
    conn = sqlite3.connect('emails.db')  
    return conn  

def init_db():  
    conn = connect_db()  
    cursor = conn.cursor()  
    cursor.execute('''  
        CREATE TABLE IF NOT EXISTS emails (  
            id INTEGER PRIMARY KEY,  
            sender TEXT,  
            recipient TEXT,  
            subject TEXT,  
            body TEXT,  
            timestamp TEXT  
        )  
    ''')  
    conn.commit()  
    conn.close()  
