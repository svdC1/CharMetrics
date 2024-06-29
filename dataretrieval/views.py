from django.shortcuts import render
from .tasks import long_running_task
from django.http import JsonResponse
from celery.result import AsyncResult
from bs4 import BeautifulSoup as bs
import requests
from CharMetrics.celery import app
# Create your views here.
def sanitize_for_json(data):
    if isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(v) for v in data]
    elif isinstance(data, float) and (data == float('inf') or data == float('-inf') or data != data):  # Check for inf and NaN
        return '0'  # or any other appropriate value
    else:
        return data

def index(request):
    return render(request,'index.html')

def results(request):
    creator_name = request.GET.get('creator_name')
    if not creator_name:
        return render(request, 'index.html', {'error': 'Please provide a creator name'})
    #Check if page is valid
    creator_url = f"https://www.gptgirlfriend.online/creators/{creator_name}"
    try:
        response = requests.get(creator_url)
        response.raise_for_status()
    except requests.RequestException:
        return render(request, 'index.html', {'error': 'Error fetching creator page'})
    c_page = bs(response.text, 'html.parser')
    page_not_found = c_page.select_one('main>template')
    no_character = c_page.select_one('h2[class="text-xl font-semibold text-gray-700 dark:text-zinc-300"]')
    if page_not_found:
        return render(request, 'index.html', {'error': 'Creator does not exist'})
    elif no_character:
        return render(request, 'index.html', {'error': 'Creator has no public characters'})
    else:
        task = long_running_task.delay(creator_name)
        return JsonResponse({'task_id': task.id})

def task_status(request, task_id,app=app):
    try:
        task_result = AsyncResult(task_id)
        if task_result.state == 'PENDING':
            return JsonResponse({'state': task_result.state, 'status': 'Pending...'})

        elif task_result.state != 'FAILURE':
            result_data = sanitize_for_json(task_result.result)
            return JsonResponse({
                'state': task_result.state,
                'result': result_data,
            })
        else:
            # something went wrong in the background job
            return JsonResponse({
                'state': task_result.state,
                'status': str(task_result.info),  # this is the exception raised
            })
    except Exception as e:
        return JsonResponse({
            'state': 'FAILURE',
            'status': 'An error occurred while fetching task status',
            'error': str(e),})

def results_page(request):
    return render(request, 'results.html')


