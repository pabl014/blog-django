from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Blog, Article, Comment, CustomUser
from .forms import CustomUserCreationForm, BlogForm, ArticleForm, CommentForm

User = get_user_model()

class BlogAppTests(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', password='password', isAdmin=True)

        # Create a blog
        self.blog = Blog.objects.create(title='Test Blog', author=self.user)

        # Create an article
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article',
            public=True,
            date='2022-01-01',
            location='Test Location',
            blog=self.blog
        )

        # Create a comment
        self.comment = Comment.objects.create(
            author=self.user,
            body='This is a test comment',
            article=self.article
        )

    def test_blog_creation(self):
        self.assertEqual(self.blog.title, 'Test Blog')
        self.assertEqual(self.blog.author.username, 'testuser')

    def test_article_creation(self):
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.blog, self.blog)

    def test_comment_creation(self):
        self.assertEqual(self.comment.body, 'This is a test comment')
        self.assertEqual(self.comment.author.username, 'testuser')
        self.assertEqual(self.comment.article, self.article)

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertEqual(response.status_code, 302)  # Check if it redirects after successful registration

        user_model = get_user_model()
        user_exists = user_model.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)  # Ensure the user is actually created

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        data = {
            'username': 'testuser',
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_blog_list_view(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/blog_list.html')

    def test_blog_detail_view(self):
        response = self.client.get(reverse('blog_detail', args=[self.blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/blog_detail.html')

    def test_article_detail_view(self):
        response = self.client.get(reverse('article_detail', args=[self.blog.id, self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_detail.html')

    def test_add_blog_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_blog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/add_blog.html')

        data = {
            'title': 'New Test Blog'
        }
        response = self.client.post(reverse('add_blog'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Blog.objects.filter(title='New Test Blog').exists())

    def test_add_article_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('add_article', args=[self.blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/add_article.html')

        data = {
            'title': 'New Test Article',
            'content': 'This is a new test article',
            'public': True,
            'date': '2022-02-01',
            'location': 'New Test Location',
        }
        response = self.client.post(reverse('add_article', args=[self.blog.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title='New Test Article').exists())

    # def test_add_comment_view(self):
    #     self.client.login(username='testuser', password='ComplexPassword123!')
    #     response = self.client.get(reverse('add_comment', args=[self.blog.id, self.article.id]))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'blogs/blog_detail.html')

    #     data = {
    #         'body': 'This is another test comment'
    #     }
    #     response = self.client.post(reverse('add_comment', args=[self.blog.id, self.article.id]), data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(Comment.objects.filter(body='This is another test comment').exists())

    def test_edit_blog_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('edit_blog', args=[self.blog.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/edit_blog.html')

        data = {
            'title': 'Updated Test Blog'
        }
        response = self.client.post(reverse('edit_blog', args=[self.blog.id]), data)
        self.assertEqual(response.status_code, 302)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Updated Test Blog')

    def test_edit_article_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('edit_article', args=[self.blog.id, self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/edit_article.html')

        data = {
            'title': 'Updated Test Article',
            'content': 'This is an updated test article',
            'public': True,
            'date': '2022-03-01',
            'location': 'Updated Test Location'
        }
        response = self.client.post(reverse('edit_article', args=[self.blog.id, self.article.id]), data)
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Test Article')

    def test_edit_comment_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('edit_comment', args=[self.blog.id, self.article.id, self.comment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comments/edit_comment.html')

        data = {
            'body': 'This is an updated test comment'
        }
        response = self.client.post(reverse('edit_comment', args=[self.blog.id, self.article.id, self.comment.id]), data)
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, 'This is an updated test comment')

    def test_delete_blog_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('delete_blog', args=[self.blog.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Blog.objects.filter(id=self.blog.id).exists())

    def test_delete_article_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('delete_article', args=[self.blog.id, self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_delete_comment_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('delete_comment', args=[self.blog.id, self.article.id, self.comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

