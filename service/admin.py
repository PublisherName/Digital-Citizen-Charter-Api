from django.contrib import admin

from .models import SampleDocments, Service, ServiceDetail


class SampleDocumentInline(admin.TabularInline):
    model = SampleDocments
    extra = 1
    fields = ("name", "file", "is_active")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "get_organization_count")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    filter_horizontal = ("organizations",)

    @admin.display(description="Allowed Organizations")
    def get_organization_count(self, obj):
        count = obj.organizations.count()
        if count == 0:
            return "All"
        return count


@admin.register(SampleDocments)
class SampleDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "service_detail", "file", "is_active")
    list_filter = ("service_detail",)
    search_fields = ("name",)
    autocomplete_fields = ("service_detail",)
    list_select_related = ("service_detail",)


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ("service", "organization", "is_active", "timeline", "fees")
    list_filter = ("is_active", "organization", "service")
    search_fields = ("service__name", "organization__name", "required_documents", "process_flow")
    autocomplete_fields = ("organization", "service", "responsible_employees")
    list_select_related = ("organization", "service")
    filter_horizontal = ("responsible_employees",)
    inlines = [SampleDocumentInline]
