from django.contrib import admin


class TimeStampedModelAdmin(admin.ModelAdmin):
    """Base admin class for timestamped models."""
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('__str__', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')


class SEOModelAdmin(admin.ModelAdmin):
    """Base admin class for SEO models."""
    fieldsets = (
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'slug'),
            'classes': ('collapse',)
        }),
    )
    prepopulated_fields = {'slug': ('name',)}