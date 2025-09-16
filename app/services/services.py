from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.models import Book, Content, Glossary, PageMap


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