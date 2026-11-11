from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "due_date", "priority", "status")
    list_filter = ("status", "priority")
    search_fields = ("title",)
