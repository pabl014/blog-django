from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Blog, Article, Comment
from django import forms

class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    admin_code = forms.CharField(max_length=6, required=False, help_text="Enter admin code if you have one")

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'avatar', 'admin_code']

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title']

class ArticleForm(forms.ModelForm):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}), required=False)
    class Meta:
        model = Article
        fields = ['title', 'content', 'public', 'password', 'date', 'location', 'images']
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Article Password')