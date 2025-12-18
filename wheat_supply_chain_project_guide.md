# Wheat Supply Chain Disruption & Price Predictor
## Complete Project Guide

---

## 🎯 Project Overview

**Goal**: Build an end-to-end data engineering and ML pipeline that predicts wheat price spikes, supply disruptions, and logistics delays by integrating real-time data from shipping, weather, trade, and geopolitical sources.

**Learning Outcomes**:
- Real-world data ingestion from multiple APIs
- Building scalable data pipelines
- Time-series forecasting and classification ML models
- Creating analytics dashboards
- Cloud deployment (optional)

---

## 📋 Prerequisites

### Required Skills
- **Python**: Intermediate (pandas, requests, APIs)
- **SQL**: Basic (querying, joins)
- **Linux/Command Line**: Basic
- **Git**: Basic version control

### Nice to Have
- Docker basics
- Cloud platform experience (AWS/GCP/Azure)
- Apache Airflow or similar orchestration tool

### Tools You'll Need
- Python 3.9+
- PostgreSQL or MySQL
- Jupyter Notebook / VS Code
- Git & GitHub
- (Optional) Docker
- (Optional) Cloud account (AWS free tier recommended)

---

## 🗺️ Project Roadmap

```
Phase 1: Setup & Data Collection (Week 1-2)
    ↓
Phase 2: Data Lake & Storage (Week 3)
    ↓
Phase 3: Data Cleaning & Processing (Week 4-5)
    ↓
Phase 4: Feature Engineering (Week 6)
    ↓
Phase 5: ML Model Development (Week 7-8)
    ↓
Phase 6: Pipeline Automation (Week 9)
    ↓
Phase 7: Analytics Dashboard (Week 10)
    ↓
Phase 8: Deployment & Documentation (Week 11-12)
```

---

# 📍 MILESTONE 1: Environment Setup & API Access
**Duration**: 3-4 days  
**Goal**: Get your development environment ready and secure API access

## Steps

### 1.1 Create Project Structure
```bash
wheat-supply-chain/
├── data/
│   ├── raw/              # Raw data from APIs
│   ├── processed/        # Cleaned data
│   └── features/         # Engineered features
├── notebooks/            # Jupyter notebooks for exploration
├── src/
│   ├── ingestion/        # Data collection scripts
│   ├── processing/       # Data cleaning
│   ├── models/           # ML models
│   └── utils/            # Helper functions
├── tests/                # Unit tests
├── config/               # Configuration files
├── docs/                 # Documentation
├── requirements.txt
├── .env                  # API keys (DO NOT COMMIT)
├── .gitignore
└── README.md
```

**Action Items**:
- [ ] Create the directory structure above
- [ ] Initialize git repository: `git init`
- [ ] Create `.gitignore` (include `.env`, `data/`, `*.csv`, `*.parquet`)
- [ ] Set up virtual environment: `python -m venv venv`
- [ ] Create `requirements.txt` (start with basics, add as you go)

### 1.2 Register for API Keys

**Priority APIs** (Free Tier):
1. **USDA PSD API**
   - URL: https://apps.fas.usda.gov/psdonline/circulars/production.pdf
   - Contact: fas-data@usda.gov (request API access)
   - **Hint**: May take 2-3 days for approval, start early!

2. **FRED API**
   - URL: https://fred.stlouisfed.org/docs/api/api_key.html
   - Sign up → Get API key instantly
   - Store in `.env` as `FRED_API_KEY=your_key_here`

3. **NewsAPI**
   - URL: https://newsapi.org/register
   - Free tier: 100 requests/day
   - Store in `.env` as `NEWS_API_KEY=your_key_here`

4. **NASA POWER API**
   - URL: https://power.larc.nasa.gov/
   - No API key needed! Completely free
   - Rate limit: Be respectful, ~10 requests/min

5. **World Bank API**
   - URL: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
   - No API key needed!

6. **GDELT Project**
   - URL: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
   - No API key needed! Massive dataset
   - **Hint**: Data is BigQuery format, can query via Google BigQuery free tier

**Optional (Add Later)**:
- MarineTraffic API (~$50/month) - Wait until Phase 2
- Quandl/Nasdaq Data Link - Free tier available
- Sentinel Hub (satellite imagery) - Free tier available

### 1.3 Create Configuration Management

Create `config/config.yaml`:
```yaml
data_sources:
  fred:
    base_url: "https://api.stlouisfed.org/fred"
    series_ids:
      - "WPU0121"  # Wheat price index
    
  nasa_power:
    base_url: "https://power.larc.nasa.gov/api"
    regions:
      - name: "US_Great_Plains"
        lat: 39.8
        lon: -98.5
      - name: "Ukraine_Wheat_Belt"
        lat: 48.3
        lon: 31.1

  newsapi:
    base_url: "https://newsapi.org/v2"
    keywords:
      - "wheat export"
      - "grain shortage"
      - "port blockade"

database:
  host: "localhost"
  port: 5432
  name: "wheat_supply_chain"
  user: "postgres"
```

Create `.env` file:
```bash
FRED_API_KEY=your_fred_key_here
NEWS_API_KEY=your_news_key_here
DB_PASSWORD=your_db_password_here
```

**Action Items**:
- [ ] Create `config.yaml` with your data sources
- [ ] Create `.env` file with API keys
- [ ] Install `python-dotenv` to load environment variables
- [ ] Add `.env` to `.gitignore` ⚠️ IMPORTANT!

### 1.4 Install Core Dependencies

Create `requirements.txt`:
```
# Data Collection
requests==2.31.0
pandas==2.1.0
numpy==1.24.0

# Database
psycopg2-binary==2.9.7
sqlalchemy==2.0.20

# Configuration
python-dotenv==1.0.0
pyyaml==6.0.1

# Data Processing
beautifulsoup4==4.12.2
lxml==4.9.3

# Notebooks
jupyter==1.0.0
matplotlib==3.7.2
seaborn==0.12.2

# Testing
pytest==7.4.0
```

**Action Items**:
- [ ] Run: `pip install -r requirements.txt`
- [ ] Test imports in Python: `import pandas, requests, sqlalchemy`

---

# 📍 MILESTONE 2: Data Ingestion - First API Call
**Duration**: 4-5 days  
**Goal**: Successfully fetch data from your first 3 APIs and save it locally

## Steps

### 2.1 Start Simple - FRED API (Wheat Prices)

Create `src/ingestion/fred_collector.py`:

```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class FREDCollector:
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    def get_wheat_prices(self, series_id='WPU0121', start_date='2020-01-01'):
        """
        Fetch wheat price index from FRED
        series_id: WPU0121 = Producer Price Index for Wheat
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Save to CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'data/raw/fred_wheat_prices_{timestamp}.csv'
            df.to_csv(filepath, index=False)
            
            print(f"✓ Fetched {len(df)} records from FRED")
            print(f"✓ Saved to {filepath}")
            return df
        else:
            print(f"✗ Error: {response.status_code}")
            return None

# Test it!
if __name__ == "__main__":
    collector = FREDCollector()
    df = collector.get_wheat_prices()
    print(df.head())
```

**Action Items**:
- [ ] Create the script above
- [ ] Run it: `python src/ingestion/fred_collector.py`
- [ ] Verify CSV is created in `data/raw/`
- [ ] Open CSV and inspect the data
- [ ] **Hint**: If you get errors, check your API key in `.env`

### 2.2 NASA POWER API (Weather Data)

Create `src/ingestion/weather_collector.py`:

```python
import requests
import pandas as pd
from datetime import datetime

class WeatherCollector:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def get_weather(self, lat, lon, start_date='20200101', end_date='20231231'):
        """
        Fetch weather data for wheat-growing regions
        Parameters: PRECTOTCORR (precipitation), T2M (temperature), 
                   T2M_MAX, T2M_MIN
        """
        params = {
            'parameters': 'PRECTOTCORR,T2M,T2M_MAX,T2M_MIN',
            'community': 'AG',  # Agricultural community
            'longitude': lon,
            'latitude': lat,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract parameters
            params_data = data['properties']['parameter']
            
            # Convert to DataFrame
            df = pd.DataFrame(params_data)
            df['date'] = pd.to_datetime(df.index, format='%Y%m%d')
            df['latitude'] = lat
            df['longitude'] = lon
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f'data/raw/weather_{lat}_{lon}_{timestamp}.csv'
            df.to_csv(filepath, index=False)
            
            print(f"✓ Fetched weather data for ({lat}, {lon})")
            print(f"✓ Saved to {filepath}")
            return df
        else:
            print(f"✗ Error: {response.status_code}")
            return None

# Test it!
if __name__ == "__main__":
    collector = WeatherCollector()
    
    # US Great Plains (Kansas wheat belt)
    df_us = collector.get_weather(lat=39.8, lon=-98.5)
    
    # Ukraine wheat belt
    df_ukraine = collector.get_weather(lat=48.3, lon=31.1)
    
    print(df_us.head())
```

**Action Items**:
- [ ] Create the weather collector script
- [ ] Run it for 2-3 wheat regions
- [ ] Check CSV files are created
- [ ] **Hint**: NASA API has no auth, but be respectful with rate limits (1-2 requests/second max)

### 2.3 NewsAPI (Geopolitical Events)

Create `src/ingestion/news_collector.py`:

```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class NewsCollector:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_wheat_news(self, query='wheat export', days_back=30):
        """
        Fetch news articles related to wheat supply chain
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'relevancy',
            'apiKey': self.api_key,
            'language': 'en',
            'pageSize': 100  # Max per request
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            df = pd.DataFrame(articles)
            
            if not df.empty:
                df['publishedAt'] = pd.to_datetime(df['publishedAt'])
                df['query'] = query
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f'data/raw/news_{query.replace(" ", "_")}_{timestamp}.csv'
                df.to_csv(filepath, index=False)
                
                print(f"✓ Fetched {len(df)} articles for '{query}'")
                print(f"✓ Saved to {filepath}")
                return df
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return None

# Test it!
if __name__ == "__main__":
    collector = NewsCollector()
    
    # Collect news for different keywords
    df1 = collector.get_wheat_news('wheat export ban')
    df2 = collector.get_wheat_news('grain shortage')
    df3 = collector.get_wheat_news('Ukraine wheat')
```

**Action Items**:
- [ ] Create the news collector script
- [ ] Run it with different keywords
- [ ] Check the articles make sense
- [ ] **Hint**: Free tier is limited to 100 requests/day, so test carefully

### 2.4 Create a Master Ingestion Runner

Create `src/ingestion/run_daily_ingestion.py`:

```python
from fred_collector import FREDCollector
from weather_collector import WeatherCollector
from news_collector import NewsCollector
from datetime import datetime

def run_daily_collection():
    """
    Run all data collectors
    """
    print(f"\n{'='*50}")
    print(f"Starting data collection: {datetime.now()}")
    print(f"{'='*50}\n")
    
    # 1. Collect wheat prices
    print("1. Collecting wheat prices from FRED...")
    fred = FREDCollector()
    fred.get_wheat_prices()
    
    # 2. Collect weather data
    print("\n2. Collecting weather data from NASA POWER...")
    weather = WeatherCollector()
    
    regions = [
        {'name': 'US_Great_Plains', 'lat': 39.8, 'lon': -98.5},
        {'name': 'Ukraine', 'lat': 48.3, 'lon': 31.1},
        {'name': 'Russia_South', 'lat': 51.5, 'lon': 46.0},
        {'name': 'Australia', 'lat': -33.9, 'lon': 151.2}
    ]
    
    for region in regions:
        weather.get_weather(region['lat'], region['lon'])
    
    # 3. Collect news
    print("\n3. Collecting news from NewsAPI...")
    news = NewsCollector()
    keywords = ['wheat export', 'grain crisis', 'Ukraine wheat']
    
    for keyword in keywords:
        news.get_wheat_news(keyword, days_back=7)
    
    print(f"\n{'='*50}")
    print(f"✓ Collection complete!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    run_daily_collection()
```

**Action Items**:
- [ ] Create the master runner script
- [ ] Run it: `python src/ingestion/run_daily_ingestion.py`
- [ ] Verify all data sources are collected
- [ ] Check `data/raw/` directory for all CSV files

**🎉 MILESTONE 2 COMPLETE!** You now have real data flowing in!

---

# 📍 MILESTONE 3: Data Lake Setup (PostgreSQL)
**Duration**: 3-4 days  
**Goal**: Set up PostgreSQL database and load raw data into it

## Steps

### 3.1 Install and Configure PostgreSQL

**On Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**On macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**On Windows**:
- Download from: https://www.postgresql.org/download/windows/
- Install and set password for `postgres` user

**Action Items**:
- [ ] Install PostgreSQL
- [ ] Set password for postgres user
- [ ] Test connection: `psql -U postgres`

### 3.2 Create Database Schema

Create `src/database/setup_db.py`:

```python
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """
    Create wheat supply chain database and tables
    """
    # Connect to default postgres database
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password=os.getenv('DB_PASSWORD')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create database
    try:
        cursor.execute("CREATE DATABASE wheat_supply_chain")
        print("✓ Database created")
    except psycopg2.errors.DuplicateDatabase:
        print("⚠ Database already exists")
    
    cursor.close()
    conn.close()
    
    # Connect to new database
    conn = psycopg2.connect(
        host="localhost",
        database="wheat_supply_chain",
        user="postgres",
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    
    # Create tables
    tables = {
        'wheat_prices': """
            CREATE TABLE IF NOT EXISTS wheat_prices (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                price_index NUMERIC(10, 2),
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, source)
            )
        """,
        
        'weather_data': """
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                latitude NUMERIC(10, 6),
                longitude NUMERIC(10, 6),
                region VARCHAR(100),
                precipitation NUMERIC(10, 2),
                temperature NUMERIC(10, 2),
                temp_max NUMERIC(10, 2),
                temp_min NUMERIC(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, latitude, longitude)
            )
        """,
        
        'news_articles': """
            CREATE TABLE IF NOT EXISTS news_articles (
                id SERIAL PRIMARY KEY,
                title TEXT,
                description TEXT,
                content TEXT,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                source VARCHAR(100),
                query_keyword VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        
        'trade_data': """
            CREATE TABLE IF NOT EXISTS trade_data (
                id SERIAL PRIMARY KEY,
                date DATE,
                exporter_country VARCHAR(100),
                importer_country VARCHAR(100),
                commodity VARCHAR(50),
                quantity NUMERIC(15, 2),
                value_usd NUMERIC(15, 2),
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    }
    
    for table_name, create_sql in tables.items():
        cursor.execute(create_sql)
        print(f"✓ Created table: {table_name}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✓ Database setup complete!")

if __name__ == "__main__":
    create_database()
```

**Action Items**:
- [ ] Add `DB_PASSWORD` to your `.env` file
- [ ] Run: `python src/database/setup_db.py`
- [ ] Verify tables: `psql -U postgres -d wheat_supply_chain -c "\dt"`

### 3.3 Load Raw Data into PostgreSQL

Create `src/database/load_data.py`:

```python
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def get_db_engine():
    """Create SQLAlchemy engine"""
    password = os.getenv('DB_PASSWORD')
    return create_engine(f'postgresql://postgres:{password}@localhost/wheat_supply_chain')

def load_wheat_prices():
    """Load FRED wheat prices into database"""
    engine = get_db_engine()
    
    # Find latest FRED CSV
    files = glob.glob('data/raw/fred_wheat_prices_*.csv')
    if not files:
        print("⚠ No wheat price data found")
        return
    
    latest_file = max(files)
    df = pd.read_csv(latest_file)
    
    # Clean and prepare
    df = df[['date', 'value']].copy()
    df.columns = ['date', 'price_index']
    df['date'] = pd.to_datetime(df['date'])
    df['source'] = 'FRED'
    df = df.dropna()
    
    # Load to database
    df.to_sql('wheat_prices', engine, if_exists='append', index=False)
    print(f"✓ Loaded {len(df)} wheat price records")

def load_weather_data():
    """Load NASA POWER weather data into database"""
    engine = get_db_engine()
    
    files = glob.glob('data/raw/weather_*.csv')
    if not files:
        print("⚠ No weather data found")
        return
    
    total_records = 0
    for file in files:
        df = pd.read_csv(file)
        
        # Prepare columns
        df = df.rename(columns={
            'PRECTOTCORR': 'precipitation',
            'T2M': 'temperature',
            'T2M_MAX': 'temp_max',
            'T2M_MIN': 'temp_min'
        })
        
        df['date'] = pd.to_datetime(df['date'])
        df['region'] = f"Lat:{df['latitude'].iloc[0]}, Lon:{df['longitude'].iloc[0]}"
        
        # Select relevant columns
        df = df[['date', 'latitude', 'longitude', 'region', 
                'precipitation', 'temperature', 'temp_max', 'temp_min']]
        
        df.to_sql('weather_data', engine, if_exists='append', index=False)
        total_records += len(df)
    
    print(f"✓ Loaded {total_records} weather records from {len(files)} regions")

def load_news_data():
    """Load NewsAPI articles into database"""
    engine = get_db_engine()
    
    files = glob.glob('data/raw/news_*.csv')
    if not files:
        print("⚠ No news data found")
        return
    
    total_records = 0
    for file in files:
        df = pd.read_csv(file)
        
        # Prepare columns
        df = df[['title', 'description', 'content', 'url', 
                'publishedAt', 'source', 'query']].copy()
        df.columns = ['title', 'description', 'content', 'url', 
                     'published_at', 'source', 'query_keyword']
        
        df['published_at'] = pd.to_datetime(df['published_at'])
        df['source'] = df['source'].astype(str)
        
        df.to_sql('news_articles', engine, if_exists='append', index=False)
        total_records += len(df)
    
    print(f"✓ Loaded {total_records} news articles")

def main():
    """Run all data loading"""
    print("\n" + "="*50)
    print("Loading data into PostgreSQL...")
    print("="*50 + "\n")
    
    load_wheat_prices()
    load_weather_data()
    load_news_data()
    
    print("\n✓ Data loading complete!")
    
    # Show summary
    engine = get_db_engine()
    with engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM wheat_prices")
        print(f"  - Wheat prices: {result.fetchone()[0]} records")
        
        result = conn.execute("SELECT COUNT(*) FROM weather_data")
        print(f"  - Weather data: {result.fetchone()[0]} records")
        
        result = conn.execute("SELECT COUNT(*) FROM news_articles")
        print(f"  - News articles: {result.fetchone()[0]} records")

if __name__ == "__main__":
    main()
```

**Action Items**:
- [ ] Run data loader: `python src/database/load_data.py`
- [ ] Verify data is loaded with SQL queries:
```sql
SELECT COUNT(*) FROM wheat_prices;
SELECT * FROM wheat_prices LIMIT 10;
SELECT * FROM weather_data LIMIT 10;
```

### 3.4 Create Utility Functions

Create `src/utils/db_utils.py`:

```python
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    """Get database engine"""
    password = os.getenv('DB_PASSWORD')
    return create_engine(f'postgresql://postgres:{password}@localhost/wheat_supply_chain')

def query_to_df(query):
    """Execute SQL query and return DataFrame"""
    engine = get_engine()
    return pd.read_sql(query, engine)

def get_latest_wheat_prices(days=30):
    """Get most recent wheat prices"""
    query = f"""
    SELECT date, price_index 
    FROM wheat_prices 
    ORDER BY date DESC 
    LIMIT {days}
    """
    return query_to_df(query)

def get_weather_by_region(region, start_date, end_date):
    """Get weather data for specific region and date range"""
    query = f"""
    SELECT * FROM weather_data
    WHERE region = '{region}'
    AND date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY date
    """
    return query_to_df(query)
```

**🎉 MILESTONE 3 COMPLETE!** You have a working data lake!

---

# 📍 MILESTONE 4: Data Cleaning & Processing
**Duration**: 5-6 days  
**Goal**: Clean, standardize, and enrich your raw data

## Steps

### 4.1 Exploratory Data Analysis (EDA)

Create `notebooks/01_eda_wheat_prices.ipynb`:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.db_utils import query_to_df

# Load data
df_prices = query_to_df("SELECT * FROM wheat_prices ORDER BY date")

# Basic info
print(df_prices.info())
print(df_prices.describe())

# Check for missing values
print("\nMissing values:")
print(df_prices.isnull().sum())

# Plot price trends
plt.figure(figsize=(12, 6))
plt.plot(df_prices['date'], df_prices['price_index'])
plt.title('Wheat Price Index Over Time')
plt.xlabel('Date')
plt.ylabel('Price Index')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Check for outliers (prices > 3 std deviations)
mean = df_prices['price_index'].mean()
std = df_prices['price_index'].std()
outliers = df_prices[abs(df_prices['price_index'] - mean) > 3 * std]
print(f"\nOutliers detected: {len(outliers)}")
```

**Action Items**:
- [ ] Create EDA notebooks for each data source
- [ ] Identify data quality issues (missing values, outliers, duplicates)
- [ ] Document findings in `docs/data_quality_report.md`
- [ ] **Hint**: Look for suspicious patterns (e.g., sudden spikes, flatlines)

### 4.2 Data Cleaning Pipeline

Create `src/processing/clean_data.py`:

```python
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from src.utils.db_utils import get_engine

class DataCleaner:
    def __init__(self):
        self.engine = get_engine()
    
    def clean_wheat_prices(self):
        """
        Clean wheat price data:
        - Remove duplicates
        - Handle missing values
        - Detect and handle outliers
        """
        df = pd.read_sql("SELECT * FROM wheat_prices", self.engine)
        
        print(f"Original records: {len(df)}")
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['date', 'source'])
        print(f"After removing duplicates: {len(df)}")
        
        # Handle missing values
        # Option 1: Forward fill (use previous value)
        df = df.sort_values('date')
        df['price_index'] = df['price_index'].fillna(method='ffill')
        
        # Option 2: Interpolate
        # df['price_index'] = df['price_index'].interpolate(method='linear')
        
        # Detect outliers using IQR method
        Q1 = df['price_index'].quantile(0.25)
        Q3 = df['price_index'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df['price_index'] < lower_bound) | 
                     (df['price_index'] > upper_bound)]
        print(f"Outliers detected: {len(outliers)}")
        
        # Option: Cap outliers instead of removing
        df['price_index'] = df['price_index'].clip(lower_bound, upper_bound)
        
        # Save to processed table
        df.to_sql('wheat_prices_clean', self.engine, 
                 if_exists='replace', index=False)
        
        print(f"✓ Cleaned data saved: {len(df)} records")
        return df
    
    def clean_weather_data(self):
        """
        Clean weather data:
        - Handle missing values
        - Remove invalid readings
        """
        df = pd.read_sql("SELECT * FROM weather_data", self.engine)
        
        print(f"Original records: {len(df)}")
        
        # Remove physically impossible values
        df = df[df['temperature'] > -100]  # Kelvin to Celsius conversion
        df = df[df['temperature'] < 60]    # Reasonable max temp
        df = df[df['precipitation'] >= 0]  # Negative rain doesn't exist
        
        # Fill missing weather values with region mean
        for col in ['precipitation', 'temperature']:
            df[col] = df.groupby('region')[col].transform(
                lambda x: x.fillna(x.mean())
            )
        
        df.to_sql('weather_data_clean', self.engine, 
                 if_exists='replace', index=False)
        
        print(f"✓ Cleaned data saved: {len(df)} records")
        return df
    
    def clean_news_data(self):
        """
        Clean news data:
        - Remove duplicates
        - Extract entities
        - Standardize text
        """
        df = pd.read_sql("SELECT * FROM news_articles", self.engine)
        
        print(f"Original records: {len(df)}")
        
        # Remove duplicates based on URL
        df = df.drop_duplicates(subset=['url'])
        
        # Remove articles with missing content
        df = df.dropna(subset=['title', 'content'])
        
        # Clean text fields
        for col in ['title', 'description', 'content']:
            if col in df.columns:
                df[col] = df[col].str.strip()
                df[col] = df[col].replace('\n', ' ', regex=True)
        
        df.to_sql('news_articles_clean', self.engine, 
                 if_exists='replace', index=False)
        
        print(f"✓ Cleaned data saved: {len(df)} records")
        return df

def main():
    cleaner = DataCleaner()
    
    print("\n" + "="*50)
    print("Cleaning data...")
    print("="*50 + "\n")
    
    cleaner.clean_wheat_prices()
    cleaner.clean_weather_data()
    cleaner.clean_news_data()
    
    print("\n✓ All data cleaned!")

if __name__ == "__main__":
    main()
```

**Action Items**:
- [ ] Run data cleaning: `python src/processing/clean_data.py`
- [ ] Verify cleaned tables exist in database
- [ ] Compare record counts before/after cleaning
- [ ] **Hint**: Document your cleaning decisions (why did you fill vs. drop?)

### 4.3 Data Enrichment

Create `src/processing/enrich_data.py`:

```python
import pandas as pd
from src.utils.db_utils import get_engine

def add_time_features():
    """
    Add temporal features to wheat prices
    """
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM wheat_prices_clean", engine)
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Add time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.dayofweek
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Is it harvest season? (June-August in Northern Hemisphere)
    df['is_harvest_season'] = df['month'].isin([6, 7, 8]).astype(int)
    
    # Calculate rolling statistics
    df = df.sort_values('date')
    df['price_7d_avg'] = df['price_index'].rolling(7, min_periods=1).mean()
    df['price_30d_avg'] = df['price_index'].rolling(30, min_periods=1).mean()
    df['price_volatility'] = df['price_index'].rolling(30, min_periods=1).std()
    
    # Save enriched data
    df.to_sql('wheat_prices_enriched', engine, 
             if_exists='replace', index=False)
    
    print(f"✓ Added time features to {len(df)} records")

def calculate_weather_aggregates():
    """
    Create regional weather aggregates
    """
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM weather_data_clean", engine)
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Weekly aggregates by region
    weekly = df.groupby(['region', pd.Grouper(key='date', freq='W')]).agg({
        'precipitation': ['mean', 'sum'],
        'temperature': ['mean', 'max', 'min'],
    }).reset_index()
    
    weekly.columns = ['region', 'week', 'precip_mean', 'precip_sum',
                     'temp_mean', 'temp_max', 'temp_min']
    
    # Identify extreme weather events
    weekly['is_drought'] = (weekly['precip_sum'] < 5).astype(int)  # Less than 5mm/week
    weekly['is_heatwave'] = (weekly['temp_max'] > 35).astype(int)  # Above 35°C
    weekly['is_freeze'] = (weekly['temp_min'] < 0).astype(int)     # Below 0°C
    
    weekly.to_sql('weather_weekly_aggregates', engine, 
                 if_exists='replace', index=False)
    
    print(f"✓ Created {len(weekly)} weekly weather aggregates")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Enriching data...")
    print("="*50 + "\n")
    
    add_time_features()
    calculate_weather_aggregates()
    
    print("\n✓ Data enrichment complete!")
```

**Action Items**:
- [ ] Run enrichment: `python src/processing/enrich_data.py`
- [ ] Verify new tables and columns are created
- [ ] **Hint**: Think about what other features might be useful (price changes, lagged features)

**🎉 MILESTONE 4 COMPLETE!** Your data is now clean and enriched!

---

# 📍 MILESTONE 5: Feature Engineering for ML
**Duration**: 5-6 days  
**Goal**: Create the final feature set for machine learning models

## Steps

### 5.1 Define Prediction Targets

Create `docs/ml_targets.md`:

```markdown
# ML Prediction Targets

## 1. Price Spike Prediction (Classification)
**Target**: Binary classification (0 = normal, 1 = spike)
**Definition**: Price spike = price increase > 10% within 7 days
**Use Case**: Alert traders/buyers of upcoming price jumps

## 2. Price Forecasting (Regression)
**Target**: Wheat price index value
**Timeframe**: Predict 7, 30, 90 days ahead
**Use Case**: Budget planning, inventory decisions

## 3. Supply Disruption (Classification)
**Target**: Multi-class (0=Normal, 1=Minor, 2=Major disruption)
**Definition**: Based on news sentiment and shipping data
**Use Case**: Supply chain risk assessment
```

**Action Items**:
- [ ] Define your prediction targets clearly
- [ ] Document the business value of each prediction

### 5.2 Create Feature Store

Create `src/features/build_features.py`:

```python
import pandas as pd
import numpy as np
from src.utils.db_utils import get_engine
from sqlalchemy import text

class FeatureBuilder:
    def __init__(self):
        self.engine = get_engine()
    
    def create_price_target(self, df, horizon=7, threshold=0.10):
        """
        Create binary target: 1 if price increases by threshold% 
        within horizon days
        """
        df = df.sort_values('date').copy()
        
        # Calculate future price change
        df['future_price'] = df['price_index'].shift(-horizon)
        df['price_change_pct'] = (
            (df['future_price'] - df['price_index']) / df['price_index']
        )
        
        # Binary target
        df['price_spike'] = (df['price_change_pct'] > threshold).astype(int)
        
        # Regression target (actual future price)
        df['target_price'] = df['future_price']
        
        return df
    
    def merge_weather_features(self, df_prices):
        """
        Merge weather data with prices
        """
        # Load weather aggregates
        df_weather = pd.read_sql(
            "SELECT * FROM weather_weekly_aggregates", 
            self.engine
        )
        
        # Convert to weekly frequency for merging
        df_prices['week'] = pd.to_datetime(df_prices['date']).dt.to_period('W')
        df_weather['week'] = pd.to_datetime(df_weather['week']).dt.to_period('W')
        
        # Pivot weather by region (one column per region)
        weather_pivot = df_weather.pivot_table(
            index='week',
            columns='region',
            values=['precip_mean', 'temp_mean', 'is_drought', 'is_heatwave'],
            aggfunc='mean'
        )
        
        # Flatten column names
        weather_pivot.columns = [
            f'{col[0]}_{col[1]}'.replace(' ', '_').replace(':', '')
            for col in weather_pivot.columns
        ]
        
        # Merge
        df_merged = df_prices.merge(
            weather_pivot,
            left_on='week',
            right_index=True,
            how='left'
        )
        
        return df_merged
    
    def add_lagged_features(self, df, columns=['price_index'], lags=[1, 7, 30]):
        """
        Add lagged values as features
        """
        for col in columns:
            for lag in lags:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    def add_news_sentiment(self, df_prices):
        """
        Add aggregated news sentiment features
        """
        # Load news data
        df_news = pd.read_sql(
            "SELECT * FROM news_articles_clean", 
            self.engine
        )
        
        # Simple sentiment: count of articles per day with keywords
        df_news['date'] = pd.to_datetime(df_news['published_at']).dt.date
        
        # Count articles mentioning disruption keywords
        disruption_keywords = ['ban', 'shortage', 'crisis', 'disruption', 
                              'blockade', 'conflict']
        
        df_news['is_disruption'] = df_news['title'].str.contains(
            '|'.join(disruption_keywords), 
            case=False, 
            na=False
        ).astype(int)
        
        # Daily aggregates
        news_daily = df_news.groupby('date').agg({
            'is_disruption': 'sum',
            'title': 'count'
        }).reset_index()
        
        news_daily.columns = ['date', 'disruption_news_count', 'total_news_count']
        news_daily['disruption_ratio'] = (
            news_daily['disruption_news_count'] / 
            news_daily['total_news_count']
        )
        
        # Merge with prices
        df_prices['date'] = pd.to_datetime(df_prices['date']).dt.date
        df_merged = df_prices.merge(news_daily, on='date', how='left')
        
        # Fill missing news counts with 0
        df_merged[['disruption_news_count', 'total_news_count']] = (
            df_merged[['disruption_news_count', 'total_news_count']].fillna(0)
        )
        
        return df_merged
    
    def build_ml_dataset(self):
        """
        Create final ML-ready dataset
        """
        print("\nBuilding ML dataset...")
        
        # 1. Load enriched prices
        df = pd.read_sql("SELECT * FROM wheat_prices_enriched", self.engine)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        print(f"Loaded {len(df)} price records")
        
        # 2. Create targets
        df = self.create_price_target(df, horizon=7, threshold=0.10)
        df = self.create_price_target(df, horizon=30, threshold=0.15)
        
        # 3. Add lagged features
        df = self.add_lagged_features(
            df, 
            columns=['price_index', 'price_volatility'],
            lags=[1, 7, 14, 30]
        )
        
        # 4. Merge weather features
        df = self.merge_weather_features(df)
        
        # 5. Add news sentiment
        df = self.add_news_sentiment(df)
        
        # 6. Drop rows with NaN (from lagging/shifting)
        print(f"Before dropping NaN: {len(df)}")
        df = df.dropna()
        print(f"After dropping NaN: {len(df)}")
        
        # 7. Save to database
        df.to_sql('ml_features', self.engine, 
                 if_exists='replace', index=False)
        
        print(f"\n✓ ML dataset created: {len(df)} samples, {len(df.columns)} features")
        
        # Save to CSV for easy access
        df.to_csv('data/processed/ml_features.csv', index=False)
        print("✓ Saved to data/processed/ml_features.csv")
        
        return df

if __name__ == "__main__":
    builder = FeatureBuilder()
    df = builder.build_ml_dataset()
    
    print("\nFeature columns:")
    print(df.columns.tolist())
    
    print("\nTarget distribution (7-day price spike):")
    print(df['price_spike'].value_counts())
```

**Action Items**:
- [ ] Run feature builder: `python src/features/build_features.py`
- [ ] Inspect `ml_features` table in database
- [ ] Check CSV file: `data/processed/ml_features.csv`
- [ ] **Hint**: You should have ~50-100 features. More isn't always better!

### 5.3 Feature Analysis

Create `notebooks/02_feature_analysis.ipynb`:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# Load ML features
df = pd.read_csv('data/processed/ml_features.csv')

# 1. Feature correlation with target
target = 'price_spike'
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

correlations = {}
for col in numeric_cols:
    if col != target and df[col].notna().sum() > 0:
        corr, _ = pearsonr(df[col].dropna(), df[target].dropna())
        correlations[col] = corr

# Plot top correlations
corr_series = pd.Series(correlations).sort_values(ascending=False)
top_20 = corr_series.head(20)

plt.figure(figsize=(10, 8))
top_20.plot(kind='barh')
plt.title('Top 20 Features Correlated with Price Spike')
plt.xlabel('Correlation')
plt.tight_layout()
plt.show()

# 2. Feature importance (using Random Forest)
from sklearn.ensemble import RandomForestClassifier

feature_cols = [col for col in numeric_cols if col not in ['price_spike', 'target_price']]
X = df[feature_cols].fillna(0)
y = df[target]

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 15 Important Features:")
print(feature_importance.head(15))
```

**Action Items**:
- [ ] Run feature analysis in notebook
- [ ] Identify top 10-15 most important features
- [ ] Document findings in `docs/feature_importance.md`
- [ ] **Hint**: Remove features with near-zero importance to simplify model

**🎉 MILESTONE 5 COMPLETE!** You have ML-ready features!

---

# 📍 MILESTONE 6: ML Model Development
**Duration**: 7-8 days  
**Goal**: Build, train, and evaluate prediction models

## Steps

### 6.1 Train-Test Split

Create `src/models/prepare_data.py`:

```python
import pandas as pd
from sklearn.model_selection import train_test_split, TimeSeriesSplit
import joblib

def prepare_ml_data(test_size=0.2):
    """
    Load and split data for ML
    """
    df = pd.read_csv('data/processed/ml_features.csv')
    
    # Define features and targets
    target_cols = ['price_spike', 'target_price']
    exclude_cols = ['date', 'week'] + target_cols
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].fillna(0)
    y_classification = df['price_spike']
    y_regression = df['target_price']
    
    # Time-based split (important for time series!)
    # Don't use random split - it leaks future info into training
    split_idx = int(len(df) * (1 - test_size))
    
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    
    y_class_train = y_classification.iloc[:split_idx]
    y_class_test = y_classification.iloc[split_idx:]
    
    y_reg_train = y_regression.iloc[:split_idx]
    y_reg_test = y_regression.iloc[split_idx:]
    
    print(f"Train size: {len(X_train)}")
    print(f"Test size: {len(X_test)}")
    print(f"Features: {len(feature_cols)}")
    
    # Save for later use
    data = {
        'X_train': X_train,
        'X_test': X_test,
        'y_class_train': y_class_train,
        'y_class_test': y_class_test,
        'y_reg_train': y_reg_train,
        'y_reg_test': y_reg_test,
        'feature_names': feature_cols
    }
    
    joblib.dump(data, 'data/processed/train_test_data.pkl')
    print("\n✓ Data prepared and saved")
    
    return data

if __name__ == "__main__":
    prepare_ml_data()
```

**Action Items**:
- [ ] Run data preparation
- [ ] Verify train/test split makes sense (test is most recent data)

### 6.2 Price Spike Classification Model

Create `src/models/train_classifier.py`:

```python
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def train_classification_models():
    """
    Train multiple classifiers and compare
    """
    # Load data
    data = joblib.load('data/processed/train_test_data.pkl')
    
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_class_train']
    y_test = data['y_class_test']
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Models to try
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(
            n_estimators=100, 
            max_depth=10,
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        print(f"{'='*50}")
        
        # Train
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Evaluate
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"ROC AUC Score: {roc_auc:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {name}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(f'data/processed/{name.replace(" ", "_")}_confusion_matrix.png')
        plt.close()
        
        # Save results
        results[name] = {
            'model': model,
            'roc_auc': roc_auc,
            'predictions': y_pred
        }
    
    # Save best model
    best_model_name = max(results, key=lambda x: results[x]['roc_auc'])
    best_model = results[best_model_name]['model']
    
    joblib.dump(best_model, 'data/processed/best_classifier.pkl')
    joblib.dump(scaler, 'data/processed/scaler.pkl')
    
    print(f"\n✓ Best model: {best_model_name}")
    print(f"✓ ROC AUC: {results[best_model_name]['roc_auc']:.4f}")
    print(f"✓ Model saved to data/processed/best_classifier.pkl")
    
    return results

if __name__ == "__main__":
    results = train_classification_models()
```

**Action Items**:
- [ ] Run classifier training: `python src/models/train_classifier.py`
- [ ] Review classification reports
- [ ] Check confusion matrices
- [ ] **Hint**: Imbalanced data? Try class weights or SMOTE

### 6.3 Price Forecasting Model

Create `src/models/train_regressor.py`:

```python
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

def train_regression_models():
    """
    Train price forecasting models
    """
    data = joblib.load('data/processed/train_test_data.pkl')
    
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_reg_train'].dropna()
    y_test = data['y_reg_test'].dropna()
    
    # Align X with y (due to dropna)
    X_train = X_train.loc[y_train.index]
    X_test = X_test.loc[y_test.index]
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        print(f"{'='*50}")
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        # Plot predictions vs actual
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], 
                [y_test.min(), y_test.max()], 
                'r--', lw=2)
        plt.xlabel('Actual Price')
        plt.ylabel('Predicted Price')
        plt.title(f'{name} - Predictions vs Actual')
        plt.tight_layout()
        plt.savefig(f'data/processed/{name.replace(" ", "_")}_predictions.png')
        plt.close()
        
        results[name] = {
            'model': model,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }
    
    # Save best model (lowest RMSE)
    best_model_name = min(results, key=lambda x: results[x]['rmse'])
    best_model = results[best_model_name]['model']
    
    joblib.dump(best_model, 'data/processed/best_regressor.pkl')
    
    print(f"\n✓ Best model: {best_model_name}")
    print(f"✓ RMSE: {results[best_model_name]['rmse']:.4f}")
    
    return results

if __name__ == "__main__":
    results = train_regression_models()
```

**Action Items**:
- [ ] Run regressor training: `python src/models/train_regressor.py`
- [ ] Compare MAE, RMSE, R² scores
- [ ] Check prediction plots
- [ ] **Hint**: Try different tree depths and learning rates

### 6.4 Model Evaluation & Tuning

Create `notebooks/03_model_evaluation.ipynb`:

```python
import joblib
import pandas as pd
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier

# Load data
data = joblib.load('data/processed/train_test_data.pkl')
X_train = data['X_train']
y_train = data['y_class_train']

# Hyperparameter tuning
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf = RandomForestClassifier(random_state=42)

grid_search = GridSearchCV(
    rf, 
    param_grid, 
    cv=5, 
    scoring='roc_auc',
    n_jobs=-1,
    verbose=2
)

print("Starting hyperparameter search...")
grid_search.fit(X_train, y_train)

print(f"\nBest parameters: {grid_search.best_params_}")
print(f"Best ROC AUC: {grid_search.best_score_:.4f}")

# Save tuned model
joblib.dump(grid_search.best_estimator_, 'data/processed/tuned_classifier.pkl')
```

**Action Items**:
- [ ] Run hyperparameter tuning (may take hours!)
- [ ] Perform cross-validation
- [ ] Document final model performance in `docs/model_evaluation.md`

**🎉 MILESTONE 6 COMPLETE!** You have trained ML models!

---

# 📍 MILESTONE 7: Pipeline Automation
**Duration**: 4-5 days  
**Goal**: Automate the entire pipeline with Apache Airflow

## Steps

### 7.1 Install Apache Airflow

```bash
# Create airflow directory
mkdir airflow
cd airflow

# Set AIRFLOW_HOME
export AIRFLOW_HOME=$(pwd)

# Install Airflow
pip install apache-airflow==2.7.0
pip install apache-airflow-providers-postgres

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

**Action Items**:
- [ ] Install Airflow
- [ ] Create admin user
- [ ] Start Airflow: `airflow webserver -p 8080` and `airflow scheduler`
- [ ] Access UI: http://localhost:8080

### 7.2 Create DAG for Daily Pipeline

Create `airflow/dags/wheat_pipeline_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
sys.path.append('/path/to/wheat-supply-chain')

from src.ingestion.run_daily_ingestion import run_daily_collection
from src.database.load_data import main as load_data
from src.processing.clean_data import main as clean_data
from src.features.build_features import FeatureBuilder

# Default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'wheat_supply_chain_pipeline',
    default_args=default_args,
    description='Daily wheat supply chain data pipeline',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    start_date=days_ago(1),
    catchup=False,
    tags=['wheat', 'supply-chain', 'ml'],
)

# Tasks
task_collect = PythonOperator(
    task_id='collect_data',
    python_callable=run_daily_collection,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_to_database',
    python_callable=load_data,
    dag=dag,
)

task_clean = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    dag=dag,
)

def build_features():
    builder = FeatureBuilder()
    builder.build_ml_dataset()

task_features = PythonOperator(
    task_id='build_features',
    python_callable=build_features,
    dag=dag,
)

def make_predictions():
    import joblib
    import pandas as pd
    
    # Load latest features
    df = pd.read_csv('data/processed/ml_features.csv')
    latest = df.iloc[-1:]  # Most recent row
    
    # Load model
    model = joblib.load('data/processed/best_classifier.pkl')
    
    # Predict
    X = latest.drop(['date', 'price_spike', 'target_price'], axis=1).fillna(0)
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0][1]
    
    print(f"\n{'='*50}")
    print(f"PREDICTION FOR NEXT 7 DAYS:")
    print(f"Price Spike Likely: {'YES' if prediction == 1 else 'NO'}")
    print(f"Probability: {probability:.2%}")
    print(f"{'='*50}\n")
    
    # Save prediction
    result = {
        'date': pd.Timestamp.now(),
        'prediction': prediction,
        'probability': probability
    }
    pd.DataFrame([result]).to_csv('data/processed/latest_prediction.csv', index=False)

task_predict = PythonOperator(
    task_id='make_prediction',
    python_callable=make_predictions,
    dag=dag,
)

# Define dependencies
task_collect >> task_load >> task_clean >> task_features >> task_predict
```

**Action Items**:
- [ ] Create DAG file
- [ ] Update file paths in DAG
- [ ] Enable DAG in Airflow UI
- [ ] Test run manually
- [ ] **Hint**: Check logs in Airflow UI if tasks fail

### 7.3 Add Monitoring & Alerts

Create `src/monitoring/monitor.py`:

```python
import smtplib
from email.mime.text import MIMEText
import pandas as pd

def send_alert(subject, message):
    """
    Send email alert (configure with your SMTP settings)
    """
    # Configure email settings in .env
    sender = "your_email@gmail.com"
    recipient = "alert_recipient@gmail.com"
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    # Use your email provider's SMTP (example: Gmail)
    # You'll need to enable "less secure apps" or use app password
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, 'your_password')
            server.send_message(msg)
        print("✓ Alert sent")
    except Exception as e:
        print(f"✗ Failed to send alert: {e}")

def check_for_alerts():
    """
    Check latest predictions and send alerts if needed
    """
    df = pd.read_csv('data/processed/latest_prediction.csv')
    latest = df.iloc[-1]
    
    if latest['prediction'] == 1 and latest['probability'] > 0.7:
        message = f"""
        WHEAT PRICE ALERT
        
        High probability ({latest['probability']:.1%}) of price spike 
        in next 7 days.
        
        Recommended action:
        - Review inventory levels
        - Consider forward purchasing
        - Monitor news for disruption events
        """
        send_alert("Wheat Price Spike Alert", message)

if __name__ == "__main__":
    check_for_alerts()
```

**Action Items**:
- [ ] Configure email settings (optional)
- [ ] Add monitoring task to DAG
- [ ] Test alert system

**🎉 MILESTONE 7 COMPLETE!** Your pipeline is automated!

---

# 📍 MILESTONE 8: Analytics Dashboard
**Duration**: 5-6 days  
**Goal**: Create interactive dashboard for insights

## Steps

### 8.1 Install Dashboard Framework

```bash
pip install streamlit plotly dash
```

### 8.2 Create Streamlit Dashboard

Create `dashboard/app.py`:

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils.db_utils import query_to_df
import joblib

st.set_page_config(page_title="Wheat Supply Chain Monitor", layout="wide")

st.title("🌾 Wheat Supply Chain Disruption Monitor")

# Sidebar
st.sidebar.header("Controls")
days_to_show = st.sidebar.slider("Days to Display", 30, 365, 90)

# Load data
@st.cache_data
def load_data():
    df_prices = query_to_df("SELECT * FROM wheat_prices_clean ORDER BY date")
    df_features = pd.read_csv('data/processed/ml_features.csv')
    return df_prices, df_features

df_prices, df_features = load_data()

# Filter by date range
df_prices_filtered = df_prices[df_prices['date'] >= 
    pd.Timestamp.now() - pd.Timedelta(days=days_to_show)]

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

current_price = df_prices_filtered['price_index'].iloc[-1]
price_change = (
    (df_prices_filtered['price_index'].iloc[-1] - 
     df_prices_filtered['price_index'].iloc[-30]) / 
    df_prices_filtered['price_index'].iloc[-30] * 100
)

col1.metric("Current Wheat Price Index", f"{current_price:.2f}")
col2.metric("30-Day Change", f"{price_change:+.1f}%")

# Load latest prediction
try:
    latest_pred = pd.read_csv('data/processed/latest_prediction.csv')
    spike_prob = latest_pred['probability'].iloc[-1]
    col3.metric("7-Day Spike Probability", f"{spike_prob:.1%}")
    
    if spike_prob > 0.7:
        col4.error("⚠️ High Alert")
    elif spike_prob > 0.4:
        col4.warning("⚡ Watch")
    else:
        col4.success("✅ Normal")
except:
    col3.metric("7-Day Spike Probability", "N/A")
    col4.info("ℹ️ No prediction")

# Price trend chart
st.subheader("📈 Wheat Price Trend")
fig_price = px.line(df_prices_filtered, x='date', y='price_index',
                   title='Wheat Price Index Over Time')
fig_price.add_hline(y=df_prices_filtered['price_index'].mean(), 
                   line_dash="dash", line_color="red",
                   annotation_text="Average")
st.plotly_chart(fig_price, use_container_width=True)

# Weather impact
st.subheader("🌡️ Weather Conditions in Key Regions")
col1, col2 = st.columns(2)

# Placeholder - replace with actual weather data
weather_data = {
    'Region': ['US Great Plains', 'Ukraine', 'Russia', 'Australia'],
    'Drought Risk': [20, 45, 15, 30],
    'Temp Alert': [False, True, False, False]
}
df_weather = pd.DataFrame(weather_data)

fig_weather = px.bar(df_weather, x='Region', y='Drought Risk',
                    title='Drought Risk by Region (%)',
                    color='Temp Alert',
                    color_discrete_map={True: 'red', False: 'green'})
col1.plotly_chart(fig_weather, use_container_width=True)

# News sentiment
st.subheader("📰 Recent Disruption News")
try:
    df_news = query_to_df("""
        SELECT title, published_at, url 
        FROM news_articles_clean 
        WHERE query_keyword LIKE '%disruption%'
        ORDER BY published_at DESC 
        LIMIT 10
    """)
    st.dataframe(df_news, use_container_width=True)
except:
    st.info("No recent news data available")

# Feature importance
st.subheader("🎯 Top Predictive Factors")
try:
    model = joblib.load('data/processed/best_classifier.pkl')
    data = joblib.load('data/processed/train_test_data.pkl')
    
    importance_df = pd.DataFrame({
        'Feature': data['feature_names'],
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False).head(10)
    
    fig_importance = px.bar(importance_df, x='Importance', y='Feature',
                           orientation='h',
                           title='Top 10 Predictive Features')
    st.plotly_chart(fig_importance, use_container_width=True)
except:
    st.info("Model feature importance not available")

# Footer
st.markdown("---")
st.caption("Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
```

**Action Items**:
- [ ] Create dashboard file
- [ ] Run: `streamlit run dashboard/app.py`
- [ ] Access at: http://localhost:8501
- [ ] Customize visualizations
- [ ] **Hint**: Add more interactive filters and drill-down capabilities

### 8.3 Deploy Dashboard (Optional)

**Option 1: Streamlit Cloud** (Free)
```bash
# Push code to GitHub
git add .
git commit -m "Add dashboard"
git push origin main

# Deploy on streamlit.io
# - Sign in with GitHub
# - Select your repo
# - Click Deploy
```

**Option 2: Docker**
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py"]
```

```bash
docker build -t wheat-dashboard .
docker run -p 8501:8501 wheat-dashboard
```

**🎉 MILESTONE 8 COMPLETE!** You have a working dashboard!

---

# 📍 MILESTONE 9: Documentation & Deployment
**Duration**: 3-4 days  
**Goal**: Document everything and prepare for production

## Steps

### 9.1 Create Comprehensive Documentation

Create `README.md`:
```markdown
# Wheat Supply Chain Disruption Predictor

## Overview
An end-to-end data engineering and ML project that predicts wheat price spikes 
and supply disruptions using real-time data from weather, shipping, news, and 
trade sources.

## Features
- Real-time data ingestion from 6+ APIs
- Automated data pipeline (Apache Airflow)
- ML models: Price spike classification, Price forecasting
- Interactive dashboard (Streamlit)
- Predictive alerts

## Architecture
[Include system diagram]

## Installation
[Step-by-step setup instructions]

## Usage
[How to run the pipeline]

## Model Performance
- Price Spike Classifier: ROC AUC = 0.85
- Price Forecaster: RMSE = 12.3

## Data Sources
- USDA PSD: Production data
- FRED: Price indices
- NASA POWER: Weather data
- NewsAPI: Geopolitical events

## License
MIT
```

Create `docs/` with:
- `architecture.md`: System design
- `data_dictionary.md`: All tables and columns
- `model_cards.md`: Model details
- `api_documentation.md`: How to use your APIs

### 9.2 Add Unit Tests

Create `tests/test_ingestion.py`:
```python
import pytest
from src.ingestion.fred_collector import FREDCollector

def test_fred_collector():
    collector = FREDCollector()
    df = collector.get_wheat_prices()
    
    assert df is not None
    assert len(df) > 0
    assert 'price_index' in df.columns
    assert df['price_index'].notna().all()

# Add more tests for each module
```

Run tests:
```bash
pytest tests/
```

### 9.3 Create Requirements File

Update `requirements.txt` with ALL dependencies:
```txt
# Core
pandas==2.1.0
numpy==1.24.0
scikit-learn==1.3.0

# Database
psycopg2-binary==2.9.7
sqlalchemy==2.0.20

# API & Web
requests==2.31.0
beautifulsoup4==4.12.2

# ML & Visualization
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.17.0
streamlit==1.27.0

# Automation
apache-airflow==2.7.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
joblib==1.3.2

# Testing
pytest==7.4.0
```

### 9.4 Production Deployment Checklist

**Option 1: AWS Deployment**
- [ ] Set up EC2 instance
- [ ] Install dependencies
- [ ] Configure RDS for PostgreSQL
- [ ] Set up S3 for data storage
- [ ] Schedule pipeline with Airflow
- [ ] Deploy dashboard on ECS/Fargate

**Option 2: Google Cloud**
- [ ] Use Cloud SQL for database
- [ ] Cloud Storage for data lake
- [ ] Cloud Composer for Airflow
- [ ] Cloud Run for dashboard

**Security**:
- [ ] Move all credentials to AWS Secrets Manager / GCP Secret Manager
- [ ] Enable SSL for database connections
- [ ] Set up VPC and security groups
- [ ] Implement authentication for dashboard

**Monitoring**:
- [ ] Set up CloudWatch / Stackdriver logs
- [ ] Create alerts for pipeline failures
- [ ] Monitor API rate limits
- [ ] Track model performance drift

---

## 🎓 Learning Checkpoints & Self-Assessment

After completing the project, you should be able to:

### Data Engineering
✅ Collect data from multiple APIs  
✅ Design and implement a data lake (PostgreSQL)  
✅ Build ETL pipelines  
✅ Handle data quality issues (missing values, outliers, duplicates)  
✅ Create scheduled workflows with Airflow  

### Machine Learning
✅ Perform feature engineering for time series  
✅ Train classification and regression models  
✅ Evaluate model performance (precision, recall, RMSE, R²)  
✅ Tune hyperparameters  
✅ Deploy ML models in production  

### Software Engineering
✅ Write clean, modular Python code  
✅ Use version control (Git)  
✅ Write unit tests  
✅ Create documentation  
✅ Containerize applications (Docker)  

### Cloud & DevOps
✅ Deploy applications on cloud platforms  
✅ Set up monitoring and alerts  
✅ Manage secrets and credentials securely  

---

## 🚀 Next Steps & Extensions

Once you complete the core project, consider these advanced features:

1. **Add More Data Sources**
   - Shipping vessel tracking (MarineTraffic API)
   - Satellite imagery for crop health (Sentinel Hub)
   - Social media sentiment (Twitter API)

2. **Advanced ML Techniques**
   - LSTM/GRU for time series forecasting
   - Ensemble methods
   - Online learning for real-time updates

3. **Real-Time Streaming**
   - Use Apache Kafka for real-time data ingestion
   - Stream processing with Apache Spark

4. **GraphQL API**
   - Build API for others to query your predictions
   - Monetize predictions (subscription model)

5. **Mobile App**
   - Create alerts app for commodity traders
   - Push notifications for high-risk events

---

## 📚 Additional Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Hands-On Machine Learning" by Aurélien Géron

### Online Courses
- Fast.ai: Practical Deep Learning
- Coursera: Machine Learning Specialization

### Communities
- r/datascience
- r/MachineLearning
- Kaggle forums

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't over-engineer early**: Start simple, add complexity later
2. **API rate limits**: Cache responses, be respectful
3. **Data leakage**: Never use future data in training
4. **Overfitting**: Use cross-validation, regularization
5. **Ignoring time series properties**: Use time-based splits
6. **Hardcoding credentials**: Always use environment variables
7. **No error handling**: Wrap API calls in try-except
8. **Skipping documentation**: Document as you go

---

## 🎯 Success Criteria

Your project is complete when:

✅ Data pipeline runs automatically daily  
✅ ML models make predictions with > 70% accuracy  
✅ Dashboard shows real-time insights  
✅ Code is on GitHub with proper documentation  
✅ You can explain every design decision  

---

**Good luck on your learning journey! 🚀**

Remember: The goal isn't perfection, it's learning. Make mistakes, iterate, improve!

---

## 📞 Need Help?

If stuck:
1. Check logs in Airflow UI
2. Print intermediate results
3. Google error messages
4. Ask on Stack Overflow
5. Review documentation of APIs/libraries

**Most importantly: HAVE FUN BUILDING! 🌾**
