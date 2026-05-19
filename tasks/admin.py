from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "status", "published_at"]
    list_filter = ["source", "status"]
    search_fields = ["title", "description"]
