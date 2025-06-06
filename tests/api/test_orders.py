import pytest
from fastapi.testclient import TestClient

from app.models.order import OrderStatus
from app.schemas.product import Product

def test_create_order(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product["id"]
    assert data["items"][0]["quantity"] == 1
    assert data["items"][0]["unit_price"] == product["price"]
    assert data["items"][0]["total_price"] == product["price"]
    assert data["total_amount"] == product["price"]
    assert data["status"] == "pending"

def test_create_order_insufficient_stock(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": product["stock"] + 1
                }
            ]
        }
    )
    
    assert response.status_code == 400
    assert "Estoque insuficiente" in response.json()["detail"]

def test_create_order_invalid_product(
    client: TestClient,
    user_token_headers: dict
):
    response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": 999,
                    "quantity": 1
                }
            ]
        }
    )
    
    assert response.status_code == 400
    assert "Produto 999 não encontrado" in response.json()["detail"]

def test_read_orders(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido
    client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    response = client.get(
        "/api/v1/orders/",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 1
    assert len(data["items"]) >= 1
    assert all("items" in order for order in data["items"])

def test_read_orders_with_status(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido
    client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    response = client.get(
        "/api/v1/orders/?status=pending",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 1
    assert len(data["items"]) >= 1
    assert all(order["status"] == "pending" for order in data["items"])

def test_read_order(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido
    create_response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    order_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product["id"]
    assert data["items"][0]["quantity"] == 1
    assert data["items"][0]["unit_price"] == product["price"]
    assert data["items"][0]["total_price"] == product["price"]
    assert data["total_amount"] == product["price"]
    assert data["status"] == "pending"

def test_read_order_not_found(
    client: TestClient,
    user_token_headers: dict
):
    response = client.get(
        "/api/v1/orders/999",
        headers=user_token_headers
    )
    
    assert response.status_code == 404
    assert "Pedido não encontrado" in response.json()["detail"]

def test_update_order_status(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido
    create_response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    order_id = create_response.json()["id"]
    
    # Atualiza o status
    response = client.put(
        f"/api/v1/orders/{order_id}",
        headers=user_token_headers,
        json={
            "status": "confirmed"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "confirmed"

def test_update_order_status_invalid(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido
    create_response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1
                }
            ]
        }
    )
    
    order_id = create_response.json()["id"]
    
    # Tenta atualizar com status inválido
    response = client.put(
        f"/api/v1/orders/{order_id}",
        headers=user_token_headers,
        json={
            "status": "invalid_status"
        }
    )
    
    assert response.status_code == 422
    assert "Input should be 'pending', 'confirmed', 'preparing', 'ready', 'delivered' or 'cancelled'" in response.json()["detail"][0]["msg"]

def test_delete_order(
    client: TestClient,
    user_token_headers: dict,
    product: dict
):
    # Cria um pedido com quantidade 6
    create_response = client.post(
        "/api/v1/orders/",
        headers=user_token_headers,
        json={
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 6
                }
            ]
        }
    )
    
    order_id = create_response.json()["id"]
    
    # Deleta o pedido
    response = client.delete(
        f"/api/v1/orders/{order_id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    
    # Verifica se o pedido foi deletado
    get_response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=user_token_headers
    )
    
    assert get_response.status_code == 404
    
    # Verifica se o estoque foi restaurado
    product_response = client.get(
        f"/api/v1/products/{product['id']}",
        headers=user_token_headers
    )
    
    assert product_response.status_code == 200
    product_data = product_response.json()
    assert product_data["stock"] == product["stock"]

def test_unauthorized_access(
    client: TestClient,
    test_product: Product
):
    response = client.get("/api/v1/orders/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"] 