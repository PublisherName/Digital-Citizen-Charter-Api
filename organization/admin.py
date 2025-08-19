import nested_admin
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


class DesignationTemplateInline(nested_admin.NestedTabularInline):
    model = DesignationTemplate
    extra = 1


class DepartmentTemplateInline(nested_admin.NestedTabularInline):
    model = DepartmentTemplate
    extra = 1
    inlines = [DesignationTemplateInline]


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """
    DesignationAdmin class is used to customize the admin panel for the Designation model.
    """

    form = DesignationForm

    list_display = ("title", "description", "priority", "organization", "department")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    OrganizationAdmin class is used to customize the admin panel for the Organization model.
    """

    form = OrganizationForm

    list_display = (
        "name",
        "tag_line",
        "province",
        "district",
        "contact_no",
        "is_active",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    DepartmentAdmin class is used to customize the admin panel for the Department model.
    """

    list_display = ("name", "organization", "contact_no", "email", "is_active")


@admin.register(OrganizationTemplate)
class OrganizationTemplateAdmin(nested_admin.NestedModelAdmin):
    """
    OrganizationTemplateAdmin class is used to nest the admin panel for OrganizationTemplate model.
    """

    inlines = [DepartmentTemplateInline]
    list_display = ("name", "is_active")
    search_fields = ("name",)
