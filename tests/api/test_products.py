import pytest
from fastapi.testclient import TestClient
from app.schemas.product import Product


def test_create_product(
    client: TestClient,
    admin_token_headers: dict
):
    response = client.post(
        "/api/v1/products/",
        headers=admin_token_headers,
        json={
            "name": "Test Product",
            "description": "Test Description",
            "price": 99.99,
            "stock": 10,
            "category": "test"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["description"] == "Test Description"
    assert data["price"] == 99.99
    assert data["stock"] == 10
    assert data["category"] == "test"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_product_unauthorized(
    client: TestClient,
    user_token_headers: dict
):
    response = client.post(
        "/api/v1/products/",
        headers=user_token_headers,
        json={
            "name": "Test Product",
            "description": "Test Description",
            "price": 99.99,
            "stock": 10,
            "category": "test"
        }
    )
    
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"]

def test_read_products(
    client: TestClient,
    user_token_headers: dict
):
    response = client.get(
        "/api/v1/products/",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 0
    assert isinstance(data["items"], list)

def test_read_products_with_search(
    client: TestClient,
    admin_token_headers: dict
):
    # Cria um produto
    client.post(
        "/api/v1/products/",
        headers=admin_token_headers,
        json={
            "name": "Search Product",
            "description": "Test Description",
            "price": 99.99,
            "stock": 10,
            "category": "test"
        }
    )
    
    response = client.get(
        "/api/v1/products/?search=Search",
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 1
    assert len(data["items"]) >= 1
    assert all("Search" in p["name"] for p in data["items"])

def test_read_products_with_category(
    client: TestClient,
    admin_token_headers: dict
):
    # Cria um produto
    client.post(
        "/api/v1/products/",
        headers=admin_token_headers,
        json={
            "name": "Category Product",
            "description": "Test Description",
            "price": 99.99,
            "stock": 10,
            "category": "test_category"
        }
    )
    
    response = client.get(
        "/api/v1/products/?category=test_category",
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 1
    assert len(data["items"]) >= 1
    assert all(p["category"] == "test_category" for p in data["items"])

def test_read_product(
    client: TestClient,
    admin_token_headers: dict,
    test_product: Product
):
    response = client.get(
        f"/api/v1/products/{test_product.id}",
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == test_product.name
    assert data["description"] == test_product.description
    assert data["price"] == test_product.price
    assert data["stock"] == test_product.stock
    assert data["category"] == test_product.category

def test_read_product_not_found(
    client: TestClient,
    admin_token_headers: dict
):
    response = client.get(
        "/api/v1/products/999",
        headers=admin_token_headers
    )
    
    assert response.status_code == 404
    assert "Produto não encontrado" in response.json()["detail"]

def test_update_product(
    client: TestClient,
    admin_token_headers: dict,
    test_product: Product
):
    response = client.put(
        f"/api/v1/products/{test_product.id}",
        headers=admin_token_headers,
        json={
            "name": "Updated Product",
            "price": 149.99,
            "stock": 20
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == "Updated Product"
    assert data["price"] == 149.99
    assert data["stock"] == 20
    assert data["description"] == test_product.description  # Não foi alterado
    assert data["category"] == test_product.category  # Não foi alterado

def test_update_product_unauthorized(
    client: TestClient,
    user_token_headers: dict
):
    response = client.put(
        "/api/v1/products/1",
        headers=user_token_headers,
        json={
            "name": "Updated Product"
        }
    )
    
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"]

def test_delete_product(
    client: TestClient,
    admin_token_headers: dict,
    test_product: Product
):
    response = client.delete(
        f"/api/v1/products/{test_product.id}",
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    
    # Verifica se o produto foi realmente deletado
    get_response = client.get(
        f"/api/v1/products/{test_product.id}",
        headers=admin_token_headers
    )
    assert get_response.status_code == 404

def test_delete_product_unauthorized(
    client: TestClient,
    user_token_headers: dict
):
    response = client.delete(
        "/api/v1/products/1",
        headers=user_token_headers
    )
    
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"] 