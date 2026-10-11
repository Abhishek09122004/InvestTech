import os
from urllib.parse import quote

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine(database: str | None = None):
    """
    Create PostgreSQL connection, or fall back to local SQLite if PostgreSQL is not configured.
    """
    host = os.getenv("POSTGRES_HOST")
    if not host:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "investor_intelligence.db"))
        return create_engine(f"sqlite:///{db_path}")

    if database is None:
        database = os.getenv("POSTGRES_DATABASE")
    
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "")
    password = os.getenv("POSTGRES_PASSWORD", "")

    # URL-encode credentials to handle special characters (e.g., @ in password)
    encoded_user = quote(user, safe="")
    encoded_password = quote(password, safe="")

    connection_string = (
        f"postgresql+psycopg2://"
        f"{encoded_user}:{encoded_password}@{host}:{port}/{database}"
        "?sslmode=require"
    )

    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        print(f"PostgreSQL connection failed ({e}). Falling back to local SQLite.")
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "investor_intelligence.db"))
        return create_engine(f"sqlite:///{db_path}")


def create_database() -> None:
    """
    Create the target database if it does not exist (PostgreSQL only).
    """
    host = os.getenv("POSTGRES_HOST")
    if not host:
        print("Note: POSTGRES_HOST not configured. Using local database storage.")
        return

    target_db = os.getenv("POSTGRES_DATABASE")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "")
    password = os.getenv("POSTGRES_PASSWORD", "")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database="postgres",
            user=user,
            password=password,
            sslmode="require",
            connect_timeout=5
        )
        conn.autocommit = True
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (target_db,)
            )
            
            if not cursor.fetchone():
                print(f"Database '{target_db}' does not exist. Creating...")
                cursor.execute(f"CREATE DATABASE {target_db}")
                print(f"Database '{target_db}' created successfully.")
            else:
                print(f"Database '{target_db}' already exists.")
        finally:
            cursor.close()
            conn.close()
    except Exception as exc:
        print(f"PostgreSQL notice: {exc}. The application will fall back to local database storage.")

