from django.urls import path
from . import views
from .views import (
    PostListView, 
    PostDetailView, 
    PostCreateView, 
    PostUpdateView,
    PostDeleteView,
    book_space, BookingsView, rate_post
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
    path('about/', views.about, name='Space4Wheels-about'),
    path('bookings/', BookingsView.as_view(), name='bookings'),
    path('post/<int:post_id>/book_space/', book_space, name='book-space'),
    path('bookings/approve/<int:booking_id>/', views.approve_booking, name='approve-booking'),
    path('bookings/reject/<int:booking_id>/', views.reject_booking, name='reject-booking'),
    path('rate-post/<int:post_id>/', rate_post, name='rate-post'),
    #path('register/', user_views.register, name='register'),
]