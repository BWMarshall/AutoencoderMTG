import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm


data = []
page = 0
while page < (1473+1):
    url = f'https://scryfall.com/search?as=full&order=name&page={page}&q=%28game%3Apaper%29+legal%3Acommander+&unique=cards'
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_=['card-profile'])
        for card in cards:
            img_src = card.find('img')['src']
            txt_tag = card.find('div', class_=['card-text'])
            title_line = txt_tag.find_all('h1', class_ = ['card-text-title'])[0].get_text().strip().replace("\n","").split("              ")
            name = title_line.pop(0)
            mana_line = title_line.pop(0) if title_line else ""
            type_line = txt_tag.find_all('p', class_ = ['card-text-type-line'])[0].get_text().strip().split(" — ")
            oracle_dump = txt_tag.find_all('div', class_ = ['card-text-oracle'])
            oracle_text =  oracle_dump[0].get_text().strip().split("\n") if oracle_dump else [""]
            stats = txt_tag.find_all('div', class_ = ['card-text-stats'])
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
                "img" : img_src
            }
            data.append(card_data)
        print(f"Page {page} Completed")
        page += 1
    else:
        print(f"Failed to retrieve Page {page}, retrying")

df = pd.DataFrame(data)
print(df.head())
df.to_json('./data/output.json', orient='records', indent=4)



