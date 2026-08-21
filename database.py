import os
import sqlite3
import psycopg2


def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    connection = sqlite3.connect("inventory.db")
    connection.row_factory = sqlite3.Row
    return connection


def using_postgres():
    return bool(os.environ.get("DATABASE_URL"))


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    if using_postgres():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id SERIAL PRIMARY KEY,
                item_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)

    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")