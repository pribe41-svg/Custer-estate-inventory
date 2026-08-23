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


    # ========================================================
    # POSTGRESQL
    # ========================================================

    if using_postgres():

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                site TEXT NOT NULL DEFAULT 'Unassigned',
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT,
                UNIQUE(name, site)
            )
        """)


        # Add site column if this is an older database

        cursor.execute("""
            ALTER TABLE inventory
            ADD COLUMN IF NOT EXISTS site TEXT
            DEFAULT 'Unassigned'
        """)


        cursor.execute("""
            UPDATE inventory
            SET site = 'Unassigned'
            WHERE site IS NULL
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id SERIAL PRIMARY KEY,
                item_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)


    # ========================================================
    # SQLITE
    # ========================================================

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                site TEXT NOT NULL DEFAULT 'Unassigned',
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT
            )
        """)


        # Check whether the existing SQLite table has a site column

        cursor.execute("""
            PRAGMA table_info(inventory)
        """)

        columns = [
            row["name"]
            for row in cursor.fetchall()
        ]


        if "site" not in columns:

            cursor.execute("""
                ALTER TABLE inventory
                ADD COLUMN site TEXT DEFAULT 'Unassigned'
            """)


        cursor.execute("""
            UPDATE inventory
            SET site = 'Unassigned'
            WHERE site IS NULL
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


    # ========================================================
    # POSTGRESQL
    # ========================================================

    if using_postgres():

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                site TEXT NOT NULL DEFAULT 'Unassigned',
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT,
                UNIQUE(name, site)
            )
        """)


        # Add site column if this is an older database

        cursor.execute("""
            ALTER TABLE inventory
            ADD COLUMN IF NOT EXISTS site TEXT
            DEFAULT 'Unassigned'
        """)


        cursor.execute("""
            UPDATE inventory
            SET site = 'Unassigned'
            WHERE site IS NULL
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id SERIAL PRIMARY KEY,
                item_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL
            )
        """)


    # ========================================================
    # SQLITE
    # ========================================================

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                site TEXT NOT NULL DEFAULT 'Unassigned',
                quantity INTEGER NOT NULL,
                minimum_stock INTEGER NOT NULL,
                category TEXT,
                location TEXT
            )
        """)


        # Check whether the existing SQLite table has a site column

        cursor.execute("""
            PRAGMA table_info(inventory)
        """)

        columns = [
            row["name"]
            for row in cursor.fetchall()
        ]


        if "site" not in columns:

            cursor.execute("""
                ALTER TABLE inventory
                ADD COLUMN site TEXT DEFAULT 'Unassigned'
            """)


        cursor.execute("""
            UPDATE inventory
            SET site = 'Unassigned'
            WHERE site IS NULL
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

  


if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")

    