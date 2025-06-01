from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Photo, UserProfile, Tag

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_picture')

class PhotoForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Photo
        fields = ('title', 'description', 'image', 'tags')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})