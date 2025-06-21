import os
import time
import schedule
from datetime import datetime
import logging
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the data collection process"""
    try:
        logger.info("Starting data collection...")
        from data_collection.scraper_primary import AgiliteScraper
        
        scraper = AgiliteScraper()
        try:
            products_data = scraper.scrape_all_products()
            logger.info(f"Successfully scraped {len(products_data)} products")
            
            # Save the collected data to file
            scraper.save_products_data(products_data)
            logger.info("Data saved to file successfully")
            
            return True
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        finally:
            scraper.close()
    except Exception as e:
        logger.error(f"Error importing or initializing scraper: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_processor():
    """Run the data processing process"""
    try:
        logger.info("Starting data processing...")
        from data_processing.data_processor import AgiliteDataProcessor
        
        processor = AgiliteDataProcessor()
        try:
            result = processor.process_data()
            if result.get("success"):
                stats = processor.get_basic_statistics()
                logger.info(f"Successfully processed {result.get('processed_count', 0)} products")
                logger.info(f"Statistics: {stats}")
                return True
            else:
                logger.error(f"Processing failed: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    except Exception as e:
        logger.error(f"Error importing or initializing processor: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_full_cycle():
    """Run both scraper and processor in sequence"""
    logger.info("Starting full data collection and processing cycle")
    
    # Run scraper first
    scraper_success = run_scraper()
    
    if scraper_success:
        # Wait a bit before processing
        logger.info("Waiting 30 seconds before processing...")
        time.sleep(30)
        
        # Run processor
        processor_success = run_processor()
        
        if processor_success:
            logger.info("Full cycle completed successfully")
        else:
            logger.error("Processing failed")
    else:
        logger.error("Scraping failed, skipping processing")

def test_database_connection():
    """Test database connection before starting"""
    try:
        logger.info("Testing database connection...")
        from db import test_connection
        
        if test_connection():
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
    except Exception as e:
        logger.error(f"Database connection test error: {str(e)}")
        return False

def main():
    try:
        logger.info("Starting Agilite Scraper & Processor application")
        
        # Test database connection first
        if not test_database_connection():
            logger.error("Cannot connect to database. Exiting.")
            sys.exit(1)
        
        # Create necessary directories if they don't exist
        os.makedirs(os.path.join("data", "raw"), exist_ok=True)
        os.makedirs(os.path.join("data", "processed"), exist_ok=True)
        os.makedirs(os.path.join("data", "test_scrape"), exist_ok=True)
        
        logger.info("Directories created successfully")
        
        # Get schedule interval from environment variable (default: 6 hours)
        schedule_hours = int(os.environ.get('SCHEDULE_HOURS', 6))
        
        logger.info(f"Setting up scheduler to run every {schedule_hours} hours")
        
        # Schedule the full cycle
        schedule.every(schedule_hours).hours.do(run_full_cycle)
        
        # Run initial cycle
        logger.info("Running initial data collection and processing cycle...")
        run_full_cycle()
        
        logger.info("Scheduler started. Waiting for next scheduled run...")
        
        # Keep the script running and check for scheduled tasks
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(60)  # Wait before retrying
                
    except Exception as e:
        logger.error(f"Critical error in main function: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 