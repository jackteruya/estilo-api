import pytest
from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate
from app.schemas.product import Product
from app.schemas.user import User
from app.services import order as order_service


def test_create_order(db: Session, test_user: User, test_product: Product):
    # Cria um pedido
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=2
            )
        ]
    )
    
    order = order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    assert order.user_id == test_user.id
    assert order.status == OrderStatus.PENDING
    assert order.total_amount == test_product.price * 2
    assert len(order.items) == 1
    assert order.items[0].product_id == test_product.id
    assert order.items[0].quantity == 2
    assert order.items[0].unit_price == test_product.price
    assert order.items[0].total_price == test_product.price * 2

def test_create_order_insufficient_stock(db: Session, test_user: User, test_product: Product):
    # Tenta criar um pedido com quantidade maior que o estoque
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=test_product.stock + 1
            )
        ]
    )
    
    with pytest.raises(ValueError) as exc_info:
        order_service.create_order(
            db=db,
            user_id=test_user.id,
            obj_in=order_in
        )
    
    assert "Estoque insuficiente" in str(exc_info.value)

def test_get_order(db: Session, test_user: User, test_product: Product):
    # Cria um pedido
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=1
            )
        ]
    )
    
    created_order = order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    # Busca o pedido
    order = order_service.get_order(db, order_id=created_order.id)
    
    assert order is not None
    assert order.id == created_order.id
    assert order.user_id == test_user.id
    assert order.status == OrderStatus.PENDING
    assert order.total_amount == test_product.price

def test_get_orders(db: Session, test_user: User, test_product: Product):
    # Cria dois pedidos
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=1
            )
        ]
    )
    
    order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    # Busca os pedidos
    orders, total = order_service.get_orders(
        db=db,
        user_id=test_user.id,
        page=1,
        size=10
    )
    
    assert total == 2
    assert len(orders) == 2
    assert all(order.user_id == test_user.id for order in orders)

def test_update_order(db: Session, test_user: User, test_product: Product):
    # Cria um pedido
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=1
            )
        ]
    )
    
    created_order = order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    # Atualiza o status do pedido
    update_data = OrderUpdate(status=OrderStatus.CONFIRMED)
    updated_order = order_service.update_order(
        db=db,
        db_obj=created_order,
        obj_in=update_data
    )
    
    assert updated_order.status == OrderStatus.CONFIRMED

def test_delete_order(db: Session, test_user: User, test_product: Product):
    # Cria um pedido
    order_in = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=test_product.id,
                quantity=1
            )
        ]
    )
    
    created_order = order_service.create_order(
        db=db,
        user_id=test_user.id,
        obj_in=order_in
    )
    
    # Deleta o pedido
    deleted_order = order_service.delete_order(
        db=db,
        order_id=created_order.id
    )
    
    assert deleted_order is not None
    assert deleted_order.id == created_order.id
    
    # Verifica se o pedido foi realmente deletado
    order = order_service.get_order(db, order_id=created_order.id)
    assert order is None
    
    # Verifica se o estoque foi restaurado
    product = db.query(Product).filter(Product.id == test_product.id).first()
    assert product.stock == test_product.stock 