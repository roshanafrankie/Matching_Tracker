import mysql.connector
import hashlib
import time  # Added for the delay

def get_connection():
    retries = 3
    while retries > 0:
        try:
            # ATTEMPT TO CONNECT
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="user_db",
                # ssl_verify_identity and ssl_ca removed to use default secure settings
            )
            cursor = conn.cursor()

            # 1. Ensure the users table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255),
                    email VARCHAR(255) UNIQUE,
                    password VARCHAR(255)
                )
            """)
            conn.commit()

            # Check and add missing columns
            required_columns = {
                'contact_no': 'VARCHAR(20)',
                'lc': 'VARCHAR(100)',
                'role': 'VARCHAR(100)',
                'image_path': 'VARCHAR(255)',
                'is_admin': 'BOOLEAN DEFAULT 0',
                'login_attempts': 'INT DEFAULT 0',
                'lockout_time': 'DATETIME NULL'
            }

            cursor.execute("DESCRIBE users")
            current_columns = [col[0] for col in cursor.fetchall()]

            for column_name, column_type in required_columns.items():
                if column_name not in current_columns:
                    try:
                        alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                        cursor.execute(alter_sql)
                        conn.commit()
                        print(f"Added missing column: {column_name}")
                    except Exception as e:
                        print(f"Error adding column {column_name}: {e}")

            # 2. Ensure interviews table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    summary LONGTEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            return conn, cursor  # SUCCESS! Return connection

        except mysql.connector.Error as err:
            print(f"Connection failed ({retries} retries left): {err}")
            retries -= 1
            if retries > 0:
                time.sleep(2)  # Wait 2 seconds before trying again
            else:
                raise Exception("Could not connect to database after 3 attempts. Check internet.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()