from django.contrib import admin  # noqa F401
from django.db.models import QuerySet
from django.http import HttpRequest

from django.utils import timezone

from .models import Category


@admin.action(description="Архивировать категории")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True, modified_at=timezone.now())


@admin.action(description="Разархивировать категории")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False, modified_at=timezone.now())


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ Категория"""

    actions = [
        mark_archived,
        mark_unarchived,
    ]
    list_display = (
        "pk",
        "parent_name_id",
        "name",
        "created_at",
        "modified_at",
        "archived",
    )
    list_display_links = (
        "pk",
        "name",
    )
    ordering = ("pk",)
    empty_value_display = "NULL"
    search_fields = [
        "name",
    ]
    search_help_text = "Поиск категории по названию"
    list_filter = (
        "created_at",
        "modified_at",
    )
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "parent",
                ),
            },
        ),
        (
            "Дополнительные функции",
            {
                "fields": ("archived",),
                "description": "Поле 'архивировано' используеться для 'soft delete'",
            },
        ),
    ]

    @admin.display(description="родительская категория")
    def parent_name_id(self, obj: Category) -> str:
        if obj.parent is None:
            return
        return str(obj.parent.id)
