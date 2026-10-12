from flask import Blueprint, jsonify

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
        "project": "StockPilot",
    }), 200