from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TicketCategory, SupportTicket, TicketReply, TicketAttachment,
    FAQ, KnowledgeBaseArticle, TicketEscalation
)


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    fields = ('author', 'message', 'is_internal', 'created_at')
    readonly_fields = ('created_at',)


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    fields = ('file', 'filename', 'uploaded_by')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'subject', 'requester', 'category', 'priority',
        'status', 'assigned_to', 'created_at'
    )
    list_filter = ('priority', 'status', 'category', 'assigned_to', 'created_at')
    search_fields = ('ticket_number', 'subject', 'requester__email', 'requester_email')
    readonly_fields = ('created_at', 'updated_at', 'ticket_number')
    inlines = [TicketReplyInline, TicketAttachmentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'subject', 'description', 'category', 'priority', 'status')
        }),
        ('Requester Information', {
            'fields': ('requester', 'requester_email', 'requester_phone', 'business')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolution_notes'),
            'classes': ('collapse',)
        }),
        ('Customer Satisfaction', {
            'fields': ('satisfaction_rating', 'satisfaction_feedback'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_me', 'mark_resolved', 'mark_closed']
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
        self.message_user(request, f"{queryset.count()} tickets assigned to you.")
    assign_to_me.short_description = "Assign selected tickets to me"
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} tickets marked as resolved.")
    mark_resolved.short_description = "Mark selected tickets as resolved"
    
    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} tickets marked as closed.")
    mark_closed.short_description = "Mark selected tickets as closed"


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('ticket__ticket_number', 'author__email', 'message')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'ticket', 'reply', 'file_size', 'uploaded_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('filename', 'ticket__ticket_number')
    readonly_fields = ('created_at', 'updated_at', 'filename', 'file_size')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published', 'view_count', 'sort_order')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    
    fieldsets = (
        ('FAQ Details', {
            'fields': ('question', 'answer', 'category', 'is_published', 'sort_order')
        }),
        ('Statistics', {
            'fields': ('view_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'author', 'is_published', 'view_count',
        'helpful_count', 'helpfulness_ratio', 'created_at'
    )
    list_filter = ('category', 'is_published', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_description')
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'helpful_count', 'not_helpful_count', 'helpfulness_ratio')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Article Details', {
            'fields': ('title', 'content', 'category', 'author', 'is_published')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'helpful_count', 'not_helpful_count', 'helpfulness_ratio'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def helpfulness_ratio(self, obj):
        return f"{obj.helpfulness_ratio:.1f}%"
    helpfulness_ratio.short_description = 'Helpfulness'


@admin.register(TicketEscalation)
class TicketEscalationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'escalation_type', 'escalated_from', 'escalated_to', 'created_at')
    list_filter = ('escalation_type', 'created_at')
    search_fields = ('ticket__ticket_number', 'reason')
    readonly_fields = ('created_at', 'updated_at')