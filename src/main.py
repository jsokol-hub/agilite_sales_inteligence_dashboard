import os
import time
import schedule
from datetime import datetime
from data_collection.scraper_primary import AgiliteScraper
from data_processing.data_processor import AgiliteDataProcessor
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the data collection process"""
    logger.info("Starting data collection...")
    scraper = AgiliteScraper()
    try:
        products_data = scraper.scrape_all_products()
        logger.info(f"Successfully scraped {len(products_data)} products")
        return True
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return False
    finally:
        scraper.close()

def run_processor():
    """Run the data processing process"""
    logger.info("Starting data processing...")
    processor = AgiliteDataProcessor()
    try:
        df = processor.process_data()
        if not df.empty:
            stats = processor.get_basic_statistics(df)
            logger.info(f"Successfully processed {len(df)} products")
            logger.info(f"Statistics: {stats}")
            return True
        else:
            logger.warning("No data to process")
            return False
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
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

def main():
    # Create necessary directories if they don't exist
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    os.makedirs(os.path.join("data", "test_scrape"), exist_ok=True)
    
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
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main() 