from django.contrib import admin

from .models import College


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", "address")
