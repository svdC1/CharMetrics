import requests
from bs4 import BeautifulSoup as soup_obj
import re
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .models import Character
from django_q.tasks import async_task

def fix_number(str_n):
    if not str_n:
        return 0
    try:
        return float(str_n)
    except ValueError:
        match = re.match(r'(\d+(\.\d+)?)(K|M)', str_n)
        if match:
            number, _, multiplier = match.groups()
            return float(number) * (1000 if multiplier == 'K' else 1000000)
        else:
            raise ValueError(f"Unable to fix number: {str_n}")

def scrape_char_metrics(char_sub):
    ggpt_url = "https://www.gptgirlfriend.online/"
    char_url = ggpt_url + char_sub
    response = requests.get(char_url)
    response.raise_for_status()
    CharPageSoup = soup_obj(response.text, 'html.parser')

    CharName = CharPageSoup.select_one('h1.mb-4.flex.items-center.gap-2.text-2xl.font-semibold.tracking-tight').get_text(strip=True)
    CharMetricsSection = CharPageSoup.select_one('div.relative.mb-4.w-full.overflow-hidden.text-sm')
    TotalChats = CharMetricsSection.select_one('button[title="Total Chats"]').get_text(strip=True)
    TotalMessages = CharMetricsSection.select_one('button[title="Total Messages"]').get_text(strip=True)
    Likes = CharMetricsSection.select_one('button[title="Likes"]').get_text(strip=True)
    Dislikes = CharMetricsSection.select_one('button[title="Dislike"]').get_text(strip=True)
    PublishedUpdatedString = CharPageSoup.select_one('div.mb-4.flex.flex-wrap.items-center.gap-x-3.gap-y-2.text-sm').get_text(strip=True)
    Creator = CharPageSoup.select_one('a.hover:text-indigo-500.dark:hover:text-indigo-400').get_text(strip=True)
    PublishedDate = re.search(r'At\s(.+?)(?=\sL)', PublishedUpdatedString).group(1).strip()
    LastUpdated = re.search(r'Updated\s(.+)', PublishedUpdatedString).group(1).strip()

    PubDatetime = datetime.strptime(PublishedDate, '%b %d, %Y')
    days_since_pub = (datetime.now() - PubDatetime).days
    avg_msg_day = round(fix_number(TotalMessages) / days_since_pub, 2)
    avg_chats_day = round(fix_number(TotalChats) / days_since_pub, 2)
    avg_likes_day = round(fix_number(Likes) / days_since_pub, 2)

    character = Character(
        name=CharName,
        total_chats=fix_number(TotalChats),
        total_messages=fix_number(TotalMessages),
        likes=fix_number(Likes),
        dislikes=fix_number(Dislikes),
        creator=Creator,
        published_date=PubDatetime,
        last_updated=LastUpdated,
        avg_messages_per_day=avg_msg_day,
        avg_chats_per_day=avg_chats_day,
        avg_likes_per_day=avg_likes_day
    )
    character.save()
    return {
        "Name": CharName,
        "Total_Chats": fix_number(TotalChats),
        "Total_Messages": fix_number(TotalMessages),
        "Likes": fix_number(Likes),
        "Dislikes": fix_number(Dislikes),
        "Creator": Creator,
        "Published_Date": PublishedDate,
        "Last_Updated": LastUpdated,
        "Avg_Messages_Day": avg_msg_day,
        "Avg_Chats_Day": avg_chats_day,
        "Avg_Likes_Day": avg_likes_day
        }

def scrape_creator_metrics(creator_name):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    ggpt_url = "https://www.gptgirlfriend.online/"
    c_url = ggpt_url + 'creators/' + creator_name
    try:
        driver.get(c_url)
        creator_page_soup = soup_obj(driver.page_source, 'html.parser')
        character_links = creator_page_soup.select('div.relative.grid.h-fit.w-full.grid-cols-2.gap-2.max-[370px]:grid-cols-1.sm:grid-cols-3.sm:gap-4.lg:grid-cols-[repeat(auto-fill,_minmax(240px,_1fr))] a')
        character_subs = [link.get('href')[1:] for link in character_links]
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(scrape_char_metrics, character_subs))
            return results
    finally:
        driver.quit()
