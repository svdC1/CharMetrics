from django.shortcuts import render
from django.template import loader
from .forms import CreatorHandleForm
from .models import CreatorHandles
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup_obj
import re
from datetime import datetime
import dateparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from django.http import HttpResponse, JsonResponse
from django_q.tasks import async_task, result
from .scraping import scrape_creator_metrics

def home(request):
    template = loader.get_template('home.html')
    if request.method == "POST":
        form = CreatorHandleForm(request.POST)
        if form.is_valid():
            creators_handle = form.cleaned_data['creators_handle']
            task_id = async_task('scrape_creator_metrics', creators_handle)
            new_handle = CreatorHandles(creators_handle=creators_handle)
            new_handle.save()
            return JsonResponse({'task_id': task_id})
    else:
        form = CreatorHandleForm()
    return render(request, 'home.html', {'form': form})

def get_task_result(request, task_id):
    task_result = result(task_id)
    if task_result is None:
        return JsonResponse({'status': 'pending'})
    elif isinstance(task_result, Exception):
        return JsonResponse({'status': 'error', 'message': str(task_result)})
    else:
        return JsonResponse({'status': 'completed', 'data': task_result})
