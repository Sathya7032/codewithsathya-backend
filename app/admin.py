from django.contrib import admin
from django.utils.html import format_html
from taggit.admin import TagAdmin
from taggit.models import Tag
from .models import *

# Unregister default Tag admin if using custom tag model
admin.site.unregister(Tag)

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'is_active', 'tag_list', 'created_at')
    list_filter = ('is_active', 'tags', 'created_at')
    search_fields = ('name', 'description', 'tags__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('logo_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'is_active')}),
        ('Media', {'fields': ('logo', 'logo_preview')}),
        ('Tags', {'fields': ('tags',)}),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'


class TopicInline(admin.StackedInline):
    model = Topic
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('title', 'slug', 'order', 'content', 'code_snippet', 'is_free', 'tags', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'author', 'difficulty', 'is_published', 'published_date', 'tag_list')
    list_filter = ('technology', 'difficulty', 'is_published', 'tags', 'published_date')
    search_fields = ('title', 'content', 'technology__name', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    inlines = [TopicInline]
    date_hierarchy = 'published_date'
    fieldsets = (
        (None, {'fields': ('technology', 'title', 'slug', 'author')}),
        ('Content', {'fields': ('content', 'video_url', 'difficulty', 'thumbnail')}),
        ('Metadata', {'fields': ('tags', 'is_published', 'published_date')}),
        ('Statistics', {'fields': ('view_count',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('technology', 'author').prefetch_related('tags')

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    def view_count(self, obj):
        return obj.views
    view_count.short_description = 'Views'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'tutorial', 'order', 'is_free', 'created_at')
    list_filter = ('is_free', 'tutorial__technology', 'tags')
    search_fields = ('title', 'content', 'tutorial__title')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('order', 'is_free')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'author', 'is_published', 'published_date', 'tag_list')
    list_filter = ('technology', 'is_published', 'tags', 'published_date')
    search_fields = ('title', 'content', 'technology__name', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'thumbnail_preview')
    date_hierarchy = 'published_date'
    fieldsets = (
        (None, {'fields': ('technology', 'title', 'slug', 'author')}),
        ('Content', {'fields': ('excerpt', 'content', 'thumbnail', 'thumbnail_preview')}),
        ('Metadata', {'fields': ('tags', 'is_published', 'published_date')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('technology', 'author').prefetch_related('tags')

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'language', 'is_public', 'author', 'created_at', 'tag_list')
    list_filter = ('technology', 'language', 'is_public', 'tags')
    search_fields = ('title', 'description', 'code', 'technology__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('technology', 'title', 'slug', 'author', 'language')}),
        ('Content', {'fields': ('description', 'code')}),
        ('Settings', {'fields': ('is_public', 'tags')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('technology', 'author').prefetch_related('tags')

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

admin.site.register(Question)
admin.site.register(Answer)