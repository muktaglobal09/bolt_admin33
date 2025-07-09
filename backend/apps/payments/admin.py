from django.contrib import admin
from django.utils.html import format_html
from .models import SubscriptionPlan, Subscription, Payment, Invoice, Refund


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'plan_type', 'price', 'billing_cycle', 'max_business_listings',
        'monthly_lead_credits', 'is_active', 'sort_order'
    )
    list_filter = ('plan_type', 'billing_cycle', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description', 'price', 'billing_cycle', 'is_active', 'sort_order')
        }),
        ('Business Limits', {
            'fields': (
                'max_business_listings', 'max_images_per_business',
                'max_services_per_business', 'max_products_per_business'
            )
        }),
        ('Lead Features', {
            'fields': ('monthly_lead_credits', 'lead_purchase_discount')
        }),
        ('Additional Features', {
            'fields': (
                'priority_listing', 'featured_listing', 'analytics_access',
                'crm_access', 'api_access', 'custom_branding', 'dedicated_support'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'business', 'plan', 'status', 'start_date', 'end_date',
        'remaining_lead_credits', 'auto_renew'
    )
    list_filter = ('status', 'plan', 'auto_renew', 'start_date', 'end_date')
    search_fields = ('user__email', 'business__name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at', 'is_active', 'remaining_lead_credits')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'business', 'plan', 'status')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'auto_renew')
        }),
        ('Usage', {
            'fields': ('used_lead_credits', 'remaining_lead_credits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def remaining_lead_credits(self, obj):
        return obj.remaining_lead_credits
    remaining_lead_credits.short_description = 'Remaining Credits'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'payment_type', 'amount', 'currency', 'payment_method',
        'status', 'paid_at', 'created_at'
    )
    list_filter = ('payment_type', 'payment_method', 'status', 'created_at', 'paid_at')
    search_fields = ('user__email', 'gateway_transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'business', 'payment_type', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Gateway Details', {
            'fields': ('gateway_transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Related Objects', {
            'fields': ('subscription',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'billing_name', 'billing_email', 'tax_amount', 'created_at')
    list_filter = ('created_at', 'billing_state')
    search_fields = ('invoice_number', 'billing_name', 'billing_email', 'payment__user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('payment', 'invoice_number', 'invoice_file')
        }),
        ('Billing Information', {
            'fields': (
                'billing_name', 'billing_email', 'billing_address',
                'billing_city', 'billing_state', 'billing_pincode', 'billing_country'
            )
        }),
        ('Tax Details', {
            'fields': ('gst_number', 'tax_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'amount', 'status', 'processed_by', 'processed_at', 'created_at')
    list_filter = ('status', 'created_at', 'processed_at')
    search_fields = ('payment__user__email', 'reason', 'gateway_refund_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Refund Details', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Processing Information', {
            'fields': ('processed_by', 'processed_at', 'gateway_refund_id', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_refunds', 'reject_refunds']
    
    def approve_refunds(self, request, queryset):
        queryset.update(status='completed', processed_by=request.user)
        self.message_user(request, f"{queryset.count()} refunds approved.")
    approve_refunds.short_description = "Approve selected refunds"
    
    def reject_refunds(self, request, queryset):
        queryset.update(status='rejected', processed_by=request.user)
        self.message_user(request, f"{queryset.count()} refunds rejected.")
    reject_refunds.short_description = "Reject selected refunds"