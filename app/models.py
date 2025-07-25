from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Technology(models.Model):
    """Parent model for all technology-specific content"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='tech_logos/')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('technology-detail', kwargs={'slug': self.slug})

    @property
    def all_content(self):
        """Get all content related to this technology"""
        return {
            'tutorials': self.tutorials.all(),
            'blogs': self.blog_posts.all(),
            'snippets': self.code_snippets.all(),
            'updates': self.tech_updates.all()
        }


class Tutorial(models.Model):
    """Tutorial model under Technology"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='tutorials')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_tutorials')
    content = models.TextField(validators=[MinLengthValidator(100)])
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    video_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='tutorial_thumbnails/')
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']
        unique_together = ['technology', 'title']

    def __str__(self):
        return f"{self.technology.name}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.technology.slug}-{self.title}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tutorial-detail', kwargs={'tech_slug': self.technology.slug, 'slug': self.slug})


class Topic(models.Model):
    """Topics under Tutorials"""
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = CKEditor5Field('Text', config_name='extends')
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    code_snippet = models.TextField(blank=True)
    is_free = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['tutorial', 'slug']

    def __str__(self):
        return f"{self.tutorial.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Blog posts under Technology"""
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_blogs')
    excerpt = models.CharField(max_length=300)
    content = CKEditor5Field('Text', config_name='extends')
    thumbnail = models.ImageField(upload_to='blog_thumbnails/')
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.technology.name}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.technology.slug}-{self.title}")
        super().save(*args, **kwargs)


class CodeSnippet(models.Model):
    """Code snippets under Technology"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('csharp', 'C#'),
        ('go', 'Go'),
        ('ruby', 'Ruby'),
        ('php', 'PHP'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('sql', 'SQL'),
    ]

    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='code_snippets')
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_snippets')
    description = models.TextField()
    code = models.TextField()
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    is_public = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.technology.name}: {self.title} ({self.language})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.technology.slug}-{self.title}")
        super().save(*args, **kwargs)



class Question(models.Model):
    """Questions related to a specific Topic"""
    DIFFICULTY_LEVELS = [
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = CKEditor5Field('Text', config_name='extends')
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_LEVELS, default='M')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.topic.title} - {self.text[:50]}..."


class Answer(models.Model):
    """Answer options for a Question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ('question', 'text')

    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text[:30]}..."
