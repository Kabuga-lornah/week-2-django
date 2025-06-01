from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.urls import reverse

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Photo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='photo_likes', blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('gallery:photo_detail', kwargs={'pk': self.pk})
    
    def total_likes(self):
        return self.likes.count()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('gallery:profile', kwargs={'pk': self.user.pk})
