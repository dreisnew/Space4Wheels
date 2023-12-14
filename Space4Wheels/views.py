from django.shortcuts import render
from django.http import HttpResponse
from .models import Post

posts = [
    {
        'author': 'Dre',
        'title': 'Post 1',
        'content': 'post 1 conetnt',
        'date_posted': 'December 13, 2023'
    },
    {
        'author': 'Lara',
        'title': 'Post 2',
        'content': 'post 2 conetnt',
        'date_posted': 'December 14, 2023'
    }
]

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'Space4Wheels/home.html', context)

def search(request):
    return render(request, 'Space4Wheels/search.html', {'title': 'Search'})

def about(request):
    return render(request, 'Space4Wheels/about.html', {'title': 'About'})

