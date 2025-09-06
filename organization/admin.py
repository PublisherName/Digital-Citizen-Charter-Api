from django.contrib import admin

from .forms import (
    DesignationForm,
    OrganizationForm,
)
from .models import (
    Department,
    DepartmentTemplate,
    Designation,
    DesignationTemplate,
    Organization,
    OrganizationTemplate,
)


class DepartmentInline(admin.StackedInline):
    model = Department
    extra = 0


class DesignationInline(admin.StackedInline):
    model = Designation
    extra = 0


class DesignationTemplateInline(admin.StackedInline):
    model = DesignationTemplate
    extra = 0


class DepartmentTemplateInline(admin.StackedInline):
    model = DepartmentTemplate
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    OrganizationAdmin class is used to customize the admin panel for the Organization model.
    """

    form = OrganizationForm
    search_fields = ("name", "tag_line", "district", "municipality")

    list_display = (
        "name",
        "tag_line",
        "province",
        "district",
        "contact_no",
        "is_active",
    )
    inlines = [DepartmentInline, DesignationInline]


@admin.register(OrganizationTemplate)
class OrganizationTemplateAdmin(admin.ModelAdmin):
    inlines = [DepartmentTemplateInline, DesignationTemplateInline]
    list_display = ("name", "description", "is_active")
    search_fields = ("name",)
