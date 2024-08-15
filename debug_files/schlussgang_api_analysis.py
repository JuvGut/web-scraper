import requests
from urllib.parse import urljoin
import json

def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.schlussgang.ch/portraet',
        'DNT': '1',
        'Connection': 'keep-alive',
    })
    return session

def analyze_api_requests(session, base_url):
    potential_endpoints = [
        '/api/portraet',
        '/api/athletes',
        '/api/schwinger',
        '/data/portraet',
        '/data/athletes',
        '/_next/data/latest/portraet.json',
    ]

    for endpoint in potential_endpoints:
        url = urljoin(base_url, endpoint)
        try:
            response = session.get(url)
            print(f"Trying endpoint: {url}")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print("Successfully retrieved JSON data. First 100 characters:")
                    print(json.dumps(json_data, indent=2)[:100])
                except json.JSONDecodeError:
                    print("Response is not JSON. First 100 characters of content:")
                    print(response.text[:100])
            print("\n")
        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}\n")

# Hauptausführung
base_url = 'https://www.schlussgang.ch'
session = get_session()
analyze_api_requests(session, base_url)