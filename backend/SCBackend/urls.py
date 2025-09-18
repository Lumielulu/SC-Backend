from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test_angular, name='test_angular')
]