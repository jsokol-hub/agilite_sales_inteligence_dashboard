import os
import json
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import SessionLocal, test_connection
from models import Product, ProductImage, ProductVariant, ScrapingSession, create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgiliteDataProcessor:
    def __init__(self):
        """
        Initializes the data processor with a database connection.
        """
        self.db = SessionLocal()
        self._ensure_database()
        
    def _ensure_database(self):
        """Checks the database connection and creates tables if necessary."""
        try:
            if not test_connection():
                raise Exception("Cannot connect to database")
            
            # Create tables if they don't exist
            from db import engine
            create_tables(engine)
            logger.info("Database connection and tables verified")
            
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def _clean_price(self, price_str: str) -> float:
        """Cleans and converts a price string to a number."""
        if not price_str:
            return 0.0
        try:
            # Remove all characters except digits, dot, and comma
            cleaned = re.sub(r'[^\d.,]', '', price_str)
            # Replace comma with a dot
            cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except Exception:
            return 0.0
    
    def _extract_category(self, title: str) -> str:
        """Extracts the category from the product title."""
        if not title:
            return 'Other'
        
        # Common categories in Hebrew
        categories = {
            'קרמון': 'Plate Carriers',
            'חגורת': 'Belts',
            'פאוץ': 'Pouches',
            'כפפות': 'Gloves',
            'כובע': 'Hats',
            'משקפי': 'Glasses',
            'פאנל': 'Panels',
            'פאץ': 'Patches',
            'שרוול': 'Sleeves',
            'ער"ד': 'Medical',
            'פלטה': 'Plates',
            'מערכת': 'Systems'
        }
        
        for heb, eng in categories.items():
            if heb in title:
                return eng
        return 'Other'
    
    def _parse_stock_status(self, status: str) -> str:
        """Parses the stock status."""
        if not status:
            return "Unknown"
        
        status_lower = status.lower()
        if "instock" in status_lower or "in stock" in status_lower:
            return "In Stock"
        elif "outofstock" in status_lower or "out of stock" in status_lower:
            return "Out of Stock"
        elif "pre-order" in status_lower:
            return "Pre-order"
        else:
            return status
    
    def _save_product_to_db(self, product_data: Dict[str, Any]) -> bool:
        """Saves a product to the database as a new record for historical data."""
        try:
            # Always create a new record to save historical data
            product = Product(
                url=product_data['url'],
                title=product_data.get('title', ''),
                price=self._clean_price(product_data.get('price', '0')),
                description=product_data.get('description', ''),
                image_count=len(product_data.get('images', [])),
                first_image_url=product_data.get('images', [''])[0] if product_data.get('images') else None,
                stock_status=self._parse_stock_status(product_data.get('stock_status', '')),
                variant_count=len(product_data.get('variants', [])),
                category=self._extract_category(product_data.get('title', '')),
                processing_timestamp=datetime.utcnow()
            )
            self.db.add(product)
            self.db.flush()  # Get the product ID
            logger.info(f"Created new historical record for product: {product_data.get('title', 'Unknown')}")
            
            # Save images
            if product_data.get('images'):
                for i, image_url in enumerate(product_data['images']):
                    if image_url:
                        product_image = ProductImage(
                            product_id=product.id,
                            url=image_url,
                            order_index=i
                        )
                        self.db.add(product_image)
            
            # Save variants
            if product_data.get('variants'):
                for variant_group in product_data['variants']:
                    variant_type = variant_group.get('type', 'Unknown')
                    for variant_name in variant_group.get('values', []):
                        if variant_name:
                            product_variant = ProductVariant(
                                product_id=product.id,
                                name=variant_name,
                                variant_type=variant_type
                            )
                            self.db.add(product_variant)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving product to database: {str(e)}")
            return False
    
    def process_data(self) -> Dict[str, Any]:
        """Main data processing method."""
        try:
            # Create a scraping session
            scraping_session = ScrapingSession()
            self.db.add(scraping_session)
            self.db.commit()
            
            logger.info(f"Started scraping session {scraping_session.id}")
            
            # Get the latest data file
            raw_data_dir = 'data/raw'
            if not os.path.exists(raw_data_dir):
                logger.warning(f"Raw data directory {raw_data_dir} does not exist")
                return {"success": False, "message": "No raw data directory"}
            
            files = [f for f in os.listdir(raw_data_dir) if f.startswith('products_') and f.endswith('.json')]
            if not files:
                logger.warning("No raw data files found")
                return {"success": False, "message": "No raw data files"}
            
            latest_file = os.path.join(raw_data_dir, sorted(files)[-1])
            logger.info(f"Processing data from {latest_file}")
            
            # Load and process data
            with open(latest_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            processed_count = 0
            failed_count = 0
            
            for product_data in raw_data:
                if self._save_product_to_db(product_data):
                    processed_count += 1
                else:
                    failed_count += 1
            
            # Update the scraping session
            scraping_session.session_end = datetime.utcnow()
            scraping_session.products_scraped = len(raw_data)
            scraping_session.products_processed = processed_count
            scraping_session.status = "completed" if failed_count == 0 else "completed_with_errors"
            if failed_count > 0:
                scraping_session.error_message = f"Failed to process {failed_count} products"
            
            self.db.commit()
            
            logger.info(f"Successfully processed {processed_count} products, failed: {failed_count}")
            
            return {
                "success": True,
                "processed_count": processed_count,
                "failed_count": failed_count,
                "session_id": scraping_session.id
            }
            
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Gets basic statistics from the processed data."""
        try:
            # Total number of products (all historical records)
            total_products = self.db.query(Product).count()
            
            # Number of unique products (by URL)
            unique_products = self.db.query(Product.url).distinct().count()
            
            # Latest data (the last record for each product)
            latest_products = self.db.query(Product).distinct(Product.url).order_by(
                Product.url, Product.processing_timestamp.desc()
            ).all()
            
            # Statistics on the latest data
            latest_prices = [p.price for p in latest_products if p.price > 0]
            avg_price = sum(latest_prices) / len(latest_prices) if latest_prices else 0
            min_price = min(latest_prices) if latest_prices else 0
            max_price = max(latest_prices) if latest_prices else 0
            
            # Products with variants (based on the latest data)
            products_with_variants = len([p for p in latest_products if p.variant_count > 0])
            
            # Average number of variants (based on the latest data)
            avg_variants = sum(p.variant_count for p in latest_products) / len(latest_products) if latest_products else 0
            
            # Products with images (based on the latest data)
            products_with_images = len([p for p in latest_products if p.image_count > 0])
            
            # Average number of images (based on the latest data)
            avg_images = sum(p.image_count for p in latest_products) / len(latest_products) if latest_products else 0
            
            # Statistics by category (based on the latest data)
            category_stats = {}
            for product in latest_products:
                if product.category:
                    category_stats[product.category] = category_stats.get(product.category, 0) + 1
            
            # Time-based statistics
            time_stats = self._get_time_based_statistics()
            
            stats = {
                'total_records': total_products,
                'unique_products': unique_products,
                'average_price': round(avg_price, 2),
                'min_price': min_price,
                'max_price': max_price,
                'products_with_variants': products_with_variants,
                'average_variants_per_product': round(avg_variants, 2),
                'products_with_images': products_with_images,
                'average_images_per_product': round(avg_images, 2),
                'category_distribution': category_stats,
                'time_based_stats': time_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Statistics calculated: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}
    
    def _get_time_based_statistics(self) -> Dict[str, Any]:
        """Gets time-based statistics for graphs."""
        try:
            # Get data for the last 30 days
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            # Daily statistics
            daily_stats = self.db.query(
                func.date(Product.processing_timestamp).label('date'),
                Product.stock_status,
                Product.category
            ).filter(
                Product.processing_timestamp >= thirty_days_ago
            ).all()
            
            # Group by day
            daily_data = {}
            for record in daily_stats:
                date_str = record.date.strftime('%Y-%m-%d')
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'total': 0,
                        'in_stock': 0,
                        'out_of_stock': 0,
                        'categories': {}
                    }
                
                daily_data[date_str]['total'] += 1
                
                if record.stock_status == 'In Stock':
                    daily_data[date_str]['in_stock'] += 1
                elif record.stock_status == 'Out of Stock':
                    daily_data[date_str]['out_of_stock'] += 1
                
                if record.category:
                    if record.category not in daily_data[date_str]['categories']:
                        daily_data[date_str]['categories'][record.category] = 0
                    daily_data[date_str]['categories'][record.category] += 1
            
            return {
                'daily_stats': daily_data,
                'period_days': 30
            }
            
        except Exception as e:
            logger.error(f"Error calculating time-based statistics: {str(e)}")
            return {}
    
    def __del__(self):
        """Closes the database connection when the object is deleted."""
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    # Example usage
    processor = AgiliteDataProcessor()
    result = processor.process_data()
    
    if result.get("success"):
        stats = processor.get_basic_statistics()
        print("\nBasic Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print(f"Processing failed: {result.get('error', 'Unknown error')}") 