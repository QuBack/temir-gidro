import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from .models import Lead


def _csv_safe(value: str) -> str:
    """Neutralises spreadsheet formulas in visitor-supplied text (CSV injection)."""
    return f"'{value}" if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["created_at", "name", "phone", "status", "source_page", "utm_source"]
    list_display_links = ["created_at", "name"]
    list_editable = ["status"]
    list_filter = ["status", "created_at", "utm_source", "language"]
    search_fields = ["name", "phone", "email", "message", "manager_note"]
    date_hierarchy = "created_at"
    list_per_page = 50
    actions = ["mark_in_progress", "mark_closed", "mark_spam", "export_csv"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "source_page",
        "landing_page",
        "referrer",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "language",
        "ip",
        "user_agent",
        "spam_reason",
    ]
    fieldsets = [
        (None, {"fields": ["status", "name", "phone", "email", "message", "manager_note"]}),
        (
            "Источник",
            {
                "fields": [
                    "source_page",
                    "landing_page",
                    "referrer",
                    "utm_source",
                    "utm_medium",
                    "utm_campaign",
                    "utm_content",
                    "utm_term",
                    "language",
                ]
            },
        ),
        (
            "Техническое",
            {
                "classes": ["collapse"],
                "fields": [
                    "created_at",
                    "updated_at",
                    "ip",
                    "user_agent",
                    "spam_reason",
                ],
            },
        ),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Spam is hidden unless explicitly filtered for.
        if request.GET.get("status__exact") is None and request.resolver_match.url_name == "leads_lead_changelist":
            qs = qs.exclude(status=Lead.Status.SPAM)
        return qs

    @admin.action(description="Отметить: в работе")
    def mark_in_progress(self, request, queryset):
        queryset.update(status=Lead.Status.IN_PROGRESS)

    @admin.action(description="Отметить: закрыта")
    def mark_closed(self, request, queryset):
        queryset.update(status=Lead.Status.CLOSED)

    @admin.action(description="Отметить: спам")
    def mark_spam(self, request, queryset):
        queryset.update(status=Lead.Status.SPAM)

    @admin.action(description="Выгрузить в CSV (Excel)")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"leads-{timezone.localdate():%Y-%m-%d}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("﻿")  # BOM: Excel opens UTF-8 Cyrillic correctly
        writer = csv.writer(response, delimiter=";")
        columns = [
            "created_at",
            "status",
            "name",
            "phone",
            "email",
            "message",
            "manager_note",
            "source_page",
            "utm_source",
            "utm_medium",
            "utm_campaign",
        ]
        writer.writerow([Lead._meta.get_field(c).verbose_name for c in columns])
        for lead in queryset:
            row = []
            for c in columns:
                if c == "created_at":
                    row.append(timezone.localtime(lead.created_at).strftime("%d.%m.%Y %H:%M"))
                elif c == "status":
                    row.append(lead.get_status_display())
                elif c == "phone":  # already normalised to digits and "+"
                    row.append(lead.phone)
                else:
                    row.append(_csv_safe(getattr(lead, c)))
            writer.writerow(row)
        return response
