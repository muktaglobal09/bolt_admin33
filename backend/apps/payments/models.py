from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class SubscriptionPlan(TimeStampedModel):
    """Subscription plans for businesses."""
    
    PLAN_TYPES = (
        ('free', 'Free'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('enterprise', 'Enterprise'),
    )
    
    BILLING_CYCLES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Features
    max_business_listings = models.PositiveIntegerField(default=1, help_text="Maximum number of business listings allowed")
    max_images_per_business = models.PositiveIntegerField(default=5, help_text="Maximum images per business listing")
    max_services_per_business = models.PositiveIntegerField(default=10, help_text="Maximum services per business")
    max_products_per_business = models.PositiveIntegerField(default=10, help_text="Maximum products per business")
    
    # Lead features
    monthly_lead_credits = models.PositiveIntegerField(default=0, help_text="Number of lead credits included per month")
    lead_purchase_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage on additional lead purchases")
    
    # Additional features
    priority_listing = models.BooleanField(default=False, help_text="Higher ranking in search results")
    featured_listing = models.BooleanField(default=False, help_text="Featured placement in category listings")
    analytics_access = models.BooleanField(default=False, help_text="Access to detailed analytics dashboard")
    crm_access = models.BooleanField(default=False, help_text="Access to CRM features")
    api_access = models.BooleanField(default=False, help_text="API access for integrations")
    custom_branding = models.BooleanField(default=False, help_text="Custom branding options")
    dedicated_support = models.BooleanField(default=False, help_text="Dedicated customer support")
    
    is_active = models.BooleanField(default=True, help_text="Whether this plan is available for purchase")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying plans (lower numbers first)")
    
    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}/{self.billing_cycle}"


class Subscription(TimeStampedModel):
    """User subscriptions."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Usage tracking
    used_lead_credits = models.PositiveIntegerField(default=0)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    @property
    def remaining_lead_credits(self):
        return max(0, self.plan.monthly_lead_credits - self.used_lead_credits)


class Payment(TimeStampedModel):
    """Payment records."""
    
    PAYMENT_METHODS = (
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Digital Wallet'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_TYPES = (
        ('subscription', 'Subscription'),
        ('lead_purchase', 'Lead Purchase'),
        ('featured_listing', 'Featured Listing'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Payment details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway details
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Related objects
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} ({self.status})"


class Invoice(TimeStampedModel):
    """Invoices for payments."""
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Billing details
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_pincode = models.CharField(max_length=10)
    billing_country = models.CharField(max_length=100, default='India')
    
    # Tax details
    gst_number = models.CharField(max_length=15, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Invoice file
    invoice_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            from django.utils import timezone
            now = timezone.now()
            self.invoice_number = f"INV-{now.year}-{now.month:02d}-{self.id or 1:06d}"
        super().save(*args, **kwargs)


class Refund(TimeStampedModel):
    """Refund records."""
    
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    # Processing details
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    processed_at = models.DateTimeField(null=True, blank=True)
    gateway_refund_id = models.CharField(max_length=100, blank=True)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund ₹{self.amount} for {self.payment}"