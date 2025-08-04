from django.contrib import admin
from .models import *

# Museum Admin
@admin.register(MuseumCategory)
class MuseumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Museum)
class MuseumAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'category', 'status', 'is_featured', 'view_count', 'created_at']
    list_filter = ['category', 'status', 'location', 'is_featured', 'created_at']
    search_fields = ['name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['view_count', 'visitor_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'long_description', 'category', 'tags')
        }),
        ('Location & Contact', {
            'fields': ('location', 'address', 'city', 'country', 'latitude', 'longitude', 
                      'phone', 'email', 'website')
        }),
        ('Media', {
            'fields': ('main_image', 'gallery_images', 'virtual_tour_url', 'video_url')
        }),
        ('Operations', {
            'fields': ('status', 'access_level', 'opening_hours', 'admission_fee', 'admission_info')
        }),
        ('Features', {
            'fields': ('has_parking', 'has_wifi', 'has_restaurant', 'has_gift_shop', 
                      'is_wheelchair_accessible', 'has_guided_tours')
        }),
        ('Statistics', {
            'fields': ('established_year', 'visitor_count', 'view_count', 'rating', 'is_featured')
        }),
        ('Administrative', {
            'fields': ('curator', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(MuseumExhibition)
class MuseumExhibitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'museum', 'exhibition_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['exhibition_type', 'is_active', 'is_featured', 'start_date']
    search_fields = ['title', 'description', 'museum__name']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'


@admin.register(MuseumReview)
class MuseumReviewAdmin(admin.ModelAdmin):
    list_display = ['museum', 'user', 'rating', 'is_approved', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified', 'created_at']
    search_fields = ['museum__name', 'user__username', 'title', 'review_text']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']


@admin.register(MuseumCollection)
class MuseumCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'curator', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['museums']


# Other existing models can be registered here as well
# Register your models here.
