# app/services/order_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.cart_service import get_cart, clear_cart
from app.services.product_service import update_stock
from app.utils.helpers import paginate, get_object_or_404

def create_order(db: Session, user_id: int, order_data: OrderCreate) -> Order:
    """
    Create a new order from cart or directly.
    
    Args:
        db: Database session
        user_id: User ID
        order_data: Order data
        
    Returns:
        Created order
    """
    # Calculate total amount and validate items
    total_amount = 0.0
    order_items = []
    
    for item_data in order_data.items:
        # Get product
        product = get_object_or_404(db, Product, item_data.product_id)
        
        # Check if product is active
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} is not available"
            )
        
        # Check if enough stock
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}"
            )
        
        # Calculate item total
        item_total = item_data.unit_price * item_data.quantity
        total_amount += item_total
        
        # Create order item
        order_items.append({
            "product_id": item_data.product_id,
            "quantity": item_data.quantity,
            "unit_price": item_data.unit_price
        })
        
        # Update product stock
        update_stock(db, product.id, -item_data.quantity)
    
    # Create order
    order = Order(
        user_id=user_id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        payment_method=order_data.payment_method
    )
    
    db.add(order)
    
    try:
        db.commit()
        db.refresh(order)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create order"
        )
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create order items"
        )
    
    # Clear cart if order was successful
    clear_cart(db, user_id)
    
    return get_order(db, order.id)

def create_order_from_cart(db: Session, user_id: int, shipping_address: str, payment_method: str) -> Order:
    """
    Create an order from user's cart.
    
    Args:
        db: Database session
        user_id: User ID
        shipping_address: Shipping address
        payment_method: Payment method
        
    Returns:
        Created order
    """
    # Get cart
    cart = get_cart(db, user_id)
    
    if not cart["items"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Prepare order data
    order_items = []
    
    for item in cart["items"]:
        order_items.append({
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "unit_price": item["product_price"]
        })
    
    # Create order data object
    order_data = OrderCreate(
        shipping_address=shipping_address,
        payment_method=payment_method,
        items=[OrderItemCreate(**item) for item in order_items]
    )
    
    # Create order
    return create_order(db, user_id, order_data)

def get_order(db: Session, order_id: int) -> Order:
    """Get order by ID with items."""
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

def get_user_orders(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: Optional[int] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get user orders with filtering and pagination.
    
    Args:
        db: Database session
        user_id: User ID
        page: Page number
        page_size: Items per page
        status: Filter by order status
        
    Returns:
        Paginated orders
    """
    query = db.query(Order).filter(Order.user_id == user_id)
    
    # Apply filters
    if status:
        try:
            order_status = OrderStatus(status)
            query = query.filter(Order.status == order_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid order status: {status}"
            )
    
    # Order by latest
    query = query.order_by(Order.created_at.desc())
    
    # Paginate results
    return paginate(query, page, page_size)

def get_all_orders(
    db: Session,
    page: int = 1,
    page_size: Optional[int] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get all orders with filtering and pagination (admin only).
    
    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        status: Filter by order status
        user_id: Filter by user ID
        
    Returns:
        Paginated orders
    """
    query = db.query(Order)
    
    # Apply filters
    if status:
        try:
            order_status = OrderStatus(status)
            query = query.filter(Order.status == order_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid order status: {status}"
            )
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    # Order by latest
    query = query.order_by(Order.created_at.desc())
    
    # Paginate results
    return paginate(query, page, page_size)

def update_order_status(db: Session, order_id: int, order_data: OrderUpdate) -> Order:
    """
    Update order status and details.
    
    Args:
        db: Database session
        order_id: Order ID
        order_data: Order update data
        
    Returns:
        Updated order
    """
    order = get_object_or_404(db, Order, order_id)
    
    update_data = order_data.dict(exclude_unset=True)
    
    # Update order attributes
    for key, value in update_data.items():
        setattr(order, key, value)
    
    # If cancelling order, restore product stock
    if order_data.status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        # Get order items
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        # Restore stock for each item
        for item in order_items:
            update_stock(db, item.product_id, item.quantity)
    
    try:
        db.commit()
        db.refresh(order)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update order"
        )
    
    return order

def cancel_order(db: Session, order_id: int) -> Order:
    """
    Cancel an order.
    
    Args:
        db: Database session
        order_id: Order ID
        
    Returns:
        Updated order
    """
    order = get_object_or_404(db, Order, order_id)
    
    # Check if order can be cancelled
    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status.value}"
        )
    
    # Update order status
    order_data = OrderUpdate(status=OrderStatus.CANCELLED)
    
    return update_order_status(db, order_id, order_data)