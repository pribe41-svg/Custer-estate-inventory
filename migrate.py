import sqlite3

connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

print("Starting inventory database migration...")

# Create a new inventory table with site-aware uniqueness
cursor.execute("""
    CREATE TABLE inventory_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        site TEXT NOT NULL DEFAULT 'Unassigned',
        quantity INTEGER NOT NULL,
        minimum_stock INTEGER NOT NULL,
        category TEXT,
        location TEXT,
        UNIQUE(name, site)
    )
""")

# Copy all existing inventory
cursor.execute("""
    INSERT INTO inventory_new
    (id, name, site, quantity, minimum_stock, category, location)
    SELECT
        id,
        name,
        COALESCE(site, 'Unassigned'),
        quantity,
        minimum_stock,
        category,
        location
    FROM inventory
""")

# Replace old table
cursor.execute("""
    DROP TABLE inventory
""")

cursor.execute("""
    ALTER TABLE inventory_new
    RENAME TO inventory
""")

connection.commit()

print("Migration complete.")
print("Existing inventory was preserved.")

cursor.close()
connection.close()