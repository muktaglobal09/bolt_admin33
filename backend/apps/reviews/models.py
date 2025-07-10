from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class Review(TimeStampedModel):
    """Customer reviews for businesses."""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews', help_text="Business being reviewed")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', help_text="User who wrote the review")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, blank=True, help_text="Review title or headline (optional)")
    comment = models.TextField(help_text="Detailed review comment")
    
    # Review status
    is_approved = models.BooleanField(default=False, help_text="Whether the review has been approved by admin")
    is_featured = models.BooleanField(default=False, help_text="Featured reviews are highlighted prominently")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="Date when review was approved")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_reviews', help_text="Admin who approved this review"
    )
    
    # Additional fields
    service_quality = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, help_text="Service quality rating (1-5 stars)"
    )
    value_for_money = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, help_text="Value for money rating (1-5 stars)"
    )
    communication = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, help_text="Communication quality rating (1-5 stars)"
    )
    timeliness = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True, help_text="Timeliness rating (1-5 stars)"
    )
    
    # Verification
    is_verified_purchase = models.BooleanField(default=False, help_text="Whether this review is from a verified customer")
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['business', 'user']  # One review per user per business
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.rating}/5)"


class ReviewReply(TimeStampedModel):
    """Business replies to reviews."""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='reply', help_text="Review being replied to")
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Business user who wrote the reply")
    message = models.TextField(help_text="Reply message to the review")
    is_approved = models.BooleanField(default=True, help_text="Whether the reply is approved and visible")
    
    class Meta:
        verbose_name = 'Review Reply'
        verbose_name_plural = 'Review Replies'
    
    def __str__(self):
        return f"Reply to {self.review}"


class ReviewImage(TimeStampedModel):
    """Images attached to reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', help_text="Review this image belongs to")
    image = models.ImageField(upload_to='reviews/images/', help_text="Image file (recommended: max 2MB)")
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image")
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
    
    def __str__(self):
        return f"Image for {self.review}"


class ReviewHelpful(TimeStampedModel):
    """Track helpful votes for reviews."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes', help_text="Review being voted on")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who voted")
    is_helpful = models.BooleanField(default=True, help_text="True for helpful, False for not helpful")
    
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
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports', help_text="Review being reported")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who reported the review")
    reason = models.CharField(max_length=20, choices=REPORT_REASONS, help_text="Reason for reporting")
    description = models.TextField(blank=True, help_text="Additional details about the report")
    is_resolved = models.BooleanField(default=False, help_text="Whether the report has been resolved")
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_reports', help_text="Admin who resolved the report"
    )
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="Date when report was resolved")
    
    class Meta:
        verbose_name = 'Review Report'
        verbose_name_plural = 'Review Reports'
        unique_together = ['review', 'reported_by']
    
    def __str__(self):
        return f"Report: {self.review} - {self.get_reason_display()}"