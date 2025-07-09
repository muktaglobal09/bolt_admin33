from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class Review(TimeStampedModel):
    """Customer reviews for businesses."""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Review status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_reviews'
    )
    
    # Additional fields
    service_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    value_for_money = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    communication = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    timeliness = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Verification
    is_verified_purchase = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['business', 'user']  # One review per user per business
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.rating}/5)"


class ReviewReply(TimeStampedModel):
    """Business replies to reviews."""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='reply')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Review Reply'
        verbose_name_plural = 'Review Replies'
    
    def __str__(self):
        return f"Reply to {self.review}"


class ReviewImage(TimeStampedModel):
    """Images attached to reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/images/')
    caption = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
    
    def __str__(self):
        return f"Image for {self.review}"


class ReviewHelpful(TimeStampedModel):
    """Track helpful votes for reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Review Helpful Vote'
        verbose_name_plural = 'Review Helpful Votes'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.review} ({'Helpful' if self.is_helpful else 'Not Helpful'})"


class ReviewReport(TimeStampedModel):
    """Reports for inappropriate reviews."""
    
    REPORT_REASONS = (
        ('spam', 'Spam'),
        ('fake', 'Fake Review'),
        ('inappropriate', 'Inappropriate Content'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant'),
        ('other', 'Other'),
    )
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Review Report'
        verbose_name_plural = 'Review Reports'
        unique_together = ['review', 'reported_by']
    
    def __str__(self):
        return f"Report: {self.review} - {self.get_reason_display()}"