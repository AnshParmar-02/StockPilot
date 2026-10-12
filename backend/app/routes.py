from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

#Temporary in-memory product storage.
products = [
    {
        "id": 1,
        "name": "Headphones",
        "price": 1500.0,
        "stock": 25
    },
    {
        "id": 2,
        "name": "Keyboard",
        "price": 900.0,
        "stock": 15
    }
]

next_product_id = 3



@api.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "application": "StockPilot API"
    }), 200

@api.route("/api/info", methods=["GET"])
def api_info():
    return jsonify({
        "name": "StockPilot",
        "description": "Inventory and Business Management Platform",
        "version": "1.0.0"
    }), 200

@api.route("/api/about", methods=["GET"])
def about():
    return jsonify({
        "developer": "Ansh Parmar",
        "project": "StockPilot",
    }), 200


def validate_product_data(data, partial=False):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    allowed_fields = {"name", "price", "stock"}

    if not data:
        return "Provide at least one product field."

    if not set(data.keys()).issubset(allowed_fields):
        return "Only name, price, and stock fields are allowed."

    if not partial:
        missing = allowed_fields - set(data.keys())
        if missing:
            return f"Missing required fields: {', '.join(sorted(missing))}"

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "Name must be a non-empty string."

    if "price" in data:
        price = data["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            return "Price must be a number."
        if price < 0:
            return "Price cannot be negative."

    if "stock" in data:
        stock = data["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int):
            return "Stock must be a whole number."
        if stock < 0:
            return "Stock cannot be negative."

    return None

@api.route("/api/products", methods=["GET"])
def get_products():
    return jsonify({
        "count": len(products),
        "products": products
    }), 200


@api.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify({"product": product}), 200

    return jsonify({"error": "Product not found."}), 404


@api.route("/api/products", methods=["POST"])
def create_product():
    global next_product_id

    data = request.get_json(silent=True)
    error = validate_product_data(data)

    if error:
        return jsonify({"error": error}), 400

    product = {
        "id": next_product_id,
        "name": data["name"].strip(),
        "price": float(data["price"]),
        "stock": data["stock"]
    }

    products.append(product)
    next_product_id += 1

    return jsonify({
        "message": "Product created successfully.",
        "product": product
    }), 201


@api.route("/api/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    data = request.get_json(silent=True)
    error = validate_product_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    for product in products:
        if product["id"] == product_id:
            for field, value in data.items():
                if field == "name":
                    product[field] = value.strip()
                elif field == "price":
                    product[field] = float(value)
                else:
                    product[field] = value

            return jsonify({
                "message": "Product updated successfully.",
                "product": product
            }), 200

    return jsonify({"error": "Product not found."}), 404


@api.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    for index, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(index)

            return jsonify({
                "message": "Product deleted successfully.",
                "product": deleted_product
            }), 200

    return jsonify({"error": "Product not found."}), 404