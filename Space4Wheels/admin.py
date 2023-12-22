from django.contrib import admin
from .models import Post, Booking, Rating, UserRating

# Register your models here.
admin.site.register(Post) #post model
admin.site.register(Booking) #booking model
admin.site.register(Rating) #rating model
admin.site.register(UserRating) #rating model