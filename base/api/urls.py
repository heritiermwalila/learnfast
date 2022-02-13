from django.urls import path
from . import views


urlpatterns = [
    path('', views.getEndpoints),
    path('rooms/', views.getRooms)
]