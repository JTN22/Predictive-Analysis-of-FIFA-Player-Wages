import random
import time

import cloudscraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# Bypass Cloudflare's anti-bot protection
def get_scraper():
    """Create a cloudscraper instance"""
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}, delay=10
    )


# HAHAHAHAHAHAHA FU CLOUDFLARE
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.fifaindex.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def get_page(url, scraper, retry_count=3):
    """Get a page with retries"""
    for attempt in range(retry_count):
        try:
            response = scraper.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retry_count - 1:
                raise
            time.sleep(random.uniform(1, 3))


base_url = "https://www.fifaindex.com/players/"
scraper = get_scraper()

url = f"{base_url}/players/"

data = []

for page in tqdm(range(1, 609)):
    url = f"{base_url}?page={page}"
    print(f"Getting page {page} at {url}")

    soup = get_page(url, scraper)

    # Find the player table
    table = soup.find("table", class_="table-players")
    if not table:
        print(f"No player table found on page {page}")

    # Find all player rows
    players = table.find("tbody").find_all("tr", attrs={"data-playerid": True})
    if not players:
        print(f"No player rows found on page {page}")

    print(f"Found {len(players)} players on page {page}")

    for player in players:
        link = player.find("a", class_="link-player")
        name = link.get("title", "").replace(" FIFA 24", "")
        player_url = base_url + link.get("href", "")

        print(f"Player: {name}. URL: {player_url}")
        data.append({"name": name, "url": player_url})

df = pd.DataFrame(data)
df.to_csv("players.csv", index=False)
