import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return psycopg2.connect(database_url)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

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

    connection.commit()
    cursor.close()
    connection.close()


def migrate_inventory():
    import json

    inventory_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "inventory.json"
    )

    if not os.path.exists(inventory_file):
        print("No inventory.json found.")
        return

    with open(inventory_file, "r") as file:
        inventory = json.load(file)

    connection = get_connection()
    cursor = connection.cursor()

    for item_name, item in inventory.items():
        cursor.execute("""
            INSERT INTO inventory
            (name, quantity, minimum_stock, category, location)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (
            item_name,
            item.get("quantity", 0),
            item.get("minimum_stock", 0),
            item.get("category", ""),
            item.get("location", "")
        ))

    connection.commit()
    cursor.close()
    connection.close()

    print("Inventory migration complete.")


if __name__ == "__main__":
    initialize_database()
    migrate_inventory()
    print("Database initialized successfully.")