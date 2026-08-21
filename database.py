import sqlite3
import os

DATABASE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "inventory.db"
)


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            minimum_stock INTEGER NOT NULL,
            category TEXT,
            location TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
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

    for item_name, item in inventory.items():
        connection.execute("""
            INSERT OR IGNORE INTO inventory
            (name, quantity, minimum_stock, category, location)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item_name,
            item.get("quantity", 0),
            item.get("minimum_stock", 0),
            item.get("category", ""),
            item.get("location", "")
        ))

    connection.commit()
    connection.close()

    print("Inventory migration complete.")   

if __name__ == "__main__":
    initialize_database()
    migrate_inventory()

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM inventory"
    ).fetchall()

    print("Items in database:", len(rows))

    for row in rows:
        print(dict(row))

    connection.close()