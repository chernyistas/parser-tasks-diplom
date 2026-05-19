from django.contrib import admin

from .models import MockTask


@admin.register(MockTask)
class MockTaskAdmin(admin.ModelAdmin):
    list_display = ["title", "published_at", "is_processed"]
    list_filter = ["is_processed"]
