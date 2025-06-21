# Agilite Data Intelligence Pipeline

This project is a **fully automated data pipeline** that collects product information and stock levels from agilite.co.il, processes the data, and stores it in a PostgreSQL database. The complete system consists of **three components** working together to provide comprehensive data intelligence capabilities.

## System Architecture

The complete system is designed as a **distributed architecture** with three main components, all **deployed in Docker containers and running automatically on a production server**:

### 1. Data Collection Microservice (`src/data_collection/scraper_primary.py`)
- **Purpose**: Automated web scraping service
- **Functionality**: 
  - Collects product data from agilite.co.il using Selenium WebDriver
  - Extracts detailed product information including variants, colors, and stock levels
  - Saves raw data to JSON files with timestamps
  - Handles pagination and product discovery automatically
- **Output**: Timestamped JSON files in `data/raw/` directory
- **Deployment**: Containerized and running on production server with automatic scheduling

### 2. Data Processing Microservice (`src/data_processing/data_processor.py`)
- **Purpose**: Data transformation and storage service
- **Functionality**:
  - Processes raw JSON data from the collection service
  - Transforms and cleans the data
  - Stores processed data in PostgreSQL database with historical tracking
  - Provides statistical analysis and reporting capabilities
- **Output**: Structured data in PostgreSQL database with full historical records
- **Deployment**: Containerized and running on production server with automatic data processing

### 3. Dashboard Application (`app.py`)
- **Purpose**: Interactive web-based data visualization and analytics interface
- **Functionality**:
  - Real-time connection to the PostgreSQL database
  - Interactive dashboards with Plotly charts and graphs
  - Historical stock level analysis over time
  - Price distribution analysis
  - High-demand product identification
  - Stock-out rate analysis by category
  - Product table with live data
  - Automatic data refresh and updates
- **Technology**: Built with Dash, Plotly, and Bootstrap
- **Features**:
  - Stock level trends over time
  - Category-based stock analysis
  - Price distribution histograms
  - High-demand product tracking
  - Database and scraping status monitoring
  - Responsive web interface
- **Deployment**: Containerized and accessible via web interface on production server

## Automation Features

The system includes comprehensive automation:

- **Scheduled Execution**: Automatic data collection every 6 hours (configurable)
- **Error Handling**: Robust error handling and logging for all services
- **Historical Data Tracking**: Each scraping session creates new records, preserving historical data
- **Database Management**: Automatic table creation and schema management
- **Monitoring**: Comprehensive logging and status tracking

## Production Deployment

This system is **currently deployed and running in production**:

- **Containerized Deployment**: All components are packaged in Docker containers for consistency and scalability
- **Production Server**: Running on a dedicated server with automatic startup and monitoring
- **Continuous Operation**: The system operates 24/7 with automatic data collection and processing
- **Web Dashboard**: Accessible via web interface for real-time monitoring and analysis
  - **Live Dashboard**: [http://agilite.bysokol.com/](http://agilite.bysokol.com/)
- **Database**: PostgreSQL database with persistent storage and backup capabilities
- **Monitoring**: Comprehensive logging and health checks for all services

The production deployment demonstrates the system's reliability and readiness for real-world business intelligence applications.

## Project Goal
The objective is to create a reliable, automated system for tracking product data over time, enabling historical analysis of stock levels, pricing, and product assortment. The distributed architecture ensures scalability, maintainability, and fault tolerance across all three components.

## How It Works

### Data Collection Methodology
The system collects data using Selenium WebDriver to simulate a real user browsing the site. The process is as follows:
1.  **Navigate to Collections**: The scraper starts at the main "all products" collection page.
2.  **Gather Product Links**: It iterates through all pagination links to find and collect the URLs for every product.
3.  **Visit Each Product Page**: The scraper visits each product URL individually. To handle dynamic content and ensure accuracy, it uses robust waiting mechanisms and verifies that the correct page has been loaded.
4.  **Extract Data**: It extracts structured data (JSON-LD) when available, falling back to parsing the HTML for key information like title, price, variants, images, and stock status.
5.  **Save Raw Data**: The collected data for all products from a single run is saved as a timestamped JSON file in the `data/raw` directory.

### Data Processing Pipeline
Once the raw data is collected, the processing script takes over:
1.  **Load Raw Data**: The processor loads the most recent JSON file from the `data/raw` directory.
2.  **Clean and Structure**: It processes each product record to clean and normalize the data. This includes:
    *   **Price Cleaning**: Removing currency symbols and converting the price to a numeric format.
    *   **Stock Status Parsing**: Interpreting text like "In Stock" or "Out of Stock" into a consistent format.
    *   **Category Extraction**: Assigning a category to each product based on keywords in its title.
3.  **Save to Database**: The cleaned data is loaded into a PostgreSQL database. A new record is created for each product on every run, preserving the `processing_timestamp` to build a history of stock levels and other attributes over time.

## Database Structure
The data is stored in a normalized PostgreSQL schema named `agilite`.

*   **`products`**: Stores a historical record of each product for every scrape session. Key fields include `url`, `title`, `price`, `stock_status`, `category`, and `processing_timestamp`.
*   **`product_images`**: Stores URLs for each product's images.
*   **`product_variants`**: Stores the different variants (e.g., color, size) for each product.
*   **`scraping_sessions`**: A log of each scraping job, including start/end times, number of products found, and status.

## Data Insights and Business Intelligence

The system provides comprehensive business intelligence capabilities through the dashboard and database analytics:

### Stock Level Insights
- **Historical Stock Trends**: Track how product availability changes over time to identify seasonal patterns
- **Stock-Out Analysis**: Identify products that frequently go out of stock, indicating high demand
- **Category Performance**: Compare stock levels across different product categories
- **Restock Timing**: Optimize inventory management by understanding when products typically need restocking

### Pricing Intelligence
- **Price Distribution Analysis**: Understand the pricing strategy across different product categories
- **Price Change Tracking**: Monitor price fluctuations over time to identify pricing trends
- **Competitive Positioning**: Analyze price points relative to product categories and features

### Product Performance Analytics
- **High-Demand Products**: Identify products that frequently transition from "In Stock" to "Out of Stock"
- **Category Popularity**: Track which product categories have the highest demand
- **Variant Analysis**: Understand which product variants (colors, sizes) are most popular
- **Product Lifecycle**: Track how long products remain in stock before selling out

### Operational Insights
- **Scraping Performance**: Monitor the reliability and completeness of data collection
- **Data Quality Metrics**: Track the consistency and accuracy of collected information
- **System Health**: Monitor the overall health and performance of the data pipeline

### Business Recommendations
Based on the collected data, the system can provide actionable insights such as:
- **Inventory Optimization**: Which products need increased stock levels
- **Pricing Strategy**: Opportunities for price adjustments based on demand patterns
- **Product Assortment**: Which categories or products to focus on or expand
- **Seasonal Planning**: Prepare for expected demand fluctuations

These insights enable data-driven decision making for inventory management, pricing strategy, and product assortment planning.

## Getting Started

### Requirements
*   Python 3.11+
*   PostgreSQL 12+
*   Git

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up the database:**
    Connect to your PostgreSQL instance and create a new database.
    ```sql
    CREATE DATABASE agilite;
    ```
4.  **Configure environment variables:**
    Copy the example file and edit it with your database credentials.
    ```bash
    cp env.example .env
    ```
    Your `.env` file should look like this:
    ```env
    # Database Configuration
    DB_HOST=localhost
    DB_PORT=5432
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_NAME=agilite

    # Application Configuration
    SCHEDULE_HOURS=6
    ```

### Running the Pipeline
To run the pipeline manually for a single cycle:
```bash
python src/main.py
```
The application will connect to the database, create the necessary tables, and run the full scrape-and-process cycle. By default, it is scheduled to run every 1 hour.

## Project Assumptions
*   **Website Structure**: The scraper assumes the general HTML structure and class names of `agilite.co.il` will remain relatively stable. Significant changes to the website's front-end may require updates to the scraper's selectors.
*   **Stock Level Interpretation**: Stock status is determined by parsing text on the page. The logic is based on the current observed values ("In Stock", "Out of Stock", "Pre-order").
*   **No Official API**: The project was built without access to an internal API, relying solely on publicly accessible information.

## Future Improvements
If more time were available, the following improvements could be made:

### Data Collection Enhancements
*   **Shopify API Integration**: Replace web scraping with official Shopify API access for more reliable and efficient data collection, including real-time inventory updates and sales data.
*   **Review and Rating Tracking**: Implement collection of customer reviews, ratings, and sentiment analysis to understand product popularity and customer satisfaction.
*   **Sales Data Integration**: Connect to Shopify's order and sales data to track actual sales velocity, revenue trends, and conversion rates.
*   **More Robust Scraping**: Implement a proxy rotation service to minimize the risk of being blocked during large-scale scraping. Add more sophisticated retry logic and error handling.

### Data Processing Improvements
*   **Data Validation**: Integrate a data validation framework (like Pandera or Great Expectations) to check the quality and integrity of the data before it's loaded into the database.
*   **Delta Processing**: Optimize the data processor to identify what has changed since the last run (e.g., only stock or price) instead of creating a full product record every time, which would make the database more efficient.
*   **Advanced Analytics**: Implement machine learning models for demand forecasting, price optimization, and inventory management recommendations.

### Intelligence and Recommendations
*   **Product Recommendation Engine**: Build a recommendation system based on historical sales data, customer behavior, and product similarities to suggest cross-selling and upselling opportunities.
*   **Demand Forecasting**: Develop predictive models to forecast product demand based on historical patterns, seasonal trends, and market indicators.
*   **Automated Alerts**: Create intelligent alerting system for low stock, price changes, or unusual sales patterns.
*   **Competitive Intelligence**: Expand data collection to include competitor pricing and inventory levels for market positioning analysis.

### Technical Improvements
*   **Containerization**: Package the application in a Docker container for easier deployment and environment consistency.
*   **Microservices Separation**: Split the current monolithic structure into truly independent microservices with their own databases and APIs.
*   **Real-time Processing**: Implement streaming data processing for real-time analytics and immediate insights.
*   **Advanced Dashboard Features**: Add user authentication, customizable dashboards, export capabilities, and mobile-responsive design.
