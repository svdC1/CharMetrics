import asyncio
from django.shortcuts import render
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import time
import requests
# Create your views here.
async def fetch_creator_data(creator_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
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
            name = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > h1')
            total_messages = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > div.relative.mb-4.w-full.overflow-hidden.text-sm > div > div:nth-child(1) > button:nth-child(1)')
            total_chats = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > div.relative.mb-4.w-full.overflow-hidden.text-sm > div > div:nth-child(1) > button:nth-child(2)')
            dislikes= await page.query_selector('#main > div > div > div > div.text-sm > div.mx-auto.w-full.max-w-screen-xl > div > section > div > div.flex.items-center.justify-between.gap-2.border-gray-200.py-2\.5.dark\:border-zinc-700 > h3 > span.flex.flex-nowrap.items-end.gap-1.text-sm.font-semibold.text-gray-500')
            likes = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > div.relative.mb-4.w-full.overflow-hidden.text-sm > div > div:nth-child(1) > div > button:nth-child(1)')
            date_published = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > div.mb-4.flex.flex-wrap.items-center.gap-x-3.gap-y-2.text-sm > div.flex.flex-wrap.items-center.gap-x-3.gap-y-2 > div:nth-child(1) > div > div.font-semibold.text-gray-600.dark\:text-zinc-400')
            last_updated = await page.query_selector('#main > div > div > div > div.mx-auto.flex.max-w-screen-xl.flex-col.items-start.gap-4.p-4.sm\:flex-row.sm\:gap-6.lg\:p-8 > div.w-full.grow.py-2\.5 > div.mb-4.flex.flex-wrap.items-center.gap-x-3.gap-y-2.text-sm > div.flex.flex-wrap.items-center.gap-x-3.gap-y-2 > div:nth-child(2) > div > div.font-semibold.text-gray-600.dark\:text-zinc-400')
            if dislikes!=None:
              dislikes= await dislikes.inner_text()
            else:
              dislikes="Error Fetching Data :( -Try Again"
            if total_messages!=None:
                total_messages=await total_messages.inner_text()
            else:
                total_messages="Error Fetching Data :( -Try Again"
            characters_data.append({
                'name': await name.inner_text(),
                'total_messages': total_messages,
                'total_chats': await total_chats.inner_text(),
                'likes': await likes.inner_text(),
                'dislikes': dislikes,
                'date_published': await date_published.inner_text(),
                'last_updated': await last_updated.inner_text()
            })

        await browser.close()
        return characters_data

def convert_to_number(s):
    if 'K' in s:
        return float(s.replace('K', '')) * 1000
    elif 'M' in s:
        return float(s.replace('M', '')) * 1000000
    else:
        return float(s)

def index(request):
    return render(request,'index.html')

def results(request):
    creator_name = request.GET.get('creator_name')
    if not creator_name:
        return render(request, 'index.html', {'error': 'Please provide a creator handle'})
    creator_url = f"https://www.gptgirlfriend.online/creators/{creator_name}"
    c_page = bs(requests.get(creator_url).text,'html.parser')
    page_not_found = c_page.select_one('main>template')
    no_character=c_page.select_one('h2[class="text-xl font-semibold text-gray-700 dark:text-zinc-300"]')
    if page_not_found:
        return render(request, 'index.html', {'error': 'Creator page does not exist'})
    elif no_character:
        return render(request, 'index.html', {'error': 'Creator has no public characters'})
    try:
      start_time=time.time()
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
      characters_data = loop.run_until_complete(fetch_creator_data(creator_name))
      retrieval_time= round(time.time()-start_time,2)
      for d in characters_data:
          if d['dislikes']!='Error Fetching Data :( -Try Again':
              d['dislikes']=d['dislikes'].split()[1]
          if d['total_messages']=="Error Fetching Data :( -Try Again":
              d['total_messages']='0'
      df=pd.DataFrame(characters_data)
      df['total_messages'] = df['total_messages'].apply(convert_to_number)
      df['total_chats'] = df['total_chats'].apply(convert_to_number)
      df['likes']=df['likes'].apply(convert_to_number)
      df['dislikes']=df['dislikes'].apply(convert_to_number)
      df['dt_date_published'] = pd.to_datetime(df['date_published'], format='%b %d, %Y')
      current_date = pd.to_datetime(datetime.now().date())
      df['days_since_published'] = (current_date - df['dt_date_published']).dt.days
      df['avg_messages_day'] = (df['total_messages'] / df['days_since_published']).round(2)
      df['avg_chats_day'] = (df['total_chats'] / df['days_since_published']).round(2)
      sum={'total_messages':df['total_messages'].sum(),'total_chats':df['total_chats'].sum(),'likes':df['likes'].sum(),'dislikes':df['dislikes'].sum()}
      return render(request, 'results.html', {'characters': df.to_dict(orient='records'),'sum':sum,'retrieval_time':retrieval_time})
    except Exception as e:
        print(e)
        return render(request,'results.html',{'error':str(e)})
