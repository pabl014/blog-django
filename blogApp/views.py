from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, PasswordForm
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, BlogForm, ArticleForm, CommentForm
from .models import Blog, Article, Comment, CustomUser

def home(request):
    return render(request, 'home.html')

def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blogs/blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    articles = Article.objects.filter(blog=blog)
    author_avatar = blog.author.avatar  # Pobieramy avatar autora bloga
    
    return render(request, 'blogs/blog_detail.html', {'blog': blog, 'articles': articles, 'author_avatar': author_avatar})

def article_detail(request, blog_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    comments = article.comment_set.all()
    images = article.article_images.all()

    if not article.public:
        # Sprawdzenie, czy użytkownik jest autorem artykułu
        if request.user != article.blog.author:
            if request.method == 'POST':
                entered_password = request.POST.get('password')
                if entered_password != article.password:
                    error_message = "Incorrect password."
                    return render(request, 'articles/article_password.html', {'error_message': error_message, 'blog_id': blog_id, 'article_id': article_id})
            else:
                return render(request, 'articles/article_password.html', {'blog_id': blog_id, 'article_id': article_id})

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('article_detail', blog_id=blog_id, article_id=article.id)
    else:
        form = CommentForm()

    return render(request, 'articles/article_detail.html', {'article': article, 'comments': comments, 'form': form, 'blog_id': blog_id, 'images': images})


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
            form = ArticleForm(request.POST, request.FILES)
            if form.is_valid():
                article = form.save(commit=False)
                article.blog = blog
                print("Images:", form.cleaned_data['images'])
                article.save()
                # Przetwarzanie wielu zdjęć dla artykułu
                for image in request.FILES.getlist('images'):
                    article.images.create(article=article, image=image)
                return redirect('blog_detail', blog_id=blog.id)
            else:
                print(form.errors)
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

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author:
        blog.delete()
    return redirect('blog_list')

@login_required
def delete_article(request, blog_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.user == article.blog.author:
        article.delete()
    return redirect('blog_detail', blog_id=blog_id)

@login_required
def delete_comment(request, blog_id, article_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    # Dodajemy warunek, sprawdzający czy aktualnie zalogowany użytkownik jest autorem komentarza
    if request.user == comment.author:
        comment.delete()
    # Przekierowanie na szczegóły artykułu po usunięciu komentarza
    return redirect('article_detail', blog_id=blog_id, article_id=article_id)

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author:
        if request.method == 'POST':
            form = BlogForm(request.POST, instance=blog)
            if form.is_valid():
                form.save()
                return redirect('blog_detail', blog_id=blog_id)
        else:
            form = BlogForm(instance=blog)
        return render(request, 'blogs/edit_blog.html', {'form': form, 'blog': blog})
    else:
        message = "You do not have permission to edit this blog."
        return render(request, 'permission_denied.html', {'message': message})

@login_required
def edit_article(request, blog_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.user == article.blog.author:
        if request.method == 'POST':
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                article = form.save(commit=False)
                article.save()
                if 'images' in request.FILES:
                    for image in request.FILES.getlist('images'):
                        article.images.create(article=article, image=image)
                return redirect('article_detail', blog_id=blog_id, article_id=article_id)
        else:
            form = ArticleForm(instance=article)
        return render(request, 'articles/edit_article.html', {'form': form, 'article': article})
    else:
        message = "You do not have permission to edit this article."
        return render(request, 'permission_denied.html', {'message': message})

@login_required
def edit_comment(request, blog_id, article_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                return redirect('article_detail', blog_id=blog_id, article_id=article_id)
        else:
            form = CommentForm(instance=comment)
        return render(request, 'comments/edit_comment.html', {'form': form, 'comment': comment})
    else:
        message = "You do not have permission to edit this comment."
        return render(request, 'permission_denied.html', {'message': message})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            admin_code = form.cleaned_data.get('admin_code')
            if admin_code == '123456':  # Replace '123456' with your desired admin code
                user.isAdmin = True
            user.save()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)
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

def error_404_view(request, exception):
    return render(request, '404.html', status=404)