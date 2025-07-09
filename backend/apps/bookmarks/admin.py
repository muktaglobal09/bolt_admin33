from django.contrib import admin
from .models import Bookmark, BookmarkCollection, BookmarkCollectionItem, BusinessComparison, Shortlist, ShortlistItem


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'created_at')
    list_filter = ('created_at', 'business__category')
    search_fields = ('user__email', 'business__name', 'notes')
    readonly_fields = ('created_at', 'updated_at')


class BookmarkCollectionItemInline(admin.TabularInline):
    model = BookmarkCollectionItem
    extra = 0
    fields = ('bookmark', 'sort_order')


@admin.register(BookmarkCollection)
class BookmarkCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'bookmark_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('user__email', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'bookmark_count')
    inlines = [BookmarkCollectionItemInline]
    
    def bookmark_count(self, obj):
        return obj.bookmark_count
    bookmark_count.short_description = 'Bookmarks'


@admin.register(BookmarkCollectionItem)
class BookmarkCollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'bookmark', 'sort_order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('collection__name', 'bookmark__business__name')


@admin.register(BusinessComparison)
class BusinessComparisonAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'business_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'business_count')
    filter_horizontal = ('businesses',)
    
    def business_count(self, obj):
        return obj.business_count
    business_count.short_description = 'Businesses'


class ShortlistItemInline(admin.TabularInline):
    model = ShortlistItem
    extra = 0
    fields = ('business', 'priority', 'contacted', 'notes')


@admin.register(Shortlist)
class ShortlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ShortlistItemInline]


@admin.register(ShortlistItem)
class ShortlistItemAdmin(admin.ModelAdmin):
    list_display = ('shortlist', 'business', 'priority', 'contacted', 'created_at')
    list_filter = ('priority', 'contacted', 'created_at')
    search_fields = ('shortlist__name', 'business__name', 'notes')
    readonly_fields = ('created_at', 'updated_at')