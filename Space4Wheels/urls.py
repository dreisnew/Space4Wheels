from django.urls import path
from . import views
from users import views as user_views

urlpatterns = [
    path('', views.home, name='Space4Wheels-home'),
    path('search/', views.search, name='Space4Wheels-search'),
    path('about/', views.about, name='Space4Wheels-about'),
    path('register/', user_views.register, name='register'),
]