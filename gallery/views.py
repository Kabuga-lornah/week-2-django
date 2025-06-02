from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Photo, Tag, UserProfile
from .forms import (
    CustomUserCreationForm, 
    CustomUserChangeForm, 
    ProfileForm, 
    PhotoForm,
    CustomPasswordChangeForm
)

def home(request):
    """Home view with photo gallery, tag filtering, and search functionality"""
    photos = Photo.objects.all().order_by('-created_at')
    tags = Tag.objects.all()
    
    # Filter by tag if specified
    if tag_filter := request.GET.get('tag'):
        photos = photos.filter(tags__name=tag_filter)
    
    # Search across titles, descriptions, and tags
    if search_query := request.GET.get('search', ''):
        photos = photos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    return render(request, 'gallery/home.html', {
        'photos': photos,
        'tags': tags,
        'tag_filter': tag_filter,
        'search_query': search_query,
    })

class PhotoListView(ListView):
    # Paginated list view of all photos
    model = Photo
    template_name = 'gallery/photo_list.html'
    context_object_name = 'photos'
    ordering = ['-created_at']
    paginate_by = 12

class PhotoDetailView(DetailView):
    # Detailed view of a single photo
    model = Photo
    template_name = 'gallery/photo_detail.html'

@login_required
def like_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    
    # Prevent photo owner from liking their own photo
    if request.user == photo.user:
        messages.error(request, "You can't like your own photo")
        return redirect('gallery:photo_detail', pk=pk)
    
    # Toggle like
    if request.user in photo.likes.all():
        photo.likes.remove(request.user)
    else:
        photo.likes.add(request.user)
    
    return redirect('gallery:photo_detail', pk=pk)

def register(request):
    # User registration view
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)  # Create profile for new user
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('gallery:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'gallery/register.html', {'form': form})

def user_login(request):
    # User login view
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('gallery:home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'gallery/login.html')

@login_required
def user_logout(request):
    # Logout view
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('gallery:home')

@login_required
def profile(request, pk):
    # User profile display
    profile = get_object_or_404(UserProfile, user__pk=pk)
    return render(request, 'gallery/profile.html', {
        'user_profile': profile,
        'user_photos': Photo.objects.filter(user=profile.user).order_by('-created_at'),
    })

@login_required
def edit_profile(request):
    # Profile editing view
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('gallery:profile', pk=request.user.pk)
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'gallery/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def change_password(request):
    # Password change view
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Maintain session
            messages.success(request, 'Password updated!')
            return redirect('gallery:profile', pk=user.pk)
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'gallery/change_password.html', {'form': form})

@login_required
def upload_photo(request):
    # Photo upload view
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            form.save_m2m()  # Save many-to-many tags
            messages.success(request, 'Photo uploaded!')
            return redirect('gallery:photo_detail', pk=photo.pk)
    else:
        form = PhotoForm()
    return render(request, 'gallery/upload_photo.html', {'form': form})

@login_required
def edit_photo(request, pk):
    # Photo editing view
    photo = get_object_or_404(Photo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo updated!')
            return redirect('gallery:photo_detail', pk=pk)
    else:
        form = PhotoForm(instance=photo)
    
    return render(request, 'gallery/edit_photo.html', {
        'form': form,
        'photo': photo,
    })

@login_required
def delete_photo(request, pk):
    # Photo deletion view
    photo = get_object_or_404(Photo, pk=pk, user=request.user)
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted!')
        return redirect('gallery:profile', pk=request.user.pk)
    return render(request, 'gallery/delete_photo.html', {'photo': photo})