# generator/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reset-history', views.reset_history, name='reset_history')
]
