import streamlit as st

st.title("🎈 Aninfolder")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- Database helper -------------------------------------------------
def init_db(conn):
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        total INTEGER NOT NULL,
        available INTEGER NOT NULL
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        borrower TEXT,
        nim TEXT,
        equipment_id INTEGER,
        qty INTEGER,
        purpose TEXT,
        time_requested TEXT,
        status TEXT, -- requested, verified, rejected, returned
        verifier TEXT,
        time_verified TEXT,
        attachment BLOB,
        attachment_name TEXT,
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
    )''')
    conn.commit()

def add_sample_equipment(conn):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM equipment')
    if c.fetchone()[0] == 0:
        items = [('Buret 25 mL',10,10), ('Pipet 10 mL',15,15), ('Erlenmeyer 250 mL',20,20)]
        c.executemany('INSERT INTO equipment (name,total,available) VALUES (?, ?, ?)', items)
        conn.commit()

def get_equipment_df(conn):
    return pd.read_sql_query('SELECT * FROM equipment', conn)

def get_loans_df(conn):
    return pd.read_sql_query('SELECT l.*, e.name as equipment_name FROM loans l LEFT JOIN equipment e ON l.equipment_id=e.id ORDER BY id DESC', conn)

def create_loan(conn, borrower, nim, equipment_id, qty, purpose, attachment, attachment_name):
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
    INSERT INTO loans (borrower,nim,equipment_id,qty,purpose,time_requested,status,attachment,attachment_name)
    VALUES (?,?,?,?,?,?, 'requested', ?,?)
    ''', (borrower, nim, equipment_id, qty, purpose, now, attachment, attachment_name))
    conn.commit()

def set_loan_status(conn, loan_id, status, verifier=None):
    c = conn.cursor()
    now = datetime.now().isoformat()
    if status == 'verified':
        c.execute('UPDATE loans SET status=?, verifier=?, time_verified=? WHERE id=?', (status, verifier, now, loan_id))
        # reduce available
        c.execute('SELECT equipment_id, qty FROM loans WHERE id=?', (loan_id,))
        eq_id, qty = c.fetchone()
        c.execute('UPDATE equipment SET available = available - ? WHERE id=?', (qty, eq_id))
    elif status == 'rejected':
        c.execute('UPDATE loans SET status=?, verifier=?, time_verified=? WHERE id=?', (status, verifier, now, loan_id))
    elif status == 'returned':
        # increase available
        c.execute('SELECT equipment_id, qty FROM loans WHERE id=?', (loan_id,))
        eq_id, qty = 
