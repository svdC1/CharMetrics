from django.urls import path
from .views import home,get_task_result

urlpatterns = [
    path('',home, name='home'),
    path('get_task_result/<str:task_id>/', get_task_result, name='get_task_result'),
]
