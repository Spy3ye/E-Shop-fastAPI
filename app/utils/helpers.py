# app/utils/helpers.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Type, TypeVar, Generic, List, Optional
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel
import math

from app.config import settings

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
# Generic type for Pydantic schemas
SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

def paginate(
    query,
    page: int = 1,
    page_size: Optional[int] = None,
):
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: The SQLAlchemy query to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dict containing paginated items and pagination metadata
    """
    if not page_size:
        page_size = settings.PAGINATION_PAGE_SIZE
        
    # Ensure positive page number
    if page < 1:
        page = 1
        
    # Count total items
    total = query.count()
    
    # Calculate pagination metadata
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Adjust page if out of range
    if page > pages:
        page = pages
        
    # Apply pagination
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }

def get_object_or_404(
    db: Session, model: Type[ModelType], id: int
) -> ModelType:
    """
    Get an object by ID or raise a 404 error.
    
    Args:
        db: Database session
        model: SQLAlchemy model
        id: Object ID
        
    Returns:
        The found object
        
    Raises:
        HTTPException with 404 status if not found
    """
    obj = db.query(model).filter(model.id == id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found"
        )
    return obj