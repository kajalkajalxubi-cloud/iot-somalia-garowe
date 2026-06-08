from db_helper import get_db_connection, execute_query
import bcrypt


def create_demo_user():
    conn, cursor = get_db_connection()
    try:
        email = "admin"
        execute_query(cursor, "SELECT id FROM register WHERE email = ?", (email,))
        if cursor.fetchone():
            print("Demo user already exists: admin")
            return

        password = "1234"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        execute_query(
            cursor,
            "INSERT INTO register (first_name, last_name, contact, email, security_question, answer, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Admin", "User", "0000000000", email, "Your First Pet Name", "pet", hashed),
        )
        conn.commit()
        print(f"Demo user created: {email} / {password}")
    except Exception as e:
        print("Failed to create demo user:", e)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    create_demo_user()
