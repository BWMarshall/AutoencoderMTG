import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

os.makedirs("data", exist_ok=True)

# Initialize session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Scraping variables
data = []
page = 0  # start from 1
max_pages = 1473  # can remove this for auto-detection

try:
    while page <= max_pages:
        url = f'https://scryfall.com/search?as=full&order=name&page={page}&q=%28game%3Apaper%29+legal%3Acommander+&unique=cards'
        response = session.get(url)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            cards = soup.find_all('div', class_=['card-profile'])

            # If no cards found, assume last page
            if not cards:
                print(f"No cards found on page {page}. Stopping.")
                break

            for card in cards:
                img_tag = card.find('img')
                img_src = img_tag['src'] if img_tag else None

                txt_tag = card.find('div', class_='card-text')
                if not txt_tag:
                    continue  # skip if missing text block

                # Name and Mana Cost
                title_line = txt_tag.find_all('h1', class_='card-text-title')
                if not title_line:
                    continue  # skip broken card
                title_line = title_line[0].get_text().strip().replace("\n", "").split("          ")
                name = title_line.pop(0).strip()
                mana_line = title_line.pop(0).strip() if title_line else ""

                # Type Line
                type_tag = txt_tag.find('p', class_='card-text-type-line')
                type_line = type_tag.get_text().strip().split(" — ") if type_tag else []

                # Oracle Text
                oracle_block = txt_tag.find('div', class_='card-text-oracle')
                oracle_text = oracle_block.get_text().strip().split("\n") if oracle_block else [""]

                # Stats
                stats_block = txt_tag.find('div', class_='card-text-stats')
                stats = stats_block.get_text().strip().split("/") if stats_block else None

                card_data = {
                    "name": name,
                    "mana_cost": mana_line,
                    "type_line": type_line,
                    "oracle_text": oracle_text,
                    "stats": stats,
                    "img": img_src
                }
                data.append(card_data)

            print(f"Page {page} completed with {len(cards)} cards.")
            page += 1

            # Optional: Save checkpoint every 100 pages
            if page % 100 == 0:
                df = pd.DataFrame(data)
                df.to_json('./data/output_checkpoint.json', orient='records', indent=4)
                print(f"Checkpoint saved at page {page}.")

            # Be polite to the server
            time.sleep(random.uniform(0.5, 1.5))

        else:
            print(f"Failed to retrieve page {page}. Status: {response.status_code}. Retrying...")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    # Final data save
    df = pd.DataFrame(data)
    df.to_json('./data/output.json', orient='records', indent=4)
    print("Final data saved.")
