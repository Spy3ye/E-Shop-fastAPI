# app/services/cart_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.utils.helpers import get_object_or_404

def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """
    Get user's cart or create if it doesn't exist.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Cart object
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        try:
            db.commit()
            db.refresh(cart)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create cart"
            )
    
    return cart

def get_cart(db: Session, user_id: int):
    """
    Get user's cart with items and calculate total price.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Cart with items and total price
    """
    # Get or create cart
    cart = get_or_create_cart(db, user_id)
    
    # Get cart items with product info
    cart_items = (
        db.query(
            CartItem,
            Product.name.label("product_name"),
            Product.price.label("product_price"),
            Product.image_url.label("product_image_url"),
        )
        .join(Product, CartItem.product_id == Product.id)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )
    
    # Process results
    items = []
    total_price = 0.0
    
    for item_data in cart_items:
        cart_item = item_data[0]
        product_name = item_data[1]
        product_price = item_data[2]
        product_image_url = item_data[3]
        
        # Calculate item total
        item_total = cart_item.quantity * product_price
        total_price += item_total
        
        # Create item dict with product info
        item_dict = {
            "id": cart_item.id,
            "cart_id": cart_item.cart_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "added_at": cart_item.added_at,
            "product_name": product_name,
            "product_price": product_price,
            "product_image_url": product_image_url,
        }
        
        items.append(item_dict)
    
    # Create result dict
    result = {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total_price": total_price,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
    }
    
    return result

def add_item_to_cart(db: Session, user_id: int, item_data: CartItemCreate):
    """
    Add item to cart.
    
    Args:
        db: Database session
        user_id: User ID
        item_data: Cart item data
        
    Returns:
        Updated cart
    """
    # Get or create cart
    cart = get_or_create_cart(db, user_id)
    
    # Check if product exists and has enough stock
    product = get_object_or_404(db, Product, item_data.product_id)
    
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )
    
    if product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock"
        )
    
    # Check if item already in cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id
        )
        .first()
    )
    
    if cart_item:
        # Update quantity
        cart_item.quantity += item_data.quantity
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        db.add(cart_item)
    
    try:
        db.commit()
        db.refresh(cart)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add item to cart"
        )
    
    # Return updated cart
    return get_cart(db, user_id)

def update_cart_item(db: Session, user_id: int, item_id: int, item_data: CartItemUpdate):
    """
    Update cart item quantity.
    
    Args:
        db: Database session
        user_id: User ID
        item_id: Cart item ID
        item_data: Cart item update data
        
    Returns:
        Updated cart
    """
    # Get cart
    cart = get_or_create_cart(db, user_id)
    
    # Get cart item
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
        .first()
    )
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check if product has enough stock
    product = get_object_or_404(db, Product, cart_item.product_id)
    
    if product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock"
        )
    
    # Update quantity
    cart_item.quantity = item_data.quantity
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update cart item"
        )
    
    # Return updated cart
    return get_cart(db, user_id)

def remove_cart_item(db: Session, user_id: int, item_id: int):
    """
    Remove item from cart.
    
    Args:
        db: Database session
        user_id: User ID
        item_id: Cart item ID
        
    Returns:
        Updated cart
    """
    # Get cart
    cart = get_or_create_cart(db, user_id)
    
    # Get cart item
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
        .first()
    )
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Delete cart item
    db.delete(cart_item)
    db.commit()
    
    # Return updated cart
    return get_cart(db, user_id)

def clear_cart(db: Session, user_id: int):
    """
    Clear all items from cart.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Empty cart
    """
    # Get cart
    cart = get_or_create_cart(db, user_id)
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    
    # Return empty cart
    return get_cart(db, user_id)