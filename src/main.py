import os
import time
import schedule
from datetime import datetime
from data_collection.scraper_primary import AgiliteScraper
from data_processing.data_processor import AgiliteDataProcessor
import subprocess
import sys

def run_scraper():
    """Run the data collection process"""
    print(f"\n[{datetime.now()}] Starting data collection...")
    scraper = AgiliteScraper()
    try:
        products_data = scraper.scrape_all_products()
        print(f"[{datetime.now()}] Successfully scraped {len(products_data)} products")
    finally:
        scraper.close()

def run_processor():
    """Run the data processing process"""
    print(f"\n[{datetime.now()}] Starting data processing...")
    processor = AgiliteDataProcessor()
    processor.process_data()

def run_dashboard():
    """Run the dashboard"""
    print(f"\n[{datetime.now()}] Starting dashboard...")
    dashboard_path = os.path.join("src", "dashboard", "app.py")
    subprocess.Popen([sys.executable, dashboard_path])

def main():
    # Create necessary directories if they don't exist
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    
    # Schedule data collection every 6 hours
    schedule.every(1).hours.do(run_scraper)
    
    # Schedule data processing every 6 hours (15 minutes after collection)
    schedule.every(1).hours.do(run_processor).at(":15")
    
    # Run initial data collection and processing
    run_scraper()
    run_processor()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 