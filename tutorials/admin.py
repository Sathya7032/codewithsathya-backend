from django.contrib import admin
from tutorials.models import (
    Course,
    Section,
    Lesson,
    LessonAttachment,
    CourseRating,
    LessonRating,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    Banner,
    LessonProgress,
    Badge,
    UserBadge,
)

# --- Inlines ---

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    prepopulated_fields = {'slug': ('title',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    prepopulated_fields = {'slug': ('title',)}


class LessonAttachmentInline(admin.TabularInline):
    model = LessonAttachment
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

# --- Admin Registrations ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'course_time', 'average_rating', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'slug')
    list_filter = ('course',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'time', 'author', 'views', 'average_rating', 'order')
    list_filter = ('section__course', 'section')
    search_fields = ('title', 'description', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonAttachmentInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score', 'created_at')
    list_filter = ('lesson__section__course',)
    search_fields = ('title', 'lesson__title')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'is_passed', 'completed_at')
    list_filter = ('is_passed', 'completed_at', 'quiz')
    search_fields = ('user__email', 'quiz__title')
    readonly_fields = ('score', 'is_passed', 'completed_at')


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('course__title', 'user__email', 'review')


@admin.register(LessonRating)
class LessonRatingAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('lesson__title', 'user__email', 'review')


admin.site.register(LessonAttachment)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'badge_text')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('user__email', 'lesson__title')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')
    search_fields = ('name', 'description')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('earned_at',)
    search_fields = ('user__email', 'badge__name')
