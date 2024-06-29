from django.urls import path
from dataretrieval import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('results_page/', views.results_page, name='results_page'),
    path('task_status/<str:task_id>/', views.task_status, name='task_status'),
]
