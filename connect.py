from db_helper import get_db_connection

if __name__ == "__main__":
    try:
        connection, cursor = get_db_connection()
        backend = "MySQL" if connection.__class__.__module__.startswith("mysql") else "SQLite"
        print("Connected successfully using backend:", backend)

        if backend == "MySQL":
            host = getattr(connection, "server_host", None)
            database = getattr(connection, "database", None)
            port = getattr(connection, "server_port", None)
            print(f"Server host: {host}")
            print(f"Server port: {port}")
            print(f"Database: {database}")
            cursor.execute("SHOW TABLES LIKE 'register'")
            mysql_result = cursor.fetchone()
            if mysql_result:
                print("Register table exists in MySQL.")
            else:
                print("Register table not found in MySQL.")
        else:
            db_file = getattr(connection, "database", None)
            print(f"SQLite file: {db_file}")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='register'")
            sqlite_result = cursor.fetchone()
            if sqlite_result:
                print("Register table exists in SQLite.")
            else:
                print("Register table not found in SQLite.")
    except Exception as error:
        print("Connection failed:", error)
    finally:
        try:
            cursor.close()
            connection.close()
        except Exception:
            pass
