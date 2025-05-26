import pytest
from sqlalchemy.orm import Session

from app.services.product import (
    create_product,
    get_product,
    get_products,
    update_product,
    delete_product
)
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def test_create_product(db: Session):
    product_data = ProductCreate(
        name="Test Product",
        description="Test Description",
        price=99.99,
        stock=10,
        category="test"
    )
    
    product = create_product(db, product_data)
    assert product is not None
    assert product.name == product_data.name
    assert product.description == product_data.description
    assert product.price == product_data.price
    assert product.stock == product_data.stock
    assert product.category == product_data.category
    assert product.id is not None
    assert product.created_at is not None
    assert product.updated_at is not None

def test_get_product(db: Session, test_product: Product):
    product = get_product(db, test_product.id)
    assert product is not None
    assert product.id == test_product.id
    assert product.name == test_product.name
    assert product.description == test_product.description
    assert product.price == test_product.price
    assert product.stock == test_product.stock
    assert product.category == test_product.category

def test_get_product_not_found(db: Session):
    product = get_product(db, 999)
    assert product is None

def test_get_products(db: Session, test_product: Product):
    products = get_products(db)
    assert len(products) >= 1
    assert any(p.id == test_product.id for p in products)

def test_get_products_with_search(db: Session):
    # Cria um produto com nome específico
    product_data = ProductCreate(
        name="Search Product",
        description="Test Description",
        price=99.99,
        stock=10,
        category="test"
    )
    create_product(db, product_data)
    
    products = get_products(db, search="Search")
    assert len(products) >= 1
    assert all("Search" in p.name for p in products)

def test_get_products_with_category(db: Session):
    # Cria um produto com categoria específica
    product_data = ProductCreate(
        name="Category Product",
        description="Test Description",
        price=99.99,
        stock=10,
        category="test_category"
    )
    create_product(db, product_data)
    
    products = get_products(db, category="test_category")
    assert len(products) >= 1
    assert all(p.category == "test_category" for p in products)

def test_update_product(db: Session, test_product: Product):
    update_data = ProductUpdate(
        name="Updated Product",
        price=149.99,
        stock=20
    )
    
    updated_product = update_product(db, test_product.id, update_data)
    assert updated_product is not None
    assert updated_product.id == test_product.id
    assert updated_product.name == update_data.name
    assert updated_product.price == update_data.price
    assert updated_product.stock == update_data.stock
    assert updated_product.description == test_product.description  # Não foi alterado
    assert updated_product.category == test_product.category  # Não foi alterado

def test_update_product_not_found(db: Session):
    update_data = ProductUpdate(
        name="Updated Product"
    )
    
    updated_product = update_product(db, 999, update_data)
    assert updated_product is None

def test_delete_product(db: Session, test_product: Product):
    deleted_product = delete_product(db, test_product.id)
    assert deleted_product is not None
    assert deleted_product.id == test_product.id
    
    # Verifica se o produto foi realmente deletado
    product = get_product(db, test_product.id)
    assert product is None

def test_delete_product_not_found(db: Session):
    deleted_product = delete_product(db, 999)
    assert deleted_product is None 