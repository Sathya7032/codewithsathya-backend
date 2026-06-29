from rest_framework import serializers
from tutorials.models import (
    Course,
    Section,
    Lesson,
    LessonAttachment,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
    CourseRating,
    LessonRating,
    Banner,
    Badge,
)
from users.serializers import UserSerializer

class LessonAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAttachment
        fields = ('id', 'name', 'file', 'created_at')

class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'slug', 'time', 'order', 'views')

class LessonDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    attachments = LessonAttachmentSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Lesson
        fields = (
            'id', 'title', 'slug', 'description', 'time', 
            'author', 'media_file', 'video_url', 'views', 'order', 
            'attachments', 'average_rating'
        )

class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ('id', 'title', 'slug', 'order', 'lessons')

class CourseListSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'level', 'course_time', 'average_rating', 'image')

class CourseDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'level', 'course_time', 'average_rating', 'image', 'sections')


# Quiz and MCQ Question Serializers
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text')

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'choices')

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'passing_score', 'questions')

# Answer Submission Serializers
class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    choice_id = serializers.IntegerField(required=True)

class QuizAttemptSubmissionSerializer(serializers.Serializer):
    answers = AnswerSubmissionSerializer(many=True, required=True)

class QuizAttemptResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ('id', 'score', 'is_passed', 'completed_at')

class LeaderboardSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    score = serializers.IntegerField()
    completed_at = serializers.DateTimeField()
    user_id = serializers.IntegerField(source='user.id')
    email = serializers.EmailField(source='user.email')
    full_name = serializers.CharField(source='user.full_name')


# Rating Serializers
class RatingSubmitSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    review = serializers.CharField(required=False, allow_blank=True, default='')

class CourseRatingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRating
        fields = ('id', 'course', 'user', 'rating', 'review', 'created_at')
        read_only_fields = ('id', 'course', 'user', 'created_at')

class LessonRatingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonRating
        fields = ('id', 'lesson', 'user', 'rating', 'review', 'created_at')
        read_only_fields = ('id', 'lesson', 'user', 'created_at')


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'title', 'badge_text', 'description', 'image', 'order', 'is_active', 'created_at')


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ('id', 'name', 'description', 'image', 'course')
