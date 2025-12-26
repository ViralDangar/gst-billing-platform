"""
Pagination utilities for list endpoints.

This module provides common pagination functionality for all API endpoints
that return lists of resources.
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel
from math import ceil

# Generic type for any model
T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Query parameters for pagination.

    Attributes:
        page: Current page number (1-indexed)
        page_size: Number of items per page
    """
    page: int = 1
    page_size: int = 10

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Attributes:
        items: List of items for the current page
        total: Total number of items across all pages
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        """Pydantic configuration."""
        from_attributes = True


def paginate(query, page: int = 1, page_size: int = 10):
    """
    Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        tuple: (paginated_items, total_count)

    Example:
        >>> query = db.query(Product)
        >>> items, total = paginate(query, page=1, page_size=10)
    """
    # Ensure valid page and page_size
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100  # Max limit to prevent excessive data retrieval

    # Get total count
    total = query.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated items
    items = query.offset(offset).limit(page_size).all()

    return items, total
