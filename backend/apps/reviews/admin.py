from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewReply, ReviewImage, ReviewHelpful, ReviewReport


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    fields = ('image', 'caption')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'business', 'user', 'rating', 'is_approved', 'is_featured',
        'is_verified_purchase', 'created_at'
    )
    list_filter = (
        'rating', 'is_approved', 'is_featured', 'is_verified_purchase',
        'created_at', 'business__category'
    )
    search_fields = ('business__name', 'user__email', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ReviewImageInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('business', 'user', 'rating', 'title', 'comment')
        }),
        ('Detailed Ratings', {
            'fields': ('service_quality', 'value_for_money', 'communication', 'timeliness'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_approved', 'is_featured', 'is_verified_purchase', 'approved_at', 'approved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews', 'feature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True, approved_by=request.user)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"
    
    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} reviews featured.")
    feature_reviews.short_description = "Feature selected reviews"


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'business_user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('review__business__name', 'business_user__email', 'message')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__business__name', 'caption')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__business__name', 'user__email')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('review', 'reported_by', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('review__business__name', 'reported_by__email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['resolve_reports']
    
    def resolve_reports(self, request, queryset):
        queryset.update(is_resolved=True, resolved_by=request.user)
        self.message_user(request, f"{queryset.count()} reports resolved.")
    resolve_reports.short_description = "Resolve selected reports"