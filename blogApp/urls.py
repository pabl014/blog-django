from django.urls import path
from . import views
urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
]