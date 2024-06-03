from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('blogs/new', views.add_blog, name='add_blog'),
    path('blogs/<int:blog_id>/delete/', views.delete_blog, name='delete_blog'),
    path('blogs/<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),
    path('blogs/<int:blog_id>/articles/new', views.add_article, name='add_article'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/delete', views.delete_article, name='delete_article'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/comments/new', views.add_comment, name='add_comment'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/comments/<int:comment_id>/delete', views.delete_comment, name='delete_comment'),
    path('blogs/<int:blog_id>/articles/<int:article_id>/comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
]

handler404 = 'blogApp.views.error_404_view'