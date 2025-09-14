import sqlite3
from datetime import datetime

DB = "electricity_billing.db"
def calculate_bill(consumption_kwh: float) -> float:
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT min_kwh, max_kwh, rate FROM tariffs ORDER BY min_kwh ASC")
    tariffs = cursor.fetchall()
    conn.close()

    remaining = consumption_kwh
    total = 0.0

    for min_kwh, max_kwh, rate in tariffs:
        if remaining <= 0:
            break

        if max_kwh is None: 
            total += remaining * rate
            break

        slab_range = max_kwh - min_kwh
        used_in_slab = min(remaining, slab_range)
        total += used_in_slab * rate
        remaining -= used_in_slab

    return total


def add_customer(name, phone, email, location):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, phone, email, location, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, location, "active"))
    conn.commit()
    conn.close()
    print(f"[+] Customer {name} added successfully!")


def add_usage_and_bill(customer_id, consumption_kwh, month, year):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_records (customer_id, month, year, consumption_kwh)
        VALUES (?, ?, ?, ?)
    """, (customer_id, month, year, consumption_kwh))

    amount_due = calculate_bill(consumption_kwh)

    cursor.execute("""
        INSERT INTO bills (customer_id, month, year, amount_due, is_paid)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, month, year, amount_due, 0))  # 0 = unpaid

    conn.commit()
    conn.close()
    print(f"[+] Bill for {month}/{year} added: {amount_due:.2f} £")


def list_customers():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()

    print("\n=== Customers ===")
    for row in rows:
        print(row)


def list_bills():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills")
    rows = cursor.fetchall()
    conn.close()

    print("\n=== Bills ===")
    for row in rows:
        print(row)
