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
from selenium.common.exceptions import TimeoutException, WebDriverException
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
        
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        
        logging.debug(f"Current URL after loading: {driver.current_url}")
        
        page_source = driver.page_source
        logging.debug(f"Page source length: {len(page_source)}")
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
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
        logging.debug(f"Current page source: {driver.page_source[:500]}...")
        return None
    except Exception as e:
        logging.error(f"Error scraping portrait {url}: {e}")
        logging.debug(f"Current page source: {driver.page_source[:500]}...")
        return None



# def scrape_portrait(driver, url):
#     try:
#         logging.info(f"Scraping portrait: {url}")
#         driver.get(url)
        
#         # Wait for any element that's likely to be on the page
#         WebDriverWait(driver, 45).until(
#             EC.presence_of_element_located((By.TAG_NAME, "h1"))
#         )
        
#         # Log the current URL to ensure we're on the right page
#         logging.debug(f"Current URL after loading: {driver.current_url}")
        
#         # Get the page source and log its length
#         page_source = driver.page_source
#         logging.debug(f"Page source length: {len(page_source)}")
        
#         soup = BeautifulSoup(page_source, 'html.parser')
        
#         data = {
#             'Name': soup.select_one('h1').text.strip() if soup.select_one('h1') else 'N/A',
#             'Wohnort': 'N/A',
#             'Geburtsdatum': 'N/A',
#             'Zivilstand': 'N/A',
#             'Grösse (cm)': 'N/A',
#             'Gewicht (kg)': 'N/A',
#             'Schuhgrösse': 'N/A',
#             'Hobbys': 'N/A',
#             'erlernter Beruf': 'N/A',
#             'jetziger Beruf': 'N/A',
#             'Lieblingsgericht': 'N/A',
#             'Lieblingsgetränk': 'N/A'
#         }
        
#         # Log the presence or absence of key elements
#         logging.debug(f"H1 tag found: {'h1' in page_source}")
#         logging.debug(f"Portrait details found: {'.portrait-details' in page_source}")
        
#         details = soup.select('.portrait-details li')
#         logging.debug(f"Number of detail elements found: {len(details)}")
        
#         for detail in details:
#             text = detail.get_text(strip=True)
#             logging.debug(f"Detail text: {text}")
#             if ':' in text:
#                 key, value = text.split(':', 1)
#                 key = key.strip()
#                 value = value.strip()
                
#                 if 'Wohnort' in key:
#                     data['Wohnort'] = value
#                 elif 'Geburtsdatum' in key:
#                     data['Geburtsdatum'] = value
#                 elif 'Zivilstand' in key:
#                     data['Zivilstand'] = value
#                 elif 'Grösse' in key:
#                     data['Grösse (cm)'] = value
#                 elif 'Gewicht' in key:
#                     data['Gewicht (kg)'] = value
#                 elif 'Schuhgrösse' in key:
#                     data['Schuhgrösse'] = value
#                 elif 'Hobbys' in key:
#                     data['Hobbys'] = value
#                 elif 'Erlernter Beruf' in key:
#                     data['erlernter Beruf'] = value
#                 elif 'Jetziger Beruf' in key:
#                     data['jetziger Beruf'] = value
#                 elif 'Lieblingsgericht' in key:
#                     data['Lieblingsgericht'] = value
#                 elif 'Lieblingsgetränk' in key:
#                     data['Lieblingsgetränk'] = value
        
#         logging.info(f"Successfully scraped data for {data['Name']}")
#         return data
#     except TimeoutException:
#         logging.error(f"Timeout waiting for portrait details on {url}")
#         logging.debug(f"Current page source: {driver.page_source[:500]}...")  # Log first 500 characters of page source
#         return None
#     except Exception as e:
#         logging.error(f"Error scraping portrait {url}: {e}")
#         logging.debug(f"Current page source: {driver.page_source[:500]}...")  # Log first 500 characters of page source
#         return None

def save_to_csv(data, filename):
    if not data:
        logging.warning("No data to save")
        return

    keys = set()
    for item in data:
        keys.update(item.keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=list(keys))
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logging.info(f"Data saved to {filename}")

def main():
    base_url = 'https://www.schlussgang.ch/portraet'
    driver = setup_driver()
    
    if not driver:
        logging.error("Konnte den WebDriver nicht initialisieren. Beende das Programm.")
        return
    
    try:
        portrait_links = get_portrait_links(driver, base_url)
        logging.info(f"Found {len(portrait_links)} portrait links")
        
        if not portrait_links:
            logging.warning("No portrait links found. The website structure might have changed.")
            return
        
        all_data = []
        for link in portrait_links:  # portrait_links[:20] -> Limit to first 10 links for testing
            full_url = f"https://www.schlussgang.ch{link}"
            portrait_data = scrape_portrait(driver, full_url)
            if portrait_data:
                all_data.append(portrait_data)
            time.sleep(1)  # Delay between requests
        
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