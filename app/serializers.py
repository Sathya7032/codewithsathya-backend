from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
from taggit.serializers import TagListSerializerField, TaggitSerializer
from taggit.models import Tag
from .permissions import AdminCreatedOnly


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def create(self, validated_data):
        # Create user using create_user to ensure password is hashed
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        return user

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'text', 'explanation', 'difficulty',
             'created_at', 'updated_at', 'answers'
        ]



class TagSerializer(serializers.ModelSerializer):
    permission_classes = [AdminCreatedOnly]
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class TechnologySerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    permission_classes = [AdminCreatedOnly]

    class Meta:
        model = Technology
        fields = '__all__'

class TutorialSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    technology = serializers.SlugRelatedField(slug_field='slug', queryset=Technology.objects.all())
    author = serializers.StringRelatedField()
    permission_classes = [AdminCreatedOnly]
    
    class Meta:
        model = Tutorial
        fields = '__all__'

class TopicSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    tutorial = serializers.SlugRelatedField(slug_field='slug', queryset=Tutorial.objects.all())
    permission_classes = [AdminCreatedOnly]
    
    class Meta:
        model = Topic
        fields = '__all__'

class BlogPostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    technology = serializers.SlugRelatedField(slug_field='slug', queryset=Technology.objects.all())
    author = serializers.StringRelatedField()
    permission_classes = [AdminCreatedOnly]
    
    class Meta:
        model = BlogPost
        fields = '__all__'

class CodeSnippetSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    technology = serializers.SlugRelatedField(slug_field='slug', queryset=Technology.objects.all())
    author = serializers.StringRelatedField()
    permission_classes = [AdminCreatedOnly]
    
    class Meta:
        model = CodeSnippet
        fields = '__all__'


# serializers.py

class MinimalTutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = ['title', 'slug', 'thumbnail']


class MinimalBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug']


class MinimalCodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippet
        fields = ['title', 'slug']

class MinimalTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['title', 'slug']