# Agilite Data Scraper & Processor

## Project Overview
This project collects and processes product data from Agilite (agilite.co.il) using automated web scraping and data processing pipelines.

## Project Structure
```
├── data/                  # Directory for storing raw and processed data
│   ├── raw/              # Raw collected data
│   ├── processed/        # Cleaned and processed data
│   └── test_scrape/      # Test data for development
├── src/                  # Source code
│   ├── data_collection/  # Scripts for data collection
│   ├── data_processing/  # Scripts for data cleaning and processing
│   ├── scraper_processor.py  # Main application script
│   └── dashboard/        # Dashboard implementation (separate app)
├── docs/                 # Documentation
├── requirements.txt      # Project dependencies
├── Dockerfile           # Docker configuration
├── captain-definition   # CapRover configuration
├── deploy.sh            # Bash deployment script
├── deploy.ps1           # PowerShell deployment script
└── DEPLOYMENT.md        # Detailed deployment instructions
```

## Features
- **Automated Data Collection**: Web scraping of product data from agilite.co.il
- **Data Processing**: Cleaning, transformation, and analysis of collected data
- **Scheduled Execution**: Configurable intervals for data collection and processing
- **Logging**: Comprehensive logging for monitoring and debugging
- **Docker Support**: Containerized deployment with CapRover

## Local Development Setup

### 1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the application:
```bash
python src/scraper_processor.py
```

## Quick Deploy on CapRover

### Prerequisites
1. CapRover server running
2. CapRover CLI installed: `npm install -g caprover`

### Automated Deployment

#### Windows (PowerShell):
```powershell
.\deploy.ps1
```

#### Linux/Mac (Bash):
```bash
./deploy.sh
```

### Manual Deployment

#### 1. Connect to CapRover:
```bash
caprover login
```

#### 2. Create and deploy application:
```bash
caprover app create agilite-scraper
caprover env set agilite-scraper SCHEDULE_HOURS=6
caprover deploy
```

### Configuration

#### Environment Variables
- `SCHEDULE_HOURS` - Interval between data collection runs (default: 6 hours)

#### Persistent Data (Volumes)
To persist data between deployments, set up a volume in CapRover:
- Go to your app in CapRover dashboard
- Click on **Volumes**
- Add a new volume:
  - **Container Path:** `/app/data`
  - **Host Path:** `/var/lib/caprover/agilite-data`
- Click **Save & Update**

### Monitoring

#### View Logs:
```bash
caprover logs agilite-scraper
```

#### Check Status:
```bash
caprover app status agilite-scraper
```

#### Real-time Logs:
```bash
caprover logs agilite-scraper --follow
```

## Data Output

### Raw Data
- Location: `data/raw/`
- Format: JSON files with timestamp
- Content: Raw scraped product data

### Processed Data
- Location: `data/processed/`
- Format: CSV files with timestamp
- Content: Cleaned and analyzed product data

### Statistics
- Location: `data/processed/`
- Format: JSON files with timestamp
- Content: Summary statistics and metrics

## Troubleshooting

### Common Issues

1. **Firefox/GeckoDriver Issues**: The application uses Firefox for web scraping. Ensure the Docker container has proper display configuration.

2. **Memory Issues**: Web scraping can be memory-intensive. Monitor container resource usage.

3. **Network Issues**: Ensure the server has internet access for scraping agilite.co.il.

### Debug Mode
To enable debug logging, set the environment variable:
```bash
caprover env set agilite-scraper DEBUG=true
```

### Restart Application
```bash
caprover app restart agilite-scraper
```

## Development

### Test Mode
For development and testing, you can run the scraper in test mode by modifying `src/scraper_primary.py`:
```python
scraper = AgiliteScraper(test_mode=True)
```

### Adding New Features
1. Modify the appropriate module in `src/`
2. Test locally
3. Update requirements.txt if needed
4. Deploy using the deployment scripts

## Documentation
Detailed documentation can be found in:
- `DEPLOYMENT.md` - Complete deployment guide
- `docs/` - Additional documentation

---

## Notes
- All data is stored in `/app/data` inside the container
- With volume mounting, data persists between deployments
- The application runs continuously and performs scheduled data collection
- Logs are available both in container and CapRover dashboard
