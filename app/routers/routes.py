from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.services import BookService, ContentService, GlossaryService, PageMapService, TocService
from app.schemas.schemas import Book, BookListResponse, Content, ContentResponse, ContentListResponse, GlossaryWithBook, GlossaryListResponse, GlossaryTermResponse, CorePageInfo, CorePagesResponse, PageMap, FullPageMapResponse, TableOfContents, TocResponse, TocListResponse

router = APIRouter()


@router.get("/books", response_model=BookListResponse)
def get_books(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get list of all books with pagination"""
    skip = (page - 1) * size
    books = BookService.get_books(db, skip=skip, limit=size)
    total = BookService.get_books_count(db)

    return BookListResponse(
        books=books,
        total=total,
        page=page,
        size=size
    )


@router.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by book_id"""
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/books/{book_id}/content/{page_number}", response_model=ContentResponse)
def get_page_content(book_id: int, page_number: int, db: Session = Depends(get_db)):
    """Get page content by book_id and page_number"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get the content for the specific page
    content = ContentService.get_page_content(db, book_id, page_number)
    if not content:
        return ContentResponse(
            content=None,
            message=f"No content found for book {book_id}, page {page_number}"
        )

    return ContentResponse(content=content)


@router.get("/books/{book_id}/content", response_model=ContentListResponse)
def get_book_content(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get all content for a book with pagination"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    skip = (page - 1) * size
    content_list = ContentService.get_book_content(db, book_id, skip=skip, limit=size)
    total = ContentService.get_book_content_count(db, book_id)

    return ContentListResponse(
        content=content_list,
        total=total,
        page=page,
        size=size,
        book_id=book_id
    )


@router.get("/books/{book_id}/glossary", response_model=GlossaryListResponse)
def get_book_glossary(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get all glossary terms for a book with pagination"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    skip = (page - 1) * size
    glossary_results = GlossaryService.get_book_glossary_terms(db, book_id, skip=skip, limit=size)
    total = GlossaryService.get_book_glossary_count(db, book_id)

    # Convert query results to GlossaryWithBook objects
    glossary_terms = []
    for result in glossary_results:
        glossary_terms.append(GlossaryWithBook(
            glossary_id=result.glossary_id,
            book_id=result.book_id,
            term=result.term,
            description=result.description,
            created_at=result.created_at,
            updated_at=result.updated_at,
            book_name=result.book_name
        ))

    return GlossaryListResponse(
        glossary_terms=glossary_terms,
        total=total,
        page=page,
        size=size,
        book_id=book_id
    )


@router.get("/books/{book_id}/glossary/{term}", response_model=GlossaryTermResponse)
def get_glossary_term(book_id: int, term: str, db: Session = Depends(get_db)):
    """Get description and book name for a specific term in a book"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get the glossary term
    result = GlossaryService.get_glossary_term_by_name(db, book_id, term)
    if not result:
        return GlossaryTermResponse(
            term=None,
            message=f"No glossary term matching '{term}' found in book {book_id}"
        )

    glossary_term = GlossaryWithBook(
        glossary_id=result.glossary_id,
        book_id=result.book_id,
        term=result.term,
        description=result.description,
        created_at=result.created_at,
        updated_at=result.updated_at,
        book_name=result.book_name
    )

    return GlossaryTermResponse(term=glossary_term)


@router.get("/glossary/search", response_model=dict)
def search_glossary_terms(
    term: str = Query(..., description="Term to search for across all books"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Search for a term across all books"""
    skip = (page - 1) * size
    search_results = GlossaryService.search_terms_across_books(db, term, skip=skip, limit=size)

    # Convert query results to GlossaryWithBook objects
    glossary_terms = []
    for result in search_results:
        glossary_terms.append(GlossaryWithBook(
            glossary_id=result.glossary_id,
            book_id=result.book_id,
            term=result.term,
            description=result.description,
            created_at=result.created_at,
            updated_at=result.updated_at,
            book_name=result.book_name
        ))

    return {
        "glossary_terms": glossary_terms,
        "total": len(glossary_terms),
        "page": page,
        "size": size,
        "search_term": term
    }


@router.get("/books/{book_id}/pages/core", response_model=CorePagesResponse)
def get_core_pages(book_id: int, db: Session = Depends(get_db)):
    """Get all page numbers and labels for Core pages of a book"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Try to get Core pages first
    core_pages = PageMapService.get_core_pages(db, book_id)

    # If no Core pages found, try Primary pages as fallback
    if not core_pages:
        core_pages = PageMapService.get_primary_pages(db, book_id)

    # Convert to CorePageInfo objects
    pages = []
    for page_map in core_pages:
        pages.append(CorePageInfo(
            page_number=page_map.page_number,
            page_label=page_map.page_label
        ))

    return CorePagesResponse(
        pages=pages,
        total=len(pages),
        book_id=book_id
    )


@router.get("/books/{book_id}/pages", response_model=FullPageMapResponse)
def get_full_page_map(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get full page map for a book with pagination"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    skip = (page - 1) * size
    page_maps = PageMapService.get_full_page_map(db, book_id, skip=skip, limit=size)
    total = PageMapService.get_page_map_count(db, book_id)

    return FullPageMapResponse(
        page_maps=page_maps,
        total=total,
        page=page,
        size=size,
        book_id=book_id
    )


@router.get("/books/{book_id}/toc", response_model=TocResponse)
def get_book_toc(book_id: int, db: Session = Depends(get_db)):
    """Get table of contents for a book"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get the complete table of contents for the book
    toc_entries = TocService.get_full_book_toc(db, book_id)
    total = len(toc_entries)

    return TocResponse(
        table_of_contents=toc_entries,
        total=total,
        book_id=book_id
    )


@router.get("/books/{book_id}/toc/paginated", response_model=TocListResponse)
def get_book_toc_paginated(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=200, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get table of contents for a book with pagination"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    skip = (page - 1) * size
    toc_entries = TocService.get_book_toc(db, book_id, skip=skip, limit=size)
    total = TocService.get_book_toc_count(db, book_id)

    return TocListResponse(
        table_of_contents=toc_entries,
        total=total,
        page=page,
        size=size,
        book_id=book_id
    )