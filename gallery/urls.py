from django.urls import path
from . import views
from .views import PhotoListView, PhotoDetailView

app_name = 'gallery'

urlpatterns = [
    path('', views.home, name='home'),
    path('photos/', PhotoListView.as_view(), name='photo_list'),
    path('photo/<int:pk>/', PhotoDetailView.as_view(), name='photo_detail'),
    path('photo/<int:pk>/like/', views.like_photo, name='like_photo'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile URLs
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Photo management URLs
    path('upload/', views.upload_photo, name='upload_photo'),
    path('photo/<int:pk>/edit/', views.edit_photo, name='edit_photo'),
    path('photo/<int:pk>/delete/', views.delete_photo, name='delete_photo'),
]