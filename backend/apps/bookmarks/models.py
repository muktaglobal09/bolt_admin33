from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class Bookmark(TimeStampedModel):
    """User bookmarks for businesses."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='bookmarks')
    notes = models.TextField(blank=True, help_text="Personal notes about this business")
    
    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ['user', 'business']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name}"


class BookmarkCollection(TimeStampedModel):
    """Collections to organize bookmarks."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmark_collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Bookmark Collection'
        verbose_name_plural = 'Bookmark Collections'
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    @property
    def bookmark_count(self):
        return self.bookmarks.count()


class BookmarkCollectionItem(TimeStampedModel):
    """Items in bookmark collections."""
    
    collection = models.ForeignKey(BookmarkCollection, on_delete=models.CASCADE, related_name='bookmarks')
    bookmark = models.ForeignKey(Bookmark, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Bookmark Collection Item'
        verbose_name_plural = 'Bookmark Collection Items'
        unique_together = ['collection', 'bookmark']
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.collection.name} - {self.bookmark.business.name}"


class BusinessComparison(TimeStampedModel):
    """Compare multiple businesses."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    name = models.CharField(max_length=100)
    businesses = models.ManyToManyField(Business, related_name='comparisons')
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Business Comparison'
        verbose_name_plural = 'Business Comparisons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
    @property
    def business_count(self):
        return self.businesses.count()


class Shortlist(TimeStampedModel):
    """Shortlisted businesses for specific needs."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortlists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    businesses = models.ManyToManyField(Business, through='ShortlistItem')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Shortlist'
        verbose_name_plural = 'Shortlists'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class ShortlistItem(TimeStampedModel):
    """Items in shortlists with additional information."""
    
    shortlist = models.ForeignKey(Shortlist, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(default=1, help_text="1=High, 2=Medium, 3=Low")
    notes = models.TextField(blank=True)
    contacted = models.BooleanField(default=False)
    contacted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Shortlist Item'
        verbose_name_plural = 'Shortlist Items'
        unique_together = ['shortlist', 'business']
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"{self.shortlist.name} - {self.business.name}"