from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from app.models.models import Book, Content, Glossary, PageMap, TableOfContents, GlossaryEmbedding


class BookService:
    @staticmethod
    def get_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get list of books with pagination"""
        return db.query(Book).offset(skip).limit(limit).all()

    @staticmethod
    def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
        """Get a specific book by book_id"""
        return db.query(Book).filter(Book.book_id == book_id).first()

    @staticmethod
    def get_books_count(db: Session) -> int:
        """Get total count of books"""
        return db.query(func.count(Book.book_id)).scalar()


class ContentService:
    @staticmethod
    def get_page_content(db: Session, book_id: int, page_number: int) -> Optional[Content]:
        """Get page content by book_id and page_number"""
        return db.query(Content).filter(
            Content.book_id == book_id,
            Content.page_number == page_number
        ).first()

    @staticmethod
    def get_book_content(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[Content]:
        """Get all content for a book with pagination"""
        return db.query(Content).filter(
            Content.book_id == book_id
        ).order_by(Content.page_number).offset(skip).limit(limit).all()

    @staticmethod
    def get_book_content_count(db: Session, book_id: int) -> int:
        """Get total count of content pages for a book"""
        return db.query(func.count(Content.content_id)).filter(
            Content.book_id == book_id
        ).scalar()


class GlossaryService:
    @staticmethod
    def get_book_glossary_terms(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all glossary terms for a book with book name (joined with book table)"""
        return db.query(
            Glossary.glossary_id,
            Glossary.book_id,
            Glossary.term,
            Glossary.description,
            Glossary.created_at,
            Glossary.updated_at,
            Book.original_book_title.label('book_name')
        ).join(Book, Glossary.book_id == Book.book_id).filter(
            Glossary.book_id == book_id
        ).order_by(Glossary.term).offset(skip).limit(limit).all()

    @staticmethod
    def get_glossary_term_by_name(db: Session, book_id: int, term: str) -> Optional[dict]:
        """Get specific glossary term with book name"""
        return db.query(
            Glossary.glossary_id,
            Glossary.book_id,
            Glossary.term,
            Glossary.description,
            Glossary.created_at,
            Glossary.updated_at,
            Book.original_book_title.label('book_name')
        ).join(Book, Glossary.book_id == Book.book_id).filter(
            Glossary.book_id == book_id,
            Glossary.term.ilike(f"%{term}%")
        ).first()

    @staticmethod
    def get_book_glossary_count(db: Session, book_id: int) -> int:
        """Get total count of glossary terms for a book"""
        return db.query(func.count(Glossary.glossary_id)).filter(
            Glossary.book_id == book_id
        ).scalar()

    @staticmethod
    def search_terms_across_books(db: Session, term: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Search for a term across all books"""
        return db.query(
            Glossary.glossary_id,
            Glossary.book_id,
            Glossary.term,
            Glossary.description,
            Glossary.created_at,
            Glossary.updated_at,
            Book.original_book_title.label('book_name')
        ).join(Book, Glossary.book_id == Book.book_id).filter(
            Glossary.term.ilike(f"%{term}%")
        ).order_by(Book.original_book_title, Glossary.term).offset(skip).limit(limit).all()

    @staticmethod
    def text_search_all_books(
        db: Session,
        query: str,
        limit: int = 5,
        book_id: Optional[int] = None
    ) -> List[dict]:
        """
        Fallback text search across all books using ILIKE on term and description.

        Args:
            db: Database session
            query: Search query text
            limit: Maximum number of results
            book_id: Optional book_id to filter results

        Returns:
            List of dictionaries with term, description, book_name, book_id
        """
        # Build base query
        base_query = db.query(
            Glossary.glossary_id,
            Glossary.book_id,
            Glossary.term,
            Glossary.description,
            Book.original_book_title.label('book_name')
        ).join(Book, Glossary.book_id == Book.book_id)

        # Apply book_id filter if provided
        if book_id is not None:
            base_query = base_query.filter(Glossary.book_id == book_id)

        # Search in both term and description
        search_pattern = f"%{query}%"
        results = base_query.filter(
            (Glossary.term.ilike(search_pattern)) |
            (Glossary.description.ilike(search_pattern))
        ).order_by(Glossary.term).limit(limit).all()

        return results


class PageMapService:
    @staticmethod
    def get_core_pages(db: Session, book_id: int) -> List[PageMap]:
        """Get all page numbers and labels for Core pages of a book"""
        return db.query(PageMap).filter(
            PageMap.book_id == book_id,
            PageMap.page_type == 'Core'
        ).order_by(PageMap.page_number).all()

    @staticmethod
    def get_primary_pages(db: Session, book_id: int) -> List[PageMap]:
        """Get all page numbers and labels for Primary pages of a book (fallback if no Core pages)"""
        return db.query(PageMap).filter(
            PageMap.book_id == book_id,
            PageMap.page_type == 'Primary'
        ).order_by(PageMap.page_number).all()

    @staticmethod
    def get_full_page_map(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[PageMap]:
        """Get full page map for a book with pagination"""
        return db.query(PageMap).filter(
            PageMap.book_id == book_id
        ).order_by(PageMap.page_number).offset(skip).limit(limit).all()

    @staticmethod
    def get_page_map_count(db: Session, book_id: int) -> int:
        """Get total count of page map entries for a book"""
        return db.query(func.count(PageMap.page_map_id)).filter(
            PageMap.book_id == book_id
        ).scalar()

    @staticmethod
    def get_core_pages_count(db: Session, book_id: int) -> int:
        """Get count of Core pages for a book"""
        return db.query(func.count(PageMap.page_map_id)).filter(
            PageMap.book_id == book_id,
            PageMap.page_type == 'Core'
        ).scalar()

    @staticmethod
    def get_all_pages(db: Session, book_id: int) -> List[PageMap]:
        """Get all pages for a book without pagination"""
        return db.query(PageMap).filter(
            PageMap.book_id == book_id
        ).order_by(PageMap.page_number).all()


class TocService:
    @staticmethod
    def get_book_toc(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[TableOfContents]:
        """Get table of contents for a book with pagination"""
        return db.query(TableOfContents).filter(
            TableOfContents.book_id == book_id
        ).order_by(TableOfContents.toc_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_book_toc_count(db: Session, book_id: int) -> int:
        """Get total count of table of contents entries for a book"""
        return db.query(func.count(TableOfContents.toc_id)).filter(
            TableOfContents.book_id == book_id
        ).scalar()

    @staticmethod
    def get_full_book_toc(db: Session, book_id: int) -> List[TableOfContents]:
        """Get complete table of contents for a book without pagination"""
        return db.query(TableOfContents).filter(
            TableOfContents.book_id == book_id
        ).order_by(TableOfContents.toc_id).all()


class GlossaryEmbeddingService:
    @staticmethod
    def semantic_search(
        db: Session,
        query_embedding: List[float],
        limit: int = 10,
        book_id: Optional[int] = None,
        similarity_threshold: float = 0.5
    ) -> List[dict]:
        """
        Perform semantic search on glossary embeddings using pgvector cosine similarity.

        Args:
            db: Database session
            query_embedding: The embedding vector for the search query (list of floats)
            limit: Maximum number of results to return
            book_id: Optional book_id to filter results
            similarity_threshold: Minimum similarity score (0-1) for results

        Returns:
            List of dictionaries containing glossary terms with similarity scores
        """
        # Convert Python list to PostgreSQL array format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # Build the base query with cosine similarity
        # Note: pgvector's <=> operator returns distance (0 = identical, 2 = opposite)
        # We convert to similarity score: similarity = 1 - (distance / 2)
        query = db.query(
            GlossaryEmbedding.glossary_id,
            GlossaryEmbedding.book_id,
            GlossaryEmbedding.term,
            Glossary.description,
            Book.original_book_title.label('book_name'),
            GlossaryEmbedding.created_at,
            GlossaryEmbedding.updated_at,
            (1 - (GlossaryEmbedding.embedding.cosine_distance(embedding_str)) / 2).label('similarity')
        ).join(
            Glossary, GlossaryEmbedding.glossary_id == Glossary.glossary_id
        ).join(
            Book, GlossaryEmbedding.book_id == Book.book_id
        )

        # Apply book_id filter if provided
        if book_id is not None:
            query = query.filter(GlossaryEmbedding.book_id == book_id)

        # Filter by similarity threshold and order by similarity (descending)
        query = query.having(
            text(f"(1 - (embedding <=> '{embedding_str}') / 2) >= {similarity_threshold}")
        ).order_by(
            text('similarity DESC')
        ).limit(limit)

        return query.all()

    @staticmethod
    def get_embedding_by_glossary_id(db: Session, glossary_id: int) -> Optional[GlossaryEmbedding]:
        """Get glossary embedding by glossary_id"""
        return db.query(GlossaryEmbedding).filter(
            GlossaryEmbedding.glossary_id == glossary_id
        ).first()

    @staticmethod
    def get_embeddings_by_book(db: Session, book_id: int, skip: int = 0, limit: int = 100) -> List[GlossaryEmbedding]:
        """Get all glossary embeddings for a specific book"""
        return db.query(GlossaryEmbedding).filter(
            GlossaryEmbedding.book_id == book_id
        ).order_by(GlossaryEmbedding.term).offset(skip).limit(limit).all()

    @staticmethod
    def get_embeddings_count(db: Session, book_id: Optional[int] = None) -> int:
        """Get total count of glossary embeddings, optionally filtered by book_id"""
        query = db.query(func.count(GlossaryEmbedding.glossary_id))
        if book_id is not None:
            query = query.filter(GlossaryEmbedding.book_id == book_id)
        return query.scalar()

    @staticmethod
    def semantic_search_all_books(
        db: Session,
        query_embedding: List[float],
        limit: int = 5,
        book_id: Optional[int] = None,
        similarity_threshold: float = 0.5
    ) -> List[dict]:
        """
        Perform semantic search across all books (or filtered by book_id).

        Args:
            db: Database session
            query_embedding: The embedding vector for the search query
            limit: Maximum number of results to return
            book_id: Optional book_id to filter results
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of dictionaries with term, description, book_name, book_id
        """
        # Convert Python list to PostgreSQL array format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # Build query with cosine similarity
        # We use raw SQL to properly handle pgvector operations
        # Similarity = 1 - (distance / 2) where distance is cosine distance
        sql = text(f"""
            SELECT
                ge.glossary_id,
                ge.book_id,
                ge.term,
                g.description,
                b.original_book_title as book_name,
                (1 - (ge.embedding <=> '{embedding_str}'::vector) / 2) as similarity
            FROM glossary_embeddings ge
            JOIN glossary g ON ge.glossary_id = g.glossary_id
            JOIN book b ON ge.book_id = b.book_id
            WHERE (1 - (ge.embedding <=> '{embedding_str}'::vector) / 2) >= {similarity_threshold}
                {f"AND ge.book_id = {book_id}" if book_id is not None else ""}
            ORDER BY similarity DESC
            LIMIT {limit}
        """)

        result = db.execute(sql)
        return result.fetchall()