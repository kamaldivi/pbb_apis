from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal


class BookBase(BaseModel):
    pdf_name: str = Field(..., max_length=255)
    original_book_title: str = Field(..., max_length=500)
    english_book_title: Optional[str] = Field(None, max_length=500)
    edition: Optional[str] = Field(None, max_length=100)
    number_of_pages: int
    file_size_bytes: Optional[int] = None
    original_author: Optional[str] = Field(None, max_length=255)
    commentary_author: Optional[str] = Field(None, max_length=255)
    header_height: Optional[Decimal] = None
    footer_height: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    page_label_location: Optional[str] = None
    toc_pages: Optional[Any] = None  # Will be serialized to string
    verse_pages: Optional[Any] = None  # Will be serialized to string
    glossary_pages: Optional[Any] = None  # Will be serialized to string


class Book(BookBase):
    book_id: int

    class Config:
        from_attributes = True

    @field_serializer('toc_pages', 'verse_pages', 'glossary_pages')
    def serialize_range(self, value: Any) -> Optional[str]:
        """Convert PostgreSQL Range objects to string representation"""
        if value is None:
            return None
        if hasattr(value, 'lower') and hasattr(value, 'upper'):
            # PostgreSQL Range object
            return f"{value.lower}-{value.upper}"
        return str(value)


class ContentBase(BaseModel):
    book_id: int
    page_number: int
    page_content: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Content(ContentBase):
    content_id: int

    class Config:
        from_attributes = True


class ContentResponse(BaseModel):
    content: Optional[Content]
    message: Optional[str] = None


class ContentListResponse(BaseModel):
    content: List[Content]
    total: int
    page: int
    size: int
    book_id: int


class GlossaryBase(BaseModel):
    book_id: int
    term: str
    description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Glossary(GlossaryBase):
    glossary_id: int

    class Config:
        from_attributes = True


class GlossaryWithBook(BaseModel):
    glossary_id: int
    book_id: int
    term: str
    description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    book_name: str  # From joined book table

    class Config:
        from_attributes = True


class GlossaryListResponse(BaseModel):
    glossary_terms: List[GlossaryWithBook]
    total: int
    page: int
    size: int
    book_id: int


class GlossaryTermResponse(BaseModel):
    term: Optional[GlossaryWithBook]
    message: Optional[str] = None


class PageMapBase(BaseModel):
    book_id: int
    page_number: int
    page_label: Optional[str] = None
    page_type: str
    page_header: Optional[str] = None
    created_at: Optional[datetime] = None


class PageMap(PageMapBase):
    page_map_id: int

    class Config:
        from_attributes = True


class CorePageInfo(BaseModel):
    page_number: int
    page_label: Optional[str] = None

    class Config:
        from_attributes = True


class CorePagesResponse(BaseModel):
    pages: List[CorePageInfo]
    total: int
    book_id: int


class FullPageMapResponse(BaseModel):
    page_maps: List[PageMap]
    total: int
    page: int
    size: int
    book_id: int


class BookListResponse(BaseModel):
    books: List[Book]
    total: int
    page: int
    size: int