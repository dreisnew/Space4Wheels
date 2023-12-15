from django.urls import path
from . import views
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView,
    PostDeleteView
)
#from users import views as user_views

urlpatterns = [
    path('', PostListView.as_view(), name='Space4Wheels-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('search/', views.search, name='Space4Wheels-search'),
    path('host/', views.host, name='Space4Wheels-host'),
    path('bookings/', views.bookings, name='Space4Wheels-bookings'),
    path('about/', views.about, name='Space4Wheels-about'),
    #path('register/', user_views.register, name='register'),
]