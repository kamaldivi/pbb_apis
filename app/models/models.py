from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import INT4RANGE
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class Book(Base):
    __tablename__ = "book"

    book_id = Column(Integer, primary_key=True, index=True)
    pdf_name = Column(String(255), nullable=False, unique=True)
    original_book_title = Column(String(500), nullable=False)
    english_book_title = Column(String(500))
    edition = Column(String(100))
    number_of_pages = Column(Integer, nullable=False)
    file_size_bytes = Column(BigInteger)
    original_author = Column(String(255))
    commentary_author = Column(String(255))
    header_height = Column(Numeric(5, 2))
    footer_height = Column(Numeric(5, 2))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    page_label_location = Column(String)
    toc_pages = Column(INT4RANGE)
    verse_pages = Column(INT4RANGE)
    glossary_pages = Column(INT4RANGE)
    book_summary = Column(Text)


class Content(Base):
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.book_id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    page_content = Column(Text)
    ai_page_content = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    book = relationship("Book", back_populates="contents")


class Glossary(Base):
    __tablename__ = "glossary"

    glossary_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.book_id"), nullable=False, index=True)
    term = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    book = relationship("Book", back_populates="glossary_terms")


class PageMap(Base):
    __tablename__ = "page_map"

    page_map_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.book_id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    page_label = Column(String(100))
    page_type = Column(String(50), nullable=False, default='Primary')
    page_header = Column(String(255))
    created_at = Column(DateTime)

    book = relationship("Book", back_populates="page_maps")


class TableOfContents(Base):
    __tablename__ = "table_of_contents"

    toc_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.book_id"), nullable=False, index=True)
    parent_toc_id = Column(Integer)
    toc_level = Column(Integer)
    toc_label = Column(String(500))
    page_label = Column(String(100))
    page_number = Column(Integer)

    book = relationship("Book", back_populates="table_of_contents")


class GlossaryEmbedding(Base):
    __tablename__ = "glossary_embeddings"

    glossary_id = Column(Integer, ForeignKey("glossary.glossary_id", ondelete="CASCADE"), primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.book_id", ondelete="CASCADE"), nullable=False, index=True)
    term = Column(String(255), nullable=False)
    embedding = Column(Vector(1024), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    book = relationship("Book")
    glossary = relationship("Glossary")


Book.contents = relationship("Content", back_populates="book")
Book.glossary_terms = relationship("Glossary", back_populates="book")
Book.page_maps = relationship("PageMap", back_populates="book")
Book.table_of_contents = relationship("TableOfContents", back_populates="book")