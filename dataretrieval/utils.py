from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import re
async def fetch_creator_data(creator_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox','-disable-setuid-sandbox','--disable-gl-drawing-for-tests','--disable-gpu-sandbox'])
        page = await browser.new_page()
        creator_url = f"https://www.gptgirlfriend.online/creators/{creator_name}"
        await page.goto(creator_url)
        await page.wait_for_selector('a.h-full')
        links = await page.query_selector_all('a.h-full')
        character_links = [await link.get_attribute('href') for link in links]

        characters_data = []
        for link in character_links:
            character_url = f"https://www.gptgirlfriend.online/{link}?tab=reviews"
            await page.goto(character_url)
            await page.wait_for_selector('#main > div > div > div > div.text-sm > div.mx-auto.w-full.max-w-screen-xl > div > section > div > div.flex.items-center.justify-between.gap-2.border-gray-200.py-2\.5.dark\:border-zinc-700 > h3 > span.flex.flex-nowrap.items-end.gap-1.text-sm.font-semibold.text-gray-500')
            full_page= await page.content()
            full_page_bs=bs(full_page,'html.parser')
            name_= full_page_bs.select('h1[class="mb-4 flex items-center gap-2 text-2xl font-semibold tracking-tight"]')
            if name_:
              name=name_[0].getText()
            else:
              name="Error Fetching Data :( -Try Again"
            m_section=full_page_bs.select('div[class="relative mb-4 w-full overflow-hidden text-sm"]')
            if m_section:
              msection=m_section[0]
              total_chats_ = msection.select('button[title="Total Chats"]')
              total_messages_ = msection.select('button[title="Total Messages"]')
              if total_chats_:
                total_chats=total_chats_[0].getText()
              else:
                total_chats="Error Fetching Data :( -Try Again"
              if total_messages_:
                total_messages=total_messages_[0].getText()
              else:
                total_messages="Error Fetching Data :( -Try Again"
              likes_ = msection.select('button[title="Likes"]')
              if likes_:
                likes=likes_[0].getText()
              else:
                likes="Error Fetching Data :( -Try Again"
            else:
              total_chats="Error Fetching Data :( -Try Again"
              total_messages="Error Fetching Data :( -Try Again"
              likes="Error Fetching Data :( -Try Again"
            dislikes_ = bs(full_page,'html.parser').select('#main > div > div > div > div.text-sm > div.mx-auto.w-full.max-w-screen-xl > div > section > div > div.flex.items-center.justify-between.gap-2.border-gray-200.py-2\.5.dark\:border-zinc-700 > h3 > span.flex.flex-nowrap.items-end.gap-1.text-sm.font-semibold.text-gray-500')
            if dislikes_:
              dislikes_=str(dislikes_[0])
              dislikes = re.search(r'(?:</svg>)(\d+)', dislikes_).groups()[0]
            else:
              dislikes="Error Fetching Data :( -Try Again"
            PublishedUpdatedString = full_page_bs.select('div[class="mb-4 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm"]')
            if PublishedUpdatedString:
              date_published_ = re.findall(r'(?:\sAt)(.+)(?=L)', PublishedUpdatedString[0].getText())
              if date_published_:
                date_published=date_published_[0]
              else:
                date_published="Error Fetching Data :( -Try Again"
              last_updated_ = re.findall(r'(?:Updated)(.*)', PublishedUpdatedString[0].getText())
              if last_updated_:
                last_updated=last_updated_[0]
              else:
                last_updated="Error Fetching Data :( -Try Again"
            else:
               date_published="Error Fetching Data :( -Try Again"
               last_updated="Error Fetching Data :( -Try Again"

            characters_data.append({
                'name': name,
                'total_messages': total_messages,
                'total_chats': total_chats,
                'likes':likes,
                'dislikes': dislikes,
                'date_published':date_published,
                'last_updated':last_updated
            })
        await browser.close()
        return characters_data

def convert_to_number(str_n):
  if str_n == '':
    return 0
  try:
    n = float(str_n)
    return n
  except:
    if re.split(r'(K|M)', str_n)[1] == 'K':
      return float(re.split(r'(K|M)', str_n)[0:-1][0]) * 1000
    elif re.split(r'(K|M)', str_n)[1] == 'M':
      return float(re.split(r'(K|M)', str_n)[0:-1][0]) * 1000000
    else:
      raise Exception("Couldn't Fix Number")

def clean_data(characters_data):
    try:
      df=pd.DataFrame([pd.Series(d) for d in characters_data])
      df['dislikes']=df['dislikes'].apply(lambda x: x if x=="Error Fetching Data :( -Try Again" else x.split()[0])
      df['total_messages']=df['total_messages'].apply(lambda x: x if x=="Error Fetching Data :( -Try Again" else convert_to_number(x))
      df['total_chats'] = df['total_chats'].apply(lambda x: x if x=="Error Fetching Data :( -Try Again" else convert_to_number(x))
      df['likes']=df['likes'].apply(lambda x: x if x=="Error Fetching Data :( -Try Again" else convert_to_number(x))
      df['dislikes']=df['dislikes'].apply(lambda x: x if x=="Error Fetching Data :( -Try Again" else convert_to_number(x))
      dt_date_published = (pd.to_datetime(df[(df['date_published']!="Error Fetching Data :( -Try Again")]['date_published'], format='%b %d, %Y'))
      current_date = pd.to_datetime(datetime.now().date())
      days_since_published = (current_date - dt_date_published).dt.days
      df['avg_messages_day'] = ((df[(df['total_messages']!="Error Fetching Data :( -Try Again") & (df['date_published']!="Error Fetching Data :( -Try Again")]['total_messages']/ days_since_published).astype(float).round(2))
      df['avg_chats_day'] = ((df[(df['total_chats']!="Error Fetching Data :( -Try Again") & (df['date_published']!="Error Fetching Data :( -Try Again")]['total_chats'] / days_since_published).astype(float).round(2))
      sum={'total_messages':df[(df['total_messages']!="Error Fetching Data :( -Try Again")]['total_messages'].sum(),'total_chats':df[(df['total_chats']!="Error Fetching Data :( -Try Again")]['total_chats'].sum(),'likes':df[(df['likes']!="Error Fetching Data :( -Try Again")]['likes'].sum(),'dislikes':df[(df['dislikes']!="Error Fetching Data :( -Try Again")]['dislikes'].sum()}
      return df.to_dict(orient='records'),sum
    except Exception as e:
      return {'error':str(e)},None