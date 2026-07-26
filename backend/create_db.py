import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='416003',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'smartbuilding'")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE smartbuilding")
            print("Database 'smartbuilding' created.")
        else:
            print("Database 'smartbuilding' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")

if __name__ == "__main__":
    create_db()
