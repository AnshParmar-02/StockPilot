
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from app import db
from app.models import Product

api = Blueprint("api", __name__)

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
        "project": "StockPilot"
    }), 200


def validate_product_data(data, partial=False):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    allowed_fields = {"name", "price", "stock"}

    if not data:
        return "Provide at least one product field."

    if not set(data).issubset(allowed_fields):
        return "Only name, price, and stock fields are allowed."

    if not partial:
        missing = allowed_fields - set(data)
        if missing:
            return f"Missing required fields: {', '.join(sorted(missing))}"

    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not name.strip():
            return "Name must be a non-empty string."
        if len(name.strip()) > 120:
            return "Name must be 120 characters or fewer."

    if "price" in data:
        try:
            price = Decimal(str(data["price"]))
        except (InvalidOperation, ValueError):
            return "Price must be a valid number."

        if isinstance(data["price"], bool) or not price.is_finite():
            return "Price must be a finite number."
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
    products = db.session.execute(
        db.select(Product).order_by(Product.id)
    ).scalars().all()

    return jsonify({
        "count": len(products),
        "products": [product.to_dict() for product in products]
    }), 200


@api.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    return jsonify({"product": product.to_dict()}), 200


@api.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True)
    error = validate_product_data(data)

    if error:
        return jsonify({"error": error}), 400

    product = Product(
        name=data["name"].strip(),
        price=Decimal(str(data["price"])),
        stock=data["stock"]
    )

    try:
        db.session.add(product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        api.logger.exception("Failed to create product")
        return jsonify({"error": "Unable to create product."}), 500

    return jsonify({
        "message": "Product created successfully.",
        "product": product.to_dict()
    }), 201


@api.route("/api/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    data = request.get_json(silent=True)
    error = validate_product_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    product = db.session.get(Product, product_id)

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    if "name" in data:
        product.name = data["name"].strip()

    if "price" in data:
        product.price = Decimal(str(data["price"]))

    if "stock" in data:
        product.stock = data["stock"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        api.logger.exception("Failed to update product")
        return jsonify({"error": "Unable to update product."}), 500

    return jsonify({
        "message": "Product updated successfully.",
        "product": product.to_dict()
    }), 200


@api.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    try:
        db.session.delete(product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        api.logger.exception("Failed to delete product")
        return jsonify({"error": "Unable to delete product."}), 500

    return jsonify({
        "message": "Product deleted successfully.",
        "product": product.to_dict()
    }), 200
