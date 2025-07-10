from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """Custom User model extending Django's AbstractUser."""
    
    USER_TYPES = (
        ('customer', 'Customer'),
        ('business_owner', 'Business Owner'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    email = models.EmailField(unique=True, help_text="Primary email address for login and communication")
    phone_number = PhoneNumberField(blank=True, null=True, help_text="Contact phone number with country code (e.g., +91 9876543210)")
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer', help_text="User role in the system")
    is_phone_verified = models.BooleanField(default=False, help_text="Whether the phone number has been verified via OTP")
    is_email_verified = models.BooleanField(default=False, help_text="Whether the email address has been verified")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending', help_text="Overall account verification status")
    profile_picture = models.ImageField(upload_to='users/profiles/', blank=True, null=True, help_text="User's profile photo (recommended: 400x400px)")
    date_of_birth = models.DateField(blank=True, null=True, help_text="Date of birth for age verification and personalization")
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, help_text="Gender for demographic analysis")
    
    # KYC Fields
    aadhar_number = models.CharField(max_length=12, blank=True, help_text="12-digit Aadhar number for identity verification")
    pan_number = models.CharField(max_length=10, blank=True, help_text="10-character PAN number for tax verification")
    kyc_document = models.FileField(upload_to='users/kyc/', blank=True, null=True, help_text="Upload KYC document (Aadhar, PAN, Passport, etc.)")
    kyc_verified = models.BooleanField(default=False, help_text="Whether KYC documents have been verified by admin")
    
    # Address
    address_line_1 = models.CharField(max_length=255, blank=True, help_text="Primary address line (house/flat number, street)")
    address_line_2 = models.CharField(max_length=255, blank=True, help_text="Secondary address line (area, landmark)")
    city = models.CharField(max_length=100, blank=True, help_text="City or town name")
    state = models.CharField(max_length=100, blank=True, help_text="State or province name")
    pincode = models.CharField(max_length=10, blank=True, help_text="Postal/ZIP code")
    country = models.CharField(max_length=100, default='India', help_text="Country name")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(TimeStampedModel):
    """Extended user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', help_text="Associated user account")
    bio = models.TextField(blank=True, help_text="Short biography or description about the user")
    website = models.URLField(blank=True, help_text="Personal or business website URL")
    linkedin_profile = models.URLField(blank=True, help_text="LinkedIn profile URL")
    facebook_profile = models.URLField(blank=True, help_text="Facebook profile URL")
    twitter_profile = models.URLField(blank=True, help_text="Twitter/X profile URL")
    instagram_profile = models.URLField(blank=True, help_text="Instagram profile URL")
    
    # Preferences
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications for important updates")
    sms_notifications = models.BooleanField(default=True, help_text="Receive SMS notifications for urgent updates")
    marketing_emails = models.BooleanField(default=False, help_text="Receive promotional and marketing emails")
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"


class UserActivity(TimeStampedModel):
    """Track user activities and login history."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', help_text="User who performed the activity")
    activity_type = models.CharField(max_length=50, help_text="Type of activity (login, logout, profile_update, etc.)")
    description = models.TextField(help_text="Detailed description of the activity performed")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address from which activity was performed")
    user_agent = models.TextField(blank=True, help_text="Browser/device information")
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"