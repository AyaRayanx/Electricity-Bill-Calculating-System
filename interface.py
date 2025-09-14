from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_db_connection, hash_password

app = Flask(__name__)
app.secret_key = "supersecretkey" 
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        national_id = request.form["national_id"]
        password = hash_password(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE national_id=? AND password=?", (national_id, password))
        user = cursor.fetchone()
        conn.close()

        if user and user["role"] == "customer":
            session["user_id"] = national_id
            return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid login credentials", "danger")

    return render_template("login.html")

@app.route("/customer")
def customer_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("customer_dashboard.html", user_id=session["user_id"])

@app.route("/customer/unpaid")
def customer_unpaid():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT month, year, consumption_kwh, amount_due, is_paid
        FROM bills
        WHERE customer_id=? AND is_paid=0
    """, (session["user_id"],))
    rows = cursor.fetchall()
    conn.close()

    return render_template("customer_bills.html", title="Unpaid Bills", rows=rows)

@app.route("/customer/history")
def customer_history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT month, year, consumption_kwh, amount_due, is_paid
        FROM bills
        WHERE customer_id=?
    """, (session["user_id"],))
    rows = cursor.fetchall()
    conn.close()

    return render_template("customer_bills.html", title="Bill History", rows=rows)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
