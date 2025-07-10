from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class TicketCategory(TimeStampedModel):
    """Categories for support tickets."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Category name (e.g., 'Technical Support', 'Billing')")
    description = models.TextField(blank=True, help_text="Description of what issues this category covers")
    is_active = models.BooleanField(default=True, help_text="Whether this category is available for new tickets")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying categories")
    
    class Meta:
        verbose_name = 'Ticket Category'
        verbose_name_plural = 'Ticket Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class SupportTicket(TimeStampedModel):
    """Support tickets from users and businesses."""
    
    PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    # Ticket Information
    ticket_number = models.CharField(max_length=20, unique=True, help_text="Auto-generated unique ticket number")
    subject = models.CharField(max_length=200, help_text="Brief description of the issue")
    description = models.TextField(help_text="Detailed description of the problem or request")
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True, help_text="Category that best describes this ticket")
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium', help_text="Priority level for resolution")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', help_text="Current status of the ticket")
    
    # Requester Information
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', help_text="User who created this ticket")
    requester_email = models.EmailField(help_text="Email address for ticket updates")
    requester_phone = models.CharField(max_length=20, blank=True, help_text="Phone number for urgent contact")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='support_tickets', null=True, blank=True, help_text="Business this ticket is related to (if applicable)")
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', help_text="Support agent assigned to handle this ticket")
    
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="Date and time when ticket was resolved")
    resolution_notes = models.TextField(blank=True, help_text="Notes about how the issue was resolved")
    
    # Customer Satisfaction
    satisfaction_rating = models.PositiveIntegerField(null=True, blank=True, help_text="Customer satisfaction rating (1-5 stars)")
    satisfaction_feedback = models.TextField(blank=True, help_text="Customer feedback about the support experience")
    
    class Meta:
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate ticket number
            from django.utils import timezone
            now = timezone.now()
            self.ticket_number = f"TKT-{now.year}-{now.month:02d}-{self.id or 1:06d}"
        super().save(*args, **kwargs)


class TicketReply(TimeStampedModel):
    """Replies to support tickets."""
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(default=False, help_text="Internal notes not visible to customer")
    
    class Meta:
        verbose_name = 'Ticket Reply'
        verbose_name_plural = 'Ticket Replies'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.ticket.ticket_number} by {self.author.email}"


class TicketAttachment(TimeStampedModel):
    """File attachments for tickets and replies."""
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    reply = models.ForeignKey(TicketReply, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    file = models.FileField(upload_to='helpdesk/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Ticket Attachment'
        verbose_name_plural = 'Ticket Attachments'
    
    def __str__(self):
        return self.filename
    
    def save(self, *args, **kwargs):
        if self.file:
            self.filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class FAQ(TimeStampedModel):
    """Frequently Asked Questions."""
    
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['sort_order', 'question']
    
    def __str__(self):
        return self.question


class KnowledgeBaseArticle(TimeStampedModel):
    """Knowledge base articles."""
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    # SEO
    slug = models.SlugField(max_length=255, unique=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    class Meta:
        verbose_name = 'Knowledge Base Article'
        verbose_name_plural = 'Knowledge Base Articles'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def helpfulness_ratio(self):
        total = self.helpful_count + self.not_helpful_count
        if total > 0:
            return (self.helpful_count / total) * 100
        return 0


class TicketEscalation(TimeStampedModel):
    """Ticket escalation rules and logs."""
    
    ESCALATION_TYPES = (
        ('time_based', 'Time Based'),
        ('priority_based', 'Priority Based'),
        ('manual', 'Manual'),
    )
    
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='escalations')
    escalation_type = models.CharField(max_length=20, choices=ESCALATION_TYPES)
    escalated_from = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_from_tickets')
    escalated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_to_tickets')
    reason = models.TextField()
    
    class Meta:
        verbose_name = 'Ticket Escalation'
        verbose_name_plural = 'Ticket Escalations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Escalation for {self.ticket.ticket_number}"