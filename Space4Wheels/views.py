from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from Space4Wheels.models import Post, Booking
from .forms import BookingForm, SearchForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def book_space(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.post = post
            booking.renter = request.user
            booking.host = post.author
            booking.save()

            # Add a success message
            messages.success(request, 'Booking created successfully.')

            return JsonResponse({'success': True})
        else:
            # Return a JSON response with form errors
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        # Instantiate the form with initial values
        form = BookingForm(instance=Booking(post=post, renter=request.user, host=post.author))
        
    return render(request, 'Space4Wheels/bookings.html', {'form': form, 'post': post})

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'Space4Wheels/home.html', context)

class BookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'Space4Wheels/bookings.html'

    def get_context_data(self, **kwargs):
        renter_bookings = Booking.objects.filter(renter=self.request.user)
        host_bookings_pending_approval = Booking.objects.filter(host=self.request.user, pending_approval=True)
        host_bookings_approved = Booking.objects.filter(host=self.request.user, pending_approval=False)

        context = {
            'renter_bookings': renter_bookings,
            'host_bookings_pending_approval': host_bookings_pending_approval,
            'host_bookings_approved': host_bookings_approved,
        }
        return context
    
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Perform approval logic, e.g., set status to 'approved'
    booking.status = 'approved'
    booking.pending_approval = False
    booking.save()
    return redirect('bookings')  # Redirect to the bookings page

def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Perform rejection logic, e.g., set status to 'rejected'
    booking.status = 'rejected'
    booking.pending_approval = False
    booking.save()
    return redirect('bookings') 

class UserParkingSpaceListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'Space4Wheels/host.html'
    context_object_name = 'user_listings'  # Rename 'posts' to 'user_listings'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        # Filter posts where the current user is the author
        return Post.objects.filter(author=self.request.user)
    
class PostListView(ListView):
    model = Post
    template_name = 'Space4Wheels/home.html' # app>/<model>_<viewtype.html>
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class PostDetailView(DetailView):
    model = Post
    template_name = 'Space4Wheels/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create an instance of the BookingForm and set initial values
        booking_form = BookingForm()
        booking_form.set_initial_values(self.object, self.request.user, self.object.author)

        context['booking_form'] = booking_form
        return context
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title', 'content', 'country', 'city', 'address', 'price',
        'price_rate', 'car_space_pics', 'car_space_type', 'map_image',
        'additional_notes', 'status'
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = [
        'title', 'content', 'country', 'city', 'address', 'price',
        'price_rate', 'car_space_pics', 'car_space_type', 'map_image',
        'additional_notes', 'status'
    ]

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
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        query = form.cleaned_data['query']
        # Modify the search logic to filter by title (case-insensitive)
        results = Post.objects.filter(title__icontains=query)

    return render(request, 'Space4Wheels/search.html', {'query': query, 'results': results})

def host(request):
    # Instantiate the class-based view and get the queryset
    user_listings_view = UserParkingSpaceListView()
    user_listings_view.request = request
    user_listings = user_listings_view.get_queryset()
    
    return render(request, 'Space4Wheels/host.html', {'title': 'Host', 'user_listings': user_listings})

def bookings(request):
    return render(request, 'Space4Wheels/bookings.html', {'title': 'Bookings'})

def about(request):
    return render(request, 'Space4Wheels/about.html', {'title': 'About'})

