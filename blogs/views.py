from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from blogs.models import Blog
from blogs.serializers import BlogListSerializer, BlogDetailSerializer

class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.filter(is_published=True)
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return BlogListSerializer
