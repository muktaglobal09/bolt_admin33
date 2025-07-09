from django.contrib import admin
from .models import NotificationTemplate, Notification, EmailLog, SMSLog, NotificationPreference


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'event_type', 'is_active', 'created_at')
    list_filter = ('notification_type', 'event_type', 'is_active')
    search_fields = ('name', 'subject', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'notification_type', 'event_type', 'is_active')
        }),
        ('Content', {
            'fields': ('subject', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'template__notification_type', 'template__event_type', 'created_at')
    search_fields = ('recipient__email', 'subject', 'content')
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at')
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'template', 'subject', 'content', 'status')
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'delivered_at', 'read_at', 'failed_reason')
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_phone', 'content_preview', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_phone', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_leads', 'sms_leads', 'push_leads', 'created_at')
    list_filter = ('email_leads', 'sms_leads', 'push_leads', 'email_marketing')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': ('email_reviews', 'email_leads', 'email_messages', 'email_marketing', 'email_system')
        }),
        ('SMS Preferences', {
            'fields': ('sms_leads', 'sms_urgent', 'sms_marketing')
        }),
        ('Push Notification Preferences', {
            'fields': ('push_reviews', 'push_leads', 'push_messages', 'push_marketing')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )