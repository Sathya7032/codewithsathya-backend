from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('pro', 'Pro'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    course_time = models.PositiveIntegerField(help_text="Total duration of the course in minutes")
    image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrolled_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)

    def average_rating(self):
        avg = self.ratings.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 2) if avg is not None else 0.0

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Section.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = CKEditor5Field('Description', config_name='extends')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    time = models.PositiveIntegerField(help_text="Duration of the lesson in minutes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='lessons')
    media_file = models.FileField(upload_to='lessons/media/', blank=True, null=True, help_text="Upload image or video file")
    video_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL of the video (e.g. YouTube, Vimeo, etc.)")
    views = models.PositiveIntegerField(default=0, help_text="Number of views this lesson has received")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def average_rating(self):
        avg = self.ratings.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 2) if avg is not None else 0.0

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Lesson.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_ratings')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'user')

    def __str__(self):
        return f"{self.user.email} rated {self.course.title} as {self.rating}"


class LessonRating(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_ratings')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lesson', 'user')

    def __str__(self):
        return f"{self.user.email} rated lesson {self.lesson.title} as {self.rating}"


class LessonAttachment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='lessons/attachments/', help_text="Upload attachment file")
    name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = self.file.name.split('/')[-1]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lesson.title} - {self.name or self.file.name}"


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    passing_score = models.PositiveIntegerField(default=70, help_text="Passing score percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.title} (Lesson: {self.lesson.title})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Question: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Q: {self.question.text[:30]} - Choice: {self.text} (Correct: {self.is_correct})"


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(help_text="User's score percentage (0-100)")
    is_passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_passed = self.score >= self.quiz.passing_score
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Passed" if self.is_passed else "Failed"
        return f"{self.user.email} - {self.quiz.title}: {self.score}% ({status})"


class Banner(models.Model):
    title = models.CharField(max_length=255)
    badge_text = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField()
    image = models.ImageField(upload_to='banners/images/')
    order = models.PositiveIntegerField(default=0, help_text="Ordering of the banner in the list")
    is_active = models.BooleanField(default=True, help_text="Whether this banner should be active and shown")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name_plural = "Lesson Progresses"

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} (Completed: {self.is_completed})"


class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/images/', blank=True, null=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='badge', blank=True, null=True, help_text="Course that rewards this badge upon completion")

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='owners')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.email} earned {self.badge.name}"
