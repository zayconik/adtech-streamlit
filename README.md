# AdTech Analytics Dashboard

A comprehensive Streamlit dashboard for analyzing advertising campaign performance across multiple dimensions.

## Features

- **Campaign Summary Dashboard**
  - Key performance indicators (KPIs)
  - Top campaigns by spend and conversions
  - Spend trends over time
  - Brand distribution analysis

- **Campaign Performance Dashboard**
  - Geographic performance analysis
  - Time series analysis
  - Detailed campaign metrics
  - Interactive filters

- **Creative Performance Dashboard**
  - Creative-level performance metrics
  - Regional distribution analysis
  - Detailed creative metrics
  - Performance visualizations

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your data file:
- Rename your Parquet file to `data.parquet`
- Place it in the root directory of the project

4. Run the application:
```bash
streamlit run app.py
```

## Data Requirements

The application expects a Parquet file with the following columns:
- date
- campaign_id
- ad_id
- brand
- country
- state
- city
- impressions
- clicks
- conversions
- spend

## Usage

1. Use the sidebar filters to select:
   - Date range
   - Brands
   - Campaigns
   - Countries

2. Navigate between tabs to view different aspects of the data:
   - Campaign Summary: Overview of campaign performance
   - Campaign Performance: Detailed campaign analysis
   - Creative Performance: Ad-level performance metrics

3. Download filtered data using the "Download CSV" button in each section

## Development

The application is structured into multiple modules:
- `app.py`: Main application file
- `utils.py`: Common utility functions
- `campaign_summary.py`: Campaign summary dashboard
- `campaign_performance.py`: Campaign performance dashboard
- `creative_performance.py`: Creative performance dashboard 