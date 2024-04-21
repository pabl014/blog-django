from django.shortcuts import render, get_object_or_404
from .models import Blog, Article, Comment

def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blogs/blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    articles = Article.objects.filter(blog=blog)
    return render(request, 'blogs/blog_detail.html', {'blog': blog, 'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    comments = Comment.objects.filter(article=article)
    return render(request, 'articles/article_detail.html', {'article': article, 'comments': comments})