from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.businesses.models import Business

User = get_user_model()


class ReferralProgram(TimeStampedModel):
    """Referral program configuration."""
    
    PROGRAM_TYPES = (
        ('user_referral', 'User Referral'),
        ('business_referral', 'Business Referral'),
    )
    
    REWARD_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('credits', 'Credits'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    
    # Reward configuration
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Referrer rewards
    referrer_reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    referrer_reward_value = models.DecimalField(max_digits=10, decimal_places=2)
    referrer_max_reward = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Program settings
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    max_referrals_per_user = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Referral Program'
        verbose_name_plural = 'Referral Programs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReferralCode(TimeStampedModel):
    """Referral codes for users and businesses."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_codes')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='referral_codes', null=True, blank=True)
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='codes')
    
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    max_usage = models.PositiveIntegerField(null=True, blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Referral Code'
        verbose_name_plural = 'Referral Codes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.user.email}"
    
    @property
    def is_valid(self):
        """Check if referral code is valid."""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        
        return True


class Referral(TimeStampedModel):
    """Individual referral records."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name='referrals')
    
    # Referral details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Rewards
    referrer_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referred_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rewards_paid = models.BooleanField(default=False)
    rewards_paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        ordering = ['-created_at']
        unique_together = ['referrer', 'referred_user']
    
    def __str__(self):
        return f"{self.referrer.email} referred {self.referred_user.email}"


class Coupon(TimeStampedModel):
    """Discount coupons."""
    
    COUPON_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    )
    
    USAGE_TYPES = (
        ('single_use', 'Single Use'),
        ('multiple_use', 'Multiple Use'),
        ('unlimited', 'Unlimited'),
    )
    
    # Basic information
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Discount configuration
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usage configuration
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='single_use')
    max_usage_count = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    max_usage_per_user = models.PositiveIntegerField(default=1)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Restrictions
    applicable_to_businesses = models.ManyToManyField(Business, blank=True, related_name='applicable_coupons')
    applicable_to_users = models.ManyToManyField(User, blank=True, related_name='applicable_coupons')
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_valid(self):
        """Check if coupon is valid."""
        from django.utils import timezone
        
        if not self.is_active:
            return False
        
        now = timezone.now()
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.usage_type != 'unlimited' and self.max_usage_count:
            if self.usage_count >= self.max_usage_count:
                return False
        
        return True


class CouponUsage(TimeStampedModel):
    """Track coupon usage."""
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='coupon_usages', null=True, blank=True)
    
    # Usage details
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.user.email}"


class RewardPoint(TimeStampedModel):
    """Reward points for users."""
    
    TRANSACTION_TYPES = (
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('adjusted', 'Adjusted'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_points')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    
    # Related objects
    referral = models.ForeignKey(Referral, on_delete=models.SET_NULL, null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Reward Point'
        verbose_name_plural = 'Reward Points'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.points} points ({self.get_transaction_type_display()})"


class UserRewardBalance(TimeStampedModel):
    """Current reward point balance for users."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward_balance')
    total_points = models.PositiveIntegerField(default=0)
    available_points = models.PositiveIntegerField(default=0)
    lifetime_earned = models.PositiveIntegerField(default=0)
    lifetime_redeemed = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'User Reward Balance'
        verbose_name_plural = 'User Reward Balances'
    
    def __str__(self):
        return f"{self.user.email} - {self.available_points} points"