# Agilite Sales Intelligence Dashboard Documentation

## Project Overview
This project creates a sales intelligence dashboard for Agilite (agilite.co.il) by collecting and analyzing product-level sales data. The system automatically collects data, processes it, and presents it in an interactive dashboard.

## System Architecture

### 1. Data Collection (`src/data_collection/scraper.py`)
- Uses Selenium WebDriver to collect product data from agilite.co.il
- Collects information about:
  - Product titles
  - Prices
  - Stock levels
  - Product variants
- Data is saved in JSON format in the `data/raw` directory

### 2. Data Processing (`src/data_processing/processor.py`)
- Processes raw data into a structured format
- Cleans and normalizes data
- Converts data into CSV format
- Saves processed data in the `data/processed` directory

### 3. Dashboard (`src/dashboard/app.py`)
- Built using Dash and Plotly
- Features:
  - Stock status overview (pie chart)
  - Price distribution (histogram)
  - Top products table
- Updates automatically every 5 minutes

## Setup Instructions

1. Install Python 3.8 or higher

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the system:
```bash
python src/main.py
```

## Data Collection Methodology

The system collects data through web scraping using Selenium WebDriver. The process:
1. Navigates to agilite.co.il
2. Collects all product links
3. Visits each product page
4. Extracts product information
5. Saves data in JSON format

## Data Processing Pipeline

1. Loads the most recent raw data file
2. Processes product information:
   - Cleans price data
   - Normalizes stock status
   - Structures variant information
3. Saves processed data in CSV format

## Dashboard Features

1. Stock Status Overview
   - Shows distribution of in-stock vs out-of-stock products
   - Updates automatically

2. Price Distribution
   - Displays histogram of product prices
   - Helps identify price ranges and patterns

3. Top Products Table
   - Shows top 10 products by price
   - Includes variant information and stock status

## Assumptions and Limitations

1. Data Collection:
   - Assumes website structure remains relatively stable
   - May need adjustments if website layout changes
   - Respects website's robots.txt and rate limits

2. Data Processing:
   - Assumes consistent data format
   - Handles missing or malformed data gracefully

3. Dashboard:
   - Requires modern web browser
   - Best viewed on desktop devices

## Future Improvements

1. Data Collection:
   - Add proxy support for better reliability
   - Implement more robust error handling
   - Add support for historical data analysis

2. Data Processing:
   - Add more data cleaning options
   - Implement data validation
   - Add support for custom data transformations

3. Dashboard:
   - Add more visualization options
   - Implement user authentication
   - Add export functionality
   - Add custom date range selection

## Maintenance

The system is designed to run continuously with minimal maintenance:
- Data collection runs every 6 hours
- Data processing runs 15 minutes after collection
- Dashboard updates every 5 minutes
- Logs are maintained for debugging purposes

## Troubleshooting

Common issues and solutions:

1. Data Collection Fails:
   - Check internet connection
   - Verify website accessibility
   - Check for website structure changes

2. Processing Errors:
   - Verify raw data format
   - Check for missing required fields
   - Ensure sufficient disk space

3. Dashboard Issues:
   - Clear browser cache
   - Check browser console for errors
   - Verify data file existence 