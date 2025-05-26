from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate

def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()

def get_orders(
    db: Session,
    user_id: int,
    page: int = 1,
    size: int = 100,
    status: Optional[OrderStatus] = None
) -> Tuple[List[Order], int]:
    """
    Retorna uma tupla contendo a lista de pedidos e o total de registros.
    """
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    # Conta o total de registros
    total = query.count()
    
    # Aplica paginação
    skip = (page - 1) * size
    orders = query.offset(skip).limit(size).all()
    
    return orders, total

def create_order(db: Session, *, user_id: int, obj_in: OrderCreate) -> Order:
    # Cria o pedido
    db_order = Order(
        user_id=user_id,
        status=obj_in.status,
        total_amount=0.0
    )
    db.add(db_order)
    db.flush()  # Para obter o ID do pedido
    
    total_amount = 0.0
    
    # Adiciona os itens do pedido
    for item in obj_in.items:
        # Busca o produto
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Produto {item.product_id} não encontrado")
        
        # Verifica se há estoque suficiente
        if product.stock < item.quantity:
            raise ValueError(f"Estoque insuficiente para o produto {product.name}")
        
        # Calcula os preços
        unit_price = product.price
        total_price = unit_price * item.quantity
        total_amount += total_price
        
        # Cria o item do pedido
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        db.add(db_item)
        
        # Atualiza o estoque
        product.stock -= item.quantity
    
    # Atualiza o valor total do pedido
    db_order.total_amount = total_amount
    
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(
    db: Session,
    *,
    db_obj: Order,
    obj_in: OrderUpdate
) -> Order:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_order(db: Session, *, order_id: int) -> Optional[Order]:
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        # Restaura o estoque dos produtos
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        
        db.delete(order)
        db.commit()
    return order 