from django.db import models
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from apps.core.models import TimeStampedModel, SEOModel

User = get_user_model()


class BlogCategory(TimeStampedModel, SEOModel):
    """Categories for blog posts."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def post_count(self):
        return self.posts.filter(is_published=True).count()


class BlogPost(TimeStampedModel, SEOModel):
    """Blog posts for SEO and content marketing."""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    excerpt = models.TextField(max_length=300, help_text="Short description for previews")
    content = RichTextUploadingField()
    
    # Publishing
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='blog/posts/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=255, blank=True)
    
    # Engagement
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    # Tags
    tags = TaggableManager(blank=True)
    
    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class BlogComment(TimeStampedModel):
    """Comments on blog posts."""
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_comments')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Threading (for replies)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Spam detection
    is_spam = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Blog Comment'
        verbose_name_plural = 'Blog Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author_name} on {self.post.title}"


class BlogNewsletter(TimeStampedModel):
    """Newsletter subscriptions."""
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class BlogSeries(TimeStampedModel, SEOModel):
    """Blog post series."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='blog/series/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Blog Series'
        verbose_name_plural = 'Blog Series'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def post_count(self):
        return self.posts.filter(is_published=True).count()


class BlogSeriesPost(TimeStampedModel):
    """Posts in a blog series."""
    
    series = models.ForeignKey(BlogSeries, on_delete=models.CASCADE, related_name='posts')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='series')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Blog Series Post'
        verbose_name_plural = 'Blog Series Posts'
        ordering = ['order']
        unique_together = ['series', 'post']
    
    def __str__(self):
        return f"{self.series.name} - {self.post.title}"


class BlogTag(TimeStampedModel):
    """Custom blog tags with additional metadata."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def post_count(self):
        from taggit.models import TaggedItem
        return TaggedItem.objects.filter(tag__name=self.name).count()