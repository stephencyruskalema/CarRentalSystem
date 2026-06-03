from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from functools import wraps
from .models import UserProfile, Car, Booking, Feedback
from .forms import (
    UserRegistrationForm, UserLoginForm,
    BookingForm, CarForm, FeedbackForm
)


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        is_admin_user = False
        
        if request.user.is_superuser or request.user.is_staff:
            is_admin_user = True
            
        if not is_admin_user:
            try:
                if request.user.profile.is_admin():
                    is_admin_user = True
            except UserProfile.DoesNotExist:
                pass
                
        if is_admin_user:
            return view_func(request, *args, **kwargs)
            
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('home')
    return wrapper


def customer_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
            
        try:
            if request.user.profile.is_admin():
                return redirect('admin_dashboard')
        except UserProfile.DoesNotExist:
            pass
            
        return view_func(request, *args, **kwargs)
    return wrapper


# Home 

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
            
        try:
            if request.user.profile.is_admin():
                return redirect('admin_dashboard')
        except UserProfile.DoesNotExist:
            pass
            
        return redirect('car_list')
        
    featured_cars = Car.objects.filter(status='available')[:6]
    return render(request, 'rental/home.html', {'featured_cars': featured_cars})


# Authentication

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                role='customer',
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', ''),
            )
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('car_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'rental/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
                
            try:
                if user.profile.is_admin():
                    return redirect('admin_dashboard')
            except UserProfile.DoesNotExist:
                pass
                
            return redirect('car_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'rental/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# Customer: Cars

@customer_required
def car_list(request):
    cars = Car.objects.filter(status='available')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    if category_filter:
        cars = cars.filter(category=category_filter)
    if search_query:
        cars = cars.filter(
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query)
        )

    categories = Car.CATEGORY_CHOICES
    return render(request, 'rental/car_list.html', {
        'cars': cars,
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query,
    })


@customer_required
def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    existing_bookings = Booking.objects.filter(
        car=car, status__in=['pending', 'approved']
    ).values('start_date', 'end_date')
    return render(request, 'rental/car_detail.html', {
        'car': car,
        'existing_bookings': list(existing_bookings),
    })


# Customer: Bookings 
@customer_required
def book_car(request, pk):
    car = get_object_or_404(Car, pk=pk, status='available')
    if request.method == 'POST':
        form = BookingForm(request.POST, car=car)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            booking.save()
            messages.success(request, f"Booking submitted successfully! Booking #{booking.pk} is pending approval.")
            return redirect('booking_history')
    else:
        form = BookingForm(car=car)
    return render(request, 'rental/book_car.html', {'form': form, 'car': car})


@customer_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rental/booking_history.html', {'bookings': bookings})


@customer_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f"Booking #{booking.pk} has been cancelled.")
    else:
        messages.error(request, "Only pending bookings can be cancelled.")
    return redirect('booking_history')


# Admin Dashboard

@admin_required
def admin_dashboard(request):
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(status='available').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    recent_bookings = Booking.objects.order_by('-created_at')[:10]
    unread_feedback = Feedback.objects.filter(is_read=False).count()

    return render(request, 'rental/admin_dashboard.html', {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'recent_bookings': recent_bookings,
        'unread_feedback': unread_feedback,
    })


@admin_required
def admin_bookings(request):
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.all().order_by('-created_at')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'rental/admin_bookings.html', {
        'bookings': bookings,
        'current_status': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    })


@admin_required
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = 'approved'
    booking.save()
    messages.success(request, f"Booking #{booking.pk} approved.")
    return redirect('admin_bookings')


@admin_required
def cancel_booking_admin(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, f"Booking #{booking.pk} cancelled.")
    return redirect('admin_bookings')


# Admin: Car CRUD 

@admin_required
def admin_cars(request):
    cars = Car.objects.all().order_by('-created_at')
    return render(request, 'rental/admin_cars.html', {'cars': cars})


@admin_required
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"{car.make} {car.model} added successfully.")
            return redirect('admin_cars')
    else:
        form = CarForm()
    return render(request, 'rental/car_form.html', {'form': form, 'action': 'Add'})


@admin_required
def car_update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f"{car.make} {car.model} updated successfully.")
            return redirect('admin_cars')
    else:
        form = CarForm(instance=car)
    return render(request, 'rental/car_form.html', {'form': form, 'car': car, 'action': 'Edit'})


@admin_required
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        name = f"{car.make} {car.model}"
        car.delete()
        messages.success(request, f"{name} has been deleted.")
        return redirect('admin_cars')
    return render(request, 'rental/car_confirm_delete.html', {'car': car})


# Feedback

def contact(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
    else:
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
            form = FeedbackForm(initial=initial)
        else:
            form = FeedbackForm()
    return render(request, 'rental/contact.html', {'form': form})


@admin_required
def admin_feedback(request):
    feedbacks = Feedback.objects.order_by('-created_at')
    Feedback.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'rental/admin_feedback.html', {'feedbacks': feedbacks})