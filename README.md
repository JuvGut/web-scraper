# Schlussgang Scraper and Analysis

This project consists of several Python scripts designed to scrape wrestler data from the Schlussgang website, process the data, and generate statistical analysis and visualizations.

## Scripts

1. `scraper_selenium.py`: Scrapes wrestler data from the Schlussgang website without using a predefined name list.
2. `scraper_selenium_namelist.py`: Scrapes wrestler data using a predefined list of names.
3. `namechanger.py`: Processes a list of names, removing duplicates and reordering names.
4. `stats.py`: Generates statistical analysis and visualizations from the scraped data.

## How to Use

### Option 1: Scraping without a name list

If you don't have a predefined list of wrestler names:

1. Run `scraper_selenium.py`:
   ```
   python scraper_selenium.py
   ```
   This will scrape all wrestler data available on the Schlussgang website.

### Option 2: Scraping with a name list

If you have a list of wrestler names:

1. Prepare your name list:
   - Copy all names from the website.
   - Use `namechanger.py` to process the list:
     ```
     python namechanger.py input_file.txt output_file.txt
     ```
     This will remove every second line (if there are duplicates) and reorder the names.

2. Run `scraper_selenium_namelist.py`:
   ```
   python scraper_selenium_namelist.py
   ```
   Make sure your processed name list is named `namelist_neu_short.txt` or update the filename in the script.

### Generating Statistics

After scraping the data:

1. Run `stats.py`:
   ```
   python stats.py
   ```
   This will generate statistical analysis and create visualization plots based on the scraped data.

## Requirements

- Python 3.x
- Selenium WebDriver
- BeautifulSoup4
- Pandas
- Matplotlib
- Firefox browser (GeckoDriver)

Make sure to install the required Python packages:

```
pip install selenium beautifulsoup4 pandas matplotlib
```

Also, ensure that GeckoDriver is installed and its path is correctly set in the scraper scripts.

## Notes

- The scraper scripts use Firefox WebDriver. Make sure Firefox is installed on your system.
- The scripts include logging for debugging purposes. Check the generated log files for detailed information about the scraping process.
- Generated CSV files and statistical plots will be saved in the same directory as the scripts.

## Troubleshooting

- If you encounter issues with web scraping, check the website structure hasn't changed and update the selectors in the scraper scripts if necessary.
- Ensure your internet connection is stable while running the scraper scripts.
- If the scraper is blocked, try adjusting the delay between requests in the scraper scripts.