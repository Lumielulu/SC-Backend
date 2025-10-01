from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name = 'token_obtain_pair'),
    path('test', views.test_angular, name='test_angular'),
    path('streaming/<int:song_id>/', views.streaming_test, name="streaming_test"),
    path('songs/', views.get_songs, name='get_songs'),
]