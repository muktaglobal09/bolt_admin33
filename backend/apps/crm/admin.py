from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from .models import (
    Lead, CRMContact, CRMDeal, CRMActivity, CRMTask, CRMNote,
    DealProduct, CRMPipeline, CRMPipelineStage, CRMReport
)
from .resources import (
    LeadResource, CRMContactResource, CRMDealResource, CRMActivityResource,
    CRMTaskResource, CRMNoteResource, DealProductResource
)




# Inline classes for related objects
class CRMActivityInline(admin.TabularInline):
    model = CRMActivity
    extra = 0
    fields = ('activity_type', 'subject', 'status', 'scheduled_at', 'assigned_to')
    readonly_fields = ('created_at',)


class CRMTaskInline(admin.TabularInline):
    model = CRMTask
    extra = 0
    fields = ('title', 'task_type', 'priority', 'status', 'due_date', 'assigned_to')
    readonly_fields = ('created_at',)


class CRMNoteInline(admin.TabularInline):
    model = CRMNote
    extra = 0
    fields = ('title', 'note_type', 'is_private', 'created_by')
    readonly_fields = ('created_at',)


class DealProductInline(admin.TabularInline):
    model = DealProduct
    extra = 0
    fields = ('product', 'quantity', 'unit_price', 'discount_percentage', 'total_amount')
    readonly_fields = ('total_amount',)


@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = LeadResource
    
    list_display = (
        'full_name', 'company', 'email', 'phone_number', 'status_badge',
        'priority_badge', 'lead_score_display', 'lead_source', 'owner',
        'last_contacted', 'created_at'
    )
    list_filter = (
        'status', 'priority', 'lead_source', 'owner', 'assigned_to',
        'created_at', 'last_contacted', 'business'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'company')
    readonly_fields = ('created_at', 'updated_at', 'lead_score', 'converted_at')
    autocomplete_fields = ['business', 'owner', 'assigned_to', 'converted_to_contact', 'converted_to_deal']
    inlines = [CRMActivityInline, CRMTaskInline, CRMNoteInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('business', 'first_name', 'last_name', 'email', 'phone_number', 'company', 'designation')
        }),
        ('Lead Details', {
            'fields': ('status', 'lead_source', 'priority', 'lead_score', 'qualification_notes')
        }),
        ('Assignment', {
            'fields': ('owner', 'assigned_to')
        }),
        ('Marketing & Campaign', {
            'fields': ('campaign_name', 'utm_source', 'utm_medium', 'utm_campaign'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('website', 'address', 'city', 'state', 'country'),
            'classes': ('collapse',)
        }),
        ('Interaction Tracking', {
            'fields': ('last_contacted', 'next_follow_up')
        }),
        ('Conversion', {
            'fields': ('converted_at', 'converted_to_contact', 'converted_to_deal'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'convert_to_contacts', 'assign_to_me', 'mark_as_qualified',
        'mark_as_contacted', 'bulk_update_source', 'calculate_lead_scores'
    ]
    
    def status_badge(self, obj):
        colors = {
            'new': '#17a2b8',
            'contacted': '#ffc107',
            'qualified': '#28a745',
            'unqualified': '#dc3545',
            'converted': '#6f42c1',
            'lost': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def lead_score_display(self, obj):
        score = obj.lead_score
        if score >= 75:
            color = '#28a745'
        elif score >= 50:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/100</span>',
            color, score
        )
    lead_score_display.short_description = 'Score'
    
    # Bulk Actions
    def convert_to_contacts(self, request, queryset):
        converted_count = 0
        for lead in queryset.filter(status__in=['qualified']):
            # Create contact from lead
            contact = CRMContact.objects.create(
                account=lead.business,
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                phone_number=lead.phone_number,
                company=lead.company,
                designation=lead.designation,
                contact_type='customer',
                lead_source=lead.lead_source,
                owner=lead.owner,
                address_line_1=lead.address,
                city=lead.city,
                state=lead.state,
                country=lead.country,
                notes=lead.notes
            )
            
            # Update lead
            lead.status = 'converted'
            lead.converted_at = timezone.now()
            lead.converted_to_contact = contact
            lead.save()
            
            converted_count += 1
        
        self.message_user(request, f"{converted_count} leads converted to contacts.")
    convert_to_contacts.short_description = "🔄 Convert qualified leads to contacts"
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f"{updated} leads assigned to you.")
    assign_to_me.short_description = "👤 Assign to me"
    
    def mark_as_qualified(self, request, queryset):
        updated = queryset.update(status='qualified')
        self.message_user(request, f"{updated} leads marked as qualified.")
    mark_as_qualified.short_description = "✅ Mark as qualified"
    
    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted', last_contacted=timezone.now())
        self.message_user(request, f"{updated} leads marked as contacted.")
    mark_as_contacted.short_description = "📞 Mark as contacted"
    
    def calculate_lead_scores(self, request, queryset):
        updated_count = 0
        for lead in queryset:
            lead.calculate_lead_score()
            lead.save()
            updated_count += 1
        self.message_user(request, f"Lead scores recalculated for {updated_count} leads.")
    calculate_lead_scores.short_description = "🔢 Recalculate lead scores"


@admin.register(CRMContact)
class CRMContactAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CRMContactResource
    
    list_display = (
        'full_name', 'company', 'email', 'phone_number', 'contact_type_badge',
        'account', 'owner', 'last_contacted', 'is_active', 'created_at'
    )
    list_filter = (
        'contact_type', 'lead_source', 'is_active', 'owner', 'account',
        'created_at', 'last_contacted', 'city', 'state'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'company')
    readonly_fields = ('created_at', 'updated_at', 'last_contacted')
    autocomplete_fields = ['account', 'owner']
    inlines = [CRMActivityInline, CRMTaskInline, CRMNoteInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('account', 'first_name', 'last_name', 'email', 'phone_number', 'company', 'designation')
        }),
        ('Contact Details', {
            'fields': ('contact_type', 'lead_source', 'owner', 'is_active')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'country'),
            'classes': ('collapse',)
        }),
        ('Interaction Tracking', {
            'fields': ('last_contacted',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['assign_to_me', 'mark_as_customer', 'mark_as_prospect', 'export_contacts']
    
    def contact_type_badge(self, obj):
        colors = {
            'lead': '#17a2b8',
            'customer': '#28a745',
            'prospect': '#ffc107',
            'partner': '#6f42c1',
            'vendor': '#fd7e14'
        }
        color = colors.get(obj.contact_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_contact_type_display()
        )
    contact_type_badge.short_description = 'Type'
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(owner=request.user)
        self.message_user(request, f"{updated} contacts assigned to you.")
    assign_to_me.short_description = "👤 Assign to me"
    
    def mark_as_customer(self, request, queryset):
        updated = queryset.update(contact_type='customer')
        self.message_user(request, f"{updated} contacts marked as customers.")
    mark_as_customer.short_description = "🎯 Mark as customer"
    
    def mark_as_prospect(self, request, queryset):
        updated = queryset.update(contact_type='prospect')
        self.message_user(request, f"{updated} contacts marked as prospects.")
    mark_as_prospect.short_description = "🔍 Mark as prospect"


@admin.register(CRMDeal)
class CRMDealAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CRMDealResource
    
    list_display = (
        'title', 'contact', 'account', 'value_display', 'stage_badge',
        'priority_badge', 'probability', 'owner', 'expected_close_date', 'created_at'
    )
    list_filter = (
        'stage', 'priority', 'owner', 'assigned_to', 'account',
        'expected_close_date', 'actual_close_date', 'created_at'
    )
    search_fields = ('title', 'description', 'contact__first_name', 'contact__last_name', 'contact__company')
    readonly_fields = ('created_at', 'updated_at', 'last_contacted')
    autocomplete_fields = ['account', 'contact', 'owner', 'assigned_to']
    inlines = [DealProductInline, CRMActivityInline, CRMTaskInline, CRMNoteInline]
    date_hierarchy = 'expected_close_date'
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('account', 'contact', 'title', 'description', 'value', 'currency')
        }),
        ('Status & Pipeline', {
            'fields': ('stage', 'priority', 'probability')
        }),
        ('Assignment', {
            'fields': ('owner', 'assigned_to')
        }),
        ('Dates', {
            'fields': ('expected_close_date', 'actual_close_date')
        }),
        ('Interaction Tracking', {
            'fields': ('last_contacted',)
        }),
        ('Competition & Source', {
            'fields': ('competitors', 'lead_source'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'assign_to_me', 'move_to_proposal', 'move_to_negotiation',
        'mark_as_won', 'mark_as_lost', 'update_probability'
    ]
    
    def value_display(self, obj):
        if obj.value:
            return f"{obj.currency} {obj.value:,.2f}"
        return "-"
    value_display.short_description = 'Value'
    
    def stage_badge(self, obj):
        colors = {
            'prospecting': '#17a2b8',
            'qualification': '#ffc107',
            'needs_analysis': '#fd7e14',
            'proposal': '#6f42c1',
            'negotiation': '#e83e8c',
            'closed_won': '#28a745',
            'closed_lost': '#dc3545'
        }
        color = colors.get(obj.stage, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_stage_display()
        )
    stage_badge.short_description = 'Stage'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    # Bulk Actions
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f"{updated} deals assigned to you.")
    assign_to_me.short_description = "👤 Assign to me"
    
    def move_to_proposal(self, request, queryset):
        updated = queryset.update(stage='proposal', probability=60)
        self.message_user(request, f"{updated} deals moved to proposal stage.")
    move_to_proposal.short_description = "📋 Move to proposal"
    
    def move_to_negotiation(self, request, queryset):
        updated = queryset.update(stage='negotiation', probability=80)
        self.message_user(request, f"{updated} deals moved to negotiation stage.")
    move_to_negotiation.short_description = "🤝 Move to negotiation"
    
    def mark_as_won(self, request, queryset):
        updated = queryset.update(stage='closed_won', probability=100, actual_close_date=timezone.now().date())
        self.message_user(request, f"{updated} deals marked as won.")
    mark_as_won.short_description = "🎉 Mark as won"
    
    def mark_as_lost(self, request, queryset):
        updated = queryset.update(stage='closed_lost', probability=0, actual_close_date=timezone.now().date())
        self.message_user(request, f"{updated} deals marked as lost.")
    mark_as_lost.short_description = "❌ Mark as lost"


@admin.register(CRMActivity)
class CRMActivityAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CRMActivityResource
    
    list_display = (
        'subject', 'activity_type_badge', 'account', 'contact', 'deal',
        'status_badge', 'scheduled_at', 'assigned_to', 'created_at'
    )
    list_filter = (
        'activity_type', 'status', 'account', 'assigned_to',
        'scheduled_at', 'completed_at', 'created_at'
    )
    search_fields = ('subject', 'description', 'contact__first_name', 'contact__last_name', 'deal__title')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['account', 'contact', 'deal', 'lead', 'assigned_to']
    date_hierarchy = 'scheduled_at'
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('account', 'contact', 'deal', 'lead', 'activity_type', 'subject', 'description', 'status')
        }),
        ('Scheduling', {
            'fields': ('activity_date', 'scheduled_at', 'completed_at', 'duration_minutes', 'assigned_to')
        }),
        ('Outcome & Follow-up', {
            'fields': ('outcome', 'follow_up_required', 'next_follow_up_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'assign_to_me', 'schedule_follow_up']
    
    def activity_type_badge(self, obj):
        colors = {
            'call': '#28a745',
            'email': '#17a2b8',
            'meeting': '#ffc107',
            'demo': '#6f42c1',
            'proposal': '#fd7e14',
            'follow_up': '#e83e8c',
            'other': '#6c757d'
        }
        color = colors.get(obj.activity_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_activity_type_display()
        )
    activity_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {
            'planned': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#6c757d',
            'overdue': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{updated} activities marked as completed.")
    mark_completed.short_description = "✅ Mark as completed"
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f"{updated} activities assigned to you.")
    assign_to_me.short_description = "👤 Assign to me"


@admin.register(CRMTask)
class CRMTaskAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CRMTaskResource
    
    list_display = (
        'title', 'task_type_badge', 'priority_badge', 'status_badge',
        'account', 'assigned_to', 'due_date', 'is_overdue_display', 'created_at'
    )
    list_filter = (
        'task_type', 'priority', 'status', 'account', 'assigned_to',
        'due_date', 'completed_at', 'created_at'
    )
    search_fields = ('title', 'description', 'contact__first_name', 'contact__last_name', 'deal__title')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue_display')
    autocomplete_fields = ['account', 'contact', 'deal', 'lead', 'assigned_to', 'created_by', 'depends_on']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Details', {
            'fields': ('account', 'contact', 'deal', 'lead', 'title', 'description', 'task_type', 'priority', 'status')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'completed_at', 'estimated_hours', 'actual_hours')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Reminders & Dependencies', {
            'fields': ('reminder_sent', 'reminder_date', 'depends_on'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'assign_to_me', 'send_reminders', 'mark_high_priority']
    
    def task_type_badge(self, obj):
        colors = {
            'follow_up': '#28a745',
            'call': '#17a2b8',
            'email': '#ffc107',
            'meeting': '#6f42c1',
            'proposal': '#fd7e14',
            'research': '#e83e8c',
            'admin': '#6c757d',
            'other': '#6c757d'
        }
        color = colors.get(obj.task_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_task_type_display()
        )
    task_type_badge.short_description = 'Type'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'in_progress': '#17a2b8',
            'completed': '#28a745',
            'cancelled': '#6c757d',
            'on_hold': '#fd7e14'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⚠️ Overdue</span>')
        return "✅ On Time"
    is_overdue_display.short_description = 'Status'
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{updated} tasks marked as completed.")
    mark_completed.short_description = "✅ Mark as completed"
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f"{updated} tasks assigned to you.")
    assign_to_me.short_description = "👤 Assign to me"
    
    def send_reminders(self, request, queryset):
        updated = queryset.update(reminder_sent=True)
        self.message_user(request, f"Reminders sent for {updated} tasks.")
    send_reminders.short_description = "📧 Send reminders"
    
    def mark_high_priority(self, request, queryset):
        updated = queryset.update(priority='high')
        self.message_user(request, f"{updated} tasks marked as high priority.")
    mark_high_priority.short_description = "🔥 Mark as high priority"


@admin.register(CRMNote)
class CRMNoteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CRMNoteResource
    
    list_display = ('title_display', 'note_type_badge', 'account', 'contact', 'deal', 'created_by', 'is_private', 'is_pinned', 'created_at')
    list_filter = ('note_type', 'is_private', 'is_pinned', 'account', 'created_by', 'created_at')
    search_fields = ('title', 'content', 'contact__first_name', 'contact__last_name', 'deal__title')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['account', 'contact', 'deal', 'lead', 'created_by']
    
    fieldsets = (
        ('Note Details', {
            'fields': ('account', 'contact', 'deal', 'lead', 'title', 'content', 'note_type')
        }),
        ('Settings', {
            'fields': ('is_private', 'is_pinned', 'created_by')
        }),
        ('Attachment', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['pin_notes', 'unpin_notes', 'mark_private', 'mark_public']
    
    def title_display(self, obj):
        return obj.title or f"Note #{obj.id}"
    title_display.short_description = 'Title'
    
    def note_type_badge(self, obj):
        colors = {
            'general': '#6c757d',
            'call_log': '#28a745',
            'meeting_minutes': '#ffc107',
            'follow_up': '#17a2b8',
            'internal': '#fd7e14',
            'customer_feedback': '#6f42c1'
        }
        color = colors.get(obj.note_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_note_type_display()
        )
    note_type_badge.short_description = 'Type'
    
    def pin_notes(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f"{updated} notes pinned.")
    pin_notes.short_description = "📌 Pin notes"
    
    def unpin_notes(self, request, queryset):
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f"{updated} notes unpinned.")
    unpin_notes.short_description = "📌 Unpin notes"
    
    def mark_private(self, request, queryset):
        updated = queryset.update(is_private=True)
        self.message_user(request, f"{updated} notes marked as private.")
    mark_private.short_description = "🔒 Mark as private"
    
    def mark_public(self, request, queryset):
        updated = queryset.update(is_private=False)
        self.message_user(request, f"{updated} notes marked as public.")
    mark_public.short_description = "🌐 Mark as public"


@admin.register(DealProduct)
class DealProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = DealProductResource
    
    list_display = ('deal', 'product', 'quantity', 'unit_price', 'discount_percentage', 'total_amount', 'created_at')
    list_filter = ('deal__account', 'created_at')
    search_fields = ('deal__title', 'product__name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    autocomplete_fields = ['deal', 'product']


@admin.register(CRMPipeline)
class CRMPipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'is_default', 'is_active', 'stage_count', 'created_at')
    list_filter = ('is_default', 'is_active', 'account', 'created_at')
    search_fields = ('name', 'description', 'account__name')
    readonly_fields = ('created_at', 'updated_at', 'stage_count')
    autocomplete_fields = ['account']
    
    def stage_count(self, obj):
        return obj.stages.count()
    stage_count.short_description = 'Stages'


@admin.register(CRMPipelineStage)
class CRMPipelineStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'pipeline', 'probability', 'sort_order', 'is_closed_stage', 'is_won_stage')
    list_filter = ('pipeline', 'is_closed_stage', 'is_won_stage')
    search_fields = ('name', 'description', 'pipeline__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['pipeline']
    ordering = ['pipeline', 'sort_order']


@admin.register(CRMReport)
class CRMReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'account', 'created_by', 'generated_at', 'is_public', 'created_at')
    list_filter = ('report_type', 'is_public', 'account', 'created_by', 'created_at')
    search_fields = ('name', 'description', 'account__name')
    readonly_fields = ('created_at', 'updated_at', 'generated_at')
    autocomplete_fields = ['account', 'created_by']
    
    fieldsets = (
        ('Report Details', {
            'fields': ('account', 'name', 'report_type', 'description')
        }),
        ('Configuration', {
            'fields': ('filters', 'date_range_start', 'date_range_end')
        }),
        ('Data & Sharing', {
            'fields': ('data', 'generated_at', 'is_public', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Don't override admin site headers here - let the main admin handle it