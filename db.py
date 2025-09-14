import sqlite3
import hashlib
import os

DB_NAME = "electricity_billing.db"

def reset_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS usage_records")
    cursor.execute("DROP TABLE IF EXISTS bills")
    cursor.execute("DROP TABLE IF EXISTS tariffs")
    cursor.execute("DROP TABLE IF EXISTS payments")
    cursor.execute("DROP TABLE IF EXISTS admins")

    cursor.execute("""
    CREATE TABLE admins (
        national_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        position TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE customers (
        national_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT UNIQUE,
        address TEXT,
        location TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    cursor.execute("""
    CREATE TABLE users (
        national_id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL, -- 'admin' or 'customer'
        FOREIGN KEY (national_id) REFERENCES customers(national_id),
        FOREIGN KEY (national_id) REFERENCES admins(national_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE usage_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        month TEXT,
        year INTEGER,
        consumption_kwh REAL,
        reading_date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(national_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        month TEXT,
        year INTEGER,
        consumption_kwh REAL,
        amount_due REAL,
        due_date DATE,
        is_paid INTEGER DEFAULT 0,
        created_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(national_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        customer_id TEXT,
        amount_paid REAL,
        payment_date DATE DEFAULT CURRENT_DATE,
        payment_method TEXT,
        FOREIGN KEY (bill_id) REFERENCES bills(id),
        FOREIGN KEY (customer_id) REFERENCES customers(national_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE tariffs (
        tier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        min_kwh REAL NOT NULL,
        max_kwh REAL,
        rate REAL NOT NULL,
        effective_date DATE DEFAULT CURRENT_DATE
    )
    """)

    tariffs = [
        (0, 100, 0.15),   # 0-100 kWh at $0.15 per kWh
        (100, None, 0.20) # Above 100 kWh at $0.20 per kWh
    ]
    cursor.executemany("INSERT INTO tariffs (min_kwh, max_kwh, rate) VALUES (?, ?, ?)", tariffs)
    
    sample_admins = [
        ("A123456789", "Admin One", "admin1@example.com", "555-0001", "System Administrator"),
        ("A987654321", "Admin Two", "admin2@example.com", "555-0002", "Billing Manager")
    ]
    cursor.executemany("INSERT INTO admins (national_id, name, email, phone, position) VALUES (?, ?, ?, ?, ?)", sample_admins)
    
    sample_customers = [
        ("C100000001", "John Smith", "555-1234", "john@example.com", "123 Main St", "New York"),
        ("C100000002", "Jane Doe", "555-5678", "jane@example.com", "456 Oak Ave", "Los Angeles"),
        ("C100000003", "Bob Johnson", "555-9012", "bob@example.com", "789 Pine Rd", "Chicago")
    ]
    cursor.executemany("INSERT INTO customers (national_id, name, phone, email, address, location) VALUES (?, ?, ?, ?, ?, ?)", sample_customers)
    
    users = []
    for national_id, name, phone, email, position in sample_admins:
        hashed_password = hash_password(national_id)  
        users.append((national_id, hashed_password, "admin"))
    
    for national_id, name, phone, email, address, location in sample_customers:
        hashed_password = hash_password(national_id)  
        users.append((national_id, hashed_password, "customer"))
    
    cursor.executemany("INSERT INTO users (national_id, password, role) VALUES (?, ?, ?)", users)
    
    sample_bills = [
        ("C100000001", "January", 2023, 350, 62.50, '2023-02-15', 1),
        ("C100000001", "February", 2023, 420, 79.00, '2023-03-15', 0),
        ("C100000002", "January", 2023, 280, 47.00, '2023-02-15', 1),
        ("C100000002", "February", 2023, 310, 53.00, '2023-03-15', 1),
        ("C100000003", "January", 2023, 190, 28.50, '2023-02-15', 0)
    ]
    cursor.executemany("INSERT INTO bills (customer_id, month, year, consumption_kwh, amount_due, due_date, is_paid) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_bills)

    sample_usage = [
        ("C100000001", "January", 2023, 350, '2023-01-31'),
        ("C100000001", "February", 2023, 420, '2023-02-28'),
        ("C100000002", "January", 2023, 280, '2023-01-31'),
        ("C100000002", "February", 2023, 310, '2023-02-28'),
        ("C100000003", "January", 2023, 190, '2023-01-31')
    ]
    cursor.executemany("INSERT INTO usage_records (customer_id, month, year, consumption_kwh, reading_date) VALUES (?, ?, ?, ?, ?)", sample_usage)

    sample_payments = [
        (1, "C100000001", 62.50, '2023-02-10', 'Credit Card'),
        (3, "C100000002", 47.00, '2023-02-12', 'Bank Transfer'),
        (4, "C100000002", 53.00, '2023-03-05', 'Debit Card')
    ]
    cursor.executemany("INSERT INTO payments (bill_id, customer_id, amount_paid, payment_date, payment_method) VALUES (?, ?, ?, ?, ?)", sample_payments)

    conn.commit()
    conn.close()
    print("Database initialized with sample data!")
    print("Admin logins: national_id=A123456789, password=A123456789")
    print("Admin logins: national_id=A987654321, password=A987654321")
    print("Customer logins: national_id=C100000001, password=C100000001")
    print("Customer logins: national_id=C100000002, password=C100000002")
    print("Customer logins: national_id=C100000003, password=C100000003")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    reset_database()