from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Space4Wheels-home'),
    path('about/', views.about, name='Space4Wheels-about'),
]