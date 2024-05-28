from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Blog, Article, Comment
from django import forms

class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)  

    class Meta:
        model = CustomUser
        fields = ['username', 'isAdmin', 'password1', 'password2', 'avatar']

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'public', 'password', 'date', 'location']
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']