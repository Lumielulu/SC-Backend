from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test_angular, name='test_angular'),
    path('streaming/<int:song_id>/', views.streaming_test, name="streaming_test"),
    path('songs/', views.get_songs, name='get_songs'),
]