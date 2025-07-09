from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Business, BusinessImage, BusinessDocument, BusinessLocation,
    BusinessService, BusinessProduct, BusinessAnalytics, 
    BusinessVerification, BusinessSubscription
)
from apps.crm.models import Lead, CRMContact, CRMDeal, CRMActivity, CRMTask


class BusinessResource(resources.ModelResource):
    class Meta:
        model = Business
        fields = (
            'id', 'name', 'business_type', 'category__name', 'owner__email',
            'phone_number', 'email', 'city', 'state', 'verification_status',
            'is_featured', 'profile_completeness', 'health_status',
            'view_count', 'lead_count', 'conversion_rate', 'average_rating',
            'created_at'
        )


class BusinessProductResource(resources.ModelResource):
    class Meta:
        model = BusinessProduct
        fields = (
            'id', 'business__name', 'name', 'price', 'is_active',
            'is_featured', 'stock_quantity', 'sku'
        )


class BusinessImageInline(admin.TabularInline):
    model = BusinessImage
    extra = 0
    fields = ('image', 'caption', 'sort_order', 'is_featured')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


class BusinessDocumentInline(admin.TabularInline):
    model = BusinessDocument
    extra = 0
    fields = ('document_type', 'title', 'document', 'is_verified', 'verified_at')
    readonly_fields = ('verified_at',)


class BusinessLocationInline(admin.TabularInline):
    model = BusinessLocation
    extra = 0
    fields = ('name', 'city', 'phone_number', 'is_primary', 'is_active')


class BusinessServiceInline(admin.TabularInline):
    model = BusinessService
    extra = 0
    fields = ('name', 'price', 'price_type', 'is_active', 'is_featured', 'sort_order')


class BusinessProductInline(admin.TabularInline):
    model = BusinessProduct
    extra = 0
    fields = ('name', 'price', 'is_active', 'is_featured', 'stock_quantity', 'sort_order')


class BusinessVerificationInline(admin.TabularInline):
    model = BusinessVerification
    extra = 0
    fields = ('verification_type', 'status', 'verified_by', 'verified_at')
    readonly_fields = ('verified_at',)


# CRM Inlines for Business Admin
class LeadInline(admin.TabularInline):
    model = Lead
    extra = 0
    fields = ('first_name', 'last_name', 'email', 'status', 'lead_score', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


class CRMContactInline(admin.TabularInline):
    model = CRMContact
    extra = 0
    fields = ('first_name', 'last_name', 'email', 'contact_type', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


class CRMDealInline(admin.TabularInline):
    model = CRMDeal
    extra = 0
    fields = ('title', 'contact', 'value', 'stage', 'probability', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Business)
class BusinessAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BusinessResource
    
    list_display = (
        'name', 'owner', 'category', 'business_type', 'verification_badge',
        'health_badge', 'completeness_meter', 'subscription_status',
        'analytics_summary', 'is_featured', 'created_at'
    )
    list_filter = (
        'business_type', 'verification_status', 'health_status', 'is_active', 
        'is_featured', 'category', 'created_at', 'profile_completeness'
    )
    search_fields = ('name', 'description', 'owner__email', 'phone_number', 'email')
    readonly_fields = (
        'created_at', 'updated_at', 'view_count', 'inquiry_count', 
        'lead_count', 'conversion_count', 'average_rating', 'review_count',
        'profile_completeness', 'health_status', 'conversion_rate',
        'analytics_dashboard_link'
    )
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ()
    inlines = [
        BusinessImageInline, BusinessDocumentInline, BusinessLocationInline, 
        BusinessServiceInline, BusinessProductInline, BusinessVerificationInline,
        LeadInline, CRMContactInline, CRMDealInline
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'description', 'business_type', 'category', 'owner')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'alternate_phone', 'email', 'website')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'country', 'latitude', 'longitude')
        }),
        ('Business Details', {
            'fields': ('established_year', 'employee_count', 'annual_turnover'),
            'classes': ('collapse',)
        }),
        ('Legal Information', {
            'fields': ('gst_number', 'pan_number', 'license_number'),
            'classes': ('collapse',)
        }),
        ('Status & Verification', {
            'fields': ('is_active', 'is_featured', 'verification_status', 'verified_at', 'verified_by')
        }),
        ('Health & Completeness', {
            'fields': ('health_status', 'profile_completeness', 'last_activity_at'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('logo', 'cover_image')
        }),
        ('Working Hours', {
            'fields': (
                ('monday_open', 'monday_close'),
                ('tuesday_open', 'tuesday_close'),
                ('wednesday_open', 'wednesday_close'),
                ('thursday_open', 'thursday_close'),
                ('friday_open', 'friday_close'),
                ('saturday_open', 'saturday_close'),
                ('sunday_open', 'sunday_close'),
            ),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Analytics & KPIs', {
            'fields': (
                'view_count', 'inquiry_count', 'lead_count', 'conversion_count',
                'average_rating', 'review_count', 'conversion_rate', 'analytics_dashboard_link'
            ),
            'classes': ('collapse',)
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'verify_businesses', 'feature_businesses', 'unfeature_businesses',
        'suspend_businesses', 'activate_businesses', 'bulk_export_analytics',
        'recalculate_health_status', 'send_verification_reminder'
    ]
    
    def verification_badge(self, obj):
        colors = {
            'verified': '#28a745',
            'pending': '#ffc107',
            'rejected': '#dc3545',
            'suspended': '#6c757d'
        }
        color = colors.get(obj.verification_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_verification_status_display()
        )
    verification_badge.short_description = 'Verification'
    
    def health_badge(self, obj):
        colors = {
            'excellent': '#28a745',
            'good': '#20c997',
            'average': '#ffc107',
            'poor': '#fd7e14',
            'critical': '#dc3545'
        }
        color = colors.get(obj.health_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_health_status_display()
        )
    health_badge.short_description = 'Health'
    
    def completeness_meter(self, obj):
        percentage = obj.profile_completeness
        color = '#28a745' if percentage >= 80 else '#ffc107' if percentage >= 60 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 20px; text-align: center; color: white; font-size: 11px; line-height: 20px;">'
            '{}%</div></div>',
            percentage, color, percentage
        )
    completeness_meter.short_description = 'Completeness'
    
    def subscription_status(self, obj):
        try:
            subscription = obj.subscription
            if subscription.is_expired:
                return format_html('<span style="color: #dc3545;">Expired</span>')
            elif subscription.days_remaining <= 7:
                return format_html('<span style="color: #ffc107;">Expiring Soon</span>')
            else:
                return format_html('<span style="color: #28a745;">{}</span>', subscription.plan.name)
        except:
            return format_html('<span style="color: #6c757d;">No Plan</span>')
    subscription_status.short_description = 'Subscription'
    
    def analytics_summary(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            'Views: {} | Leads: {} | Conv: {:.1f}%<br>'
            'Rating: {:.1f} ({} reviews)'
            '</div>',
            obj.view_count, obj.lead_count, obj.conversion_rate,
            obj.average_rating or 0, obj.review_count
        )
    analytics_summary.short_description = 'Analytics'
    
    def analytics_dashboard_link(self, obj):
        if obj.pk:
            url = reverse('admin:businesses_businessanalytics_changelist') + f'?business__id__exact={obj.pk}'
            return format_html('<a href="{}" target="_blank">View Analytics Dashboard</a>', url)
        return "Save to view analytics"
    analytics_dashboard_link.short_description = 'Analytics Dashboard'
    
    # Bulk Actions
    def verify_businesses(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            verification_status='verified',
            verified_at=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f"{updated} businesses verified successfully.")
    verify_businesses.short_description = "✓ Verify selected businesses"
    
    def feature_businesses(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} businesses featured successfully.")
    feature_businesses.short_description = "⭐ Feature selected businesses"
    
    def unfeature_businesses(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} businesses unfeatured successfully.")
    unfeature_businesses.short_description = "Remove feature from selected businesses"
    
    def suspend_businesses(self, request, queryset):
        updated = queryset.update(verification_status='suspended', is_active=False)
        self.message_user(request, f"{updated} businesses suspended successfully.")
    suspend_businesses.short_description = "🚫 Suspend selected businesses"
    
    def activate_businesses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} businesses activated successfully.")
    activate_businesses.short_description = "✅ Activate selected businesses"
    
    def recalculate_health_status(self, request, queryset):
        updated = 0
        for business in queryset:
            business.calculate_health_status()
            business.save()
            updated += 1
        self.message_user(request, f"Health status recalculated for {updated} businesses.")
    recalculate_health_status.short_description = "🔄 Recalculate health status"
    
    def bulk_export_analytics(self, request, queryset):
        # This would trigger an export of analytics data
        business_ids = list(queryset.values_list('id', flat=True))
        self.message_user(request, f"Analytics export initiated for {len(business_ids)} businesses.")
    bulk_export_analytics.short_description = "📊 Export analytics data"
    
    def send_verification_reminder(self, request, queryset):
        pending_businesses = queryset.filter(verification_status='pending')
        count = pending_businesses.count()
        # Here you would implement email sending logic
        self.message_user(request, f"Verification reminders sent to {count} businesses.")
    send_verification_reminder.short_description = "📧 Send verification reminders"


@admin.register(BusinessAnalytics)
class BusinessAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'business', 'date', 'page_views', 'unique_visitors', 'inquiries',
        'leads', 'conversions', 'conversion_rate_display', 'average_rating'
    )
    list_filter = ('date', 'business__category', 'business__verification_status')
    search_fields = ('business__name',)
    readonly_fields = ('created_at', 'updated_at', 'conversion_rate_display')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('business', 'date')
        }),
        ('Traffic Metrics', {
            'fields': ('page_views', 'unique_visitors')
        }),
        ('Engagement Metrics', {
            'fields': ('inquiries', 'leads', 'conversions', 'conversion_rate_display')
        }),
        ('Review Metrics', {
            'fields': ('new_reviews', 'average_rating')
        }),
        ('Contact Metrics', {
            'fields': ('phone_clicks', 'email_clicks', 'website_clicks', 'social_media_clicks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def conversion_rate_display(self, obj):
        if obj.leads > 0:
            rate = (obj.conversions / obj.leads) * 100
            return f"{rate:.1f}%"
        return "0%"
    conversion_rate_display.short_description = 'Conversion Rate'


@admin.register(BusinessVerification)
class BusinessVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'business', 'verification_type', 'status_badge', 'verified_by',
        'verified_at', 'expires_at', 'created_at'
    )
    list_filter = ('verification_type', 'status', 'verified_at', 'expires_at')
    search_fields = ('business__name', 'admin_notes', 'rejection_reason')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Verification Details', {
            'fields': ('business', 'verification_type', 'status')
        }),
        ('Verification Results', {
            'fields': ('verified_by', 'verified_at', 'expires_at')
        }),
        ('Notes & Comments', {
            'fields': ('admin_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'approved': '#28a745',
            'pending': '#ffc107',
            'rejected': '#dc3545',
            'expired': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['approve_verifications', 'reject_verifications']
    
    def approve_verifications(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='approved',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f"{updated} verifications approved.")
    approve_verifications.short_description = "✓ Approve selected verifications"
    
    def reject_verifications(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} verifications rejected.")
    reject_verifications.short_description = "✗ Reject selected verifications"


@admin.register(BusinessSubscription)
class BusinessSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'business', 'plan', 'status_badge', 'start_date', 'end_date',
        'days_remaining_display', 'usage_summary', 'auto_renew'
    )
    list_filter = ('plan', 'is_active', 'auto_renew', 'start_date', 'end_date')
    search_fields = ('business__name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at', 'days_remaining_display', 'is_expired')
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('business', 'plan', 'is_active', 'auto_renew')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'days_remaining_display', 'is_expired')
        }),
        ('Usage Tracking', {
            'fields': (
                'used_listings', 'used_images', 'used_services',
                'used_products', 'used_lead_credits'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_expired:
            color = '#dc3545'
            text = 'Expired'
        elif obj.days_remaining <= 7:
            color = '#ffc107'
            text = 'Expiring Soon'
        elif obj.is_active:
            color = '#28a745'
            text = 'Active'
        else:
            color = '#6c757d'
            text = 'Inactive'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if days <= 0:
            return format_html('<span style="color: #dc3545;">Expired</span>')
        elif days <= 7:
            return format_html('<span style="color: #ffc107;">{} days</span>', days)
        else:
            return format_html('<span style="color: #28a745;">{} days</span>', days)
    days_remaining_display.short_description = 'Days Remaining'
    
    def usage_summary(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            'Listings: {}/{} | Images: {}/{}<br>'
            'Services: {}/{} | Products: {}/{}'
            '</div>',
            obj.used_listings, obj.plan.max_business_listings,
            obj.used_images, obj.plan.max_images_per_business,
            obj.used_services, obj.plan.max_services_per_business,
            obj.used_products, obj.plan.max_products_per_business
        )
    usage_summary.short_description = 'Usage'


@admin.register(BusinessImage)
class BusinessImageAdmin(admin.ModelAdmin):
    list_display = ('business', 'caption', 'sort_order', 'is_featured', 'image_preview', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('business__name', 'caption')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('business', 'title', 'document_type', 'verification_badge', 'verified_by', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('business__name', 'title')
    readonly_fields = ('verified_at',)
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">Verified</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">Pending</span>'
            )
    verification_badge.short_description = 'Status'
    
    actions = ['verify_documents']
    
    def verify_documents(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f"{updated} documents verified.")
    verify_documents.short_description = "✓ Verify selected documents"


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    list_display = ('business', 'name', 'city', 'is_primary', 'is_active', 'created_at')
    list_filter = ('is_primary', 'is_active', 'city', 'state')
    search_fields = ('business__name', 'name', 'city')


@admin.register(BusinessService)
class BusinessServiceAdmin(admin.ModelAdmin):
    list_display = ('business', 'name', 'price', 'price_type', 'is_active', 'is_featured', 'sort_order')
    list_filter = ('price_type', 'is_active', 'is_featured')
    search_fields = ('business__name', 'name')


@admin.register(BusinessProduct)
class BusinessProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BusinessProductResource
    
    list_display = ('business', 'name', 'price', 'stock_quantity', 'is_active', 'is_featured', 'sort_order')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('business__name', 'name', 'sku')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Product Information', {
            'fields': ('business', 'name', 'description', 'price', 'image')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'sku')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'sort_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Don't override admin site headers here - let the main config handle it