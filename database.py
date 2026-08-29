import os
import sqlite3
import psycopg2


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    database_url = os.environ.get("DATABASE_URL")

    if database_url:

        return psycopg2.connect(
            database_url
        )

    connection = sqlite3.connect(
        "inventory.db"
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE TYPE
# ============================================================

def using_postgres():

    return bool(
        os.environ.get("DATABASE_URL")
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    if using_postgres():

        # ----------------------------------------------------
        # INVENTORY TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (

                id SERIAL PRIMARY KEY,

                name TEXT NOT NULL,

                site TEXT NOT NULL,

                quantity INTEGER NOT NULL,

                minimum_stock INTEGER NOT NULL,

                category TEXT,

                location TEXT,

                UNIQUE (name, site)

            )
            """
        )

        # ----------------------------------------------------
        # USAGE LOG TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_log (

                id SERIAL PRIMARY KEY,

                item_name TEXT NOT NULL,

                amount INTEGER NOT NULL,

                date TEXT NOT NULL

            )
            """
        )

        # ----------------------------------------------------
        # RECEIVING TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS receiving (

                id SERIAL PRIMARY KEY,

                item_name TEXT NOT NULL,

                quantity INTEGER NOT NULL,

                date TEXT NOT NULL,

                stocked_at TEXT NOT NULL

            )
            """
        )

    else:

        # ----------------------------------------------------
        # SQLITE INVENTORY TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                site TEXT NOT NULL,

                quantity INTEGER NOT NULL,

                minimum_stock INTEGER NOT NULL,

                category TEXT,

                location TEXT,

                UNIQUE (name, site)

            )
            """
        )

        # ----------------------------------------------------
        # SQLITE USAGE LOG TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_log (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_name TEXT NOT NULL,

                amount INTEGER NOT NULL,

                date TEXT NOT NULL

            )
            """
        )

        # ----------------------------------------------------
        # SQLITE RECEIVING TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS receiving (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_name TEXT NOT NULL,

                quantity INTEGER NOT NULL,

                date TEXT NOT NULL,

                stocked_at TEXT NOT NULL

            )
            """
        )

    connection.commit()

    cursor.close()
    connection.close()


# ============================================================
# INITIALIZE DATABASE WHEN APP STARTS
# ============================================================

initialize_database()


# ============================================================
# DIRECT DATABASE TEST
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print(
        "Database initialized successfully."
    )
    