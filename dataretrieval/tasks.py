from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .utils import fetch_creator_data,clean_data  # Ensure this function is properly defined in utils.py
import asyncio
import time
@shared_task
def long_running_task(creator_name):
    start_time=time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_creator_data(creator_name))
    retrieval_time=time.time()-start_time
    characters_data,sum_=clean_data(data)
    return {'characters':characters_data,'sum':sum_,'retrieval_time':retrieval_time}