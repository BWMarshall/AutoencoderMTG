import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm


data = []
page = 1
while page < 488:
    url = f'https://scryfall.com/search?as=text&order=name&page={page}&q=%28game%3Apaper%29+legal%3Acommander+&unique=cards'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('a', class_=['card-text text-grid-item'])
        for card in cards:
            link = card.get('href')
            title_line = card.find_all('h6', class_ = ['card-text-title'])[0].get_text().strip().replace("\n","").split("              ")
            name = title_line.pop(0)
            mana_line = title_line.pop(0) if title_line else ""
            type_line = card.find_all('p', class_ = ['card-text-type-line'])[0].get_text().strip().split(" — ")
            oracle_dump = card.find_all('div', class_ = ['card-text-oracle'])
            oracle_text =  oracle_dump[0].get_text().strip().split("\n") if oracle_dump else [""]
            stats = card.find_all('div', class_ = ['card-text-stats'])
            if stats:
                stats = stats[0].get_text().strip().split("/")
            else:
                stats = None
            card_data = {
                "name": name,
                "mana_cost" : mana_line,
                "type_line" : type_line,
                "oracle_text" : oracle_text,
                "stats" : stats,
                "link" : link
            }
            data.append(card_data)
        print(f"Page {page} Completed")
        page += 1
    else:
        print(f"Failed to retrieve Page {page}, retrying")

df = pd.DataFrame(data)
print(df.head())
df.to_json('./data/output.json', orient='records', indent=4)



