# Agilite Data Intelligence Pipeline

This project is a **fully automated data pipeline** that collects product information and stock levels from agilite.co.il, processes the data, and stores it in a PostgreSQL database. The system consists of **two microservices** working together to provide continuous data collection and processing capabilities.

## System Architecture

The pipeline is designed as a **microservices architecture** with two main components:

### 1. Data Collection Microservice (`src/data_collection/scraper_primary.py`)
- **Purpose**: Automated web scraping service
- **Functionality**: 
  - Collects product data from agilite.co.il using Selenium WebDriver
  - Extracts detailed product information including variants, colors, and stock levels
  - Saves raw data to JSON files with timestamps
  - Handles pagination and product discovery automatically
- **Output**: Timestamped JSON files in `data/raw/` directory

### 2. Data Processing Microservice (`src/data_processing/data_processor.py`)
- **Purpose**: Data transformation and storage service
- **Functionality**:
  - Processes raw JSON data from the collection service
  - Transforms and cleans the data
  - Stores processed data in PostgreSQL database with historical tracking
  - Provides statistical analysis and reporting capabilities
- **Output**: Structured data in PostgreSQL database with full historical records

## Automation Features

The system includes comprehensive automation:

- **Scheduled Execution**: Automatic data collection every 6 hours (configurable)
- **Error Handling**: Robust error handling and logging for both services
- **Historical Data Tracking**: Each scraping session creates new records, preserving historical data
- **Database Management**: Automatic table creation and schema management
- **Monitoring**: Comprehensive logging and status tracking

## Project Goal
The objective is to create a reliable, automated system for tracking product data over time, enabling historical analysis of stock levels, pricing, and product assortment. The microservices architecture ensures scalability, maintainability, and fault tolerance.

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
*   **More Robust Scraping**: Implement a proxy rotation service to minimize the risk of being blocked during large-scale scraping. Add more sophisticated retry logic and error handling.
*   **Data Validation**: Integrate a data validation framework (like Pandera or Great Expectations) to check the quality and integrity of the data before it's loaded into the database.
*   **Delta Processing**: Optimize the data processor to identify what has changed since the last run (e.g., only stock or price) instead of creating a full product record every time, which would make the database more efficient.
*   **Containerization**: Package the application in a Docker container for easier deployment and environment consistency.
