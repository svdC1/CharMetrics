from django.contrib import admin
from django.urls import path
from dataretrieval import views

urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
]
