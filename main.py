import json
import uuid

import pandas as pandas
import requests
from bs4 import BeautifulSoup
from utils import generate_headers

BASE_URL = "https://www.polovniautomobili.com"
FIRST_PAGE_FILE = "/auto-oglasi/audi/tt"


def get_all_next_pages_from_page(page):
    pages = []
    pages_len = 0

    bs = BeautifulSoup(page, 'html.parser')

    for item in bs.find_all('a', class_='js-pagination-numeric', href=True):
        pages.append(item['href'])

    pages = list(dict.fromkeys(pages))

    return pages


def get_page(page = FIRST_PAGE_FILE):
    global BASE_URL, FIRST_PAGE_FILE

    r = requests.get(f"{BASE_URL}{page}", headers=generate_headers())

    return r.text


def page_info(page):
    page_id = str(uuid.uuid4())
    value = {page_id : []}
    bs = BeautifulSoup(page, 'html.parser')

    for number, item in enumerate(bs.find_all('div', class_='textContentHolder')):
        text_content = item.findChildren("div", class_='textContent', recursive=False)
        for div in text_content:
            title = div.find('a', class_='ga-title').text.strip("\n\t")
            price_all = div.find('div', class_='price').text.strip('\n\t').split('+')[0].split(' ')
            price = price_all[0].replace('.', '')
            currency = price_all[1]
            href = BASE_URL + div.find('a', class_='ga-title', href=True)['href'].strip('\n',)
            try:
                value[page_id].append({"title": title, "price": int(price), "currency": currency, "href": href})
            except:
                value[page_id].append({"title": title, "price": -1, "currency": None, "href": href})

    return list(value.values())


if __name__ == "__main__":
    first_page = get_page()
    saved = page_info(first_page)

    pages = get_all_next_pages_from_page(first_page)

    for index, page in enumerate(pages):
        saved.append(page_info(get_page(page)))

    #print(len(saved))
    print(saved)

    with open('tt.json', 'w') as json_file:
        json.dump(saved, json_file)
