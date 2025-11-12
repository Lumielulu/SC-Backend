from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name = 'token_obtain_pair'),
    path('login/', views.test_angular, name='test_angular'),
    path('streaming/<int:song_id>/', views.stream_master, name="streaming_master"),
    path('songs/', views.get_songs, name='get_songs'),
    path('users/', views.getUsers, name='users'),
    path('register/', views.regUser, name='regUser'),
    path('download/<int:song_id>', views.downloadRequestedSong, name='downloadRequestedSong'),
    path('health/', views.health, name="health")
]