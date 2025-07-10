from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
from decimal import Decimal
from apps.core.models import TimeStampedModel, AddressModel, SEOModel
from apps.categories.models import Category

User = get_user_model()


class Business(TimeStampedModel, AddressModel, SEOModel):
    """Main business model with enhanced features."""
    
    BUSINESS_TYPES = (
        ('service', 'Service Provider'),
        ('product', 'Product Seller'),
        ('manufacturing', 'Manufacturing'),
        ('freelancer', 'Freelancer/Professional'),
        ('retail', 'Retail Store'),
        ('restaurant', 'Restaurant/Food'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('real_estate', 'Real Estate'),
        ('automotive', 'Automotive'),
        ('other', 'Other'),
    )
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    HEALTH_STATUS = (
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    )
    
    # Basic Information
    name = models.CharField(max_length=200, help_text="Business name as it should appear publicly")
    description = models.TextField(help_text="Detailed description of the business, services, and offerings")
    short_description = models.CharField(max_length=255, blank=True, help_text="Brief one-line description for listings and previews")
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES, help_text="Primary type of business operation")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='businesses', help_text="Primary business category")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses', help_text="User who owns and manages this business")
    
    # Contact Information
    phone_number = PhoneNumberField(help_text="Primary contact phone number with country code")
    alternate_phone = PhoneNumberField(blank=True, null=True, help_text="Secondary contact number (optional)")
    email = models.EmailField(help_text="Business email address for inquiries")
    website = models.URLField(blank=True, help_text="Business website URL (include http:// or https://)")
    
    # Business Details
    established_year = models.PositiveIntegerField(null=True, blank=True, help_text="Year the business was established (e.g., 2020)")
    employee_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of employees in the business")
    annual_turnover = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Annual turnover in INR (optional, for business credibility)")
    
    # Legal Information
    gst_number = models.CharField(max_length=15, blank=True, help_text="15-character GST number (for Indian businesses)")
    pan_number = models.CharField(max_length=10, blank=True, help_text="10-character PAN number")
    license_number = models.CharField(max_length=50, blank=True, help_text="Business license or registration number")
    
    # Status and Verification
    is_active = models.BooleanField(default=True, help_text="Whether the business listing is active and visible")
    is_featured = models.BooleanField(default=False, help_text="Featured businesses appear prominently in search results")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending', help_text="Business verification status by admin")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="Date and time when business was verified")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_businesses', help_text="Admin user who verified this business")
    
    # Health and Completeness
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS, default='average', help_text="Overall business profile health score")
    profile_completeness = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Profile completion percentage (0-100%)")
    last_activity_at = models.DateTimeField(null=True, blank=True, help_text="Last time the business profile was updated")
    
    # Media
    logo = models.ImageField(upload_to='businesses/logos/', blank=True, null=True, help_text="Business logo (recommended: 200x200px, square format)")
    cover_image = models.ImageField(upload_to='businesses/covers/', blank=True, null=True, help_text="Cover image for business profile (recommended: 1200x400px)")
    
    # Working Hours
    monday_open = models.TimeField(null=True, blank=True, help_text="Monday opening time (24-hour format)")
    monday_close = models.TimeField(null=True, blank=True, help_text="Monday closing time (24-hour format)")
    tuesday_open = models.TimeField(null=True, blank=True, help_text="Tuesday opening time")
    tuesday_close = models.TimeField(null=True, blank=True, help_text="Tuesday closing time")
    wednesday_open = models.TimeField(null=True, blank=True, help_text="Wednesday opening time")
    wednesday_close = models.TimeField(null=True, blank=True, help_text="Wednesday closing time")
    thursday_open = models.TimeField(null=True, blank=True, help_text="Thursday opening time")
    thursday_close = models.TimeField(null=True, blank=True, help_text="Thursday closing time")
    friday_open = models.TimeField(null=True, blank=True, help_text="Friday opening time")
    friday_close = models.TimeField(null=True, blank=True, help_text="Friday closing time")
    saturday_open = models.TimeField(null=True, blank=True, help_text="Saturday opening time")
    saturday_close = models.TimeField(null=True, blank=True, help_text="Saturday closing time")
    sunday_open = models.TimeField(null=True, blank=True, help_text="Sunday opening time")
    sunday_close = models.TimeField(null=True, blank=True, help_text="Sunday closing time")
    
    # Social Media
    facebook_url = models.URLField(blank=True, help_text="Facebook page URL")
    instagram_url = models.URLField(blank=True, help_text="Instagram profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn company page URL")
    youtube_url = models.URLField(blank=True, help_text="YouTube channel URL")
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, help_text="Total number of profile views")
    inquiry_count = models.PositiveIntegerField(default=0, help_text="Total number of inquiries received")
    lead_count = models.PositiveIntegerField(default=0, help_text="Total number of leads generated")
    conversion_count = models.PositiveIntegerField(default=0, help_text="Total number of successful conversions")
    
    # Tags
    tags = TaggableManager(blank=True, help_text="Tags for better discoverability (comma-separated)")
    
    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['verification_status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['health_status']),
            models.Index(fields=['category']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def review_count(self):
        """Count of approved reviews."""
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def conversion_rate(self):
        """Calculate conversion rate."""
        if self.lead_count > 0:
            return (self.conversion_count / self.lead_count) * 100
        return 0
    
    def calculate_profile_completeness(self):
        """Calculate profile completeness percentage."""
        total_fields = 20
        completed_fields = 0
        
        # Required fields (weight: 1 each)
        required_fields = [
            self.name, self.description, self.phone_number, self.email,
            self.category, self.business_type, self.address_line_1,
            self.city, self.state, self.pincode
        ]
        completed_fields += sum(1 for field in required_fields if field)
        
        # Optional but important fields (weight: 0.5 each)
        optional_fields = [
            self.logo, self.cover_image, self.website, self.established_year,
            self.employee_count, self.gst_number, self.short_description,
            self.latitude, self.longitude, self.facebook_url
        ]
        completed_fields += sum(0.5 for field in optional_fields if field)
        
        # Calculate percentage
        percentage = min(100, int((completed_fields / total_fields) * 100))
        self.profile_completeness = percentage
        return percentage
    
    def calculate_health_status(self):
        """Calculate business health status."""
        score = 0
        
        # Profile completeness (40% weight)
        completeness_score = (self.profile_completeness / 100) * 40
        score += completeness_score
        
        # Verification status (30% weight)
        if self.verification_status == 'verified':
            score += 30
        elif self.verification_status == 'pending':
            score += 15
        
        # Activity and engagement (30% weight)
        if self.review_count > 10:
            score += 15
        elif self.review_count > 5:
            score += 10
        elif self.review_count > 0:
            score += 5
        
        if self.average_rating >= 4.5:
            score += 15
        elif self.average_rating >= 4.0:
            score += 10
        elif self.average_rating >= 3.5:
            score += 5
        
        # Determine health status
        if score >= 85:
            self.health_status = 'excellent'
        elif score >= 70:
            self.health_status = 'good'
        elif score >= 50:
            self.health_status = 'average'
        elif score >= 30:
            self.health_status = 'poor'
        else:
            self.health_status = 'critical'
        
        return self.health_status
    
    def save(self, *args, **kwargs):
        # Calculate metrics before saving
        self.calculate_profile_completeness()
        self.calculate_health_status()
        super().save(*args, **kwargs)


class BusinessAnalytics(TimeStampedModel):
    """Daily analytics for businesses."""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='analytics', help_text="Business this analytics data belongs to")
    date = models.DateField(help_text="Date for this analytics record")
    
    # Traffic metrics
    page_views = models.PositiveIntegerField(default=0, help_text="Total page views for this date")
    unique_visitors = models.PositiveIntegerField(default=0, help_text="Number of unique visitors")
    
    # Engagement metrics
    inquiries = models.PositiveIntegerField(default=0, help_text="Number of inquiries received")
    leads = models.PositiveIntegerField(default=0, help_text="Number of leads generated")
    conversions = models.PositiveIntegerField(default=0, help_text="Number of successful conversions")
    
    # Review metrics
    new_reviews = models.PositiveIntegerField(default=0, help_text="Number of new reviews received")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average rating for this date")
    
    # Contact metrics
    phone_clicks = models.PositiveIntegerField(default=0, help_text="Number of phone number clicks")
    email_clicks = models.PositiveIntegerField(default=0, help_text="Number of email clicks")
    website_clicks = models.PositiveIntegerField(default=0, help_text="Number of website link clicks")
    
    # Social media metrics
    social_media_clicks = models.PositiveIntegerField(default=0, help_text="Total social media link clicks")
    
    class Meta:
        verbose_name = 'Business Analytics'
        verbose_name_plural = 'Business Analytics'
        unique_together = ['business', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['business', 'date']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.date}"


class BusinessVerification(TimeStampedModel):
    """Business verification tracking."""
    
    VERIFICATION_TYPES = (
        ('document', 'Document Verification'),
        ('phone', 'Phone Verification'),
        ('email', 'Email Verification'),
        ('address', 'Address Verification'),
        ('manual', 'Manual Verification'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Verification details
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_verifications')
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Notes and comments
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Business Verification'
        verbose_name_plural = 'Business Verifications'
        unique_together = ['business', 'verification_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.get_verification_type_display()}"


class BusinessImage(TimeStampedModel):
    """Additional images for businesses."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='businesses/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Business Image'
        verbose_name_plural = 'Business Images'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return f"{self.business.name} - Image {self.id}"


class BusinessDocument(TimeStampedModel):
    """Business documents and certificates."""
    
    DOCUMENT_TYPES = (
        ('license', 'Business License'),
        ('certificate', 'Certificate'),
        ('registration', 'Registration Document'),
        ('tax', 'Tax Document'),
        ('insurance', 'Insurance Document'),
        ('identity', 'Identity Proof'),
        ('address', 'Address Proof'),
        ('other', 'Other'),
    )
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='businesses/documents/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Business Document'
        verbose_name_plural = 'Business Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.title}"


class BusinessLocation(TimeStampedModel, AddressModel):
    """Multiple locations for a business."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=200, help_text="Branch/Location name")
    phone_number = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Business Location'
        verbose_name_plural = 'Business Locations'
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class BusinessService(TimeStampedModel):
    """Services offered by a business."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed Price'),
        ('hourly', 'Per Hour'),
        ('daily', 'Per Day'),
        ('project', 'Per Project'),
        ('negotiable', 'Negotiable'),
    ], default='fixed')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Business Service'
        verbose_name_plural = 'Business Services'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class BusinessProduct(TimeStampedModel):
    """Products offered by a business."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='businesses/products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(null=True, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Business Product'
        verbose_name_plural = 'Business Products'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class BusinessSubscription(TimeStampedModel):
    """Link businesses to subscription plans."""
    
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey('payments.SubscriptionPlan', on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    
    # Usage tracking
    used_listings = models.PositiveIntegerField(default=0)
    used_images = models.PositiveIntegerField(default=0)
    used_services = models.PositiveIntegerField(default=0)
    used_products = models.PositiveIntegerField(default=0)
    used_lead_credits = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Business Subscription'
        verbose_name_plural = 'Business Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.plan.name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.end_date
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now()).days