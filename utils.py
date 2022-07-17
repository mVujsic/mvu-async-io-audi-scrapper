from fake_useragent import UserAgent

UA = UserAgent()

def generate_headers():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'user-agent': UA.random,
        'cookies': 'pa-cookies--message=accepted',
        'accept-language': 'en-US,en;q=0.5',
        'sec-fetch-site': 'cross-site',
        'accept-encoding': 'gzip, deflate',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
    }
