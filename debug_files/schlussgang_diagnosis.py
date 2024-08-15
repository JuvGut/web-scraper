import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin
import time
import random

def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    return session

def analyze_page_structure(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        print(f"Analyzing page structure of {url}")
        print(f"Title: {soup.title.string if soup.title else 'No title found'}")

        # Suche nach verschiedenen möglichen Selektoren für Portrait-Links
        selectors = [
            'a[href^="/portraet/"]',
            'a[href*="portraet"]',
            '.portrait-link',
            '.athlete-link',
            'a.link'  # Allgemeiner Selektor für Links
        ]

        for selector in selectors:
            links = soup.select(selector)
            print(f"Links found with selector '{selector}': {len(links)}")
            if links:
                print("Sample links:")
                for link in links[:5]:  # Zeige die ersten 5 Links
                    print(f"  {link.get('href')} - {link.text.strip()}")

        # Suche nach möglichen Container-Elementen
        containers = [
            '.portrait-container',
            '.athlete-list',
            '.content-area',
            'main',
            'div[id*="content"]'
        ]

        for container in containers:
            elements = soup.select(container)
            print(f"Elements found with selector '{container}': {len(elements)}")
            if elements:
                print(f"Content preview of first element:")
                print(elements[0].text[:200] + "...")  # Zeige die ersten 200 Zeichen

        # Suche nach JavaScript-Dateien
        scripts = soup.find_all('script', src=True)
        print(f"Number of external scripts: {len(scripts)}")
        if scripts:
            print("Sample script sources:")
            for script in scripts[:5]:
                print(f"  {script['src']}")

        return soup

    except requests.RequestException as e:
        print(f"Error analyzing {url}: {e}")
        return None

# Hauptausführung
base_url = 'https://www.schlussgang.ch/portraet'
session = get_session()

soup = analyze_page_structure(session, base_url)

if soup:
    print("\nFull HTML content:")
    print(soup.prettify()[:1000])  # Drucke die ersten 1000 Zeichen des formatierten HTML
else:
    print("Failed to retrieve page content.")