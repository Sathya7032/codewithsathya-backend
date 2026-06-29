from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from blogs.models import Blog

User = get_user_model()

class BlogTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='author@example.com',
            email='author@example.com',
            password='password123'
        )
        self.blog1 = Blog.objects.create(
            title='Understanding Django Rest Framework',
            description='A guide to DRF serialization and views.',
            content='<p>This is the main rich text content of the blog.</p>',
            author=self.user,
            is_published=True
        )
        self.blog2 = Blog.objects.create(
            title='Draft Blog post',
            description='Draft blog content.',
            content='<p>Draft rich text content.</p>',
            author=self.user,
            is_published=False
        )

    def test_blog_slug_auto_generation(self):
        # Blog 1 slug should be auto generated from title
        self.assertEqual(self.blog1.slug, 'understanding-django-rest-framework')
        
        # Test unique slug resolution
        duplicate_blog = Blog.objects.create(
            title='Understanding Django Rest Framework',
            description='Another version.',
            content='Some content',
            is_published=True
        )
        self.assertEqual(duplicate_blog.slug, 'understanding-django-rest-framework-1')

    def test_get_all_blogs_api(self):
        url = reverse('blogs:blog-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only list published blogs (blog1), draft (blog2) should be excluded
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.blog1.title)
        self.assertNotIn('content', response.data[0]) # list serializer shouldn't have content

    def test_get_blog_by_slug_api(self):
        url = reverse('blogs:blog-detail', kwargs={'slug': self.blog1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.blog1.title)
        self.assertEqual(response.data['content'], self.blog1.content)
        self.assertEqual(response.data['author']['email'], self.user.email)

    def test_get_draft_blog_by_slug_api(self):
        # Retrieve should fail/not found for drafts since queryset restricts to is_published=True
        url = reverse('blogs:blog-detail', kwargs={'slug': self.blog2.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
