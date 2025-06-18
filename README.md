# Agilite Sales Intelligence Dashboard

## Project Overview
This project aims to create a sales intelligence dashboard for Agilite (agilite.co.il) by collecting and analyzing product-level sales data.

## Project Structure
```
├── data/                  # Directory for storing raw and processed data
│   ├── raw/              # Raw collected data
│   └── processed/        # Cleaned and processed data
├── src/                  # Source code
│   ├── data_collection/  # Scripts for data collection
│   ├── data_processing/  # Scripts for data cleaning and processing
│   └── dashboard/        # Dashboard implementation
├── docs/                 # Documentation
└── requirements.txt      # Project dependencies
```

## Setup Instructions
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Collection
The project uses web scraping to collect product data from agilite.co.il. The data collection process is automated and runs periodically to track changes in product information.

## Dashboard
The dashboard is built using [Tool to be determined] and provides insights into:
- Top-selling products
- Sales trends by day and month
- Product variant analysis
- Stock level monitoring

## Documentation
Detailed documentation can be found in the `docs/` directory:
- Data collection methodology
- Data processing pipeline
- Dashboard implementation
- Analysis and insights

## Quick Deploy on CapRover (Docker)

### 1. Build & Deploy
- Make sure you have a CapRover server running.
- Push this repo or upload as a tar/zip to CapRover.
- CapRover will use the provided `Dockerfile` to build the image.

### 2. Persistent Data (Volumes)
To persist raw and processed data between deployments, set up a volume in CapRover:
- Go to your app in CapRover dashboard
- Click on **Volumes**
- Add a new volume:
  - **Container Path:** `/app/data`
  - **Host Path:** `/var/lib/caprover/agilite-data` (or any persistent path on your server)
- Click **Save & Update**

### 3. Environment Variables (Optional)
You can set environment variables in CapRover for debug, port, etc.

### 4. Expose Dashboard
- The Dash dashboard runs on port 8050 by default.
- Make sure CapRover routes traffic to this port.

### 5. Useful Commands
- To run locally: `xvfb-run -a python src/main.py`
- To build manually: `docker build -t agilite-dashboard .`

### 6. Project Structure
```
/
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── captain-definition
├── README.md
├── src/
│   ├── main.py
│   ├── dashboard/
│   │   └── app.py
│   ├── data_collection/
│   │   └── scraper_primary.py
│   ├── data_processing/
│   │   └── data_processor.py
│   └── ...
└── data/
    ├── raw/
    └── processed/
```

---

## Notes
- All data (raw and processed) will be stored in `/app/data` inside the container.
- With the volume, your data will persist even if you redeploy or update the app.
- For troubleshooting, check CapRover app logs.
