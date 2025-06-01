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
    photos = Photo.objects.all().order_by('-created_at')
    tags = Tag.objects.all()
    

    tag_filter = request.GET.get('tag')
    if tag_filter:
        photos = photos.filter(tags__name=tag_filter)
    

    search_query = request.GET.get('search', '')
    if search_query:
        photos = photos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    context = {
        'photos': photos,
        'tags': tags,
        'tag_filter': tag_filter,
        'search_query': search_query,
    }
    return render(request, 'gallery/home.html', context)

class PhotoListView(ListView):
    model = Photo
    template_name = 'gallery/photo_list.html'
    context_object_name = 'photos'
    ordering = ['-created_at']
    paginate_by = 12

class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'gallery/photo_detail.html'

@login_required
def like_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.user in photo.likes.all():
        photo.likes.remove(request.user)
    else:
        photo.likes.add(request.user)
    return redirect('gallery:photo_detail', pk=pk)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('gallery:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'gallery/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('gallery:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'gallery/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('gallery:home')

@login_required
def profile(request, pk):
    user_profile = get_object_or_404(UserProfile, user__pk=pk)
    user_photos = Photo.objects.filter(user=user_profile.user).order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'user_photos': user_photos,
    }
    return render(request, 'gallery/profile.html', context)

@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('gallery:profile', pk=request.user.pk)
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'gallery/edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('gallery:profile', pk=request.user.pk)
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'gallery/change_password.html', {'form': form})

@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            form.save_m2m() 
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('gallery:photo_detail', pk=photo.pk)
    else:
        form = PhotoForm()
    return render(request, 'gallery/upload_photo.html', {'form': form})

@login_required
def edit_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo updated successfully!')
            return redirect('gallery:photo_detail', pk=photo.pk)
    else:
        form = PhotoForm(instance=photo)
    
    context = {
        'form': form,
        'photo': photo,
    }
    return render(request, 'gallery/edit_photo.html', context)

@login_required
def delete_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk, user=request.user)
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('gallery:profile', pk=request.user.pk)
    return render(request, 'gallery/delete_photo.html', {'photo': photo})
