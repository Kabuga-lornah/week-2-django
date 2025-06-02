from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.urls import reverse

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Unique tag names
    
    def __str__(self):
        return self.name

class Photo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image')  # Cloudinary-stored image
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updates on save
    tags = models.ManyToManyField(Tag, blank=True)  # Optional tags
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Owner of the photo
    likes = models.ManyToManyField(User, related_name='photo_likes', blank=True)  # Like system
    
    def __str__(self):
        return self.title
    
    # URL to view this photo's details
    def get_absolute_url(self):
        return reverse('gallery:photo_detail', kwargs={'pk': self.pk})
    
    def total_likes(self):
        return self.likes.count()  # Count of likes

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Extends User model
    bio = models.TextField(blank=True, null=True)  # Optional bio
    profile_picture = CloudinaryField('image', blank=True, null=True)  # Optional Cloudinary image
    
    def __str__(self):
        return self.user.username
    
    # URL to view this profile
    def get_absolute_url(self):
        return reverse('gallery:profile', kwargs={'pk': self.user.pk})