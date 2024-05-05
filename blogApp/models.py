from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    isAdmin = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class Blog(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    public = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True)
    date = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"