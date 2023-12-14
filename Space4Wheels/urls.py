from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Space4Wheels-home'),
    path('search/', views.search, name='Space4Wheels-search'),
    path('about/', views.about, name='Space4Wheels-about'),
]