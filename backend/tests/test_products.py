
import pytest

from app import create_app, db
from app.models import Product


@pytest.fixture()
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })

    with app.app_context():
        db.create_all()

        db.session.add_all([
            Product(name="Wireless Mouse", price=799, stock=30),
            Product(name="USB Mouse", price=399, stock=3),
            Product(name="Keyboard", price=999, stock=10),
        ])
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_list_products(client):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.json["total"] == 3
    assert len(response.json["products"]) == 3


def test_search_products(client):
    response = client.get("/api/products?search=mouse")

    assert response.status_code == 200
    assert response.json["total"] == 2


def test_low_stock_filter(client):
    response = client.get("/api/products?low_stock=true")

    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["products"][0]["name"] == "USB Mouse"


def test_pagination(client):
    response = client.get("/api/products?page=1&per_page=2")

    assert response.status_code == 200
    assert response.json["total"] == 3
    assert len(response.json["products"]) == 2
    assert response.json["total_pages"] == 2


def test_invalid_page(client):
    response = client.get("/api/products?page=0")

    assert response.status_code == 400


def test_create_product(client):
    response = client.post(
        "/api/products",
        json={
            "name": "Webcam",
            "price": 1499,
            "stock": 12,
        },
    )

    assert response.status_code == 201
    assert response.json["product"]["name"] == "Webcam"


def test_reject_invalid_product(client):
    response = client.post(
        "/api/products",
        json={
            "name": "",
            "price": 100,
            "stock": 2,
        },
    )

    assert response.status_code == 400
