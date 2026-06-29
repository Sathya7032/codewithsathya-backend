from django.contrib import admin
from blogs.models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'description', 'content')
    prepopulated_fields = {'slug': ('title',)}
