# app/services/product_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any

from app.models.product import Product, Category
from app.schemas.product import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate
from app.utils.helpers import paginate, get_object_or_404

# Category services
def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """Create a new category."""
    # Check if category with same name exists
    if db.query(Category).filter(Category.name == category_data.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = Category(**category_data.dict())
    
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create category"
        )
    
    return category

def get_category(db: Session, category_id: int) -> Category:
    """Get a category by ID."""
    return get_object_or_404(db, Category, category_id)

def get_categories(db: Session) -> List[Category]:
    """Get all categories."""
    return db.query(Category).all()

def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Category:
    """Update a category."""
    category = get_object_or_404(db, Category, category_id)
    
    update_data = category_data.dict(exclude_unset=True)
    
    # Check if updating to an existing name
    if update_data.get("name") and update_data["name"] != category.name:
        if db.query(Category).filter(Category.name == update_data["name"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    # Update category attributes
    for key, value in update_data.items():
        setattr(category, key, value)
    
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update category"
        )
    
    return category

def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category."""
    category = get_object_or_404(db, Category, category_id)
    
    # Check if category has products
    if db.query(Product).filter(Product.category_id == category_id).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with existing products"
        )
    
    db.delete(category)
    db.commit()
    
    return True

# Product services
def create_product(db: Session, product_data: ProductCreate) -> Product:
    """Create a new product."""
    # Check if category exists
    get_object_or_404(db, Category, product_data.category_id)
    
    product = Product(**product_data.dict())
    
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create product"
        )
    
    return product

def get_product(db: Session, product_id: int) -> Product:
    """Get a product by ID."""
    return get_object_or_404(db, Product, product_id)

def get_products(
    db: Session,
    page: int = 1,
    page_size: Optional[int] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """Get products with filtering and pagination."""
    query = db.query(Product)
    
    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    # Order by latest
    query = query.order_by(Product.created_at.desc())
    
    # Paginate results
    return paginate(query, page, page_size)

def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
    """Update a product."""
    product = get_object_or_404(db, Product, product_id)
    
    update_data = product_data.dict(exclude_unset=True)
    
    # If updating category_id, check if category exists
    if update_data.get("category_id"):
        get_object_or_404(db, Category, update_data["category_id"])
    
    # Update product attributes
    for key, value in update_data.items():
        setattr(product, key, value)
    
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update product"
        )
    
    return product

def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product."""
    product = get_object_or_404(db, Product, product_id)
    
    db.delete(product)
    db.commit()
    
    return True

def update_stock(db: Session, product_id: int, quantity: int) -> Product:
    """Update product stock."""
    product = get_object_or_404(db, Product, product_id)
    
    # Check if have enough stock
    if product.stock_quantity + quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock"
        )
    
    product.stock_quantity += quantity
    
    db.commit()
    db.refresh(product)
    
    return product