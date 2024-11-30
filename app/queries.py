# queries.py

from .db import get_db

def get_all_subscriptions():
    db=get_db()
    cursor=db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT subscription_id FROM subscriptions""")
    return cursor.fetchall()

# Payment Queries
def get_all_payments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.payment_id, p.payment_amount, p.card_no, p.payment_date, p.payment_method, s.subscription_id
        FROM payments p
        JOIN subscriptions s ON p.subscription_id = s.subscription_id
    """)
    return cursor.fetchall()

def add_payment(payment_amount, card_no, payment_date, payment_method, subscription_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO payments (payment_amount, card_no, payment_date, payment_method, subscription_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (payment_amount, card_no, payment_date, payment_method, subscription_id))
    db.commit()

def get_payment_by_id(payment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
    return cursor.fetchone()

def update_payment(payment_id, payment_amount, card_no, payment_date, payment_method, subscription_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE payments
        SET payment_amount = %s, card_no = %s, payment_date = %s, payment_method = %s, subscription_id = %s
        WHERE payment_id = %s
        """,
        (payment_amount, card_no, payment_date, payment_method, subscription_id, payment_id)
    )
    db.commit()

def delete_payment(payment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
    db.commit()