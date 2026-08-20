from flask import Flask, render_template, request
import json
import os
from datetime import datetime

app = Flask(__name__)

INVENTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "inventory.json"
)
USAGE_LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "usage_log.json"
)


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r") as file:
        return json.load(file)


def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)

def load_usage_log():
    if not os.path.exists(USAGE_LOG_FILE):
        return []

    with open(USAGE_LOG_FILE, "r") as file:
        return json.load(file)


def save_usage_log(usage_log):
    with open(USAGE_LOG_FILE, "w") as file:
        json.dump(usage_log, file, indent=4)

@app.route("/")
def home():
    inventory = load_inventory()
    return render_template("index.html", inventory=inventory)


@app.route("/add", methods=["POST"])
def add_item():
    inventory = load_inventory()

    item_name = request.form["itemName"]
    quantity = int(request.form["quantity"])
    minimum_stock = int(request.form["minimumStock"])
    category = request.form["category"]
    location = request.form["location"]

    inventory[item_name] = {
        "quantity": quantity,
        "minimum_stock": minimum_stock,
        "category": category,
        "location": location
    }

    save_inventory(inventory)

    return render_template("index.html", inventory=inventory)


@app.route("/use", methods=["POST"])
def use_item():
    inventory = load_inventory()
    usage_log = load_usage_log()

    item_name = request.form["useItem"]
    quantity_used = int(request.form["useQuantity"])

    if item_name not in inventory:
        return "Item not found", 404

    current_quantity = inventory[item_name]["quantity"]

    if quantity_used > current_quantity:
        return "You cannot use more than the current quantity.", 400

    inventory[item_name]["quantity"] = current_quantity - quantity_used

    usage_log.append({
        "item": item_name,
        "amount": quantity_used,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    save_inventory(inventory)
    save_usage_log(usage_log)

    return render_template("index.html", inventory=inventory)

@app.route("/low-stock")
def low_stock():
    inventory = load_inventory()

    low_stock_items = {}

    for item_name, item in inventory.items():
        if item["quantity"] <= item["minimum_stock"]:
            low_stock_items[item_name] = item

    return render_template(
        "index.html",
        inventory=inventory,
        low_stock_items=low_stock_items
    )

@app.route("/search")
def search_inventory():
    inventory = load_inventory()

    query = request.args.get("q", "").strip().lower()

    search_results = {}

    if query:
        for item_name, item in inventory.items():
            if (
                query in item_name.lower()
                or query in item["location"].lower()
            ):
                search_results[item_name] = item

    return render_template(
        "index.html",
        inventory=inventory,
        search_results=search_results,
        search_query=query
    )

@app.route("/locations")
def view_locations():
    inventory = load_inventory()

    locations = {}

    for item_name, item in inventory.items():
        location = item["location"]

        if location not in locations:
            locations[location] = []

        locations[location].append((item_name, item))

    return render_template(
        "index.html",
        inventory=inventory,
        locations=locations
    )

@app.route("/usage-report")
def usage_report():
    usage_log = load_usage_log()

    totals = {}

    for entry in usage_log:
        item = entry["item"]
        amount = entry["amount"]

        totals[item] = totals.get(item, 0) + amount

    return render_template(
        "index.html",
        inventory=load_inventory(),
        usage_totals=totals
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)