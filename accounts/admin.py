from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import College, Property, PropertyImage, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Application role", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Application role", {"fields": ("email", "role")}),
    )
    list_display = ("id", "email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("id",)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", "address")


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
