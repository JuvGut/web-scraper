import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import urllib.request

# Configure logging to write to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='schlussgang_scraper.log',
    filemode='w'
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def download_ublock():
    url = "https://github.com/gorhill/uBlock/releases/download/1.52.2/uBlock0_1.52.2.firefox.signed.xpi"
    xpi_path = os.path.join(os.getcwd(), "ublock_origin.xpi")
    urllib.request.urlretrieve(url, xpi_path)
    return xpi_path

def setup_driver():
    firefox_options = Options()
    # firefox_options.add_argument("--headless")  # Uncomment this line to run in headless mode
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.set_preference("javascript.enabled", True)
    
    geckodriver_path = '/opt/homebrew/bin/geckodriver'
    if not os.path.isfile(geckodriver_path):
        logging.error(f"GeckoDriver nicht gefunden unter {geckodriver_path}.")
        return None
    
    service = Service(geckodriver_path)
    
    try:
        driver = webdriver.Firefox(options=firefox_options, service=service)
        driver.set_page_load_timeout(30)
        
        # Install uBlock Origin
        ublock_path = download_ublock()
        driver.install_addon(ublock_path, temporary=True)
        logging.info("uBlock Origin installed")
        
        return driver
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des WebDrivers: {e}")
        return None

def generate_urls_from_names(names_file):
    base_url = "https://www.schlussgang.ch/portraet/"
    urls = []
    with open(names_file, 'r', encoding='utf-8') as file:
        for name in file:
            name = name.strip().lower().replace(" ", "-")
            urls.append(f"{base_url}{name}")
            urls.append(f"{base_url}{name}-0")  # Adding the -0 variant
    return urls

def get_portrait_links(driver, url):
    try:
        logging.info(f"Navigating to {url}")
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logging.info("Page loaded successfully")
        
        # Scroll to load all content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.select("a[href*='portraet']")
        logging.debug(f"Found {len(links)} potential portrait links")
        
        portrait_links = [link['href'] for link in links if link['href'] != '/portraet']
        logging.debug(f"Filtered to {len(portrait_links)} valid portrait links")
        
        return portrait_links
    except TimeoutException:
        logging.error("Timeout waiting for page to load")
        return []
    except WebDriverException as e:
        logging.error(f"WebDriver exception: {e}")
        return []
    except Exception as e:
        logging.error(f"Error in get_portrait_links: {e}")
        return []

def scrape_portrait(driver, url):
    try:
        logging.info(f"Scraping portrait: {url}")
        driver.get(url)
        
        # Wait for either the table or the "Seite nicht gefunden" message
        element = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody, .alert-danger"))
        )
        
        # Check if we got the "Seite nicht gefunden" message
        try:
            error_message = driver.find_element(By.CLASS_NAME, "alert-danger")
            if "Seite nicht gefunden" in error_message.text:
                logging.warning(f"Page not found: {url}")
                return None
        except NoSuchElementException:
            pass  # No error message found, continue with scraping
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        data = {'Name': soup.select_one('h1').text.strip() if soup.select_one('h1') else 'N/A'}
        
        table = soup.select_one('tbody')
        if table:
            rows = table.select('tr')
            for row in rows:
                th = row.select_one('th')
                td = row.select_one('td')
                if th and td:
                    key = th.text.strip()
                    value = td.text.strip()
                    data[key] = value
                    logging.debug(f"Extracted: {key} - {value}")
        else:
            logging.warning("Table not found on the page")
        
        logging.info(f"Successfully scraped data for {data.get('Name', 'Unknown')}")
        return data
    except TimeoutException:
        logging.error(f"Timeout waiting for portrait details on {url}")
        return None
    except Exception as e:
        logging.error(f"Error scraping portrait {url}: {e}")
        return None

def scrape_name(driver, base_url, name):
    url = f"{base_url}{name}"
    data = scrape_portrait(driver, url)
    if data is None:
        # If the first attempt failed, try with "-0" suffix
        url_with_suffix = f"{url}-0"
        data = scrape_portrait(driver, url_with_suffix)
    return data

def save_to_csv(data, filename):
    if not data:
        logging.warning("No data to save")
        return

    keys = set()
    for item in data:
        keys.update(item.keys())
    
    sorted_keys = ['Name'] + sorted(key for key in keys if key != 'Name')

    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=sorted_keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logging.info(f"Data saved to {filename}")
    logging.debug(f"CSV columns: {sorted_keys}")

def main():
    names_file = "namelist_neu_short.txt"
    base_url = "https://www.schlussgang.ch/portraet/"
    driver = setup_driver()
    
    if not driver:
        logging.error("Konnte den WebDriver nicht initialisieren. Beende das Programm.")
        return
    
    try:
        all_data = []
        with open(names_file, 'r', encoding='utf-8') as file:
            for name in file:
                name = name.strip().lower().replace(" ", "-")
                portrait_data = scrape_name(driver, base_url, name)
                if portrait_data:
                    all_data.append(portrait_data)
                    logging.info(f"Successfully scraped data for {portrait_data.get('Name', 'Unknown')}")
                else:
                    logging.warning(f"Failed to scrape data for {name}")
                time.sleep(2)  # Reduced delay between requests
        
        if all_data:
            save_to_csv(all_data, 'schlussgang_portraits.csv')
            logging.info(f"{len(all_data)} portraits have been extracted and saved to 'schlussgang_portraits.csv'")
        else:
            logging.warning("No data was extracted. Please check the connection and website structure.")
    
    except Exception as e:
        logging.exception(f"Ein Fehler ist aufgetreten: {e}")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()