from rest_framework import serializers
from blogs.models import Blog
from users.serializers import UserSerializer

class BlogListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'description', 'author', 'image', 'is_published', 'created_at', 'updated_at')


class BlogDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'description', 'content', 'author', 'image', 'is_published', 'created_at', 'updated_at')
