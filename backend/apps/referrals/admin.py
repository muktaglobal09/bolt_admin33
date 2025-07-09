from django.contrib import admin
from .models import (
    ReferralProgram, ReferralCode, Referral, Coupon, CouponUsage,
    RewardPoint, UserRewardBalance
)


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'program_type', 'reward_type', 'reward_value',
        'is_active', 'start_date', 'end_date'
    )
    list_filter = ('program_type', 'reward_type', 'is_active', 'start_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Program Information', {
            'fields': ('name', 'description', 'program_type', 'is_active')
        }),
        ('Reward Configuration', {
            'fields': ('reward_type', 'reward_value', 'max_reward_amount')
        }),
        ('Referrer Rewards', {
            'fields': ('referrer_reward_type', 'referrer_reward_value', 'referrer_max_reward')
        }),
        ('Program Settings', {
            'fields': ('start_date', 'end_date', 'max_referrals_per_user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'user', 'business', 'program', 'is_active',
        'usage_count', 'max_usage', 'expires_at'
    )
    list_filter = ('is_active', 'program', 'expires_at', 'created_at')
    search_fields = ('code', 'user__email', 'business__name')
    readonly_fields = ('created_at', 'updated_at', 'usage_count', 'is_valid')
    
    fieldsets = (
        ('Code Information', {
            'fields': ('user', 'business', 'program', 'code', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('usage_count', 'max_usage', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_valid',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        'referrer', 'referred_user', 'referral_code', 'status',
        'referrer_reward_amount', 'referred_reward_amount', 'rewards_paid', 'completed_at'
    )
    list_filter = ('status', 'rewards_paid', 'completed_at', 'created_at')
    search_fields = ('referrer__email', 'referred_user__email', 'referral_code__code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Referral Information', {
            'fields': ('referrer', 'referred_user', 'referral_code', 'status', 'completed_at')
        }),
        ('Rewards', {
            'fields': ('referrer_reward_amount', 'referred_reward_amount', 'rewards_paid', 'rewards_paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'pay_rewards']
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} referrals marked as completed.")
    mark_completed.short_description = "Mark selected referrals as completed"
    
    def pay_rewards(self, request, queryset):
        from django.utils import timezone
        queryset.update(rewards_paid=True, rewards_paid_at=timezone.now())
        self.message_user(request, f"Rewards paid for {queryset.count()} referrals.")
    pay_rewards.short_description = "Pay rewards for selected referrals"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'coupon_type', 'discount_value', 'usage_count',
        'max_usage_count', 'is_active', 'valid_from', 'valid_until'
    )
    list_filter = ('coupon_type', 'usage_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'usage_count', 'is_valid')
    filter_horizontal = ('applicable_to_businesses', 'applicable_to_users')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'is_active')
        }),
        ('Discount Configuration', {
            'fields': ('coupon_type', 'discount_value', 'max_discount_amount', 'min_order_amount')
        }),
        ('Usage Configuration', {
            'fields': ('usage_type', 'max_usage_count', 'usage_count', 'max_usage_per_user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Restrictions', {
            'fields': ('applicable_to_businesses', 'applicable_to_users'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_valid',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'business', 'order_amount', 'discount_amount', 'created_at')
    list_filter = ('coupon', 'business', 'created_at')
    search_fields = ('coupon__code', 'user__email', 'business__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RewardPoint)
class RewardPointAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'points', 'description', 'expires_at', 'created_at')
    list_filter = ('transaction_type', 'expires_at', 'created_at')
    search_fields = ('user__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('user', 'transaction_type', 'points', 'description')
        }),
        ('Related Objects', {
            'fields': ('referral', 'business'),
            'classes': ('collapse',)
        }),
        ('Expiry', {
            'fields': ('expires_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRewardBalance)
class UserRewardBalanceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'available_points', 'total_points', 'lifetime_earned',
        'lifetime_redeemed', 'updated_at'
    )
    list_filter = ('updated_at',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Current Balance', {
            'fields': ('available_points', 'total_points')
        }),
        ('Lifetime Statistics', {
            'fields': ('lifetime_earned', 'lifetime_redeemed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )