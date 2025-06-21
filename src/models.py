from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, MetaData, text
from sqlalchemy.orm import relationship
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Schema setup
metadata = MetaData(schema='agilite')
Base = declarative_base(metadata=metadata)

class Product(Base):
    """Model for storing product information."""
    __tablename__ = "products"
    __table_args__ = {'schema': 'agilite'}
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), index=True, nullable=False)
    title = Column(String(500), nullable=True)
    price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    image_count = Column(Integer, default=0)
    first_image_url = Column(String(500), nullable=True)
    stock_status = Column(String(100), nullable=True)
    variant_count = Column(Integer, default=0)
    category = Column(String(200), nullable=True)
    processing_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with other tables
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', price={self.price})>"

class ProductImage(Base):
    """Model for storing product images."""
    __tablename__ = "product_images"
    __table_args__ = {'schema': 'agilite'}
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("agilite.products.id"), nullable=False)
    url = Column(String(500), nullable=False)
    order_index = Column(Integer, default=0)  # Image order
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with product
    product = relationship("Product", back_populates="images")
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, url='{self.url}')>"

class ProductVariant(Base):
    """Model for storing product variants."""
    __tablename__ = "product_variants"
    __table_args__ = {'schema': 'agilite'}
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("agilite.products.id"), nullable=False)
    name = Column(String(200), nullable=False)
    variant_type = Column(String(100), nullable=True)  # color, size, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with product
    product = relationship("Product", back_populates="variants")
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, name='{self.name}')>"

class ScrapingSession(Base):
    """Model for tracking scraping sessions."""
    __tablename__ = "scraping_sessions"
    __table_args__ = {'schema': 'agilite'}
    
    id = Column(Integer, primary_key=True, index=True)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    products_scraped = Column(Integer, default=0)
    products_processed = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ScrapingSession(id={self.id}, status='{self.status}', products_scraped={self.products_scraped})>"

def create_tables(engine):
    """Creates all tables in the database."""
    try:
        # First, create the schema if it doesn't exist
        with engine.connect() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS agilite"))
            connection.commit()
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully in schema 'agilite'")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def drop_tables(engine):
    """Drops all tables from the database (for development only!)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully from schema 'agilite'")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise 