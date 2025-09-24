# Cybersecurity Job Scraper

A comprehensive, full-featured job scraper specifically designed to find cybersecurity and information security positions from multiple job boards with advanced analytics and reporting capabilities.

## 🚀 Features

### Core Functionality
- **Multi-source scraping**: Indeed, LinkedIn, Glassdoor
- **Smart filtering**: 40+ cybersecurity keywords and job titles
- **Modern web interface**: Beautiful, responsive web UI with real-time progress
- **PDF reports**: Professional PDF reports with statistics and job listings
- **Data visualization**: Charts and analytics for job market insights
- **Multiple export formats**: CSV, JSON, PDF, and PNG charts
- **Command-line interface**: Full CLI with customizable options
- **Real-time progress**: Live progress tracking during scraping
- **Background processing**: Non-blocking scraping with status updates
- **Respectful scraping**: Built-in delays and proper headers

### 🆕 Advanced Filtering Options
- **Time Filters**: 24 hours, 3 days, 7 days, 14 days, 30 days
- **Experience Levels**: Entry Level, Internship, Mid Level, Senior Level
- **Job Board Selection**: Choose which sources to scrape (Indeed, LinkedIn, Glassdoor)
- **Sponsored Jobs**: Detect and flag sponsored job postings
- **Company Extraction**: Improved company name extraction (fixed Indeed "Unknown" issue)

### 🆕 Enhanced Outputs
- **PDF Reports**: Include direct job posting links for easy application
- **Data Analytics**: Comprehensive statistics and breakdowns
- **Visual Charts**: Professional charts showing job distribution
- **Real-time Progress**: Live updates during scraping process

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 🌐 Web Interface (Recommended)

Start the web application:
```bash
./start.sh
# or
venv/bin/python3 web_app.py
```

Then open your browser and go to `http://localhost:5001`

Features:
- Real-time scraping progress
- Beautiful, modern interface
- Export to CSV, JSON, PDF, and PNG
- Live statistics and analytics
- Background processing

### 💻 Command Line Usage

Run the scraper directly:
```bash
# Basic scraping
venv/bin/python3 job_scraper.py

# Enhanced CLI with new filtering options
venv/bin/python3 cli.py --location "San Francisco" --sources indeed --pages 3 --output pdf

# Find entry-level jobs from last 24 hours
venv/bin/python3 cli.py --sources linkedin --time-filter 24h --experience entry

# Find internships from all sources
venv/bin/python3 cli.py --sources all --experience internship --time-filter 7d

# Find senior-level jobs from LinkedIn only
venv/bin/python3 cli.py --sources linkedin --experience senior --pages 5

# Start web interface after scraping
venv/bin/python3 cli.py --web
```

CLI Options:
- `--location` or `-l`: Location to search (default: "United States")
- `--sources` or `-s`: Sources to scrape (indeed, linkedin, glassdoor, all)
- `--time-filter` or `-t`: Time filter (24h, 3d, 7d, 14d, 30d)
- `--experience` or `-e`: Experience level (all, entry, internship, mid, senior)
- `--output` or `-o`: Output format (csv, json, pdf, all)
- `--pages` or `-p`: Number of pages per source (default: 3)
- `--web` or `-w`: Start web interface after scraping

## Configuration

The scraper looks for cybersecurity-related keywords including:
- cybersecurity, cyber security, information security
- security engineer, security analyst, penetration tester
- SOC analyst, incident response, threat hunter
- And many more...

## Job Sources

1. **Indeed**: Primary source with detailed job descriptions
2. **LinkedIn**: Professional network job postings
3. **Glassdoor**: Company reviews and job listings

## 📊 Output Files

The scraper generates multiple output formats:

- **CSV files**: `cybersecurity_jobs_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- **JSON files**: `cybersecurity_jobs_YYYYMMDD_HHMMSS.json` - Structured data
- **PDF reports**: `cybersecurity_jobs_report_YYYYMMDD_HHMMSS.pdf` - Professional reports
- **Analytics charts**: `jobs_analysis_YYYYMMDD_HHMMSS.png` - Visual analytics

## 🌐 Web Interface Features

- **Real-time scraping**: Live progress tracking with status updates
- **Modern UI**: Beautiful, responsive design with Bootstrap 5
- **Multiple exports**: CSV, JSON, PDF reports, and PNG charts
- **Live statistics**: Real-time job market analytics
- **Background processing**: Non-blocking scraping operations
- **Direct job links**: Click through to original job postings
- **Search customization**: Adjustable location and page limits

## Ethical Considerations

This scraper includes:
- Respectful delays between requests
- Proper User-Agent headers
- Rate limiting to avoid overwhelming servers
- Focus on publicly available job postings

## Legal Notice

Please ensure you comply with the terms of service of the websites you're scraping. This tool is for educational and personal use only.

## Troubleshooting

1. **No jobs found**: Try adjusting the location or search terms
2. **Rate limiting**: The scraper includes delays, but you may need to increase them
3. **Website changes**: Job board structures may change, requiring code updates

## Contributing

Feel free to contribute by:
- Adding new job sources
- Improving the cybersecurity keyword detection
- Enhancing the web interface
- Adding new export formats

## License

This project is for educational purposes. Please respect the terms of service of job board websites.
