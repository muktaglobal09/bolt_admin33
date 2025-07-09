from django.contrib import admin
from .models import Conversation, Message, MessageReport, MessageTemplate, ChatSettings, BlockedUser


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'message_type', 'content', 'is_read', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'business', 'business_user', 'status', 'last_message_at',
        'unread_count_for_user', 'unread_count_for_business'
    )
    list_filter = ('status', 'business', 'last_message_at', 'created_at')
    search_fields = ('user__email', 'business__name', 'subject')
    readonly_fields = ('created_at', 'updated_at', 'unread_count_for_user', 'unread_count_for_business')
    inlines = [MessageInline]
    
    fieldsets = (
        ('Participants', {
            'fields': ('user', 'business', 'business_user')
        }),
        ('Conversation Details', {
            'fields': ('subject', 'status')
        }),
        ('Last Message Info', {
            'fields': ('last_message_at', 'last_message_by')
        }),
        ('Read Status', {
            'fields': ('user_last_read', 'business_user_last_read')
        }),
        ('Statistics', {
            'fields': ('unread_count_for_user', 'unread_count_for_business'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def unread_count_for_user(self, obj):
        return obj.unread_count_for_user
    unread_count_for_user.short_description = 'User Unread'
    
    def unread_count_for_business(self, obj):
        return obj.unread_count_for_business
    unread_count_for_business.short_description = 'Business Unread'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message_type', 'content_preview', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'is_deleted', 'created_at')
    search_fields = ('conversation__user__email', 'conversation__business__name', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('conversation', 'sender', 'message_type', 'content')
        }),
        ('Attachments', {
            'fields': ('attachment', 'attachment_name'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    list_display = ('message', 'reported_by', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('message__content', 'reported_by__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('message', 'reported_by', 'reason', 'description')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['resolve_reports']
    
    def resolve_reports(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_by=request.user, resolved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} reports resolved.")
    resolve_reports.short_description = "Resolve selected reports"


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('business', 'name', 'is_active', 'usage_count', 'created_at')
    list_filter = ('is_active', 'business', 'created_at')
    search_fields = ('business__name', 'name', 'content')
    readonly_fields = ('created_at', 'updated_at', 'usage_count')


@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    list_display = ('business', 'is_chat_enabled', 'auto_reply_enabled', 'created_at')
    list_filter = ('is_chat_enabled', 'auto_reply_enabled', 'created_at')
    search_fields = ('business__name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('business', 'is_chat_enabled', 'auto_reply_enabled', 'auto_reply_message')
        }),
        ('Working Hours', {
            'fields': (
                ('monday_start', 'monday_end'),
                ('tuesday_start', 'tuesday_end'),
                ('wednesday_start', 'wednesday_end'),
                ('thursday_start', 'thursday_end'),
                ('friday_start', 'friday_end'),
                ('saturday_start', 'saturday_end'),
                ('sunday_start', 'sunday_end'),
            ),
            'classes': ('collapse',)
        }),
        ('Offline Settings', {
            'fields': ('offline_message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('business', 'user', 'blocked_by', 'created_at')
    list_filter = ('business', 'created_at')
    search_fields = ('business__name', 'user__email', 'reason')
    readonly_fields = ('created_at', 'updated_at')