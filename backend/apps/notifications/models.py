from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class NotificationTemplate(TimeStampedModel):
    """Templates for different types of notifications."""
    
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    )
    
    EVENT_TYPES = (
        ('user_registration', 'User Registration'),
        ('business_registration', 'Business Registration'),
        ('business_verification', 'Business Verification'),
        ('review_submitted', 'Review Submitted'),
        ('review_approved', 'Review Approved'),
        ('lead_received', 'Lead Received'),
        ('payment_received', 'Payment Received'),
        ('subscription_expiry', 'Subscription Expiry'),
        ('ticket_created', 'Support Ticket Created'),
        ('ticket_replied', 'Support Ticket Replied'),
        ('message_received', 'Message Received'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, help_text="Type of notification (email, SMS, push, etc.)")
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, help_text="Event that triggers this notification")
    subject = models.CharField(max_length=200, help_text="Subject line for email notifications (use {{variables}} for dynamic content)")
    content = models.TextField(help_text="Notification content - use {{variable}} for dynamic content like {{user_name}}, {{business_name}}")
    is_active = models.BooleanField(default=True, help_text="Whether this template is active and can be used")
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ['notification_type', 'event_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class Notification(TimeStampedModel):
    """Individual notifications sent to users."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', help_text="User who will receive this notification")
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, help_text="Template used to generate this notification")
    subject = models.CharField(max_length=200, help_text="Processed subject with variables replaced")
    content = models.TextField(help_text="Processed content with variables replaced")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Current delivery status")
    
    # Delivery details
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was sent")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was delivered")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was read by user")
    failed_reason = models.TextField(blank=True, help_text="Reason for delivery failure (if any)")
    
    # Additional data
    data = models.JSONField(default=dict, blank=True, help_text="Additional data used for generating the notification")
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.email} - {self.subject}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if self.status != 'read':
            self.status = 'read'
            self.read_at = models.timezone.now()
            self.save()


class EmailLog(TimeStampedModel):
    """Log of all emails sent."""
    
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ])
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.subject}"


class SMSLog(TimeStampedModel):
    """Log of all SMS sent."""
    
    recipient_phone = models.CharField(max_length=20)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ])
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_phone} - {self.content[:50]}"


class NotificationPreference(TimeStampedModel):
    """User preferences for notifications."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_reviews = models.BooleanField(default=True)
    email_leads = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    email_system = models.BooleanField(default=True)
    
    # SMS preferences
    sms_leads = models.BooleanField(default=True)
    sms_urgent = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)
    
    # Push notification preferences
    push_reviews = models.BooleanField(default=True)
    push_leads = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_marketing = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"