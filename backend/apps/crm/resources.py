from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from .models import (
    Lead, CRMContact, CRMDeal, CRMActivity, CRMTask, CRMNote,
    DealProduct, CRMPipeline, CRMPipelineStage
)
from apps.businesses.models import Business
from django.contrib.auth import get_user_model

User = get_user_model()


class LeadResource(resources.ModelResource):
    """Import/Export resource for Lead model."""
    
    business = fields.Field(
        column_name='business',
        attribute='business',
        widget=ForeignKeyWidget(Business, 'name')
    )
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User, 'email')
    )
    assigned_to = fields.Field(
        column_name='assigned_to',
        attribute='assigned_to',
        widget=ForeignKeyWidget(User, 'email')
    )
    full_name = fields.Field(
        column_name='full_name',
        attribute='full_name',
        readonly=True
    )
    
    class Meta:
        model = Lead
        fields = (
            'id', 'business', 'first_name', 'last_name', 'full_name', 'email',
            'phone_number', 'company', 'designation', 'status', 'lead_source',
            'priority', 'lead_score', 'owner', 'assigned_to', 'campaign_name',
            'last_contacted', 'next_follow_up', 'created_at', 'updated_at'
        )
        export_order = fields


class CRMContactResource(resources.ModelResource):
    """Import/Export resource for CRMContact model."""
    
    account = fields.Field(
        column_name='account',
        attribute='account',
        widget=ForeignKeyWidget(Business, 'name')
    )
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User, 'email')
    )
    full_name = fields.Field(
        column_name='full_name',
        attribute='full_name',
        readonly=True
    )
    
    class Meta:
        model = CRMContact
        fields = (
            'id', 'account', 'first_name', 'last_name', 'full_name', 'email',
            'phone_number', 'company', 'designation', 'contact_type',
            'lead_source', 'owner', 'city', 'state', 'country',
            'last_contacted', 'is_active', 'created_at', 'updated_at'
        )
        export_order = fields


class CRMDealResource(resources.ModelResource):
    """Import/Export resource for CRMDeal model."""
    
    account = fields.Field(
        column_name='account',
        attribute='account',
        widget=ForeignKeyWidget(Business, 'name')
    )
    contact = fields.Field(
        column_name='contact',
        attribute='contact',
        widget=ForeignKeyWidget(CRMContact, 'full_name')
    )
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User, 'email')
    )
    assigned_to = fields.Field(
        column_name='assigned_to',
        attribute='assigned_to',
        widget=ForeignKeyWidget(User, 'email')
    )
    
    class Meta:
        model = CRMDeal
        fields = (
            'id', 'account', 'contact', 'title', 'description', 'value',
            'currency', 'stage', 'priority', 'probability', 'owner',
            'assigned_to', 'expected_close_date', 'actual_close_date',
            'last_contacted', 'lead_source', 'created_at', 'updated_at'
        )
        export_order = fields


class CRMActivityResource(resources.ModelResource):
    """Import/Export resource for CRMActivity model."""
    
    account = fields.Field(
        column_name='account',
        attribute='account',
        widget=ForeignKeyWidget(Business, 'name')
    )
    contact = fields.Field(
        column_name='contact',
        attribute='contact',
        widget=ForeignKeyWidget(CRMContact, 'full_name')
    )
    deal = fields.Field(
        column_name='deal',
        attribute='deal',
        widget=ForeignKeyWidget(CRMDeal, 'title')
    )
    lead = fields.Field(
        column_name='lead',
        attribute='lead',
        widget=ForeignKeyWidget(Lead, 'full_name')
    )
    assigned_to = fields.Field(
        column_name='assigned_to',
        attribute='assigned_to',
        widget=ForeignKeyWidget(User, 'email')
    )
    
    class Meta:
        model = CRMActivity
        fields = (
            'id', 'account', 'contact', 'deal', 'lead', 'activity_type',
            'subject', 'description', 'status', 'activity_date',
            'scheduled_at', 'completed_at', 'duration_minutes',
            'assigned_to', 'outcome', 'follow_up_required',
            'created_at', 'updated_at'
        )
        export_order = fields


class CRMTaskResource(resources.ModelResource):
    """Import/Export resource for CRMTask model."""
    
    account = fields.Field(
        column_name='account',
        attribute='account',
        widget=ForeignKeyWidget(Business, 'name')
    )
    contact = fields.Field(
        column_name='contact',
        attribute='contact',
        widget=ForeignKeyWidget(CRMContact, 'full_name')
    )
    deal = fields.Field(
        column_name='deal',
        attribute='deal',
        widget=ForeignKeyWidget(CRMDeal, 'title')
    )
    lead = fields.Field(
        column_name='lead',
        attribute='lead',
        widget=ForeignKeyWidget(Lead, 'full_name')
    )
    assigned_to = fields.Field(
        column_name='assigned_to',
        attribute='assigned_to',
        widget=ForeignKeyWidget(User, 'email')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'email')
    )
    
    class Meta:
        model = CRMTask
        fields = (
            'id', 'account', 'contact', 'deal', 'lead', 'title',
            'description', 'task_type', 'priority', 'status',
            'due_date', 'completed_at', 'estimated_hours',
            'actual_hours', 'assigned_to', 'created_by',
            'reminder_sent', 'created_at', 'updated_at'
        )
        export_order = fields


class CRMNoteResource(resources.ModelResource):
    """Import/Export resource for CRMNote model."""
    
    account = fields.Field(
        column_name='account',
        attribute='account',
        widget=ForeignKeyWidget(Business, 'name')
    )
    contact = fields.Field(
        column_name='contact',
        attribute='contact',
        widget=ForeignKeyWidget(CRMContact, 'full_name')
    )
    deal = fields.Field(
        column_name='deal',
        attribute='deal',
        widget=ForeignKeyWidget(CRMDeal, 'title')
    )
    lead = fields.Field(
        column_name='lead',
        attribute='lead',
        widget=ForeignKeyWidget(Lead, 'full_name')
    )
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'email')
    )
    
    class Meta:
        model = CRMNote
        fields = (
            'id', 'account', 'contact', 'deal', 'lead', 'title',
            'content', 'note_type', 'is_private', 'is_pinned',
            'created_by', 'created_at', 'updated_at'
        )
        export_order = fields


class DealProductResource(resources.ModelResource):
    """Import/Export resource for DealProduct model."""
    
    deal = fields.Field(
        column_name='deal',
        attribute='deal',
        widget=ForeignKeyWidget(CRMDeal, 'title')
    )
    
    class Meta:
        model = DealProduct
        fields = (
            'id', 'deal', 'product', 'quantity', 'unit_price',
            'discount_percentage', 'total_amount', 'created_at'
        )
        export_order = fields