from django.contrib import admin
from .models import Post, Comment

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['post_title', 'slug', 'post_author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'post_author']
    search_fields = ['post_title', 'post_content']
    prepopulated_fields = {'slug': ('post_title',)}
    raw_id_fields = ['post_author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']