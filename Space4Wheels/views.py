from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post



def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'Space4Wheels/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'Space4Wheels/home.html' # app>/<model>_<viewtype.html>
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class PostDetailView(DetailView):
    model = Post
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content'] # add the fields you want for the user to add/edit

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content'] # add the fields you want for the user to add/edit

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def search(request):
    return render(request, 'Space4Wheels/search.html', {'title': 'Search'})

def host(request):
    return render(request, 'Space4Wheels/host.html', {'title': 'Host'})

def bookings(request):
    return render(request, 'Space4Wheels/bookings.html', {'title': 'Bookings'})

def about(request):
    return render(request, 'Space4Wheels/about.html', {'title': 'About'})

