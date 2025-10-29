from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.services import BookService, ContentService, GlossaryService, PageMapService, TocService, GlossaryEmbeddingService
from app.schemas.schemas import Book, BookListResponse, Content, ContentResponse, ContentListResponse, GlossaryWithBook, GlossaryListResponse, GlossaryTermResponse, CorePageInfo, CorePagesResponse, PageMap, FullPageMapResponse, TableOfContents, TocResponse, TocListResponse, SemanticSearchRequest, SemanticSearchResponse, GlossaryEmbeddingWithSimilarity, GlossarySearchRequest, GlossarySearchResponse, GlossarySearchResult
from app.services.ollama_service import ollama_service
from app.services.content_filter import ContentFilter
import logging

logger = logging.getLogger(__name__)

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


@router.get("/books/{book_id}/glossary/embeddings")
def get_book_glossary_embeddings(
    book_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Get all glossary embeddings for a specific book (without the actual embedding vectors)"""
    # Check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    skip = (page - 1) * size
    embeddings = GlossaryEmbeddingService.get_embeddings_by_book(db, book_id, skip=skip, limit=size)
    total = GlossaryEmbeddingService.get_embeddings_count(db, book_id=book_id)

    # Return without the actual embedding vectors for performance
    results = [
        {
            "glossary_id": emb.glossary_id,
            "book_id": emb.book_id,
            "term": emb.term,
            "created_at": emb.created_at,
            "updated_at": emb.updated_at
        }
        for emb in embeddings
    ]

    return {
        "embeddings": results,
        "total": total,
        "page": page,
        "size": size,
        "book_id": book_id
    }


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


@router.post("/glossary/search", response_model=GlossarySearchResponse)
def search_glossary(
    search_request: GlossarySearchRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Search for glossary terms across all books using semantic search with text fallback.

    This endpoint uses AI-powered semantic search to find relevant glossary terms
    based on meaning and context, not just exact text matches.

    Example queries:
    - "water purification ritual" → finds "ācamana"
    - "devotional songs" → finds "bhajana", "kīrtana"
    - "spiritual teacher" → finds "guru", "ācārya"
    """
    # Sanitize the query first
    query = ContentFilter.sanitize_query(search_request.query)
    limit = search_request.limit
    book_id = search_request.book_id

    # Validate content appropriateness
    is_appropriate, reason = ContentFilter.is_appropriate(query)
    if not is_appropriate:
        logger.warning(f"Inappropriate query rejected: '{search_request.query}' - Reason: {reason}")
        raise HTTPException(
            status_code=400,
            detail="Your search query cannot be processed. Please use respectful language appropriate for sacred content."
        )

    # Validate book_id if provided
    if book_id is not None:
        book = BookService.get_book_by_id(db, book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

    results = []
    search_method_used = "semantic"

    try:
        # Try semantic search first
        logger.info(f"Attempting semantic search for: '{query}'")
        embedding = ollama_service.generate_embedding(query)

        if embedding:
            # Semantic search succeeded
            logger.info(f"Embedding generated successfully, searching database...")
            semantic_results = GlossaryEmbeddingService.semantic_search_all_books(
                db=db,
                query_embedding=embedding,
                limit=limit,
                book_id=book_id,
                similarity_threshold=0.5
            )

            # Convert to response format
            for result in semantic_results:
                results.append(GlossarySearchResult(
                    term=result.term,
                    description=result.description,
                    book_name=result.book_name,
                    book_id=result.book_id
                ))

            logger.info(f"Semantic search returned {len(results)} results")
        else:
            # Embedding generation failed, use fallback
            logger.warning("Embedding generation failed, using text search fallback")
            search_method_used = "text"

    except Exception as e:
        logger.error(f"Semantic search error: {str(e)}, falling back to text search")
        search_method_used = "text"

    # Fallback to text search if semantic search returned no results or failed
    if not results:
        logger.info(f"Using text search fallback for: '{query}'")
        text_results = GlossaryService.text_search_all_books(
            db=db,
            query=query,
            limit=limit,
            book_id=book_id
        )

        for result in text_results:
            results.append(GlossarySearchResult(
                term=result.term,
                description=result.description,
                book_name=result.book_name,
                book_id=result.book_id
            ))

        logger.info(f"Text search returned {len(results)} results")

    # Prepare response message
    message = None
    if not results:
        message = "No matching terms found. Try different words or check spelling."

    return GlossarySearchResponse(
        results=results,
        total_found=len(results),
        query=query,
        message=message
    )


@router.get("/glossary/search-legacy", response_model=dict)
def search_glossary_terms_legacy(
    term: str = Query(..., description="Term to search for across all books"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """Legacy endpoint: Search for a term across all books (text-based only)"""
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
    db: Session = Depends(get_db)
):
    """Get full page map for a book (all pages, no pagination)"""
    # First check if book exists
    book = BookService.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get all pages without pagination
    page_maps = PageMapService.get_all_pages(db, book_id)
    total = len(page_maps)

    return FullPageMapResponse(
        page_maps=page_maps,
        total=total,
        page=1,
        size=total,
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


@router.post("/glossary/semantic-search", response_model=SemanticSearchResponse)
def semantic_search_glossary(
    search_request: SemanticSearchRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search on glossary terms using vector embeddings.

    This endpoint requires a pre-computed embedding vector for the query.
    The embedding should be a 1024-dimensional vector matching the model used to create glossary embeddings.

    Example request body:
    {
        "query": "purification ritual",
        "query_embedding": [0.123, -0.456, ...],  // 1024 dimensions
        "limit": 10,
        "book_id": 2,  // Optional
        "similarity_threshold": 0.7
    }
    """
    # Note: This endpoint expects the client to provide the embedding vector
    # In a production scenario, you would integrate with an embedding service
    # For now, this is a placeholder that would need the embedding to be passed

    raise HTTPException(
        status_code=501,
        detail="This endpoint requires integration with an embedding service. Please use /glossary/semantic-search-with-text instead or provide query_embedding in the request."
    )


@router.get("/glossary/embeddings/stats")
def get_embeddings_stats(db: Session = Depends(get_db)):
    """Get statistics about glossary embeddings"""
    total_embeddings = GlossaryEmbeddingService.get_embeddings_count(db)

    # Get count per book
    books = BookService.get_books(db, skip=0, limit=1000)
    book_stats = []
    for book in books:
        count = GlossaryEmbeddingService.get_embeddings_count(db, book_id=book.book_id)
        if count > 0:
            book_stats.append({
                "book_id": book.book_id,
                "book_name": book.original_book_title,
                "embedding_count": count
            })

    return {
        "total_embeddings": total_embeddings,
        "books_with_embeddings": len(book_stats),
        "book_breakdown": book_stats
    }