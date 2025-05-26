from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

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

def create_product(db: Session, obj_in: ProductCreate, **kwargs) -> Product:
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

def update_product(
    db: Session,
    product_id: int,
    obj_in: ProductUpdate,
) -> Optional[Product]:
    db_obj = db.query(Product).filter(Product.id == product_id).first()
    if not db_obj:
        return None
        
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product 