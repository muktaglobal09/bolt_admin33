from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class CRMSettings(TimeStampedModel):
    """Global CRM settings and configurations."""
    
    # Lead Management
    auto_convert_leads = models.BooleanField(default=False, help_text="Automatically convert qualified leads to contacts")
    lead_score_threshold = models.PositiveIntegerField(default=75, help_text="Lead score threshold for auto-conversion")
    
    # Activity Tracking
    auto_update_last_contacted = models.BooleanField(default=True, help_text="Auto-update last contacted date on activities")
    
    # Notifications
    notify_on_lead_assignment = models.BooleanField(default=True)
    notify_on_deal_stage_change = models.BooleanField(default=True)
    notify_on_task_overdue = models.BooleanField(default=True)
    
    # Data Retention
    archive_old_leads_days = models.PositiveIntegerField(default=365, help_text="Archive leads older than X days")
    delete_old_activities_days = models.PositiveIntegerField(default=730, help_text="Delete activities older than X days")
    
    # Default Values
    default_lead_source = models.CharField(max_length=50, default='website')
    default_deal_probability = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = 'CRM Settings'
        verbose_name_plural = 'CRM Settings'
    
    def __str__(self):
        return "CRM Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and CRMSettings.objects.exists():
            raise ValueError("Only one CRM Settings instance is allowed")
        super().save(*args, **kwargs)


class Lead(TimeStampedModel):
    """Lead management for potential customers."""
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )
    
    LEAD_SOURCES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('cold_call', 'Cold Call'),
        ('email_campaign', 'Email Campaign'),
        ('trade_show', 'Trade Show'),
        ('partner', 'Partner'),
        ('organic_search', 'Organic Search'),
        ('paid_search', 'Paid Search'),
        ('other', 'Other'),
    )
    
    PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    # Basic Information
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_leads')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone_number = PhoneNumberField(blank=True, null=True)
    company = models.CharField(max_length=200, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    
    # Lead Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCES, default='website')
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium')
    
    # Scoring and Qualification
    lead_score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    qualification_notes = models.TextField(blank=True)
    
    # Assignment and Ownership
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_leads')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    
    # Campaign and Marketing
    campaign_name = models.CharField(max_length=200, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    
    # Interaction Tracking
    last_contacted = models.DateTimeField(null=True, blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    
    # Conversion Tracking
    converted_at = models.DateTimeField(null=True, blank=True)
    converted_to_contact = models.ForeignKey('CRMContact', on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_lead')
    converted_to_deal = models.ForeignKey('CRMDeal', on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_lead')
    
    # Additional Information
    notes = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    
    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'status']),
            models.Index(fields=['lead_source']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['lead_score']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company or self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def calculate_lead_score(self):
        """Calculate lead score based on various factors."""
        score = 0
        
        # Company information (20 points)
        if self.company:
            score += 10
        if self.designation:
            score += 10
        
        # Contact completeness (20 points)
        if self.phone_number:
            score += 10
        if self.website:
            score += 5
        if self.address:
            score += 5
        
        # Engagement (30 points)
        activity_count = self.activities.count()
        if activity_count >= 5:
            score += 20
        elif activity_count >= 3:
            score += 15
        elif activity_count >= 1:
            score += 10
        
        # Source quality (15 points)
        source_scores = {
            'referral': 15,
            'partner': 12,
            'trade_show': 10,
            'website': 8,
            'social_media': 6,
            'advertisement': 5,
            'cold_call': 3,
            'other': 2
        }
        score += source_scores.get(self.lead_source, 0)
        
        # Recency (15 points)
        if self.last_contacted:
            from django.utils import timezone
            days_since_contact = (timezone.now() - self.last_contacted).days
            if days_since_contact <= 7:
                score += 15
            elif days_since_contact <= 30:
                score += 10
            elif days_since_contact <= 90:
                score += 5
        
        self.lead_score = min(100, score)
        return self.lead_score


class CRMContact(TimeStampedModel):
    """Enhanced CRM contacts for businesses."""
    
    CONTACT_TYPES = (
        ('lead', 'Lead'),
        ('customer', 'Customer'),
        ('prospect', 'Prospect'),
        ('partner', 'Partner'),
        ('vendor', 'Vendor'),
    )
    
    LEAD_SOURCES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('cold_call', 'Cold Call'),
        ('email_campaign', 'Email Campaign'),
        ('trade_show', 'Trade Show'),
        ('other', 'Other'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_contacts')
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    company = models.CharField(max_length=200, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    
    # Contact Details
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES, default='lead')
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCES, blank=True)
    
    # Assignment and Ownership
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_contacts')
    
    # Address
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='India')
    
    # Interaction Tracking
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'CRM Contact'
        verbose_name_plural = 'CRM Contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'contact_type']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.account.name})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class CRMDeal(TimeStampedModel):
    """Enhanced CRM deals/opportunities."""
    
    DEAL_STAGES = (
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('needs_analysis', 'Needs Analysis'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    )
    
    PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_deals')
    contact = models.ForeignKey(CRMContact, on_delete=models.CASCADE, related_name='deals')
    
    # Deal Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='INR')
    
    # Status and Pipeline
    stage = models.CharField(max_length=20, choices=DEAL_STAGES, default='prospecting')
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium')
    probability = models.PositiveIntegerField(default=0, help_text="Probability of closing (0-100%)")
    
    # Assignment and Ownership
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_deals')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deals')
    
    # Dates
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    
    # Interaction Tracking
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    
    # Competition and Source
    competitors = models.TextField(blank=True, help_text="Competing companies or solutions")
    lead_source = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'CRM Deal'
        verbose_name_plural = 'CRM Deals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account', 'stage']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.contact.full_name}"


class DealProduct(TimeStampedModel):
    """Products associated with deals."""
    
    deal = models.ForeignKey(CRMDeal, on_delete=models.CASCADE, related_name='deal_products')
    product = models.ForeignKey('businesses.BusinessProduct', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Deal Product'
        verbose_name_plural = 'Deal Products'
        unique_together = ['deal', 'product']
    
    def __str__(self):
        return f"{self.deal.title} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        discounted_price = self.unit_price * (1 - self.discount_percentage / 100)
        self.total_amount = discounted_price * self.quantity
        super().save(*args, **kwargs)


class CRMActivity(TimeStampedModel):
    """Enhanced CRM activities and interactions."""
    
    ACTIVITY_TYPES = (
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('task', 'Task'),
        ('note', 'Note'),
        ('sms', 'SMS'),
        ('demo', 'Product Demo'),
        ('proposal', 'Proposal Sent'),
        ('follow_up', 'Follow Up'),
        ('other', 'Other'),
    )
    
    ACTIVITY_STATUS = (
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_activities')
    contact = models.ForeignKey(CRMContact, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    deal = models.ForeignKey(CRMDeal, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    
    # Activity Details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ACTIVITY_STATUS, default='planned')
    
    # Scheduling
    activity_date = models.DateField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities')
    
    # Outcome
    outcome = models.TextField(blank=True, help_text="Result or outcome of the activity")
    follow_up_required = models.BooleanField(default=False)
    next_follow_up_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'CRM Activity'
        verbose_name_plural = 'CRM Activities'
        ordering = ['-scheduled_at', '-created_at']
        indexes = [
            models.Index(fields=['account', 'activity_type']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} ({self.get_activity_type_display()})"


class CRMTask(TimeStampedModel):
    """Enhanced CRM tasks and reminders."""
    
    TASK_PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    TASK_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    )
    
    TASK_TYPES = (
        ('follow_up', 'Follow Up'),
        ('call', 'Make Call'),
        ('email', 'Send Email'),
        ('meeting', 'Schedule Meeting'),
        ('proposal', 'Prepare Proposal'),
        ('research', 'Research'),
        ('admin', 'Administrative'),
        ('other', 'Other'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_tasks')
    contact = models.ForeignKey(CRMContact, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    deal = models.ForeignKey(CRMDeal, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    
    # Task Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default='other')
    priority = models.CharField(max_length=10, choices=TASK_PRIORITIES, default='medium')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending')
    
    # Scheduling
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateTimeField(null=True, blank=True)
    
    # Dependencies
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks')
    
    class Meta:
        verbose_name = 'CRM Task'
        verbose_name_plural = 'CRM Tasks'
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['account', 'status']),
            models.Index(fields=['assigned_to', 'due_date']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} (Due: {self.due_date.strftime('%Y-%m-%d')})"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status not in ['completed', 'cancelled']


class CRMNote(TimeStampedModel):
    """Enhanced CRM notes and comments."""
    
    NOTE_TYPES = (
        ('general', 'General Note'),
        ('call_log', 'Call Log'),
        ('meeting_minutes', 'Meeting Minutes'),
        ('follow_up', 'Follow Up Note'),
        ('internal', 'Internal Note'),
        ('customer_feedback', 'Customer Feedback'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_notes')
    contact = models.ForeignKey(CRMContact, on_delete=models.CASCADE, related_name='crm_notes', null=True, blank=True)
    deal = models.ForeignKey(CRMDeal, on_delete=models.CASCADE, related_name='crm_notes', null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='crm_notes', null=True, blank=True)
    
    # Note Details
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    is_private = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Author
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crm_notes')
    
    # Attachments
    attachment = models.FileField(upload_to='crm/notes/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'CRM Note'
        verbose_name_plural = 'CRM Notes'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['account', 'note_type']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Note'} by {self.created_by.email}"


class CRMPipeline(TimeStampedModel):
    """Custom sales pipelines for different business types."""
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_pipelines')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'CRM Pipeline'
        verbose_name_plural = 'CRM Pipelines'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.account.name} - {self.name}"


class CRMPipelineStage(TimeStampedModel):
    """Stages within a sales pipeline."""
    
    pipeline = models.ForeignKey(CRMPipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    probability = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    sort_order = models.PositiveIntegerField(default=0)
    is_closed_stage = models.BooleanField(default=False)
    is_won_stage = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'CRM Pipeline Stage'
        verbose_name_plural = 'CRM Pipeline Stages'
        ordering = ['sort_order']
        unique_together = ['pipeline', 'name']
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class CRMReport(TimeStampedModel):
    """Custom CRM reports and analytics."""
    
    REPORT_TYPES = (
        ('leads', 'Leads Report'),
        ('deals', 'Deals Report'),
        ('activities', 'Activities Report'),
        ('performance', 'Performance Report'),
        ('pipeline', 'Pipeline Report'),
        ('forecast', 'Sales Forecast'),
    )
    
    account = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='crm_reports')
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Report Configuration
    filters = models.JSONField(default=dict, blank=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    
    # Report Data
    data = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crm_reports')
    
    class Meta:
        verbose_name = 'CRM Report'
        verbose_name_plural = 'CRM Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account.name} - {self.name}"