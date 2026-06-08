import sqlite3
import hashlib
import argparse
from datetime import datetime

DB = "iot_data.db"

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def upsert_admin(password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created_at TEXT NOT NULL)")
    cur.execute("SELECT id FROM users WHERE email = ?", ("admin",))
    row = cur.fetchone()
    now = datetime.utcnow().isoformat() + "Z"
    if row:
        cur.execute("UPDATE users SET password = ?, name = ?, created_at = ? WHERE id = ?", (hash_password(password), "Admin", now, row[0]))
        print(f"Updated admin (id={row[0]}) password")
    else:
        cur.execute("INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)", ("Admin", "admin", hash_password(password), now))
        print("Inserted admin user: admin")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--password', '-p', default='1234', help='Admin password to set')
    args = p.parse_args()
    upsert_admin(args.password)
