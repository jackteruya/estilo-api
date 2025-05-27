from typing import List, Optional, Tuple, Union, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int) -> Optional[Product]:
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def get_products(
    db: Session,
    page: int = 1,
    size: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None
) -> Tuple[List[Product], int]:
    """
    Retorna uma tupla contendo a lista de produtos e o total de registros.
    """
    try:
        query = db.query(Product)
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search),
                    Product.description.ilike(search)
                )
            )
        
        if category:
            query = query.filter(Product.category == category)
        
        # Conta o total de registros
        total = query.count()
        
        # Aplica paginação
        skip = (page - 1) * size
        products = query.offset(skip).limit(size).all()
        
        return products, total
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def create_product(db: Session, obj_in: ProductCreate, **kwargs) -> Product:
    try:
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            stock=obj_in.stock,
            category=obj_in.category,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def update_product(
    db: Session,
    product_id: int,
    obj_in: Union[ProductUpdate, Dict[str, Any]]
) -> Product:
    """
    Atualiza um produto.
    """
    try:
        product = get_product(db, product_id=product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado."
            )
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def delete_product(db: Session, product_id: int) -> Product:
    try:
        product = get_product(db, product_id=product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        # Verifica se existem pedidos associados
        from app.models.order import OrderItem
        order_items = db.query(OrderItem).filter(OrderItem.product_id == product_id).first()
        if order_items:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir um produto que possui pedidos associados"
            )
        
        db.delete(product)
        db.commit()
        return product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 