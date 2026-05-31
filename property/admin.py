from django.contrib import admin

from .models import Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]
    list_display = ("id", "title", "owner", "city", "rent", "status", "created_at")
    list_filter = ("status", "city", "state")
    search_fields = ("title", "description", "address", "city", "owner__email")


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "is_primary", "sort_order", "created_at")
    list_filter = ("is_primary",)
    search_fields = ("property__title", "alt_text")
