from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, BlogForm, ArticleForm, CommentForm
from .models import Blog, Article, Comment, CustomUser


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blogs/blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    articles = Article.objects.filter(blog=blog)
    return render(request, 'blogs/blog_detail.html', {'blog': blog, 'articles': articles})

def article_detail(request, blog_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    comments = article.comment_set.all()  # Pobierz wszystkie komentarze dla tego artykułu

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('article_detail', blog_id=blog_id, article_id=article.id)  # Przeładuj stronę, aby zobaczyć dodany komentarz
    else:
        form = CommentForm()

    return render(request, 'articles/article_detail.html', {'article': article, 'comments': comments, 'form': form})

def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'blogs/add_blog.html', {'form': form})

def add_article(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author:
        if request.method == 'POST':
            form = ArticleForm(request.POST)
            if form.is_valid():
                article = form.save(commit=False)
                article.blog = blog
                article.save()
                return redirect('blog_detail', blog_id=blog.id)
        else:
            form = ArticleForm()
        return render(request, 'articles/add_article.html', {'form': form})
    else:
        message = "You have no permission to add articles on this blog."
        return render(request, 'permission_denied.html', {'message': message})

def add_comment(request, blog_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = CommentForm()
    return render(request, 'comments/add_comment.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/blogs')  # Redirect to the desired page after login
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('/blogs')