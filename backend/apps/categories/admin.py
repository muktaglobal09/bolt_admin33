from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, CategoryAttribute, CategoryAttributeOption, Tag
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category

class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    extra = 0
    fields = ('name', 'attribute_type', 'is_required', 'is_filterable', 'sort_order')


class CategoryAttributeOptionInline(admin.TabularInline):
    model = CategoryAttributeOption
    extra = 0
    fields = ('value', 'display_name', 'sort_order')


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, MPTTModelAdmin):
    resource_class = CategoryResource


    list_display = ('name', 'parent', 'is_active', 'sort_order', 'business_count', 'created_at')
    list_filter = ('is_active', 'is_service', 'is_product', 'is_manufacturing', 'is_freelancer', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'business_count')
    inlines = [CategoryAttributeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent', 'sort_order', 'is_active')
        }),
        ('Visual', {
            'fields': ('icon', 'image', 'color')
        }),
        ('Business Types', {
            'fields': ('is_service', 'is_product', 'is_manufacturing', 'is_freelancer'),
            'description': 'Select which business types this category applies to'
        }),
        ('SEO', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def business_count(self, obj):
        return obj.business_count
    business_count.short_description = 'Businesses'


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'attribute_type', 'is_required', 'is_filterable', 'sort_order')
    list_filter = ('attribute_type', 'is_required', 'is_filterable', 'category')
    search_fields = ('name', 'category__name')
    inlines = [CategoryAttributeOptionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'attribute_type', 'help_text')
        }),
        ('Settings', {
            'fields': ('is_required', 'is_filterable', 'sort_order')
        }),
    )


@admin.register(CategoryAttributeOption)
class CategoryAttributeOptionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'attribute', 'value', 'sort_order')
    list_filter = ('attribute__category', 'attribute')
    search_fields = ('display_name', 'value', 'attribute__name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')