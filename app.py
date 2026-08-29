from flask import Flask, render_template, request, send_file, redirect
import os
from datetime import datetime
import csv

from database import get_connection, initialize_database, using_postgres

app = Flask(__name__)


# ============================================================
# LOAD INVENTORY FROM DATABASE
# ============================================================

def load_inventory_from_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, quantity, minimum_stock, category, location
        FROM inventory
        ORDER BY name
    """)

    rows = cursor.fetchall()

    inventory = {}

    for row in rows:
        if using_postgres():
            name, quantity, minimum_stock, category, location = row
        else:
            name = row["name"]
            quantity = row["quantity"]
            minimum_stock = row["minimum_stock"]
            category = row["category"]
            location = row["location"]

        inventory[name] = {
            "quantity": quantity,
            "minimum_stock": minimum_stock,
            "category": category,
            "location": location
        }

    cursor.close()
    connection.close()

    return inventory


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    inventory = load_inventory_from_database()

    total_items = len(inventory)

    total_quantity = sum(
        item["quantity"]
        for item in inventory.values()
    )

    low_stock_count = sum(
        1
        for item in inventory.values()
        if item["quantity"] <= item["minimum_stock"]
    )

    out_of_stock_count = sum(
        1
        for item in inventory.values()
        if item["quantity"] == 0
    )

    return render_template(
        "index.html",
        inventory=inventory,
        total_items=total_items,
        total_quantity=total_quantity,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )


# ============================================================
# DATABASE CHECK
# ============================================================

@app.route("/database-check")
def database_check():

    connection = get_connection()
    cursor = connection.cursor()

    database_type = (
        "PostgreSQL"
        if using_postgres()
        else "SQLite"
    )

    database_name = "Unknown"

    if using_postgres():

        cursor.execute("SELECT current_database()")
        row = cursor.fetchone()

        if row:
            database_name = row[0]

    else:
        database_name = "inventory.db"

    cursor.close()
    connection.close()

    return f"""
    <h1>Database Check</h1>

    <p><strong>Database Type:</strong> {database_type}</p>

    <p><strong>Database Name:</strong> {database_name}</p>

    <p><strong>DATABASE_URL detected:</strong>
    {bool(os.environ.get("DATABASE_URL"))}</p>
    """


# ============================================================
# ADD ITEM
# ============================================================

@app.route("/add", methods=["POST"])
def add_item():

    name = request.form.get("itemName", "").strip()
    quantity = int(request.form.get("quantity", 0))
    minimum_stock = int(
        request.form.get("minimumStock", 0)
    )
    category = request.form.get(
        "category", ""
    ).strip()
    location = request.form.get(
        "location", ""
    ).strip()

    connection = get_connection()
    cursor = connection.cursor()

    if using_postgres():

        cursor.execute(
            """
            INSERT INTO inventory
                (name, quantity, minimum_stock, category, location)
            VALUES
                (%s, %s, %s, %s, %s)
            """,
            (
                name,
                quantity,
                minimum_stock,
                category,
                location
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO inventory
                (name, quantity, minimum_stock, category, location)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            (
                name,
                quantity,
                minimum_stock,
                category,
                location
            )
        )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")


# ============================================================
# ADD STOCK
# ============================================================

@app.route("/add-stock", methods=["POST"])
def add_stock():

    item_name = request.form["stockItem"]
    quantity_added = int(
        request.form["stockQuantity"]
    )

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    cursor.execute(
        f"""
        SELECT quantity
        FROM inventory
        WHERE name = {placeholder}
        """,
        (item_name,)
    )

    item = cursor.fetchone()

    if item is None:

        cursor.close()
        connection.close()

        return "Item not found", 404

    current_quantity = item[0]

    new_quantity = (
        current_quantity + quantity_added
    )

    cursor.execute(
        f"""
        UPDATE inventory
        SET quantity = {placeholder}
        WHERE name = {placeholder}
        """,
        (
            new_quantity,
            item_name
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")

# ============================================================
# RECEIVE STOCK
# ============================================================

@app.route("/receive", methods=["POST"])
def receive_stock():

    item_name = request.form["receiveItem"]
    quantity_received = int(
        request.form["receiveQuantity"]
    )
    stocked_at = request.form.get(
        "stockedAt",
        ""
    ).strip()

    if not item_name or quantity_received < 1:

        return "Item and quantity are required.", 400

    if not stocked_at:

        return "Stocked at location is required.", 400

    received_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    # --------------------------------------------------------
    # FIND INVENTORY ITEM
    # --------------------------------------------------------

    cursor.execute(
        f"""
        SELECT quantity
        FROM inventory
        WHERE name = {placeholder}
        """,
        (item_name,)
    )

    item = cursor.fetchone()

    if item is None:

        cursor.close()
        connection.close()

        return "Item not found.", 404

    # --------------------------------------------------------
    # ADD RECEIVED QUANTITY TO INVENTORY
    # --------------------------------------------------------

    new_quantity = item[0] + quantity_received

    cursor.execute(
        f"""
        UPDATE inventory
        SET quantity = {placeholder}
        WHERE name = {placeholder}
        """,
        (
            new_quantity,
            item_name
        )
    )

    # --------------------------------------------------------
    # SAVE RECEIVING RECORD
    # --------------------------------------------------------

    cursor.execute(
        f"""
        INSERT INTO receiving
            (
                item_name,
                quantity,
                date,
                stocked_at
            )
        VALUES
            (
                {placeholder},
                {placeholder},
                {placeholder},
                {placeholder}
            )
        """,
        (
            item_name,
            quantity_received,
            received_date,
            stocked_at
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")


# ============================================================
# EDIT ITEM
# ============================================================

@app.route("/edit-item", methods=["POST"])
def edit_item():

    original_name = request.form[
        "originalName"
    ]

    item_name = request.form[
        "itemName"
    ]

    quantity = int(
        request.form["quantity"]
    )

    minimum_stock = int(
        request.form["minimumStock"]
    )

    category = request.form[
        "category"
    ]

    location = request.form[
        "location"
    ]

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    cursor.execute(
        f"""
        UPDATE inventory
        SET
            name = {placeholder},
            quantity = {placeholder},
            minimum_stock = {placeholder},
            category = {placeholder},
            location = {placeholder}
        WHERE name = {placeholder}
        """,
        (
            item_name,
            quantity,
            minimum_stock,
            category,
            location,
            original_name
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")


# ============================================================
# USE ITEM
# ============================================================

@app.route("/use", methods=["POST"])
def use_item():

    item_name = request.form["useItem"]

    quantity_used = int(
        request.form["useQuantity"]
    )

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    cursor.execute(
        f"""
        SELECT quantity
        FROM inventory
        WHERE name = {placeholder}
        """,
        (item_name,)
    )

    item = cursor.fetchone()

    if item is None:

        cursor.close()
        connection.close()

        return "Item not found", 404

    current_quantity = item[0]

    if quantity_used > current_quantity:

        cursor.close()
        connection.close()

        return (
            "You cannot use more than "
            "the current quantity.",
            400
        )

    new_quantity = (
        current_quantity - quantity_used
    )

    cursor.execute(
        f"""
        UPDATE inventory
        SET quantity = {placeholder}
        WHERE name = {placeholder}
        """,
        (
            new_quantity,
            item_name
        )
    )

    cursor.execute(
        f"""
        INSERT INTO usage_log
            (item_name, amount, date)
        VALUES
            ({placeholder}, {placeholder}, {placeholder})
        """,
        (
            item_name,
            quantity_used,
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")


# ============================================================
# LOW STOCK
# ============================================================

@app.route("/low-stock")
def low_stock():

    inventory = load_inventory_from_database()

    low_stock_items = {}

    for item_name, item in inventory.items():

        if item["quantity"] <= item["minimum_stock"]:
            low_stock_items[item_name] = item

    total_items = len(inventory)

    total_quantity = sum(
        item["quantity"]
        for item in inventory.values()
    )

    low_stock_count = len(
        low_stock_items
    )

    out_of_stock_count = sum(
        1
        for item in inventory.values()
        if item["quantity"] == 0
    )

    return render_template(
        "index.html",
        inventory=inventory,
        low_stock_items=low_stock_items,
        total_items=total_items,
        total_quantity=total_quantity,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )


# ============================================================
# SEARCH
# ============================================================

@app.route("/search")
def search_inventory():

    query = request.args.get(
        "q", ""
    ).strip().lower()

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    search_results = {}

    if query:

        search_pattern = f"%{query}%"

        cursor.execute(
            f"""
            SELECT
                name,
                quantity,
                minimum_stock,
                category,
                location
            FROM inventory
            WHERE LOWER(name) LIKE {placeholder}
               OR LOWER(location) LIKE {placeholder}
            ORDER BY name
            """,
            (
                search_pattern,
                search_pattern
            )
        )

        rows = cursor.fetchall()

        for row in rows:

            if using_postgres():

                (
                    name,
                    quantity,
                    minimum_stock,
                    category,
                    location
                ) = row

            else:

                name = row["name"]
                quantity = row["quantity"]
                minimum_stock = row[
                    "minimum_stock"
                ]
                category = row["category"]
                location = row["location"]

            search_results[name] = {
                "quantity": quantity,
                "minimum_stock": minimum_stock,
                "category": category,
                "location": location
            }

    cursor.close()
    connection.close()

    inventory = load_inventory_from_database()

    return render_template(
        "index.html",
        inventory=inventory,
        search_results=search_results,
        search_query=query
    )


# ============================================================
# LOCATIONS
# ============================================================

@app.route("/locations")
def view_locations():

    inventory = load_inventory_from_database()

    locations = {}

    for item_name, item in inventory.items():

        location = item["location"]

        if location not in locations:
            locations[location] = []

        locations[location].append(
            (item_name, item)
        )

    return render_template(
        "index.html",
        inventory=inventory,
        locations=locations
    )


# ============================================================
# USAGE REPORT
# ============================================================

@app.route("/usage-report")
def usage_report():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT item_name, amount, date
        FROM usage_log
        ORDER BY date DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    usage_log = []

    for row in rows:

        if using_postgres():

            item_name, amount, date = row

        else:

            item_name = row["item_name"]
            amount = row["amount"]
            date = row["date"]

        usage_log.append({
            "item": item_name,
            "quantity": amount,
            "date": date
        })

    inventory = load_inventory_from_database()

    return render_template(
        "index.html",
        inventory=inventory,
        usage_log=usage_log,
        show_usage_report=True
    )


# ============================================================
# MONTHLY REPORT
# ============================================================

@app.route("/monthly-report")
def monthly_report():

    month = request.args.get(
        "month"
    )

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    if month:

        cursor.execute(
            f"""
            SELECT
                item_name,
                SUM(amount) AS total_used
            FROM usage_log
            WHERE date LIKE {placeholder}
            GROUP BY item_name
            ORDER BY item_name
            """,
            (month + "%",)
        )

    else:

        cursor.execute(
            """
            SELECT
                item_name,
                SUM(amount) AS total_used
            FROM usage_log
            GROUP BY item_name
            ORDER BY item_name
            """
        )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    monthly_totals = {}

    for row in rows:

        item_name = row[0]
        total_used = row[1]

        monthly_totals[item_name] = (
            total_used
        )

    inventory = load_inventory_from_database()

    return render_template(
        "index.html",
        inventory=inventory,
        monthly_totals=monthly_totals,
        selected_month=month
    )


# ============================================================
# DELETE ITEM
# ============================================================

@app.route("/delete", methods=["POST"])
def delete_item():

    item_name = request.form[
        "deleteItem"
    ]

    connection = get_connection()
    cursor = connection.cursor()

    placeholder = (
        "%s"
        if using_postgres()
        else "?"
    )

    cursor.execute(
        f"""
        DELETE FROM inventory
        WHERE name = {placeholder}
        """,
        (item_name,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/")


# ============================================================
# EXPORT CSV
# ============================================================

@app.route("/export-csv")
def export_csv():

    inventory = load_inventory_from_database()

    filename = "inventory_export.csv"

    with open(
        filename,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Item",
            "Quantity",
            "Minimum Stock",
            "Category",
            "Location"
        ])

        for item_name, item in inventory.items():

            writer.writerow([
                item_name,
                item["quantity"],
                item["minimum_stock"],
                item["category"],
                item["location"]
            ])

    return send_file(
        filename,
        as_attachment=True
    )
# ============================================================
# RECEIVING REPORT
# ============================================================

@app.route("/receiving-report")
def receiving_report():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            date,
            stocked_at
        FROM receiving
        ORDER BY id DESC
        """
    )

    receiving_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "receiving_report.html",
        receiving_records=receiving_records
    )

# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    initialize_database()

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )