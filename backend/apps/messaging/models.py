from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class Conversation(TimeStampedModel):
    """Conversations between users and businesses."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('blocked', 'Blocked'),
    )
    
    # Participants
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_conversations', help_text="Customer/user in the conversation")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_conversations', help_text="Business involved in the conversation")
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_user_conversations', help_text="Business representative handling the conversation")
    
    # Conversation details
    subject = models.CharField(max_length=200, blank=True, help_text="Conversation subject or topic")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', help_text="Current status of the conversation")
    
    # Last message info
    last_message_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last message")
    last_message_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_messages', help_text="User who sent the last message")
    
    # Read status
    user_last_read = models.DateTimeField(null=True, blank=True, help_text="Last time the user read messages")
    business_user_last_read = models.DateTimeField(null=True, blank=True, help_text="Last time the business user read messages")
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at', '-created_at']
        unique_together = ['user', 'business']
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name}"
    
    @property
    def unread_count_for_user(self):
        """Unread messages count for the user."""
        if not self.user_last_read:
            return self.messages.count()
        return self.messages.filter(created_at__gt=self.user_last_read, sender=self.business_user).count()
    
    @property
    def unread_count_for_business(self):
        """Unread messages count for the business user."""
        if not self.business_user_last_read:
            return self.messages.count()
        return self.messages.filter(created_at__gt=self.business_user_last_read, sender=self.user).count()


class Message(TimeStampedModel):
    """Individual messages in conversations."""
    
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System Message'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True)
    
    # File attachments
    attachment = models.FileField(upload_to='messages/attachments/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    
    # Message status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation's last message info
        self.conversation.last_message_at = self.created_at
        self.conversation.last_message_by = self.sender
        self.conversation.save()


class MessageReport(TimeStampedModel):
    """Reports for inappropriate messages."""
    
    REPORT_REASONS = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('fraud', 'Fraud/Scam'),
        ('other', 'Other'),
    )
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_message_reports')
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Message Report'
        verbose_name_plural = 'Message Reports'
        unique_together = ['message', 'reported_by']
    
    def __str__(self):
        return f"Report: {self.message} - {self.get_reason_display()}"


class MessageTemplate(TimeStampedModel):
    """Pre-defined message templates for businesses."""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='message_templates')
    name = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Message Template'
        verbose_name_plural = 'Message Templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class ChatSettings(TimeStampedModel):
    """Chat settings for businesses."""
    
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='chat_settings')
    
    # Availability
    is_chat_enabled = models.BooleanField(default=True)
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_message = models.TextField(blank=True, default="Thank you for your message. We'll get back to you soon!")
    
    # Working hours for chat
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    wednesday_start = models.TimeField(null=True, blank=True)
    wednesday_end = models.TimeField(null=True, blank=True)
    thursday_start = models.TimeField(null=True, blank=True)
    thursday_end = models.TimeField(null=True, blank=True)
    friday_start = models.TimeField(null=True, blank=True)
    friday_end = models.TimeField(null=True, blank=True)
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)
    
    # Offline message
    offline_message = models.TextField(blank=True, default="We're currently offline. Please leave a message and we'll get back to you.")
    
    class Meta:
        verbose_name = 'Chat Settings'
        verbose_name_plural = 'Chat Settings'
    
    def __str__(self):
        return f"Chat Settings for {self.business.name}"


class BlockedUser(TimeStampedModel):
    """Blocked users for businesses."""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='blocked_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_businesses')
    reason = models.TextField(blank=True)
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    
    class Meta:
        verbose_name = 'Blocked User'
        verbose_name_plural = 'Blocked Users'
        unique_together = ['business', 'user']
    
    def __str__(self):
        return f"{self.business.name} blocked {self.user.email}"