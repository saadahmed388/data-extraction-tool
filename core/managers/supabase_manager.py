import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    connection = psycopg2.connect(
        DATABASE_URL,
        connect_timeout=10,
        sslmode="require",
    )

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                current_database(),
                current_user,
                inet_server_addr(),
                inet_server_port(),
                version()
        """)

        database, user, server_ip, server_port, version = cursor.fetchone()

    print("SUCCESS: PostgreSQL connection established")
    print("Database:", database)
    print("Authenticated user:", user)
    print("Server IP:", server_ip)
    print("Server port:", server_port)
    print("Server version:", version.split(",")[0])

except Exception as exc:
    print("CONNECTION FAILED:", type(exc).__name__, str(exc))

finally:
    if connection is not None:
        connection.close()