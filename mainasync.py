import asyncio
import functools

import aiohttp
import pandas
from bs4 import BeautifulSoup
from datetime import date
import utils

TASKS = []
BASE_URL = "https://www.polovniautomobili.com"
FIRST_PAGE_URL = BASE_URL + "/auto-oglasi/audi/tt"

PAGES = []
CAR_TASK_LIST = []
CAR_URLs = []

CARS_OBJECT = []
SEMAPHORE = asyncio.BoundedSemaphore(5)


async def _get_request(url):
    async with aiohttp.ClientSession(headers=utils.generate_headers()) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                return None


def get_first_page_callback(url, future, first=True):
    text = future.result()
    print(f"First url:{url}")
    bs = BeautifulSoup(text, 'html.parser')

    pages = []
    for item in bs.find_all('a', class_='js-pagination-numeric', href=True):
        pages.append(BASE_URL + item['href'])

    pages = list(dict.fromkeys(pages))

    PAGES.extend(pages)

    return True


def tt_urls_callback(page, future):
    global CAR_URLs
    print(f"TT page url:{page}")
    text = future.result()
    bs = BeautifulSoup(text, 'html.parser')

    for index, item in enumerate(bs.find_all('a', class_='ga-title', href=True)):
        print(f"{index}.TT:{BASE_URL+item['href']}")
        url = BASE_URL+item['href']
        CAR_URLs.append(url)


def _car_info_parser(page, future):
    SEMAPHORE.release()

    print(f'Parsing page {page}')
    text = future.result()
    bs = BeautifulSoup(text, 'html.parser')
    car_obj = {'href': page}
    property_obj = ['Stanje', 'Marka', 'Model',
                    'Godiste', 'Kilometraza', 'Tip',
                    'Gorivo', 'Kubikaza', 'Snaga',
                    'Fiksno', 'Zamena']

    values = bs.find_all('div', class_='uk-width-1-2 uk-text-bold')

    for index, value in enumerate(values):
        try:
            car_obj[property_obj[index]] = value.text
        except IndexError:
            pass

    if car_obj.get('Stanje', 'None'):
        CARS_OBJECT.append(car_obj)

async def scrape_for_all_tt_post():
    tasks = []
    for url in PAGES:
        task = asyncio.create_task(_get_request(url))
        task.add_done_callback(functools.partial(tt_urls_callback, url))
        tasks.append(task)

    await asyncio.gather(*tasks)

async def scrape_tt_post():
    for car_post_url in CAR_URLs:
        await SEMAPHORE.acquire()
        car_task = asyncio.create_task(_get_request(car_post_url))
        car_task.add_done_callback(functools.partial(_car_info_parser, car_post_url))
        CAR_TASK_LIST.append(car_task)

    await asyncio.gather(*CAR_TASK_LIST)

async def main():
    t1 = loop.create_task(_get_request(FIRST_PAGE_URL))
    t1.add_done_callback(functools.partial(get_first_page_callback, FIRST_PAGE_URL, first=True))

    PAGES.append(FIRST_PAGE_URL)

    await asyncio.gather(t1)

    await scrape_for_all_tt_post()
    await scrape_tt_post()

    print(CARS_OBJECT)
    df = pandas.DataFrame(CARS_OBJECT)

    d1 = date.today().strftime("%d_%m_%Y")

    df.to_csv(f"car-{d1}.csv")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())