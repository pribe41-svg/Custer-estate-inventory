from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

INVENTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")


def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r") as file:
        return json.load(file)


def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)


@app.route("/")
def home():
    return render_template("index.html")


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

    return f"{item_name} saved successfully!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)