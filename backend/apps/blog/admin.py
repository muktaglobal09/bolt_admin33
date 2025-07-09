from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BlogCategory, BlogPost, BlogComment, BlogNewsletter,
    BlogSeries, BlogSeriesPost, BlogTag
)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'post_count')
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description', 'image', 'is_active', 'sort_order')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('post_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_count(self, obj):
        return obj.post_count
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'status', 'is_published',
        'is_featured', 'view_count', 'comment_count', 'published_at'
    )
    list_filter = ('status', 'is_published', 'is_featured', 'category', 'author', 'published_at', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'comment_count')
    filter_horizontal = ()
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'excerpt', 'content', 'author', 'category')
        }),
        ('Publishing', {
            'fields': ('status', 'is_published', 'published_at', 'is_featured', 'allow_comments')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'comment_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_posts', 'unpublish_posts', 'feature_posts']
    
    def publish_posts(self, request, queryset):
        queryset.update(is_published=True, status='published')
        self.message_user(request, f"{queryset.count()} posts published.")
    publish_posts.short_description = "Publish selected posts"
    
    def unpublish_posts(self, request, queryset):
        queryset.update(is_published=False, status='draft')
        self.message_user(request, f"{queryset.count()} posts unpublished.")
    unpublish_posts.short_description = "Unpublish selected posts"
    
    def feature_posts(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} posts featured.")
    feature_posts.short_description = "Feature selected posts"
    
    def comment_count(self, obj):
        return obj.comment_count
    comment_count.short_description = 'Comments'


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'post', 'is_approved', 'is_spam', 'created_at')
    list_filter = ('is_approved', 'is_spam', 'created_at', 'post__category')
    search_fields = ('author_name', 'author_email', 'content', 'post__title')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author_name', 'author_email', 'author_website', 'content', 'parent')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'approved_by', 'approved_at', 'is_spam')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'disapprove_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_approved=True, approved_by=request.user, approved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} comments disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"
    
    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True, is_approved=False)
        self.message_user(request, f"{queryset.count()} comments marked as spam.")
    mark_as_spam.short_description = "Mark selected comments as spam"


@admin.register(BlogNewsletter)
class BlogNewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'confirmed_at', 'created_at')
    list_filter = ('is_active', 'confirmed_at', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('created_at', 'updated_at', 'confirmed_at', 'unsubscribed_at')
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


class BlogSeriesPostInline(admin.TabularInline):
    model = BlogSeriesPost
    extra = 0
    fields = ('post', 'order')


@admin.register(BlogSeries)
class BlogSeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'post_count')
    inlines = [BlogSeriesPostInline]
    
    fieldsets = (
        ('Series Information', {
            'fields': ('name', 'description', 'image', 'is_active')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('post_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_count(self, obj):
        return obj.post_count
    post_count.short_description = 'Posts'


@admin.register(BlogSeriesPost)
class BlogSeriesPostAdmin(admin.ModelAdmin):
    list_display = ('series', 'post', 'order', 'created_at')
    list_filter = ('series', 'created_at')
    search_fields = ('series__name', 'post__title')


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'is_featured', 'color', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'post_count')
    
    def post_count(self, obj):
        return obj.post_count
    post_count.short_description = 'Posts'