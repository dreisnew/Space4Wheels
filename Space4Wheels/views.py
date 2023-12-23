from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from Space4Wheels.models import Post, Booking, Rating, UserRating
from .forms import BookingForm, SearchForm, RatingForm, UserRatingForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User

@login_required
def book_space(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            new_booking = form.save(commit=False)
            new_booking.post = post
            new_booking.renter = request.user
            new_booking.host = post.author

            # Check for overlapping bookings for the specific post
            overlapping_bookings = Booking.objects.filter(
                Q(post=post) &
                Q(reservation_start_date__lte=new_booking.reservation_end_date) &
                Q(reservation_end_date__gte=new_booking.reservation_start_date) &
                Q(status='approved')
            )

            if overlapping_bookings.exists():
                # If there are overlapping bookings for the specific post, return an error
                errors = {'reservation_start_date': 'Dates are not available. Please choose different dates.'}
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            new_booking.save()

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
        renter_bookings = Booking.objects.filter(renter=self.request.user).order_by('-date_requested')
        host_bookings_pending_approval = Booking.objects.filter(host=self.request.user, status='pending').order_by('-date_requested')
        host_bookings_approved = Booking.objects.filter(host=self.request.user, status='approved').order_by('-date_requested')
        host_bookings_done = Booking.objects.filter(host=self.request.user, status='done').order_by('-date_requested')
        host_bookings_rejected = Booking.objects.filter(host=self.request.user, status='rejected').order_by('-date_requested')
        renter_bookings = Booking.objects.filter(renter=self.request.user).order_by('-date_requested')
        renter_pending_bookings = renter_bookings.filter(status='pending').order_by('-date_requested')
        renter_approved_bookings = renter_bookings.filter(status='approved').order_by('-date_requested')
        renter_done_bookings = renter_bookings.filter(status='done').order_by('-date_requested')
        renter_rejected_bookings = renter_bookings.filter(status='rejected').order_by('-date_requested')


        user_ratings = {}
        for booking in renter_bookings:
            user_ratings[booking.post.id] = booking.post.rating_set.filter(user=self.request.user).first()

        context = {
            'renter_pending_bookings': renter_pending_bookings,
            'renter_approved_bookings': renter_approved_bookings,
            'renter_done_bookings': renter_done_bookings,
            'renter_rejected_bookings': renter_rejected_bookings,
            'renter_bookings': renter_bookings,
            'host_bookings_pending_approval': host_bookings_pending_approval,
            'host_bookings_approved': host_bookings_approved,
            'host_bookings_done': host_bookings_done,
            'host_bookings_rejected': host_bookings_rejected,
            'user_ratings': user_ratings,
        }
        return context

    
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check for overlapping bookings with pending status
    overlapping_bookings = Booking.objects.filter(
        Q(reservation_start_date__range=(booking.reservation_start_date, booking.reservation_end_date)) |
        Q(reservation_end_date__range=(booking.reservation_start_date, booking.reservation_end_date)),
        post=booking.post,
        status='pending'
    )

    # Approve the selected booking
    booking.status = 'approved'
    booking.pending_approval = False
    booking.save()

    # Reject overlapping bookings
    for overlapping_booking in overlapping_bookings:
        overlapping_booking.status = 'rejected'
        overlapping_booking.pending_approval = False
        overlapping_booking.save()

    return redirect('bookings')

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
    paginate_by = 5
    
    def get_queryset(self):
        # Filter the queryset to include only posts with status='available'
        queryset = Post.objects.filter(status='available')
        # Order the queryset by the 'date_posted' field in descending order (most recent first)
        queryset = queryset.order_by('-date_posted')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_username'] = self.request.GET.get('author_username', '')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'Space4Wheels/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create an instance of the BookingForm and set initial values
        booking_form = BookingForm()
        booking_form.set_initial_values(self.object, self.request.user, self.object.author)

        # Calculate the average rating for the post
        post_ratings = Rating.objects.filter(post=self.object)
        average_rating = post_ratings.aggregate(Avg('rating'))['rating__avg']

        # Check if the user has already rated the post
        user_rating = Rating.objects.filter(post=self.object, user=self.request.user).first()

        context['booking_form'] = booking_form
        context['average_rating'] = average_rating
        context['user_rating'] = user_rating  # Pass the user's rating to the template
        context['booking'] = None  # Add this line

        if self.request.user.is_authenticated:
            # Check if there is a booking with 'done' status
            context['booking'] = Booking.objects.filter(
                post=self.object,
                renter=self.request.user,
                status='done'
            ).first()

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
    
    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})

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
    
    def get_success_url(self):
        post_id = self.kwargs['pk']  # Get the post ID from URL parameters
        return reverse_lazy('post-detail', kwargs={'pk': post_id})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/host/'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def search(request):
    form = SearchForm(request.GET)
    query = request.GET.get('query', '')
    results = []

    if form.is_valid():
        # Split the query into individual keywords
        keywords = query.split()  # Split by space, you can use any separator if needed

        # Start with all posts that are available
        results = Post.objects.filter(status='available')

        # Search each keyword in title, city, and country fields (case-insensitive)
        for keyword in keywords:
            results = results.filter(
                Q(title__icontains=keyword) |
                Q(city__icontains=keyword) |
                Q(country__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(car_space_type__icontains=keyword) 
            ).distinct()

    # Pagination
    paginator = Paginator(results, 5)
    page = request.GET.get('page')

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    return render(request, 'Space4Wheels/search.html', {'query': query, 'results': results})

def author_profile(request):
    author_username = request.GET.get('author_username', '')
    author = get_object_or_404(User, username=author_username)

    # Fetch all ratings given to the author
    author_ratings = UserRating.objects.filter(target_user=author)

    # Calculate average rating
    average_rating = author_ratings.aggregate(Avg('rating'))['rating__avg']

    context = {
        'author': author,
        'average_rating': average_rating,
    }

    return render(request, 'Space4Wheels/author_profile.html', context)


def host(request):
    # Instantiate the class-based view and get the queryset
    user_listings_view = UserParkingSpaceListView()
    user_listings_view.request = request
    user_listings = user_listings_view.get_queryset()
    return render(request, 'Space4Wheels/host.html', {'title': 'Host', 'user_listings': user_listings})

def rate_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    booking = Booking.objects.filter(post=post, renter=request.user, status='done').first()

    if not booking:
        # Redirect or display an error message indicating that the user cannot rate the post.
        return redirect('post-detail', pk=post_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']

            # Save the rating
            rating = Rating.objects.create(user=request.user, post=post, rating=rating_value)

            if rating:
                print(f"Rating saved successfully: {rating}")
            else:
                print("Failed to save the rating")

            # Update the average rating for the post
            post_ratings = Rating.objects.filter(post=post)
            average_rating = post_ratings.aggregate(Avg('rating'))['rating__avg']

            # Update the post's average rating
            post.rating = average_rating
            post.save()

            return redirect('post-detail', pk=post_id)
    else:
        form = RatingForm()

    # Calculate average rating
    post_ratings = Rating.objects.filter(post=post)
    average_rating = post_ratings.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'Space4Wheels/rate_post.html', {'form': form, 'post': post, 'average_rating': average_rating})

@login_required
def rate_user(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = UserRatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']

            print(f'Rater: {request.user}, Target User: {booking.renter}, Rating: {rating_value}')
            
            # Save the rating
            user_rating = UserRating.objects.create(rater=request.user, target_user=booking.renter, rating=rating_value)

            if user_rating:
                print(f"User rating saved successfully: {user_rating}")
            else:
                print("Failed to save user rating")

            # Redirect or return a response as needed
            return redirect('bookings')  # Redirect to the bookings page or any other page

    else:
        form = UserRatingForm()

    return render(request, 'Space4Wheels/rate_user.html', {'form': form, 'booking': booking})


def bookings(request):
    return render(request, 'Space4Wheels/bookings.html', {'title': 'Bookings'})

def about(request):
    return render(request, 'Space4Wheels/about.html', {'title': 'About'})

