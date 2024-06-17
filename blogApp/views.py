import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, PasswordForm
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, BlogForm, ArticleForm, CommentForm
from .models import Blog, Article, Comment, CustomUser

logger = logging.getLogger('blogApp')

def home(request):
    logger.info('User accessed the home page')
    return render(request, 'home.html')

def blog_list(request):
    blogs = Blog.objects.all()
    user_blogs = Blog.objects.filter(author=request.user) if request.user.is_authenticated else None
    logger.info('Displaying list of blogs')
    # Dane udostępniane dla pliku html z listą wszystkich blogów i listą blogów zalogowanego użytkownika
    context = {
        'blogs': blogs,
        'user_blogs': user_blogs,
    }
    return render(request, 'blogs/blog_list.html', context)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    logger.info('Displaying details of a blog')
    articles = Article.objects.filter(blog=blog)
    author_avatar = blog.author.avatar  # Pobieramy avatar autora bloga
    
    return render(request, 'blogs/blog_detail.html', {'blog': blog, 'articles': articles, 'author_avatar': author_avatar})

def article_detail(request, blog_id, article_id):
    logger.info('Displaying details of an article')
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
                logger.info('Password needed to see an article')
                return render(request, 'articles/article_password.html', {'blog_id': blog_id, 'article_id': article_id})

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            logger.info('Comment has been added')
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
        logger.info('Adding a blog')
        form = BlogForm(request.POST)
        if form.is_valid():
            logger.info('Blog has been added')
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog_list')
    else:
        logger.info('Displaying a form for adding a blog')
        form = BlogForm()
    return render(request, 'blogs/add_blog.html', {'form': form})

def add_article(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author:
        if request.method == 'POST':
            logger.info('Adding an article')
            form = ArticleForm(request.POST, request.FILES)
            if form.is_valid():
                logger.info('Article has been added')
                article = form.save(commit=False)
                article.blog = blog
                print("Images:", form.cleaned_data['images'])
                article.save()
                # Przetwarzanie wielu zdjęć dla artykułu
                for image in request.FILES.getlist('images'):
                    article.images.create(article=article, image=image)
                return redirect('blog_detail', blog_id=blog.id)
            else:
                logger.info("Article not added")
                print(form.errors)
        else:
            logger.info('Displaying a form for adding an article')
            form = ArticleForm()
        return render(request, 'articles/add_article.html', {'form': form})
    else:
        logger.warning('You have no permission to add articles on this blog.')
        message = "You have no permission to add articles on this blog."
        return render(request, 'permission_denied.html', {'message': message})


def add_comment(request, blog_id, article_id):
    # Pobranie artykułu o danym id
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        logger.info('Adding a comment')
        form = CommentForm(request.POST)
        if form.is_valid():
            logger.info('Comment has been added')
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
    logger.info('Deleting a blog')
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author or request.user.isAdmin:
        logger.info('Blog has been deleted')
        blog.delete()
    else:
        logger.error('You cannot delete a blog while not being an author of one')
    return redirect('blog_list')

@login_required
def delete_article(request, blog_id, article_id):
    logger.info('Deleting an article')
    article = get_object_or_404(Article, pk=article_id)
    if request.user == article.blog.author or request.user.isAdmin:
        logger.info('Blog has been deleted')
        article.delete()
    else:
        logger.error('You cannot delete an article while not being an author of one')
    return redirect('blog_detail', blog_id=blog_id)

@login_required
def delete_comment(request, blog_id, article_id, comment_id):
    logger.info('Deleting a comment')
    comment = get_object_or_404(Comment, pk=comment_id)
    # Dodajemy warunek, sprawdzający czy aktualnie zalogowany użytkownik jest autorem komentarza
    if request.user == comment.author or request.user.isAdmin:
        logger.info('Comment has been deleted')
        comment.delete()
    else:
        logger.error('You cannot delete a comment while not being an author of one')
    # Przekierowanie na szczegóły artykułu po usunięciu komentarza
    return redirect('article_detail', blog_id=blog_id, article_id=article_id)

@login_required
def edit_blog(request, blog_id):
    logger.info('Editing a blog')
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.user == blog.author:
        if request.method == 'POST':
            form = BlogForm(request.POST, instance=blog)
            if form.is_valid():
                logger.info('Blog has been edited')
                form.save()
                return redirect('blog_detail', blog_id=blog_id)
        else:
            logger.info('Displaying a form for editing a blog')
            form = BlogForm(instance=blog)
        return render(request, 'blogs/edit_blog.html', {'form': form, 'blog': blog})
    else:
        logger.error('You cannot edit a blog while not being an author of one')
        # Pokazanie komunikatu o braku uprawnień w przypadku sytuacji, gdy chcesz edytować blog, kiedy nie jesteś jego autorem
        message = "You do not have permission to edit this blog."
        return render(request, 'permission_denied.html', {'message': message})

@login_required
def edit_article(request, blog_id, article_id):
    logger.info('Editing an article')
    article = get_object_or_404(Article, pk=article_id)
    # Sprawdzamy czy zalogowany użytkownik jest autorem artykułu
    if request.user == article.blog.author:
        if request.method == 'POST':
            form = ArticleForm(request.POST, request.FILES, instance=article)
            if form.is_valid():
                logger.info('Article has been edited')
                article = form.save(commit=False)
                article.save()
                if 'images' in request.FILES:
                    for image in request.FILES.getlist('images'):
                        article.images.create(article=article, image=image)
                return redirect('article_detail', blog_id=blog_id, article_id=article_id)
        else:
            logger.info('Displaying a form for editing an article')
            form = ArticleForm(instance=article)
        return render(request, 'articles/edit_article.html', {'form': form, 'article': article})
    else:
        logger.error('You cannot edit an article while not being an author of one')
        message = "You do not have permission to edit this article."
        return render(request, 'permission_denied.html', {'message': message})

@login_required
def edit_comment(request, blog_id, article_id, comment_id):
    logger.info('Editing a comment')
    comment = get_object_or_404(Comment, pk=comment_id)
    # Sprawdzamy czy zalogowany użytkownik jest autorem komentarza
    if request.user == comment.author:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                logger.info('Comment has been edited')
                form.save()
                return redirect('article_detail', blog_id=blog_id, article_id=article_id)
        else:
            logger.info('Displaying a form for editing a comment')
            form = CommentForm(instance=comment)
        return render(request, 'comments/edit_comment.html', {'form': form, 'comment': comment})
    else:
        logger.error('You cannot edit a comment while not being an author of one')
        message = "You do not have permission to edit this comment."
        return render(request, 'permission_denied.html', {'message': message})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info('Registered successfully')
            user = form.save(commit=False)
            admin_code = form.cleaned_data.get('admin_code')
            if admin_code == '123456':  # Kod ustalony z góry dający uprawnienia admina
                user.isAdmin = True
                logger.info('User granted with admin rights')
            user.save()
            login(request, user)
            return redirect('home')
        else:
            logger.warring('Errors related to form occured')
            print(form.errors)
    else:
        logger.info('Displaying a form for registering a user')
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            logger.info('Logging in a user')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info('Logged in successfully')
                return redirect('/blogs')  # Redirect do listy z blogami po pomyślnym zalogowaniu
            else:
                logger.error('Username or password is not correct')
    else:
        logger.info('Displaying a form for logging in a user')
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logger.info('Successfully logged out')
    logout(request)
    return redirect('/blogs')

def error_404_view(request, exception):
    logger.error('Page does not exist')
    return render(request, '404.html', status=404)